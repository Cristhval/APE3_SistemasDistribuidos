package com.arelys.fabrica.controller;

import com.arelys.fabrica.service.FabricaService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/fabrica")
@CrossOrigin(origins = "*")
public class FabricaController {

    @Autowired
    private FabricaService service;

    /**
     * Inicia la simulación con la configuración indicada.
     *
     * @param productores  número de productores (entero 1-10)
     * @param consumidores número de consumidores (entero 1-10)
     * @param piezas       piezas por productor (entero 1-50)
     * @param retardo      tiempo por operación en ms (0-6000)
     */
    @PostMapping("/iniciar")
    public Map<String, Object> iniciar(@RequestParam(required = false) Integer productores,
                                       @RequestParam(required = false) Integer consumidores,
                                       @RequestParam(required = false) Integer piezas,
                                       @RequestParam(required = false) Long retardo) {
        return service.iniciarSimulacion(productores, consumidores, piezas, retardo);
    }

    @PostMapping("/detener")
    public Map<String, Object> detener() {
        return service.detenerSimulacion();
    }

    /** Ajusta el ritmo de la simulación en caliente. */
    @PostMapping("/velocidad")
    public Map<String, Object> velocidad(@RequestParam long retardo) {
        return service.configurarVelocidad(retardo);
    }

    @GetMapping("/estado")
    public Map<String, Object> estado() {
        return service.obtenerEstado();
    }

    /** Muestra claramente los errores de validación (HTTP 400 + mensaje). */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> errorValidacion(IllegalArgumentException ex) {
        Map<String, Object> cuerpo = new HashMap<>();
        cuerpo.put("error", ex.getMessage());
        cuerpo.put("mensaje", "Configuración inválida: " + ex.getMessage());
        return ResponseEntity.badRequest().body(cuerpo);
    }
}
