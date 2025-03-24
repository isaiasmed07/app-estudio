const apiBaseUrl = 'https://app-estudio-docker.onrender.com/api';

async function fetchData(endpoint) {
    try {
        const response = await fetch(`${apiBaseUrl}/${endpoint}`);
        if (!response.ok) {
            throw new Error(`Error al obtener datos: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return [];
    }
}

async function loadContent() {
    // Obtener datos de "lecciones"
    const lecciones = await fetchData('lecciones');
    const leccionesDiv = document.getElementById('lecciones');
    lecciones.forEach(item => {
        leccionesDiv.innerHTML += `<p>${item.contenido.titulo}</p>`;
    });

    // Obtener datos de "clases"
    const clases = await fetchData('clases');
    const clasesDiv = document.getElementById('clases');
    clases.forEach(item => {
        clasesDiv.innerHTML += `<p>${item.contenido.titulo}</p>`;
    });
}

// Ejecutar al cargar la página
window.onload = loadContent;
