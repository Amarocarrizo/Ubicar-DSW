var map = L.map('map').setView([-34.16327, -58.95919], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);


let marcadorActualO = null;
let marcadorActualD = null;

let buscadorO = document.getElementById('buscadorO')
let buscadorD = document.getElementById('buscadorD')

let origen = document.getElementById('origen')
let destino = document.getElementById('destino')


origen.addEventListener("click", async function () {

    // if (e.key == "Enter") {
    let busqueda = buscadorO.value.trim()

    let resultado = await getInfo(busqueda)

    if (resultado && resultado.length > 0) {
        actualizarMarcadorO(resultado[0]);
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
        actualizarMarcadorD(resultado[0]); // Pasamos el primer objeto del array
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

    map.setView([latitud, longitud], 10);

    if (marcadorActualO) {
        map.removeLayer(marcadorActualO);
    }

    // Crear un nuevo marcador y agregarlo al mapa
    marcadorActualO = L.marker([latitud, longitud]).addTo(map)
        .bindPopup(nombre)
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

    map.setView([latitud, longitud], 10);

    // Si ya había un marcador previo, lo eliminamos
    if (marcadorActualD) {
        map.removeLayer(marcadorActualD);
    }

    // Crear un nuevo marcador y agregarlo al mapa
    marcadorActualD = L.marker([latitud, longitud]).addTo(map)
        .bindPopup(nombre)
        .openPopup();

    //console.log(nombre)
    //console.log(latitud)
    //console.log(longitud)
    return [latitud, longitud]


}


