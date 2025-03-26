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

// Función para cargar clases y renderizarlas en la página clases.html
async function loadClases() {
    try {
        const response = await fetch(`${apiBaseUrl}/clases`);
        if (!response.ok) {
            throw new Error(`Error al obtener las clases: ${response.statusText}`);
        }
        const clases = await response.json();

        const clasesDiv = document.getElementById('clases');
        if (!clasesDiv) throw new Error("Elemento con ID 'clases' no encontrado en el DOM.");

        clasesDiv.innerHTML = '<h3>Clases:</h3>'; // Encabezado para las clases
        clases.forEach(clase => {
            clasesDiv.innerHTML += `<p><strong>${clase.contenido.Matematicas}</strong>: ${clase.contenido.Descripcion}</p>`;
        });
    } catch (error) {
        console.error('Error al cargar las clases:', error);
    }
}

// Función para cargar lecciones y renderizarlas en la página lecciones.html
async function loadLecciones() {
    try {
        const response = await fetch(`${apiBaseUrl}/lecciones`);
        if (!response.ok) {
            throw new Error(`Error al obtener las lecciones: ${response.statusText}`);
        }
        const lecciones = await response.json();

        const leccionesDiv = document.getElementById('lecciones');
        if (!leccionesDiv) throw new Error("Elemento con ID 'lecciones' no encontrado en el DOM.");

        leccionesDiv.innerHTML = '<h3>Lecciones:</h3>'; // Encabezado para las lecciones
        lecciones.forEach(leccion => {
            leccionesDiv.innerHTML += `<p><strong>${leccion.contenido.titulo}</strong></p>`;
        });
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
    const loginSection = document.getElementById('login-section');
    const contentSection = document.getElementById('content-section');
    if (loginSection && contentSection) {
        loginSection.hidden = true;
        contentSection.hidden = false;
    }
}

// Asignar evento al botón de inicio de sesión
document.getElementById('loginBtn')?.addEventListener('click', login);

// Verificar estado de autenticación al cargar la página
window.onload = () => {
    if (typeof handleAuthentication === "function") {
        handleAuthentication();
    }
};
