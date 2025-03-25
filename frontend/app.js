// Forzar la carga dinámica del script de Auth0
const script = document.createElement('script');
script.src = "https://cdn.auth0.com/js/auth0/9.18/auth0.min.js"; // Usar CDN directamente
script.onload = () => {
    console.log("Script de Auth0 cargado correctamente.");
    iniciarApp(); // Solo iniciar si el script está listo
};
script.onerror = () => {
    console.error("Error al cargar el script de Auth0.");
};
document.head.appendChild(script);

function iniciarApp() {
    // Verificar si el objeto auth0 está disponible
    const auth0 = window.auth0;
    if (!auth0) {
        console.error("El objeto auth0 no está disponible. Verifica la carga del script auth0.min.js.");
        return;
    }

    // Inicializar WebAuth desde el objeto global auth0
    const webAuth = new auth0.WebAuth({
        domain: 'dev-vg0llritbkja3g86.us.auth0.com',
        clientID: 'ncYW7gHwfN0N3mCZZRx4yUog7ExJ1zOI',
        redirectUri: 'https://app-estudio.vercel.app',
        responseType: 'token id_token',
        scope: 'openid profile email'
    });

    console.log("WebAuth inicializado correctamente.");

    // Función para iniciar sesión
    async function login() {
        try {
            webAuth.authorize();
        } catch (error) {
            console.error('Error durante el inicio de sesión:', error);
        }
    }

    // Función para verificar si el usuario está autenticado
    function checkAuth() {
        webAuth.parseHash((err, authResult) => {
            if (err) {
                console.error('Error al procesar el hash:', err);
                return;
            }

            if (authResult && authResult.accessToken && authResult.idToken) {
                console.log('Usuario autenticado:', authResult);
                document.getElementById('login-section').hidden = true;
                document.getElementById('content-section').hidden = false;
                // Aquí puedes cargar información adicional del usuario si es necesario
            } else {
                document.getElementById('login-section').hidden = false;
                document.getElementById('content-section').hidden = true;
            }
        });
    }

    // Asignar eventos al botón de inicio de sesión
    document.getElementById('loginBtn').addEventListener('click', login);

    // Ejecutar verificación de autenticación al cargar la página
    window.onload = checkAuth;
}
