/* Lo común a las pantallas del administrador: autenticación, cabecera y datos de los viajes. */
const Panel = {
  viajes: {},   // id_viaje -> viaje (con ruta, vehículo y conductor), para completar las tablas

  /* Llamar al inicio de cada pantalla. Devuelve el usuario (o null si redirigió). */
  async iniciar() {
    const me = await API.requerir('admin');
    if (!me) return null;
    const a = me.administrador || {};
    document.querySelectorAll('[data-nombre]').forEach(el => el.textContent = (a.nombre || me.username) + ' ' + (a.apellido || ''));
    document.querySelectorAll('[data-inicial]').forEach(el => el.textContent = (a.nombre || me.username)[0].toUpperCase());
    document.querySelectorAll('[data-salir]').forEach(b => b.onclick = () => API.logout());
    document.querySelectorAll('.p-cabecera nav a').forEach(l => { if (l.getAttribute('href') === location.pathname) l.classList.add('activo'); });

    // Gastos y alertas traen solo el id del viaje: se cargan todos los viajes una vez y se cruzan por id.
    (await API.get('/api/viaje/')).forEach(v => this.viajes[v.id_viaje] = v);
    return me;
  },

  /* Celdas que se repiten en las tablas. */
  conductor(idViaje) { const v = this.viajes[idViaje]; return v && v.conductor ? `${v.conductor.nombre} ${v.conductor.apellido}` : '—'; },
  vehiculo(idViaje) { const v = this.viajes[idViaje]; return v && v.vehiculo ? `${v.vehiculo.patente}<span class="sub">${F.texto(v.vehiculo.modelo)}</span>` : '—'; },
  ruta(idViaje) { const v = this.viajes[idViaje]; return v ? `${F.texto(v.ruta.origen)} → ${F.texto(v.ruta.destino)}` : '—'; },
  numero(id) { return '#TRP-' + String(id).padStart(4, '0'); },

  /* Las alertas de desvío guardan los metros en la descripción. */
  metrosDesvio(descripcion) { const m = /([\d.]+)\s*metros/.exec(descripcion || ''); return m ? parseFloat(m[1]) : null; },

  TIPO_ALERTA: { DESVIO: 'Desvío de ruta', TARDANZA: 'Tardanza', PERDIDA_CONEXION: 'Pérdida de conexión', GASTO_INCONSISTENTE: 'Gasto inconsistente' },
  ESTADO_ALERTA: { PENDIENTE: ['Pendiente', 'naranja'], IRREGULARIDAD_CONFIRMADA: ['Irregularidad confirmada', 'rojo'],
                   REVISADA_SIN_NOVEDAD: ['Revisada sin novedad', 'verde'], RESUELTA: ['Resuelta', 'gris'] },
  ESTADO_GASTO: { PENDIENTE: ['Pendiente', 'naranja'], VALIDADO: ['Validado', 'verde'], A_REVISAR: ['A revisar', 'rojo'],
                  ACEPTADO: ['Aprobado', 'verde'], RECHAZADO: ['Rechazado', 'rojo'] },
  TIPO_GASTO: { COMBUSTIBLE: 'Combustible', PEAJE: 'Peaje', OTROS: 'Otros' },
};
