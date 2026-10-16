const API = 'http://localhost:8080/api/estacionamiento';
let intervalId = null;
let tiempoInicio = null;
let ultimoLogCount = 0;
let idsAnteriores = new Set();

const $ = (id) => document.getElementById(id);

// ============ INICIAR ============
$('btnIniciar').addEventListener('click', async () => {
    const body = {
        totalVehiculos: parseInt($('total').value),
        capacidad: parseInt($('capacidad').value),
        tiempoMinMs: 800,
        tiempoMaxMs: 2500
    };

    $('btnIniciar').disabled = true;
    tiempoInicio = Date.now();
    ultimoLogCount = 0;
    idsAnteriores = new Set();

    try {
        const res = await fetch(`${API}/iniciar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.error || 'Error al iniciar');
            $('btnIniciar').disabled = false;
            return;
        }

        prepararVista(body.capacidad);
        $('logContainer').innerHTML = '';
        arrancarPolling();
    } catch (e) {
        console.error(e);
        alert('Error de conexión con el backend');
        $('btnIniciar').disabled = false;
    }
});

// ============ LIMPIAR ============
$('btnLimpiar').addEventListener('click', async () => {
    await fetch(`${API}/limpiar`, { method: 'POST' });
    $('logContainer').innerHTML = '';
    $('logCount').textContent = '0 eventos';
    $('estacionamientoGrid').innerHTML = '';
    $('colaContainer').innerHTML = '<div class="cola-empty">Sin vehículos esperando</div>';
    $('colaCount').textContent = '0';
    $('ocupados').textContent = '0';
    $('maxSim').textContent = '0';
    $('tiempo').textContent = '0s';
    $('ocupadosBar').style.width = '0%';
    $('progressBar').style.setProperty('--progress', '0%');
    $('progressText').textContent = '0%';
    setStatus('Inactivo', '');
    ultimoLogCount = 0;
    idsAnteriores = new Set();
});

// ============ PREPARAR VISTA ============
function prepararVista(capacidad) {
    const grid = $('estacionamientoGrid');
    grid.innerHTML = '';
    for (let i = 0; i < capacidad; i++) {
        const espacio = document.createElement('div');
        espacio.className = 'espacio vacio';
        espacio.dataset.slot = i;
        espacio.innerHTML = `<span class="emoji">🅿️</span>`;
        grid.appendChild(espacio);
    }
}

// ============ POLLING ============
function arrancarPolling() {
    if (intervalId) clearInterval(intervalId);
    setStatus('Ejecutando…', 'running');
    intervalId = setInterval(actualizar, 400);
    actualizar();
}

async function actualizar() {
    try {
        const res = await fetch(`${API}/estado`);
        const data = await res.json();

        // ===== Calcular IDs dentro y esperando desde el log =====
        const { dentro, esperando } = analizarLog(data.eventos);

        // ===== Métricas =====
        animarNumero($('ocupados'), dentro.size);
        $('capacidadVista').textContent = data.capacidad;
        $('maxSim').textContent = data.maxSimultaneos;

        if (tiempoInicio) {
            const seg = Math.floor((Date.now() - tiempoInicio) / 1000);
            $('tiempo').textContent = seg + 's';
        }

        // ===== Barra de ocupados =====
        const pctOcupados = (dentro.size / data.capacidad) * 100;
        $('ocupadosBar').style.width = pctOcupados + '%';

        // ===== Barra de progreso =====
        const totalVehiculos = parseInt($('total').value);
        const pctProgreso = Math.min(100, Math.round((data.eventos.filter(e => e.mensaje.includes('SALE')).length / totalVehiculos) * 100));
        $('progressBar').style.setProperty('--progress', pctProgreso + '%');
        $('progressText').textContent = pctProgreso + '%';

        // ===== Grid con animaciones =====
        actualizarGrid(dentro);

        // ===== Cola de espera =====
        actualizarCola(esperando);

        // ===== Log con transiciones =====
        actualizarLog(data.eventos);

        // ===== Estado final =====
        if (!data.ejecutando && data.maxSimultaneos > 0) {
            clearInterval(intervalId);
            intervalId = null;
            setStatus('Finalizado', 'finished');
            $('btnIniciar').disabled = false;
        }
    } catch (e) {
        console.error(e);
    }
}

// ============ ANÁLISIS DEL LOG ============
function analizarLog(eventos) {
    const dentro = new Set();
    const llego = new Set();

    eventos.forEach(ev => {
        const mIng = ev.mensaje.match(/Vehículo (\d+) INGRESA/);
        const mSal = ev.mensaje.match(/Vehículo (\d+) SALE/);
        const mLle = ev.mensaje.match(/Vehículo (\d+) llega/);

        if (mLle) llego.add(mLle[1]);
        if (mIng) dentro.add(mIng[1]);
        if (mSal) dentro.delete(mSal[1]);
    });

    // Esperando = llegaron pero no han ingresado (ni salido)
    const esperando = new Set();
    llego.forEach(id => {
        if (!dentro.has(id) && !fueIngresado(id, eventos)) {
            esperando.add(id);
        }
    });

    return { dentro, esperando };
}

function fueIngresado(id, eventos) {
    return eventos.some(e => e.mensaje.includes(`Vehículo ${id} INGRESA`) ||
        e.mensaje.includes(`Vehículo ${id} SALE`));
}

// ============ GRID ANIMADO ============
function actualizarGrid(dentro) {
    const grid = $('estacionamientoGrid');
    const espacios = grid.querySelectorAll('.espacio');
    const ids = Array.from(dentro).sort((a, b) => a - b);

    espacios.forEach((esp, i) => {
        const idVehiculo = ids[i];
        const idAnterior = esp.dataset.idActual;

        if (idVehiculo && idVehiculo !== idAnterior) {
            // Nuevo vehículo entra
            esp.className = 'espacio ocupado';
            esp.dataset.idActual = idVehiculo;
            esp.innerHTML = `
                <span class="emoji">🚗</span>
                <span class="id">#${idVehiculo}</span>
            `;
        } else if (!idVehiculo && idAnterior) {
            // Vehículo sale
            esp.classList.add('saliendo');
            setTimeout(() => {
                esp.className = 'espacio vacio';
                esp.removeAttribute('data-id-actual');
                esp.innerHTML = `<span class="emoji">🅿️</span>`;
            }, 400);
        } else if (!idVehiculo) {
            esp.className = 'espacio vacio';
            esp.removeAttribute('data-id-actual');
            esp.innerHTML = `<span class="emoji">🅿️</span>`;
        }
    });
}

// ============ COLA DE ESPERA ============
function actualizarCola(esperando) {
    const cont = $('colaContainer');
    const count = $('colaCount');

    count.textContent = esperando.size;

    if (esperando.size === 0) {
        cont.innerHTML = '<div class="cola-empty">Sin vehículos esperando</div>';
        return;
    }

    // Renderizar solo si cambió
    const idsActuales = Array.from(esperando).sort((a, b) => a - b);
    const html = idsActuales.map(id =>
        `<div class="cola-item"><span class="mini-car">🚙</span> #${id}</div>`
    ).join('');
    cont.innerHTML = html;
}

// ============ LOG ============
function actualizarLog(eventos) {
    const cont = $('logContainer');
    const count = $('logCount');

    if (eventos.length > ultimoLogCount) {
        // Remover mensaje vacío
        const empty = cont.querySelector('.cola-empty');
        if (empty) empty.remove();

        for (let i = ultimoLogCount; i < eventos.length; i++) {
            const ev = eventos[i];
            const div = document.createElement('div');
            div.className = 'log-entry ' + clasificarEvento(ev.mensaje);
            div.innerHTML = `
                <span class="hora">[${ev.hora}]</span>
                <span class="msg">${ev.mensaje}</span>
            `;
            cont.appendChild(div);
        }
        ultimoLogCount = eventos.length;
        cont.scrollTop = cont.scrollHeight;
    }

    count.textContent = eventos.length + ' eventos';
}

function clasificarEvento(msg) {
    if (msg.includes('INGRESA')) return 'ingresa';
    if (msg.includes('SALE')) return 'sale';
    if (msg.includes('llega')) return 'llega';
    if (msg.includes('Inicio')) return 'inicio';
    if (msg.includes('finalizada')) return 'fin';
    return '';
}

// ============ ANIMAR NÚMEROS ============
function animarNumero(el, target) {
    const actual = parseInt(el.textContent) || 0;
    if (actual === target) return;

    const duracion = 300;
    const inicio = performance.now();

    function paso(ahora) {
        const t = Math.min(1, (ahora - inicio) / duracion);
        const eased = 1 - Math.pow(1 - t, 3);
        const valor = Math.round(actual + (target - actual) * eased);
        el.textContent = valor;
        if (t < 1) requestAnimationFrame(paso);
    }

    requestAnimationFrame(paso);
}

// ============ STATUS ============
function setStatus(texto, clase) {
    $('statusText').textContent = texto;
    $('statusBadge').className = 'status-badge ' + clase;
}