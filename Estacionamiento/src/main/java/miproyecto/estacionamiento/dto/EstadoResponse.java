package miproyecto.estacionamiento.dto;

import 	miproyecto.estacionamiento.model.EventoLog;
import java.util.List;

public class EstadoResponse {
    private boolean ejecutando;
    private int ocupados;
    private int capacidad;
    private int maxSimultaneos;
    private List<EventoLog> eventos;

    public EstadoResponse(boolean ejecutando, int ocupados, int capacidad,
                          int maxSimultaneos, List<EventoLog> eventos) {
        this.ejecutando = ejecutando;
        this.ocupados = ocupados;
        this.capacidad = capacidad;
        this.maxSimultaneos = maxSimultaneos;
        this.eventos = eventos;
    }

    public boolean isEjecutando() { return ejecutando; }
    public int getOcupados() { return ocupados; }
    public int getCapacidad() { return capacidad; }
    public int getMaxSimultaneos() { return maxSimultaneos; }
    public List<EventoLog> getEventos() { return eventos; }
}