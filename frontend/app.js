const apiBaseUrl = 'https://app-estudio-docker.onrender.com/api';

async function fetchData(endpoint) {
    const response = await fetch(`${apiBaseUrl}/${endpoint}`);
    return await response.json();
}

async function showContent() {
    const lecciones = await fetchData('lecciones');
    const clases = await fetchData('clases');

    const leccionesDiv = document.getElementById('lecciones');
    lecciones.forEach(item => {
        leccionesDiv.innerHTML += `<p>${item.contenido.titulo}</p>`;
    });

    const clasesDiv = document.getElementById('clases');
    clases.forEach(item => {
        clasesDiv.innerHTML += `<p>${item.contenido.titulo}</p>`;
    });

    document.getElementById('content-section').hidden = false;
}

showContent();
