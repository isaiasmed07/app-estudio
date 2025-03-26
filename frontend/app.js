// URL base de tu backend en Render
const apiBaseUrl = 'https://app-estudio-docker.onrender.com/api';

// Función para cargar clases
async function loadClases() {
    try {
        const response = await fetch(`${apiBaseUrl}/clases`);
        if (!response.ok) {
            throw new Error(`Error al obtener las clases: ${response.statusText}`);
        }
        const clases = await response.json();

        // Mostrar clases como enlaces dinámicos
        const clasesDiv = document.getElementById('clases');
        clasesDiv.innerHTML = ''; // Limpiar contenido previo
        clases.forEach(clase => {
            clasesDiv.innerHTML += `
                <a href="#" onclick="showDetails('clases', '${clase.id}')">${clase.contenido.Matematicas}</a><br>
            `;
        });
    } catch (error) {
        console.error('Error al cargar las clases:', error);
    }
}

// Función para cargar lecciones
async function loadLecciones() {
    try {
        const response = await fetch(`${apiBaseUrl}/lecciones`);
        if (!response.ok) {
            throw new Error(`Error al obtener las lecciones: ${response.statusText}`);
        }
        const lecciones = await response.json();

        // Mostrar lecciones como enlaces dinámicos
        const leccionesDiv = document.getElementById('lecciones');
        leccionesDiv.innerHTML = ''; // Limpiar contenido previo
        lecciones.forEach(leccion => {
            leccionesDiv.innerHTML += `
                <a href="#" onclick="showDetails('lecciones', '${leccion.id}')">${leccion.contenido.titulo}</a><br>
            `;
        });
    } catch (error) {
        console.error('Error al cargar las lecciones:', error);
    }
}

// Función para mostrar los detalles al hacer clic en un enlace
async function showDetails(type, id) {
    try {
        const response = await fetch(`${apiBaseUrl}/${type}/${id}`);
        if (!response.ok) {
            throw new Error(`Error al obtener los detalles: ${response.statusText}`);
        }
        const details = await response.json();

        const detailsDiv = document.getElementById('details');
        detailsDiv.innerHTML = ''; // Limpiar contenido previo
        detailsDiv.innerHTML = `<p>${JSON.stringify(details.contenido)}</p>`;
    } catch (error) {
        console.error('Error al mostrar los detalles:', error);
    }
}

// Cargar clases y lecciones al inicio
window.onload = () => {
    loadClases();
    loadLecciones();
};
