package miproyecto.estacionamiento.service;

import miproyecto.estacionamiento.dto.VehiculoRequest;
import miproyecto.estacionamiento.model.Vehiculo;
import miproyecto.estacionamiento.util.LogBuffer;
import org.springframework.stereotype.Service;

import java.util.Random;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

@Service
public class EstacionamientoService {

    private final LogBuffer log;
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final Random random = new Random();

    private volatile boolean ejecutando = false;
    private volatile int capacidad = 4;
    private final AtomicInteger ocupados = new AtomicInteger(0);
    private final AtomicInteger maxSimultaneos = new AtomicInteger(0);

    public EstacionamientoService(LogBuffer log) {
        this.log = log;
    }

    public synchronized void iniciar(VehiculoRequest req) {
        if (ejecutando) {
            throw new IllegalStateException("Ya hay una simulación en curso");
        }
        ejecutando = true;
        log.clear();
        ocupados.set(0);
        maxSimultaneos.set(0);
        this.capacidad = req.getCapacidad();

        // Semáforo contador inicializado en la capacidad (4 por defecto)
        Semaphore espacios = new Semaphore(req.getCapacidad(), true);
        CountDownLatch latch = new CountDownLatch(req.getTotalVehiculos());

        log.add("=== Inicio de simulación: " + req.getTotalVehiculos()
                + " vehículos, " + req.getCapacidad() + " espacios ===");

        for (int i = 1; i <= req.getTotalVehiculos(); i++) {
            long tiempo = req.getTiempoMinMs() +
                    (long) (random.nextDouble() * (req.getTiempoMaxMs() - req.getTiempoMinMs()));
            Vehiculo v = new Vehiculo(i, tiempo);
            executor.submit(new VehiculoWorker(v, espacios, ocupados, maxSimultaneos, log, latch));
        }

        // Hilo monitor: marca fin cuando todos terminan
        new Thread(() -> {
            try {
                latch.await();
                log.add("=== Simulación finalizada. Máx. simultáneos: "
                        + maxSimultaneos.get() + " ===");
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                ejecutando = false;
            }
        }).start();
    }

    public boolean isEjecutando() { return ejecutando; }
    public int getOcupados() { return ocupados.get(); }
    public int getCapacidad() { return capacidad; }
    public int getMaxSimultaneos() { return maxSimultaneos.get(); }
    public LogBuffer getLog() { return log; }
}