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
window.loadClases = async function () {
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
};

// Función para cargar lecciones
window.loadLecciones = async function () {
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
};

// Función para mostrar el libro y su índice con lógica dinámica
window.mostrarLibro = async function () {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const archivo = urlParams.get('archivo');

        if (!archivo) {
            console.error('Archivo no especificado en la URL');
            return;
        }

        // Mostrar mensaje de carga
        const visorElemento = document.getElementById("visor");
        visorElemento.innerHTML = "<p>Cargando libro, por favor espere...</p>";

        const visor = ePub(archivo);

        // Renderizar el libro en el visor
        await visor.renderTo("visor");
        visorElemento.innerHTML = ""; // Eliminar mensaje de carga

        // Intentar cargar el índice
        if (visor.navigation && visor.navigation.contents) {
            const indice = await visor.navigation.contents;
            const indiceElemento = document.getElementById('indice');
            indice.forEach(capitulo => {
                const li = document.createElement('li');
                li.textContent = capitulo.label;
                li.addEventListener('click', () => {
                    visor.goto(capitulo.href);
                });
                indiceElemento.appendChild(li);
            });
            console.log('Índice cargado correctamente:', indice);
        } else {
            console.warn('El índice no está disponible para este archivo.');
            const indiceElemento = document.getElementById('indice');
            indiceElemento.innerHTML = "<p>El índice no está disponible para este archivo.</p>";
        }
    } catch (error) {
        console.error('Error al mostrar el libro:', error);

        // Mostrar mensaje de error si falla la carga
        const visorElemento = document.getElementById("visor");
        visorElemento.innerHTML = "<p>Error al cargar el libro. Por favor, inténtalo de nuevo más tarde.</p>";
    }
};

// Función para cargar y redirigir al libro
window.cargarLibro = async function (grado, materia) {
    try {
        const response = await fetch(`${apiBaseUrl}/libros?grado=${grado}&materia=${materia}`);
        if (!response.ok) {
            throw new Error(`Error al obtener el libro: ${response.statusText}`);
        }
        const libro = await response.json();

        if (libro.error) {
            console.error('No se pudo cargar el libro:', libro.error);
            alert('Error: Libro no encontrado');
            return;
        }

        console.log('Libro cargado:', libro);

        // Redirige a libro.html con el enlace del archivo como parámetro
        window.location.href = `libro.html?archivo=${libro.archivo}`;
    } catch (error) {
        console.error('Error al cargar el libro:', error);
    }
};

// Función para iniciar sesión
window.login = function () {
    console.log('Iniciando sesión...');
    auth0Client.authorize();
};

// Manejar la autenticación después de redirección
window.handleAuthentication = function () {
    console.log('Procesando autenticación...');
    auth0Client.parseHash((err, authResult) => {
        if (err) {
            console.error('Error al manejar la autenticación:', err);
            return;
        }

        if (authResult && authResult.accessToken && authResult.idToken) {
            console.log('Autenticación exitosa:', authResult);
            guardarSesion(authResult);

            // Quitar el hash de la URL
            window.history.replaceState({}, document.title, '/');

            // Mostrar el contenido protegido
            const loginSection = document.getElementById('login-section');
            const contentSection = document.getElementById('content-section');
            if (loginSection && contentSection) {
                loginSection.hidden = true;
                contentSection.hidden = false;
                console.log('Contenido protegido mostrado.');
            } else {
                console.error('No se encontraron las secciones del DOM necesarias.');
            }
        } else {
            console.log('No hay datos de autenticación disponibles.');
        }
    });
};

// Guardar sesión en almacenamiento local
window.guardarSesion = function (authResult) {
    localStorage.setItem('accessToken', authResult.accessToken);
    localStorage.setItem('idToken', authResult.idToken);
    console.log('Sesión guardada en el almacenamiento local.');
};

// Verificar si ya hay una sesión activa
window.verificarSesion = function () {
    const accessToken = localStorage.getItem('accessToken');
    const idToken = localStorage.getItem('idToken');
    if (accessToken && idToken) {
        console.log('Sesión existente detectada, mostrando contenido protegido...');
        const loginSection = document.getElementById('login-section');
        const contentSection = document.getElementById('content-section');
        if (loginSection && contentSection) {
            loginSection.hidden = true;
            contentSection.hidden = false;
        }
    } else {
        console.log('No se encontró una sesión activa.');
    }
};

// Asignar eventos en el DOM
document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('loginBtn');
    if (loginButton) {
        console.log('Botón de inicio de sesión encontrado, asignando evento...');
        loginButton.addEventListener('click', () => {
            console.log('Botón de inicio de sesión clicado.');
            login();
        });
    } else {
        console.error('Botón de inicio de sesión no encontrado.');
    }

    // Verificar sesión activa o manejar autenticación
    if (window.location.hash.includes('access_token')) {
        handleAuthentication();
    } else {
        verificarSesion();
    }

    // Mostrar el libro si estamos en libro.html
    if (document.body.contains(document.getElementById('visor'))) {
        mostrarLibro();
    }
});
