// URL base de tu backend en Render
const apiBaseUrl = 'https://app-estudio-docker.onrender.com/api';

// Configuración del cliente Auth0
const auth0Client = new auth0.WebAuth({
    domain: 'dev-vg0llritbkja3g86.us.auth0.com', // Reemplaza con tu dominio Auth0
    clientID: 'ncYW7gHwfN0N3mCZZRx4yUog7ExJ1zOI', // Reemplaza con tu Client ID
    redirectUri: 'https://app-estudio.vercel.app', // URL de redirección en Auth0
    responseType: 'token id_token',
    scope: 'openid profile email'
});

// Función para cargar clases y mostrar detalles
async function loadClases() {
    try {
        const response = await fetch(`${apiBaseUrl}/clases`);
        if (!response.ok) {
            throw new Error(`Error al obtener las clases: ${response.statusText}`);
        }
        const clases = await response.json();

        // Mostrar detalles en la sección correspondiente
        const detailsDiv = document.getElementById('details');
        detailsDiv.innerHTML = '<h3>Clases:</h3>'; // Encabezado de detalles
        clases.forEach(clase => {
            detailsDiv.innerHTML += `<p>${clase.contenido.Matematicas}: ${clase.contenido.Descripcion}</p>`;
        });
        document.getElementById('details-section').hidden = false; // Mostrar sección de detalles
    } catch (error) {
        console.error('Error al cargar las clases:', error);
    }
}

// Función para cargar lecciones y mostrar detalles
async function loadLecciones() {
    try {
        const response = await fetch(`${apiBaseUrl}/lecciones`);
        if (!response.ok) {
            throw new Error(`Error al obtener las lecciones: ${response.statusText}`);
        }
        const lecciones = await response.json();

        // Mostrar detalles en la sección correspondiente
        const detailsDiv = document.getElementById('details');
        detailsDiv.innerHTML = '<h3>Lecciones:</h3>'; // Encabezado de detalles
        lecciones.forEach(leccion => {
            detailsDiv.innerHTML += `<p>${leccion.contenido.titulo}</p>`;
        });
        document.getElementById('details-section').hidden = false; // Mostrar sección de detalles
    } catch (error) {
        console.error('Error al cargar las lecciones:', error);
    }
}

// Función para iniciar sesión
function login() {
    auth0Client.authorize();
}

// Función para manejar el inicio de sesión después de la redirección
function handleAuthentication() {
    auth0Client.parseHash((err, authResult) => {
        if (err) {
            console.error('Error al manejar la autenticación:', err);
            return;
        }
        if (authResult && authResult.accessToken && authResult.idToken) {
            console.log('Autenticación exitosa:', authResult);
            guardarSesion(authResult);
            mostrarContenido();
        } else {
            console.log('No hay datos de autenticación disponibles.');
        }
    });
}

// Función para guardar los datos de la sesión
function guardarSesion(authResult) {
    localStorage.setItem('accessToken', authResult.accessToken);
    localStorage.setItem('idToken', authResult.idToken);
}

// Función para mostrar el contenido después de iniciar sesión
function mostrarContenido() {
    document.getElementById('login-section').hidden = true;
    document.getElementById('content-section').hidden = false;
}

// Asignar evento al botón de inicio de sesión
document.getElementById('loginBtn').addEventListener('click', login);

// Verificar estado de autenticación al cargar la página
window.onload = handleAuthentication;
