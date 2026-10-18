/* ============================================================
   Fábrica de ensamblaje · Productor-Consumidor
   Cliente de monitoreo en tiempo real (Polling Pattern)
   ============================================================ */

const API = '/api/fabrica';
const CAPACIDAD = 5;
const POLL_MS = 400;

const $ = (id) => document.getElementById(id);

let slots = [];
let slotPrevio = new Array(CAPACIDAD).fill(null);
let logRenderizados = 0;
let fabricadasPrevio = 0;

/* ---------- Construcción del grid de slots ---------- */
function construirGrid() {
    const grid = $('grid');
    grid.innerHTML = '';
    slots = [];
    for (let i = 0; i < CAPACIDAD; i++) {
        const slot = document.createElement('div');
        slot.className = 'espacio vacio';
        slot.dataset.slot = String(i + 1).padStart(2, '0');
        slot.innerHTML = `<span class="slot-num">${String(i + 1).padStart(2, '0')}</span><span class="id"></span>`;
        grid.appendChild(slot);
        slots.push(slot);
    }
}

/* ---------- Utilidades ---------- */
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
));

function setTexto(id, valor) {
    const el = $(id);
    if (el && el.textContent !== String(valor)) el.textContent = valor;
}

/* ---------- Render: grid del almacén (con animaciones) ---------- */
function renderGrid(almacen) {
    for (let i = 0; i < CAPACIDAD; i++) {
        const slot = slots[i];
        const valor = almacen[i] || null;
        const previo = slotPrevio[i];

        if (valor && valor !== previo) {
            slot.classList.remove('vacio', 'saliendo');
            const idEl = slot.querySelector('.id');
            idEl.textContent = valor;
            // forzar reflow para reiniciar la animación de entrada
            void slot.offsetWidth;
            slot.classList.add('ocupado');
            slotPrevio[i] = valor;
        } else if (!valor && previo) {
            slot.classList.add('saliendo');
            slotPrevio[i] = null;
            window.setTimeout(() => {
                if (slotPrevio[i] === null) {
                    slot.classList.remove('ocupado', 'saliendo');
                    slot.classList.add('vacio');
                    slot.querySelector('.id').textContent = '';
                }
            }, 600);
        } else if (!valor && !previo) {
            slot.classList.remove('ocupado', 'saliendo');
            slot.classList.add('vacio');
            slot.querySelector('.id').textContent = '';
        }
    }
}

/* ---------- Render: piezas fabricadas recientemente ---------- */
function renderCola(fabricadas) {
    const cola = $('cola');
    const lista = fabricadas || [];
    setTexto('colaCount', lista.length === 0 ? '0' : String(lista.length));

    if (lista.length === 0) {
        if (!cola.querySelector('.cola-empty')) {
            cola.innerHTML = '<span class="cola-empty">Aún no se ha fabricado ninguna pieza</span>';
        }
        fabricadasPrevio = 0;
        return;
    }

    if (lista.length < fabricadasPrevio || cola.querySelector('.cola-empty')) {
        cola.innerHTML = '';
    }
    const visibles = lista.slice(-12);
    cola.innerHTML = '';
    const inicio = Math.max(0, lista.length - visibles.length);
    visibles.forEach((pieza, idx) => {
        const chip = document.createElement('span');
        chip.className = 'cola-item';
        chip.textContent = pieza;
        if (inicio + idx >= fabricadasPrevio) chip.style.animationDelay = '0s';
        cola.appendChild(chip);
    });
    fabricadasPrevio = lista.length;
}

/* ---------- Render: bitácora ---------- */
function renderLogs(logs) {
    const cont = $('logContainer');
    const lista = logs || [];

    if (lista.length < logRenderizados) {
        cont.innerHTML = '';
        logRenderizados = 0;
    }

    for (let i = logRenderizados; i < lista.length; i++) {
        const e = lista[i];
        const div = document.createElement('div');
        div.className = 'log-entry ' + (e.tipo || '');
        div.innerHTML = `<span class="hora">${esc(e.hora)}</span><span class="msg">${esc(e.mensaje)}</span>`;
        cont.appendChild(div);
    }

    if (lista.length > logRenderizados) {
        logRenderizados = lista.length;
        cont.scrollTop = cont.scrollHeight;
    }
    setTexto('logCount', lista.length + ' evento' + (lista.length === 1 ? '' : 's'));
}

