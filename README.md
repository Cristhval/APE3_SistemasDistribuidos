
# Simulador de Estacionamiento Concurrente

## Descripción
Este proyecto es una simulación interactiva de un estacionamiento con capacidad limitada. El objetivo principal es demostrar el uso de **semáforos contadores** en un entorno de programación concurrente para controlar el acceso a un recurso limitado (los espacios de estacionamiento).

El sistema está compuesto por un backend desarrollado en **Spring Boot (Java)** que gestiona la concurrencia, y un frontend en **HTML/CSS/JavaScript** que se conecta mediante peticiones HTTP para visualizar los eventos en tiempo real.

## Arquitectura del Sistema

El proyecto sigue una arquitectura **Cliente-Servidor** dividida en dos partes claramente separadas:

### 1. Backend (Spring Boot)
Ubicación: `src/main/java/miproyecto/estacionamiento/`
El backend está diseñado siguiendo el patrón de arquitectura en capas (MVC):

- **`controller/`**: Expone los endpoints REST (`/iniciar`, `/estado`, `/limpiar`). Recibe las peticiones del frontend y delega la lógica al servicio.
- **`service/`**: Contiene la lógica de negocio. Aquí se implementa el semáforo (`java.util.concurrent.Semaphore`) y el pool de hilos para simular los vehículos concurrentes.
- **`model/`**: Define las entidades del dominio (`Vehiculo`, `EventoLog`).
- **`dto/`**: Objetos de Transferencia de Datos (`VehiculoRequest`, `EstadoResponse`) para estructurar el JSON de entrada y salida.
- **`util/`**: Utilidades transversales como el `LogBuffer` (buffer thread-safe para guardar los logs en memoria).
- **`config/`**: Configuración global, como el `WebConfig` para permitir CORS (Cross-Origin Resource Sharing).

### 2. Frontend (Vanilla Web)
Ubicación: `src/frontend/`
- **`index.html`**: Estructura semántica de la interfaz.
- **`style.css`**: Estilos basados en un diseño "Editorial Oscuro".
- **`app.js`**: Lógica del cliente. Realiza un *polling* cada 500ms al backend para obtener el estado actualizado y anima los vehículos basándose en los eventos devueltos.


## ¿Cómo funciona la simulación?

1. Al presionar **"Iniciar simulación"**, el frontend envía una petición `POST` al backend con la cantidad de vehículos (ej. 10) y la capacidad del estacionamiento (ej. 4).
2. El backend inicializa un **Semáforo contador** con el valor de la capacidad.
3. Se crea un pool de hilos (`ExecutorService`). Por cada vehículo, se lanza un hilo (`VehiculoWorker`).
4. Cada hilo ejecuta la siguiente lógica:
    - Registra en el log que el vehículo "llegó".
    - Llama a `semaphore.acquire()`. Si hay espacio, el semáforo disminuye su contador y el vehículo entra. Si el contador está en 0, el hilo se **bloquea** hasta que alguien libere un espacio.
    - Simula un tiempo de estacionamiento aleatorio.
    - Al terminar, llama a `semaphore.release()`, liberando el espacio para el siguiente vehículo bloqueado.
5. El frontend lee el estado y el log, y pinta los autos en pantalla, manteniendo la interfaz actualizada en tiempo real.


## ¿Se logró lo solicitado?

### Objetivo General
> *Implementar mecanismos de exclusión mutua y sincronización para proteger secciones críticas, garantizando que no se produzcan condiciones de carrera al acceder a recursos compartidos.*

**Sí se logró.** El estacionamiento nunca supera su capacidad máxima, demostrando que el semáforo protege el recurso compartido.

### Criterios de la Rúbrica (Guía Práctica)
- **Resultado Esperado:** Vehículos dentro ≤ 4.
    - **Verificación:** Se ejecutó la simulación con 10 vehículos y capacidad 4. El campo `Máx. simultáneos` en el frontend y en el backend arrojó exactamente **4**. Los vehículos adicionales esperaron su turno en la cola lógica bloqueados por el hilo.
- **Resultado Esperado:** El sistema muestra un log claro de quién entra y sale, respetando el límite.
    - **Verificación:** La bitácora muestra eventos intercalados de entrada y salida (`Vehículo X INGRESA`) que son consecuentes con los eventos de salida (`Vehículo Y SALE`), respetando el orden.



## Cómo ejecutar el proyecto

### Requisitos
- Java 17 o superior.
- Maven (o el wrapper incluido).
- IDE (recomendado IntelliJ IDEA).

