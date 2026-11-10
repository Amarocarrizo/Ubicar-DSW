/* Cliente de la API de UBICAR.
   Guarda el token JWT en localStorage, lo agrega a cada pedido y lo renueva si venció. */
const API = {
  token() { return localStorage.getItem('access'); },

  /* Login: pide los tokens y los guarda. */
  async login(username, password) {
    const r = await fetch('/api/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!r.ok) throw new Error('Usuario o contraseña incorrectos');
    const data = await r.json();
    sessionStorage.removeItem('me'); // olvida al usuario anterior (si cambió de cuenta)
    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);
  },

  logout() {
    localStorage.clear();
    sessionStorage.clear();
    location.href = '/login/';
  },

  /* Pide un access token nuevo usando el refresh token. Devuelve true si pudo. */
  async renovar() {
    const refresh = localStorage.getItem('refresh');
    if (!refresh) return false;
    const r = await fetch('/api/token/refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!r.ok) return false;
    localStorage.setItem('access', (await r.json()).access);
    return true;
  },

  /* Pedido genérico: agrega el token; si da 401 intenta renovar una vez; si no, vuelve al login.
     body puede ser un objeto (se manda como JSON) o un FormData (para subir archivos). */
  async pedir(metodo, url, body) {
    const opciones = { method: metodo, headers: { Authorization: 'Bearer ' + this.token() } };
    if (body instanceof FormData) opciones.body = body;
    else if (body) { opciones.headers['Content-Type'] = 'application/json'; opciones.body = JSON.stringify(body); }

    let r = await fetch(url, opciones);
    if (r.status === 401 && await this.renovar()) {
      opciones.headers.Authorization = 'Bearer ' + this.token();
      r = await fetch(url, opciones);
    }
    if (r.status === 401) return this.logout();

    const data = r.status === 204 ? null : await r.json().catch(() => null);
    if (!r.ok) {
      // DRF devuelve {"error": "..."} o {"campo": ["mensaje"]}; se arma un texto legible
      const msg = data ? (data.error || data.detail || Object.values(data).flat().join(' ')) : 'Error ' + r.status;
      throw new Error(msg);
    }
    return data;
  },

  get(url) { return this.pedir('GET', url); },
  post(url, body) { return this.pedir('POST', url, body || {}); },

  /* Quién soy. Se guarda en sessionStorage para no pedirlo en cada pantalla. */
  async me() {
    const guardado = sessionStorage.getItem('me');
    if (guardado) return JSON.parse(guardado);
    const me = await this.get('/api/me/');
    sessionStorage.setItem('me', JSON.stringify(me));
    return me;
  },

  /* Protege una pantalla: sin token va al login; con otro rol va a su propia pantalla. */
  async requerir(rol) {
    if (!this.token()) { location.href = '/login/'; return null; }
    const me = await this.me();
    if (me.rol !== rol) { location.href = me.rol === 'admin' ? '/panel/' : '/conductor/'; return null; }
    return me;
  },
};

/* Helpers de formato usados por todas las pantallas. */
const F = {
  plata(n) { return '$' + Number(n || 0).toLocaleString('es-AR', { maximumFractionDigits: 2 }); },
  km(n) { return Number(n || 0).toLocaleString('es-AR', { maximumFractionDigits: 1 }) + ' km'; },
  fecha(iso) { return iso ? new Date(iso).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'; },
  hora(iso) { return iso ? new Date(iso).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' }) : '—'; },
  duracion(minutos) {
    const total = Math.max(0, Math.round(Number(minutos || 0)));
    if (total < 60) return total + ' min';
    const h = Math.floor(total / 60);
    const m = total % 60;
    return m === 0 ? `${h} hs` : `${h}:${String(m).padStart(2, '0')} hs`;
  },
  texto(s) { return String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); },
};

/* Mensaje flotante breve (confirmaciones y errores). */
function aviso(msg, esError) {
  let t = document.getElementById('aviso');
  if (!t) { t = document.createElement('div'); t.id = 'aviso'; document.body.appendChild(t); }
  t.textContent = msg;
  t.className = 'aviso visible' + (esError ? ' error' : '');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('visible'), 2500);
}
