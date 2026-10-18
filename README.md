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

---

**Asignatura:** Sistemas Distribuidos  
**Práctica:** N.º 3 — Sincronización de Procesos  
**Ciclo:** Sexto
