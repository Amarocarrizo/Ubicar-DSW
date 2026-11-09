/* Lo común a todas las pantallas del conductor: autenticación, cabecera, menú lateral y barra inferior. */
const Conductor = {
  /* Llamar al inicio de cada pantalla. Devuelve los datos del usuario (o null si redirigió). */
  async iniciar() {
    const me = await API.requerir('conductor');
    if (!me) return null;

    const c = me.conductor, v = me.vehiculo_asignado;
    const hora = new Date().getHours();
    const poner = (sel, texto) => document.querySelectorAll(sel).forEach(el => el.textContent = texto);
    poner('[data-saludo]', hora < 13 ? 'Hola, buen día' : hora < 20 ? 'Hola, buenas tardes' : 'Hola, buenas noches');
    poner('[data-nombre]', c.nombre + ' ' + c.apellido);
    poner('[data-iniciales]', c.nombre[0] + c.apellido[0]);
    poner('[data-licencia]', 'Licencia Tipo ' + c.tipo_licencia);
    poner('[data-vehiculo]', v ? `Vehículo Asignado: ${v.modelo} (${v.patente})` : 'Sin vehículo asignado');

    // menú lateral
    const menu = document.getElementById('menu'), fondo = document.getElementById('menu-fondo');
    document.querySelectorAll('[data-abrir-menu]').forEach(b => b.onclick = () => { menu.classList.remove('oculto'); fondo.classList.remove('oculto'); });
    document.querySelectorAll('[data-cerrar-menu]').forEach(b => b.onclick = () => { menu.classList.add('oculto'); fondo.classList.add('oculto'); });
    document.querySelectorAll('[data-salir]').forEach(b => b.onclick = () => API.logout());

    // resalta el link de la pantalla actual
    document.querySelectorAll('.barra a, .menu a').forEach(a => { if (a.getAttribute('href') === location.pathname) a.classList.add('activo'); });
    return me;
  },

  /* Etiqueta y color para cada estado de viaje. */
  estado(e) {
    return { 'PENDIENTE': ['Pendiente', 'gris'], 'EN CURSO': ['En ruta', 'verde'], 'FINALIZADO': ['Completado', 'gris'],
             'CANCELADO': ['Cancelado', 'rojo'] }[e] || [e, 'gris'];
  },

  /* El viaje activo del conductor (iniciado y no finalizado), o null. */
  async viajeActivo() {
    const viajes = await API.get('/api/viaje/');
    return viajes.find(v => v.hora_inicio && !v.hora_llegada && v.estado !== 'CANCELADO') || null;
  },

  numero(id) { return '#TRP-' + String(id).padStart(4, '0'); },
};
