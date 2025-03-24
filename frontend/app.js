const apiBaseUrl = 'https://app-estudio-docker.onrender.com/api';

// Configuración de Auth0
const auth0 = new Auth0Client({
    domain: dev-vg0llritbkja3g86.us.auth0.com, // Reemplaza con tu Domain de Auth0
    client_id: ncYW7gHwfN0N3mCZZRx4yUog7ExJ1zOI, // Reemplaza con tu Client ID de Auth0
    redirect_uri: 'https://app-estudio.vercel.app'
});

// Función para iniciar sesión
async function login() {
    try {
        await auth0.loginWithRedirect();
    } catch (error) {
        console.error('Error durante el inicio de sesión:', error);
    }
}

// Función para cerrar sesión
async function logout() {
    try {
        await auth0.logout({ returnTo: 'https://app-estudio.vercel.app' });
    } catch (error) {
        console.error('Error durante el cierre de sesión:', error);
    }
}

// Verificar si el usuario está autenticado
async function checkAuth() {
    try {
        const isAuthenticated = await auth0.isAuthenticated();
        if (isAuthenticated) {
            const user = await auth0.getUser();
            document.getElementById('login-section').hidden = true;
            document.getElementById('content-section').hidden = false;

            console.log('Usuario autenticado:', user);

            // Cargar contenido después de autenticar al usuario
            loadContent();
        } else {
            document.getElementById('login-section').hidden = false;
            document.getElementById('content-section').hidden = true;
        }
    } catch (error) {
        console.error('Error al verificar la autenticación:', error);
    }
}

// Función para obtener datos del backend
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

// Función para cargar contenido desde el backend
async function loadContent() {
    try {
        // Obtener datos de "lecciones"
        const lecciones = await fetchData('lecciones');
        const leccionesDiv = document.getElementById('lecciones');
        leccionesDiv.innerHTML = ''; // Limpia contenido anterior
        lecciones.forEach(item => {
            leccionesDiv.innerHTML += `<p>${item.contenido.titulo}</p>`;
        });

        // Obtener datos de "clases"
        const clases = await fetchData('clases');
        const clasesDiv = document.getElementById('clases');
        clasesDiv.innerHTML = ''; // Limpia contenido anterior
        clases.forEach(item => {
            clasesDiv.innerHTML += `<p>${item.contenido.titulo}</p>`;
        });
    } catch (error) {
        console.error('Error al cargar contenido:', error);
    }
}

// Asignar evento al botón de inicio de sesión
document.getElementById('loginBtn').addEventListener('click', login);

// Ejecutar autenticación al cargar la página
window.onload = checkAuth;
