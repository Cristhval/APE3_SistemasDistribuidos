package miproyecto.estacionamiento.controller;

import miproyecto.estacionamiento.dto.EstadoResponse;
import miproyecto.estacionamiento.dto.VehiculoRequest;
import miproyecto.estacionamiento.service.EstacionamientoService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/estacionamiento")
public class EstacionamientoController {

    private final EstacionamientoService service;

    public EstacionamientoController(EstacionamientoService service) {
        this.service = service;
    }

    @PostMapping("/iniciar")
    public ResponseEntity<?> iniciar(@RequestBody VehiculoRequest req) {
        try {
            service.iniciar(req);
            return ResponseEntity.ok(Map.of("mensaje", "Simulación iniciada"));
        } catch (IllegalStateException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/estado")
    public EstadoResponse estado() {
        return new EstadoResponse(
                service.isEjecutando(),
                service.getOcupados(),
                service.getCapacidad(),
                service.getMaxSimultaneos(),
                service.getLog().getEventos()
        );
    }

    @PostMapping("/limpiar")
    public ResponseEntity<?> limpiar() {
        service.getLog().clear();
        return ResponseEntity.ok(Map.of("mensaje", "Log limpiado"));
    }
}