package miproyecto.estacionamiento.dto;

public class VehiculoRequest {
    private int totalVehiculos = 10;
    private int capacidad = 4;
    private long tiempoMinMs = 1000;
    private long tiempoMaxMs = 3000;

    public int getTotalVehiculos() { return totalVehiculos; }
    public void setTotalVehiculos(int totalVehiculos) { this.totalVehiculos = totalVehiculos; }
    public int getCapacidad() { return capacidad; }
    public void setCapacidad(int capacidad) { this.capacidad = capacidad; }
    public long getTiempoMinMs() { return tiempoMinMs; }
    public void setTiempoMinMs(long tiempoMinMs) { this.tiempoMinMs = tiempoMinMs; }
    public long getTiempoMaxMs() { return tiempoMaxMs; }
    public void setTiempoMaxMs(long tiempoMaxMs) { this.tiempoMaxMs = tiempoMaxMs; }
}