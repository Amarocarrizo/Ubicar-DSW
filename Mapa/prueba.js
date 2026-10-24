var map = L.map('map').setView([-34.16327, -58.95919], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


let marcadorActualO = null;
let marcadorActualD = null;
let routeLayer= null; // apa para almacenar la ruta dibujada y poder limpiarla si se actualiza

let coordsOrigen = null;
let coordsDestino = null;

let buscadorO = document.getElementById('buscadorO')
let buscadorD = document.getElementById('buscadorD')
let origen = document.getElementById('origen')
let destino = document.getElementById('destino')


origen.addEventListener("click", async function () {

    // if (e.key == "Enter") {
    let busqueda = buscadorO.value.trim()

    let resultado = await getInfo(busqueda)

    if (resultado && resultado.length > 0) {
        coordsOrigen = await actualizarMarcadorO(resultado[0]);
        intentarTrazarRuta();
        //actualizarMarcadorO(resultado[0]);
    } else {
        alert("No existe la localidad");
    }

    // }

});



destino.addEventListener("click", async function () {

    // if (e.key == "Enter") {
    let busqueda = buscadorD.value.trim()

    let resultado = await getInfo(busqueda)

    if (resultado && resultado.length > 0) {
        coordsDestino = await actualizarMarcadorD(resultado[0]);
        intentarTrazarRuta();
       // actualizarMarcadorD(resultado[0]); // Pasamos el primer objeto del array
    } else {
        alert("No existe la localidad");
    }

    // }

});



const getInfo = async (a) => {
    let peticion = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(a)} , Buenos Aires&format=json&limit=1`)
    let resultado = await peticion.json()
    return resultado
}

const actualizarMarcadorO = async (json) => {
    let nombre = json.display_name
    let latitud = parseFloat(json.lat)
    let longitud = parseFloat(json.lon)

    //map.setView([latitud, longitud], 10);

    if (marcadorActualO) {
        map.removeLayer(marcadorActualO);
    }

    // Crear un nuevo marcador y agregarlo al mapa
    marcadorActualO = L.marker([latitud, longitud]).addTo(map)
        .bindPopup("Origen: "+ nombre)
        .openPopup();

    //console.log(nombre)
    //console.log(latitud)
    //console.log(longitud)
    return [latitud, longitud]

}

const actualizarMarcadorD = async (json) => {
    let nombre = json.display_name
    let latitud = parseFloat(json.lat)
    let longitud = parseFloat(json.lon)

    //map.setView([latitud, longitud], 10);

    // Si ya había un marcador previo, lo eliminamos
    if (marcadorActualD) {
        map.removeLayer(marcadorActualD);
    }

    // Crear un nuevo marcador y agregarlo al mapa
    marcadorActualD = L.marker([latitud, longitud]).addTo(map)
        .bindPopup("Destino: " + nombre)
        .openPopup();

    //console.log(nombre)
    //console.log(latitud)
    //console.log(longitud)
    return [latitud, longitud]


}


// Función encargada de consultar a OSRM y dibujar la ruta
const intentarTrazarRuta = async () => {
    if (coordsOrigen && coordsDestino) {
        // OSRM espera las coordenadas en formato: {longitud},{latitud};{longitud},{latitud}
        let url = `https://router.project-osrm.org/route/v1/driving/${coordsOrigen[1]},${coordsOrigen[0]};${coordsDestino[1]},${coordsDestino[0]}?overview=full&geometries=geojson`;

        try {
            let response = await fetch(url);
            let data = await response.json();

            if (data.routes && data.routes.length > 0) {
                let routeGeoJson = data.routes[0].geometry;
                let distanciaKm = data.routes[0].distance / 1000;
                let duracionMinutos = data.routes[0].duration / 60;

                // Si ya existía una ruta dibujada previamente, la eliminamos del mapa
                if (routeLayer) {
                    map.removeLayer(routeLayer);
                }

                // Dibujar la nueva ruta usando la geometría GeoJSON que devuelve OSRM
                routeLayer = L.geoJSON(routeGeoJson, {
                    style: {
                        color: '#3388ff',
                        weight: 5,
                        opacity: 0.8
                    }
                }).addTo(map);

                // Ajustar el zoom del mapa para que abarque toda la ruta calculada
                map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });

                // Opcional: Puedes aprovechar de leer la distancia y el tiempo estimado para tu backend o modelo Ruta
                let distanciaMetros = data.routes[0].distance; // en metros
                let duracionSegundos = data.routes[0].duration; // en segundos
                
                console.log(`Distancia estimada: ${(distanciaMetros / 1000).toFixed(2)} km`);
                console.log(`Tiempo estimado: ${(duracionSegundos / 60).toFixed(0)} minutos`);
                // ==========================================
    // NUEVO: Enviar los datos de la ruta a Django
    // ==========================================
       const guardarRutaEnBackend = async () => {
           try {
            let respuestaRuta = await fetch('http://127.0.0.1:8000/api/ruta/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Si Django te pide CSRF token y estás usando sesión web, 
                    // puedes incluirlo aquí. Si es DRF con SessionAuthentication pura, 
                    // recuerda enviarlo o configurar AllowAny temporalmente para pruebas.
                },
                body: JSON.stringify({
                    origen: buscadorO.value.trim(),
                    destino: buscadorD.value.trim(),
                    distancia_estimada: distanciaKm.toFixed(2),
                    tiempo_estimado: duracionMinutos.toFixed(2),
                    geometria_ruta: routeGeoJson // El JSON completo de OSRM que guardamos en MySQL
                })
            });

            if (respuestaRuta.ok) {
                let rutaCreada = await respuestaRuta.json();
                console.log("Ruta guardada exitosamente en Django con ID:", rutaCreada.id_ruta);
                
                // Opcional: Aquí podrías disparar la creación del Viaje asociando este id_ruta
            } else {
                console.error("Error al guardar la ruta en el backend");
            }
        } catch (error) {
            console.error("Error de red al intentar guardar la ruta:", error);
        }
    };

    guardarRutaEnBackend();
            } else {
                alert("No se pudo calcular una ruta por carretera entre estos puntos.");
            }
        } catch (error) {
            console.error("Error al conectar con el servicio de enrutamiento:", error);
        }
    }

};
