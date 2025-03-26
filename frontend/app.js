// URL base de tu backend en Render
const apiBaseUrl = 'https://app-estudio-docker.onrender.com/api';

// Configuración del cliente Auth0
const auth0Client = new auth0.WebAuth({
    domain: 'dev-vg0llritbkja3g86.us.auth0.com',
    clientID: 'ncYW7gHwfN0N3mCZZRx4yUog7ExJ1zOI',
    redirectUri: 'https://app-estudio.vercel.app',
    responseType: 'token id_token',
    scope: 'openid profile email'
});

// Función para cargar clases
async function loadClases() {
    try {
        const response = await fetch(`${apiBaseUrl}/clases`);
        if (!response.ok) {
            throw new Error(`Error al obtener las clases: ${response.statusText}`);
        }
        const clases = await response.json();

        const clasesDiv = document.getElementById('clases');
        if (!clasesDiv) throw new Error("El contenedor con ID 'clases' no se encontró en el DOM.");

        clasesDiv.innerHTML = '<h3>Clases:</h3>';
        clases.forEach(clase => {
            clasesDiv.innerHTML += `<p><strong>${clase.contenido.Matematicas}</strong>: ${clase.contenido.Descripcion}</p>`;
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

        const leccionesDiv = document.getElementById('lecciones');
        if (!leccionesDiv) throw new Error("El contenedor con ID 'lecciones' no se encontró en el DOM.");

        leccionesDiv.innerHTML = '<h3>Lecciones:</h3>';
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

// Manejar la autenticación después de redirección
function handleAuthentication() {
    auth0Client.parseHash((err, authResult) => {
        if (err) {
            console.error('Error al manejar la autenticación:', err);
            return;
        }
        if (authResult && authResult.accessToken && authResult.idToken) {
            console.log('Autenticación exitosa:', authResult);
            guardarSesion(authResult);
        } else {
            console.log('No hay datos de autenticación disponibles.');
        }
    });
}

// Guardar sesión en almacenamiento local
function guardarSesion(authResult) {
    localStorage.setItem('accessToken', authResult.accessToken);
    localStorage.setItem('idToken', authResult.idToken);
}