### Backend
1. Abre la carpeta del proyecto en tu IDE.
2. Recarga las dependencias de Maven (`pom.xml`).
3. Ejecuta la clase `EstacionamientoApplication.java`.
4. El servidor estará disponible en: `http://localhost:8080` (verifica la consola).

### Frontend
1. Abre el archivo `src/frontend/index.html` en tu navegador (puedes usar la extensión *Live Server* de VS Code o simplemente doble clic).
2. Asegúrate de que en `app.js` la variable `API` apunte al puerto correcto (ej. `http://localhost:8080/api/estacionamiento`).
3. Presiona **Iniciar Simulación**.

# Práctica 3: Sincronización de Procesos

Implementación de cinco ejercicios de concurrencia para la asignatura **Sistemas Distribuidos**. La práctica aborda el uso de semáforos, exclusión mutua y coordinación de hilos o procesos para administrar recursos compartidos y establecer un orden seguro de ejecución.

## Ejercicios implementados

### 1. Control de acceso a un estacionamiento — Semáforo contador
Simula la llegada concurrente de 10 vehículos a un estacionamiento con capacidad para 4. Un semáforo contador limita el número de vehículos que pueden permanecer dentro y hace esperar a los demás hasta que se libere un espacio.

**Validación:** nunca deben estar dentro más de 4 vehículos simultáneamente.

### 2. Cajero automático compartido — Exclusión mutua
Simula operaciones concurrentes sobre una cuenta bancaria con saldo inicial de **$1000**: retiros de **$300** y **$250**, y un depósito de **$200**. Un mutex protege el saldo durante las operaciones para evitar condiciones de carrera.

**Validación:** el saldo final esperado es **$650**, independientemente del orden de ejecución.

### 3. Fábrica de ensamblaje — Productor-Consumidor
Modela una fábrica con una cola compartida de capacidad máxima de **5 piezas**. Los productores agregan piezas y los consumidores las retiran para ensamblarlas. Los semáforos controlan los espacios disponibles y las piezas existentes, mientras que la exclusión mutua protege el acceso al almacén.

**Validación:** el almacén nunca debe superar su capacidad y las piezas producidas deben ser consumidas sin inconsistencias.

### 4. Cruce de vehículos — Control de acceso en una dirección
Simula un puente por el que pueden circular vehículos en ambos sentidos, pero solo puede haber una dirección activa a la vez. La sincronización coordina la entrada y salida de vehículos y evita cruces simultáneos en sentidos opuestos.

**Validación:** nunca deben circular vehículos en direcciones opuestas al mismo tiempo. También se considera el posible problema de inanición de una dirección.

### 5. Centro de impresión — Sincronización por etapas
Coordina tres procesos para que cada documento siga obligatoriamente el orden **Diseño → Revisión → Impresión**. Los semáforos habilitan cada etapa y permiten repetir el ciclo para tres documentos.

**Validación:** ningún documento puede revisarse antes de diseñarse ni imprimirse antes de revisarse.

## Conceptos principales

- **Semáforos contadores:** limitan el acceso a recursos con capacidad definida.
- **Exclusión mutua (mutex):** protege los datos compartidos y las secciones críticas.
- **Productor-Consumidor:** coordina la producción y el consumo mediante un búfer limitado.
- **Sincronización y orden de ejecución:** obliga a que las tareas se realicen en la secuencia requerida.
- **Condiciones de carrera, interbloqueos e inanición:** problemas de concurrencia analizados durante la práctica.

## Tecnologías

Las implementaciones descritas en el informe utilizan tecnologías según cada ejercicio, entre ellas **Java 17**, **Spring Boot**, **HTML5**, **CSS3**, **JavaScript** y, en algunos proyectos, **React con Vite** y **Docker**. La arquitectura y los comandos de ejecución dependen del repositorio específico de cada ejercicio.

## Repositorios relacionados

- **Ejercicio 1 — Estacionamiento:** []()
- **Ejercicio 2 — Cajero automático:** []()
- **Ejercicio 3 — Fábrica Productor-Consumidor:** []()
- **Ejercicio 4 — Cruce de vehículos:** []().
- **Ejercicio 5 — Centro de impresión:** []()

## Objetivo de la práctica

Aplicar mecanismos de sincronización para administrar recursos compartidos, prevenir condiciones de carrera, limitar accesos concurrentes y garantizar el orden correcto de ejecución entre procesos e hilos.



**Asignatura:** Sistemas Distribuidos  
**Práctica:** N.º 3 — Sincronización de Procesos  
**Ciclo:** Sexto

