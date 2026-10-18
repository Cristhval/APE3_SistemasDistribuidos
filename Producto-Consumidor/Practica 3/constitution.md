# CONSTITUCIÓN DEL PROYECTO - SISTEMAS DISTRIBUIDOS: PRODUCTOR-CONSUMIDOR (SPRING BOOT & DOCKER)

## 1. Información General
* **Asignatura:** Sistemas Distribuidos (6to Ciclo - Paralelo A)
* **Estudiante:** Arelys Ajila
* **Institución:** Universidad Nacional de Loja (UNL) - FEIRNNR
* **Práctica:** Nro. 003 - Ejercicio 3: Fábrica de Ensamblaje (Productor-Consumidor)

## 2. Objetivo del Proyecto
Implementar la solución al problema clásico del Productor-Consumidor aplicando patrones de diseño de software, arquitectura full-stack, concurrencia avanzada en Java con **Spring Boot**, y contenedores Docker para asegurar que:
1. El almacén temporal nunca supere una capacidad máxima de 5 piezas[cite: 5].
2. Un productor no pueda colocar una pieza si el almacén está lleno[cite: 5].
3. Un consumidor no pueda retirar una pieza si el almacén está vacío[cite: 5].
4. Todos los productos producidos sean consumidos sin inconsistencias[cite: 11] ni condiciones de carrera.

## 3. Arquitectura y Tecnologías
* **Backend:** Java 21 con **Spring Boot**, utilizando `BlockingQueue`, `Semaphore`, hilos nativos de Java y endpoints REST (`@RestController`).
* **Frontend:** Interfaz web interactiva utilizando HTML5, Tailwind CSS y JavaScript para el monitoreo visual en tiempo real.
* **Dockerización:** El proyecto completo se encuentra dockerizado mediante un archivo `Dockerfile` y `docker-compose.yml` para garantizar un entorno de ejecución estandarizado y reproducible.
* **Patrones de Diseño Aplicados:**
  * *Producer-Consumer Pattern:* Desacoplamiento de la producción y el consumo mediante un buffer acotado.
  * *Singleton / Service Pattern:* Gestión centralizada del estado de la fábrica en Spring Beans.
  * *Polling Pattern:* Actualización dinámica de la interfaz web respecto al estado del backend.

## 4. Criterios de Verificación y Resultados Esperados
* El almacén de piezas mantiene un tamaño $0 \le \text{elementos} \le 5$[cite: 11].
* Ausencia absoluta de *deadlocks* o pérdida de datos ante ráfagas concurrentes.
* Ejecución limpia y empaquetada dentro de contenedores Docker.