/* ---------- Render: estado completo ---------- */
function render(data) {
    const almacen = data.almacen || [];
    const producidas = data.producidos || 0;
    const consumidas = data.consumidos || 0;
    const total = data.totalPiezas || 1;
    const retardo = data.retardo || 0;

    // Estado general
    const badge = $('statusBadge');
    badge.classList.toggle('running', !!data.activo);
    badge.classList.toggle('finished', !data.activo && consumidas > 0);
    setTexto('statusText', data.activo ? 'Simulación en curso' : (consumidas > 0 ? 'Detenida' : 'En espera'));
    $('pulseDot').classList.toggle('red', !data.activo);

    // Métricas
    setTexto('mAlmacen', almacen.length);
    setTexto('mProducidas', producidas);
    setTexto('mConsumidas', consumidas);
    setTexto('mRitmo', retardo);
    $('barAlmacen').style.width = (almacen.length / CAPACIDAD) * 100 + '%';
    $('barProducidas').style.width = (producidas / total) * 100 + '%';
    $('barConsumidas').style.width = (consumidas / total) * 100 + '%';
    $('barRitmo').style.width = Math.min(100, (retardo / 6000) * 100) + '%';

    // Progreso global
    const pct = Math.round((consumidas / total) * 100);
    $('progressBar').style.setProperty('--progress', pct + '%');
    setTexto('progressText', pct + '%');

    // Visualización
    renderGrid(almacen);
    renderCola(data.fabricadas);
    renderLogs(data.logs);

    // Botones
    $('btnIniciar').disabled = !!data.activo;
    $('btnDetener').disabled = !data.activo;
    $('btnAplicar').disabled = !data.activo;
}

/* ---------- Polling ---------- */
async function consultarEstado() {
    try {
        const r = await fetch(`${API}/estado`, { cache: 'no-store' });
        if (!r.ok) throw new Error('HTTP ' + r.status);
        render(await r.json());
    } catch (err) {
        $('statusBadge').classList.remove('running');
        setTexto('statusText', 'Sin conexión');
    }
}

/* ---------- Acciones ---------- */
function mostrarError(msg) {
    const el = $('panelError');
    if (!msg) { el.hidden = true; el.textContent = ''; return; }
    el.hidden = false;
    el.textContent = msg;
}

/** Validación en el cliente (misma que el backend). */
function validarConfig(p, c, k, r) {
    const errs = [];
    if (!Number.isInteger(p) || p < 1 || p > 10) errs.push('Número de productores: entero entre 1 y 10.');
    if (!Number.isInteger(c) || c < 1 || c > 10) errs.push('Número de consumidores: entero entre 1 y 10.');
    if (!Number.isInteger(k) || k < 1 || k > 50) errs.push('Piezas por productor: entero entre 1 y 50.');
    if (!Number.isInteger(r) || r < 0 || r > 6000) errs.push('Tiempo por operación: entre 0 y 6000 ms.');
    return errs;
}

async function iniciar() {
    const productores = parseInt($('productores').value, 10);
    const consumidores = parseInt($('consumidores').value, 10);
    const piezas = parseInt($('piezas').value, 10);
    const retardo = parseInt($('velocidad').value, 10);

    const errs = validarConfig(productores, consumidores, piezas, retardo);
    if (errs.length) {
        mostrarError(errs.join(' '));
        return;
    }
    mostrarError('');

    // reiniciamos la vista local para animar desde cero
    slotPrevio = new Array(CAPACIDAD).fill(null);
    logRenderizados = 0;
    fabricadasPrevio = 0;
    $('logContainer').innerHTML = '';
    construirGrid();

    const url = `${API}/iniciar?productores=${productores}&consumidores=${consumidores}`
        + `&piezas=${piezas}&retardo=${retardo}`;
    const r = await fetch(url, { method: 'POST' });
    if (!r.ok) {
        const cuerpo = await r.json().catch(() => ({}));
        mostrarError(cuerpo.mensaje || cuerpo.error || ('Error HTTP ' + r.status));
    }
    consultarEstado();
}

async function detener() {
    await fetch(`${API}/detener`, { method: 'POST' });
    consultarEstado();
}

async function aplicarRitmo() {
    const retardo = parseInt($('velocidad').value, 10);
    if (!Number.isInteger(retardo) || retardo < 0 || retardo > 6000) {
        mostrarError('Tiempo por operación: entre 0 y 6000 ms.');
        return;
    }
    mostrarError('');
    const r = await fetch(`${API}/velocidad?retardo=${retardo}`, { method: 'POST' });
    if (!r.ok) {
        const cuerpo = await r.json().catch(() => ({}));
        mostrarError(cuerpo.mensaje || cuerpo.error || ('Error HTTP ' + r.status));
    }
    consultarEstado();
}

/* ---------- Arranque ---------- */
$('btnIniciar').addEventListener('click', iniciar);
$('btnDetener').addEventListener('click', detener);
$('btnAplicar').addEventListener('click', aplicarRitmo);

construirGrid();
consultarEstado();
window.setInterval(consultarEstado, POLL_MS);
