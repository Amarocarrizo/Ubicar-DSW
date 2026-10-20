var map = L.map('map').setView([-34.16327, -58.95919], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

L.marker([-34.16327, -58.95919]).addTo(map)
    .bindPopup('A pretty CSS popup.<br> Easily customizable.')
    .openPopup();

let marcadorActual = null;
// 3. Instanciar el proveedor de búsqueda de OpenStreetMap
const provider = new GeoSearch.OpenStreetMapProvider();

// 4. Capturar el input que ya creaste en el HTML
const inputBuscador = document.getElementById('buscador');

// Escuchar cuando el usuario presione la tecla "Enter" en tu input
partida.addEventListener('keypress', async function (e) {
    if (e.key === 'Enter') {
        const query = inputBuscador.value;
        if (!query) return;

        try {
            // Buscar los resultados usando el proveedor de GeoSearch
            const results = await provider.search({ query: query });

            if (results && results.length > 0) {
                const lugar = results[0]; // Tomamos el primer resultado

                const lat = lugar.y;
                const lon = lugar.x;
                const nombre = lugar.label;

                // Centrar el mapa en las coordenadas encontradas
                map.setView([lat, lon], 13);

                // Si ya había un marcador previo, lo eliminamos
                if (marcadorActual) {
                    map.removeLayer(marcadorActual);
                }

                // Crear un nuevo marcador y agregarlo al mapa
                marcadorActual = L.marker([lat, lon]).addTo(map)
                    .bindPopup(nombre)
                    .openPopup();

                console.log("Coordenadas capturadas:", { lat, lon, nombre });
            } else {
                alert("No se encontró la localidad.");
            }
        } catch (error) {
            console.error("Error en la búsqueda:", error);
        }
    }
});