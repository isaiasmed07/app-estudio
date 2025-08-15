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

// ====== Función para mostrar opciones de profesor ======
async function mostrarOpcionesProfesor(email) {
    try {
        const response = await fetch(`${apiBaseUrl}/rol?email=${encodeURIComponent(email)}`);
        if (!response.ok) throw new Error("Error consultando rol");
        const data = await response.json();

        if (data.rol === "profesor") {
            console.log("Usuario es profesor, agregando opciones extra...");
            const container = document.querySelector(".card-container");
            if (container) {
                container.innerHTML += `
                    <a href="subir_pdf.html" class="card">
                        <h3>📄 Subir PDF</h3>
                        <p>Agrega nuevos documentos</p>
                    </a>
                    <a href="subir_video.html" class="card">
                        <h3>🎥 Subir Video</h3>
                        <p>Agrega clases en video</p>
                    </a>
                    <a href="dashboard.html" class="card">
                        <h3>📊 Dashboard</h3>
                        <p>Ver estadísticas y administración</p>
                    </a>
                `;
            }
        }
    } catch (error) {
        console.error("Error al verificar rol:", error);
    }
}

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

// Función para mostrar libro
window.mostrarLibro = async function () {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const archivo = urlParams.get('archivo');

        if (!archivo) {
            console.error('Archivo no especificado en la URL');
            return;
        }

        const visorElemento = document.getElementById("visor");
        visorElemento.innerHTML = "<p>Cargando libro, por favor espere...</p>";

        const visor = ePub(archivo);
        await visor.renderTo("visor");

        visorElemento.innerHTML = "";

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
        } else {
            const indiceElemento = document.getElementById('indice');
            indiceElemento.innerHTML = "<p>El índice no está disponible para este archivo.</p>";
        }
    } catch (error) {
        console.error('Error al mostrar el libro:', error);
        document.getElementById("visor").innerHTML = "<p>Error al cargar el libro.</p>";
    }
};

// Función para cargar y redirigir libro
window.cargarLibro = async function (grado, materia) {
    try {
        const response = await fetch(`${apiBaseUrl}/libros?grado=${grado}&materia=${materia}`);
        if (!response.ok) throw new Error(`Error al obtener el libro: ${response.statusText}`);
        const libro = await response.json();

        if (libro.error) {
            alert('Error: Libro no encontrado');
            return;
        }
        window.location.href = `libro.html?archivo=${libro.archivo}`;
    } catch (error) {
        console.error('Error al cargar el libro:', error);
    }
};

// Iniciar sesión
window.login = function () {
    auth0Client.authorize();
};

// Manejar autenticación
window.handleAuthentication = function () {
    auth0Client.parseHash((err, authResult) => {
        if (err) {
            console.error('Error al manejar la autenticación:', err);
            return;
        }

        if (authResult && authResult.accessToken && authResult.idToken) {
            guardarSesion(authResult);

            // Guardar email
            if (authResult.idTokenPayload && authResult.idTokenPayload.email) {
                localStorage.setItem('userEmail', authResult.idTokenPayload.email);
                mostrarOpcionesProfesor(authResult.idTokenPayload.email);
            }

            window.history.replaceState({}, document.title, '/');

            const loginSection = document.getElementById('login-section');
            const contentSection = document.getElementById('content-section');
            if (loginSection && contentSection) {
                loginSection.hidden = true;
                contentSection.hidden = false;
            }
        }
    });
};

// Guardar sesión
window.guardarSesion = function (authResult) {
    localStorage.setItem('accessToken', authResult.accessToken);
    localStorage.setItem('idToken', authResult.idToken);
};

// Verificar sesión
window.verificarSesion = function () {
    const accessToken = localStorage.getItem('accessToken');
    const idToken = localStorage.getItem('idToken');
    const email = localStorage.getItem('userEmail');

    if (accessToken && idToken) {
        const loginSection = document.getElementById('login-section');
        const contentSection = document.getElementById('content-section');
        if (loginSection && contentSection) {
            loginSection.hidden = true;
            contentSection.hidden = false;
            if (email) mostrarOpcionesProfesor(email);
        }
    }
};

// Eventos DOM
document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('loginBtn');
    if (loginButton) {
        loginButton.addEventListener('click', login);
    }

    if (window.location.hash.includes('access_token')) {
        handleAuthentication();
    } else {
        verificarSesion();
    }

    if (document.body.contains(document.getElementById('visor'))) {
        mostrarLibro();
    }
});
