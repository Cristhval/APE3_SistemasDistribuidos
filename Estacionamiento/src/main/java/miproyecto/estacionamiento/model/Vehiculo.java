package miproyecto.estacionamiento.model;

public class Vehiculo {
    private final int id;
    private final long tiempoEstacionadoMs;

    public Vehiculo(int id, long tiempoEstacionadoMs) {
        this.id = id;
        this.tiempoEstacionadoMs = tiempoEstacionadoMs;
    }

    public int getId() { return id; }
    public long getTiempoEstacionadoMs() { return tiempoEstacionadoMs; }
}