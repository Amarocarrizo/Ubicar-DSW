/* Mapas: Leaflet para dibujar, Nominatim (OpenStreetMap) para buscar lugares, OSRM para calcular rutas. */
const Mapa = {
  CENTRO: [-34.1633, -58.9592], // Campana, Buenos Aires

  crear(idElemento, zoom = 12) {
    const mapa = L.map(idElemento, { attributionControl: false }).setView(this.CENTRO, zoom);
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}').addTo(mapa);
    return mapa;
  },

  /* Texto -> {lat, lon, nombre}. Devuelve null si no encuentra nada. */
  async buscarLugar(texto) {
    const url = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=ar&q=' + encodeURIComponent(texto);
    const res = await (await fetch(url)).json();
    if (!res.length) return null;
    return { lat: +res[0].lat, lon: +res[0].lon, nombre: res[0].display_name };
  },

  /* Ruta por carretera entre dos puntos -> {geometria (GeoJSON), distanciaKm, duracionMin}. */
  async calcularRuta(origen, destino) {
    const url = `https://router.project-osrm.org/route/v1/driving/${origen.lon},${origen.lat};${destino.lon},${destino.lat}?overview=full&geometries=geojson`;
    const data = await (await fetch(url)).json();
    if (!data.routes || !data.routes.length) return null;
    const r = data.routes[0];
    return { geometria: r.geometry, distanciaKm: r.distance / 1000, duracionMin: r.duration / 60 };
  },

  /* Dibuja una geometría GeoJSON (la ruta planificada). */
  dibujarRuta(mapa, geometria, color = '#1d5cff', punteada = false) {
    return L.geoJSON(geometria, { style: { color, weight: 5, opacity: .85, dashArray: punteada ? '8 8' : null } }).addTo(mapa);
  },

  /* Dibuja una línea por los puntos [{lat, lon}] (el recorrido real). */
  dibujarRecorrido(mapa, puntos, color = '#dc2626') {
    return L.polyline(puntos.map(p => [p.lat, p.lon]), { color, weight: 4 }).addTo(mapa);
  },

  marcador(mapa, lat, lon, color = '#1d5cff', texto = '') {
    const icono = L.divIcon({
      className: '',
      html: `<div style="width:26px;height:26px;border-radius:50%;background:${color};border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,.35);display:grid;place-items:center;color:#fff;font-size:11px;font-weight:700">${texto}</div>`,
      iconSize: [26, 26], iconAnchor: [13, 13],
    });
    return L.marker([lat, lon], { icon: icono }).addTo(mapa);
  },

  /* Ajusta el zoom para que se vean todas las capas pasadas. */
  encuadrar(mapa, capas) {
    const grupo = L.featureGroup(capas.filter(Boolean));
    if (grupo.getLayers().length) mapa.fitBounds(grupo.getBounds(), { padding: [30, 30] });
  },

  /* GeoJSON LineString guarda [lon, lat]; esto lo pasa a [{lat, lon}]. */
  puntos(geometria) {
    return geometria ? geometria.coordinates.map(c => ({ lat: c[1], lon: c[0] })) : [];
  },
};
