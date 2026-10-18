package com.arelys.fabrica.service;

import org.springframework.stereotype.Service;

import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

@Service
public class FabricaService {

    /** Capacidad fija del almacén compartido (nunca se configura). */
    private static final int CAPACIDAD = 5;

    /* ---- Límites razonables de configuración ---- */
    private static final int MIN_PRODUCTORES = 1, MAX_PRODUCTORES = 10;
    private static final int MIN_CONSUMIDORES = 1, MAX_CONSUMIDORES = 10;
    private static final int MIN_PIEZAS = 1, MAX_PIEZAS = 50;
    private static final long MIN_RETARDO = 0L, MAX_RETARDO = 6000L;

    private static final int MAX_LOGS = 400;
    /** Espera acotada del consumidor para poder detectar el fin de la producción. */
    private static final long ESPERA_SONDEO_MS = 250L;

    /* ---- Recurso compartido y sincronización ---- */
    private final BlockingQueue<String> almacen = new ArrayBlockingQueue<>(CAPACIDAD);
    private final Semaphore espacios = new Semaphore(CAPACIDAD, true); // espacios libres (inicia en 5)
    private final Semaphore elementos = new Semaphore(0, true);        // elementos disponibles (inicia en 0)
    private final Object mutex = new Object();                         // mutex del recurso compartido

    /* ---- Estado de control (visible entre hilos) ---- */
    private volatile boolean activo = false;
    private volatile int generacion = 0;               // invalida hilos de ejecuciones anteriores
    private volatile long retardoMs = 1500L;           // tiempo por operación (>= 0)
    private volatile int piezasPorProductor = 10;
    private volatile int numProductores = 2;           // ahora configurable
    private volatile int numConsumidores = 2;          // ahora configurable

    private final List<Thread> hilos = Collections.synchronizedList(new ArrayList<>());
    private final List<Map<String, Object>> logs = Collections.synchronizedList(new ArrayList<>());
    private final List<String> fabricadas = Collections.synchronizedList(new ArrayList<>());

    /** Productores que aún no han terminado: cuando llega a 0 se "cierra" la producción. */
    private final AtomicInteger productoresActivos = new AtomicInteger(0);

    private volatile int producidos = 0;
    private volatile int consumidos = 0;

    private static final DateTimeFormatter HORA = DateTimeFormatter.ofPattern("HH:mm:ss");

    /* =========================================================
       Bitácora
       ========================================================= */
    private void agregarLog(String tipo, String mensaje) {
        Map<String, Object> entrada = new HashMap<>();
        entrada.put("hora", LocalTime.now().format(HORA));
        entrada.put("tipo", tipo);
        entrada.put("mensaje", mensaje);
        synchronized (logs) {
            if (logs.size() >= MAX_LOGS) logs.remove(0);
            logs.add(entrada);
        }
    }

    /* =========================================================
       Validación de parámetros
       ========================================================= */
    private void validar(int productores, int consumidores, int piezas, long retardo) {
        List<String> errores = new ArrayList<>();
        if (productores < MIN_PRODUCTORES || productores > MAX_PRODUCTORES) {
            errores.add("Número de productores debe ser un entero entre "
                    + MIN_PRODUCTORES + " y " + MAX_PRODUCTORES + " (recibido: " + productores + ")");
        }
        if (consumidores < MIN_CONSUMIDORES || consumidores > MAX_CONSUMIDORES) {
            errores.add("Número de consumidores debe ser un entero entre "
                    + MIN_CONSUMIDORES + " y " + MAX_CONSUMIDORES + " (recibido: " + consumidores + ")");
        }
        if (piezas < MIN_PIEZAS || piezas > MAX_PIEZAS) {
            errores.add("Piezas por productor debe ser un entero entre "
                    + MIN_PIEZAS + " y " + MAX_PIEZAS + " (recibido: " + piezas + ")");
        }
        if (retardo < MIN_RETARDO || retardo > MAX_RETARDO) {
            errores.add("Tiempo por operación debe estar entre "
                    + MIN_RETARDO + " y " + MAX_RETARDO + " ms (recibido: " + retardo + ")");
        }
        if (!errores.isEmpty()) {
            throw new IllegalArgumentException(String.join(". ", errores) + ".");
        }
    }

