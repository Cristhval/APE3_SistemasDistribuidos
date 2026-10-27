package miproyecto.estacionamiento.service;

import 	miproyecto.estacionamiento.model.Vehiculo;
import 	miproyecto.estacionamiento.util.LogBuffer;


import java.util.Random;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicInteger;

public class VehiculoWorker implements Runnable {

    private final Vehiculo vehiculo;
    private final Semaphore espacios;          // semáforo contador
    private final AtomicInteger ocupados;      // métrica en vivo
    private final AtomicInteger maxSimultaneos;
    private final LogBuffer log;
    private final CountDownLatch latch;
    private final Random random = new Random();

    public VehiculoWorker(Vehiculo vehiculo, Semaphore espacios,
                          AtomicInteger ocupados, AtomicInteger maxSimultaneos,
                          LogBuffer log, CountDownLatch latch) {
        this.vehiculo = vehiculo;
        this.espacios = espacios;
        this.ocupados = ocupados;
        this.maxSimultaneos = maxSimultaneos;
        this.log = log;
        this.latch = latch;
    }

    @Override
    public void run() {
        try {
            int id = vehiculo.getId();
            log.add("Vehículo " + id + " llega al estacionamiento");

            // wait(espacios): bloquea si no hay espacio
            espacios.acquire();

            int actuales = ocupados.incrementAndGet();
            maxSimultaneos.accumulateAndGet(actuales, Math::max);
            log.add("Vehículo " + id + " INGRESA (ocupados: " + actuales + ")");

            // simular permanencia
            Thread.sleep(vehiculo.getTiempoEstacionadoMs());

            int restantes = ocupados.decrementAndGet();
            log.add("Vehículo " + id + " SALE (ocupados: " + restantes + ")");

            // signal(espacios)
            espacios.release();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            latch.countDown();
        }
    }
}