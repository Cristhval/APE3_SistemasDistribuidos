# GUÍA DE ESTILOS Y DIRECTRICES VISUALES (style.md)

## 1. Concepto y Filosofía de Diseño
* **Estilo:** Panel de Control Editorial / Modo Oscuro Académico (Editorial Dark Mode).
* **Enfoque:** Minimalismo técnico, tipografía serif combinada con sans-serif para lecturas de alto contraste, sobriedad institucional y estética de simulación formal.
* **Prohibiciones:** Se prohíben estrictamente los colores neones, fluorescentes, morados intensos o amarillos brillantes. Se priorizan tonos mate, apagados y profesionales.

## 2. Paleta de Colores (Variables del Sistema)
* **Fondos:**
  * Fondo General (`--bg`): `#121212` (Negro pizarra profundo)
  * Superficies y Paneles (`--surface`): `#1e1e1e` (Gris oscuro mate)
  * Fondo Alternativo / Contenedores (`--bg-alt` / `--surface-2`): `#1a1a1a` a `#262626`
* **Tipografía y Textos:**
  * Tinta Principal (`--ink`): `#f5f5f4` (Blanco suave / Marfil tenue)
  * Tinta Secundaria (`--ink-soft`): `#d6d3d1`
  * Tinta Muted / Etiquetas (`--ink-muted` / `--ink-faint`): `#a8a29e` a `#78716c`
* **Bordes:**
  * Estándar (`--border` / `--border-strong`): `#2a2a2a` a `#3f3f3f` (Delgados, sutiles, de alta definición).
* **Acentos de Estado (Apagados y Profesionales):**
  * Éxito / Ingreso (`--success`): `#34d399` (Verde esmeralda sobrio)
  * Advertencia / Cola (`--warning`): `#fbbf24` (Ámbar cálido institucional)
  * Peligro / Salida / Error (`--accent`): `#ef4444` (Rojo quemado / terracota apagado)
  * Información (`--info`): `#60a5fa` (Azul corporativo claro)

## 3. Tipografía y Jerarquía
* **Familias Tipográficas:**
  * Títulos, Encabezados y Cifras Clave: `'Georgia', 'Times New Roman', serif` (Estilo editorial con presencia de cursivas en subtítulos).
  * Etiquetas, Botones, Contadores y Consola de Logs: `'Inter', sans-serif` (Limpia, moderna, altamente legible).
  * Monospaciada (Horas en Bitácora): `'Courier New', monospace`.
* **Escala y Tratamiento:**
  * Títulos principales (`h1`): Cursiva o combinados con bloques de acento sutiles inferiores (línea translúcida).
  * Etiquetas técnicas (`.card-tag`, `.input-group label`): En mayúsculas, espaciado de letras ampliado (`letter-spacing: 2px`) y tipografía `Inter` en tamaño pequeño (0.65rem - 0.75rem).

## 4. Componentes y Estructura Visual
* **Paneles y Tarjetas (Cards):**
  * Bordes sutiles de 1px con esquinas ligeramente redondeadas (`border-radius: 4px`).
  * Efecto hover con líneas superiores deslizantes (`transform: scaleX(0)` a `1`) en color de acento según la métrica.
* **Botones y Controles:**
  * Botones primarios con tipografía en mayúsculas, espaciado de letras (`letter-spacing: 1.5px`) e inversión de color en hover (fondo claro con texto oscuro o viceversa).
  * Campos de entrada (`input`) con tipografía numérica grande en Serif y bordes que se iluminan sutilmente al enfocar.
* **Visualizador Gráfico (Slots / Grid):**
  * Celdas cuadradas (`aspect-ratio: 1`) que representan espacios de recursos compartidos (como estacionamientos o buffers).
  * Transiciones fluidas de entrada y salida para los elementos activos (vehículos o piezas) con animaciones de desplazamiento lateral (`blogCarEnter` / `blogCarExit`).
* **Bitácora de Eventos (Logs):**
  * Contenedor con scroll vertical personalizado y diseño en formato de lista corrida.
  * Líneas laterales izquierdas de 3px con códigos de color estrictamente ligados al tipo de evento (`ingresa`, `sale`, `llega`) para facilitar la lectura técnica sin recargar la vista.