    /* =========================================================
       Control de la simulación
       ========================================================= */
    public synchronized Map<String, Object> iniciarSimulacion(Integer productores, Integer consumidores,
                                                              Integer piezas, Long retardo) {
        // Evita arrancar una simulación mientras otra sigue en curso.
        if (activo) {
            return Map.of("mensaje", "La simulación ya está en marcha. Deténgala antes de iniciar otra.");
        }

        int p = (productores != null) ? productores : numProductores;
        int c = (consumidores != null) ? consumidores : numConsumidores;
        int k = (piezas != null) ? piezas : piezasPorProductor;
        long r = (retardo != null) ? retardo : retardoMs;

        validar(p, c, k, r);

        numProductores = p;
        numConsumidores = c;
        piezasPorProductor = k;
        retardoMs = r;

        // Reinicio coherente del estado compartido (no hay hilos activos aquí).
        generacion++;
        final int gen = generacion;

        synchronized (almacen) { almacen.clear(); }
        synchronized (logs) { logs.clear(); }
        synchronized (fabricadas) { fabricadas.clear(); }
        synchronized (hilos) { hilos.clear(); }

        producidos = 0;
        consumidos = 0;

        // Sincronización coherente en cada ejecución:
        //   espacios  -> 5 (capacidad completa)
        //   elementos -> 0 (almacén vacío)
        //   mutex     -> el mismo objeto monitor de siempre
        elementos.drainPermits();
        espacios.drainPermits();
        espacios.release(CAPACIDAD);
        productoresActivos.set(numProductores);

        activo = true;

        int totalPiezas = numProductores * k;
        agregarLog("inicio", "Simulación iniciada · " + numProductores + " productor(es), "
                + numConsumidores + " consumidor(es), " + k + " piezas/productor (" + totalPiezas
                + " en total) · ritmo " + r + " ms · capacidad " + CAPACIDAD);

        List<Thread> trabajadores = new ArrayList<>();

        // Productores (desfase escalonado para que los eventos no ocurran de golpe).
        for (int i = 1; i <= numProductores; i++) {
            final int id = i;
            final long desfase = (numProductores > 1) ? (long) (i - 1) * r / numProductores : 0;
            Thread t = new Thread(() -> ejecutarProductor(id, gen, desfase), "Productor-" + id);
            trabajadores.add(t);
            hilos.add(t);
        }

        // Consumidores (entran intercalados con los productores).
        for (int i = 1; i <= numConsumidores; i++) {
            final int id = i;
            long desfase = r / 2 + (numConsumidores > 1 ? (long) (i - 1) * r / numConsumidores : 0);
            desfase = Math.min(desfase, r);
            final long desfaseFinal = desfase;
            Thread t = new Thread(() -> ejecutarConsumidor(id, gen, desfaseFinal), "Consumidor-" + id);
            trabajadores.add(t);
            hilos.add(t);
        }

        for (Thread t : trabajadores) t.start();

        // Vigilante: al terminar todos los hilos cierra la simulación con un log final.
        Thread vigilante = new Thread(() -> {
            for (Thread t : trabajadores) {
                try {
                    t.join();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
            synchronized (FabricaService.this) {
                if (gen == generacion && activo) {
                    activo = false;
                    generacion++;
                    agregarLog("fin", "Simulación finalizada · " + producidos + " producidas, "
                            + consumidos + " consumidas, " + almacen.size() + " en el almacén");
                }
            }
        }, "Vigilante");
        vigilante.start();

        return Map.of(
                "mensaje", "Simulación iniciada correctamente",
                "productores", numProductores,
                "consumidores", numConsumidores,
                "piezasPorProductor", k,
                "totalPiezas", totalPiezas,
                "retardo", r);
    }

    public synchronized Map<String, Object> detenerSimulacion() {
        if (!activo) {
            return Map.of("mensaje", "La simulación no está en marcha");
        }
        activo = false;
        generacion++; // invalida los hilos en curso
        synchronized (hilos) {
            for (Thread t : hilos) t.interrupt();
            hilos.clear();
        }
        agregarLog("fin", "Simulación detenida por el usuario");
        return Map.of("mensaje", "Simulación detenida");
    }

    /** Cambia el ritmo (ms por operación) sin reiniciar la simulación. */
    public synchronized Map<String, Object> configurarVelocidad(long retardo) {
        if (retardo < MIN_RETARDO || retardo > MAX_RETARDO) {
            throw new IllegalArgumentException("Tiempo por operación debe estar entre "
                    + MIN_RETARDO + " y " + MAX_RETARDO + " ms (recibido: " + retardo + ").");
        }
        retardoMs = retardo;
        agregarLog("inicio", "Ritmo ajustado a " + retardoMs + " ms por operación");
        return Map.of("mensaje", "Velocidad actualizada", "retardo", retardoMs);
    }

    /* =========================================================
       Hilos productores / consumidores
       ========================================================= */
    private void esperarDesfase(long desfase) {
        if (desfase <= 0) return;
        try {
            Thread.sleep(desfase);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    /** Pausa entre operaciones. Con 0 ms se cede el turno (sin bloquear). */
    private void dormir(long ms) throws InterruptedException {
        if (ms > 0) {
            Thread.sleep(ms);
        } else {
            Thread.yield();
        }
    }

    private void ejecutarProductor(int id, int gen, long desfase) {
        esperarDesfase(desfase);
        try {
            for (int i = 1; i <= piezasPorProductor; i++) {
                if (!activo || gen != generacion) return;
                String pieza = "Pieza-" + id + "-" + i;
                try {
                    if (espacios.availablePermits() == 0) {
                        agregarLog("espera", "Productor " + id + " espera: almacén lleno (" + CAPACIDAD + "/" + CAPACIDAD + ")");
                    }
                    espacios.acquire(); // se bloquea solo si el almacén está lleno

                    boolean colocado = false;
                    synchronized (mutex) {
                        if (activo && gen == generacion) {
                            almacen.put(pieza);
                            producidos++;
                            synchronized (fabricadas) {
                                fabricadas.add(pieza);
                                if (fabricadas.size() > 12) fabricadas.remove(0);
                            }
                            agregarLog("llega", "Productor " + id + " fabricó " + pieza);
                            agregarLog("ingresa", pieza + " ingresó al almacén ["
                                    + almacen.size() + "/" + CAPACIDAD + "]");
                            colocado = true;
                        }
                    }

                    if (!colocado) return; // el permiso se descarta (se reinicia en la próxima simulación)
                    elementos.release();   // avisa que hay un elemento disponible
                    dormir(retardoMs);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        } finally {
            // CIERRE DE PRODUCTORES: al terminar el último, se marca el fin de la producción.
            if (gen == generacion) {
                int restantes = productoresActivos.decrementAndGet();
                if (restantes <= 0) {
                    agregarLog("fin", "Producción finalizada: no se generarán más piezas");
                }
            }
        }
    }

    private void ejecutarConsumidor(int id, int gen, long desfase) {
        esperarDesfase(desfase);
        boolean avisoVacio = false;
        while (activo && gen == generacion) {
            // SEÑALIZACIÓN DE FIN: si ya no hay productores activos y el almacén quedó vacío,
            // el consumidor termina (sin bloquearse indefinidamente).
            if (productoresActivos.get() == 0 && almacen.isEmpty()) {
                return;
            }
            try {
                if (!avisoVacio && productoresActivos.get() > 0 && elementos.availablePermits() == 0) {
                    agregarLog("espera", "Consumidor " + id + " espera: almacén vacío (0/" + CAPACIDAD + ")");
                    avisoVacio = true;
                }

                // Espera acotada: permite volver a evaluar la condición de fin.
                if (!elementos.tryAcquire(ESPERA_SONDEO_MS, TimeUnit.MILLISECONDS)) {
                    continue;
                }

                boolean retirado = false;
                synchronized (mutex) {
                    if (activo && gen == generacion && !almacen.isEmpty()) {
                        String pieza = almacen.take();
                        consumidos++;
                        agregarLog("sale", "Consumidor " + id + " retiró " + pieza
                                + " [" + almacen.size() + "/" + CAPACIDAD + "]");
                        retirado = true;
                    }
                }

                if (!retirado) {
                    elementos.release(); // no había nada: se devuelve el permiso y se reintenta
                    continue;
                }
                espacios.release();      // libera un espacio del almacén
                dormir(retardoMs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
    }

    /* =========================================================
       Estado para el frontend
       ========================================================= */
    public Map<String, Object> obtenerEstado() {
        Map<String, Object> estado = new HashMap<>();
        estado.put("activo", activo);
        estado.put("almacen", new ArrayList<>(almacen));
        estado.put("logs", new ArrayList<>(logs));
        estado.put("fabricadas", new ArrayList<>(fabricadas));
        estado.put("producidos", producidos);
        estado.put("consumidos", consumidos);
        estado.put("capacidad", CAPACIDAD);
        estado.put("retardo", retardoMs);
        estado.put("productores", numProductores);
        estado.put("consumidores", numConsumidores);
        estado.put("piezasPorProductor", piezasPorProductor);
        estado.put("totalPiezas", numProductores * piezasPorProductor);
        estado.put("productoresActivos", productoresActivos.get());
        estado.put("hilos", nombresHilos());
        return estado;
    }

    private List<String> nombresHilos() {
        List<String> nombres = new ArrayList<>();
        synchronized (hilos) {
            for (Thread t : hilos) {
                if (t.isAlive()) nombres.add(t.getName());
            }
        }
        return nombres;
    }
}
