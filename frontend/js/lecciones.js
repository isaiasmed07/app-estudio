// Mostrar grados al cargar la página
function mostrarGradosLecciones() {
    const grados = ["Primer Grado", "Segundo Grado", "Tercer Grado", "Cuarto Grado", "Quinto Grado", "Sexto Grado", "Séptimo Grado", "Octavo Grado", "Noveno Grado"];
    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = "<h3>Seleccione su grado:</h3>";

    grados.forEach(grado => {
        const div = document.createElement("div");
        div.innerHTML = `<button onclick="seleccionarGradoLecciones('${grado}')">${grado}</button><br>${grado === "Primer Grado" ? "" : "<small>Próximamente</small>"}`;
        container.appendChild(div);
    });
}

function seleccionarGradoLecciones(grado) {
    if (grado !== "Primer Grado") {
        alert("Contenido disponible próximamente");
        return;
    }

    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = "<h3>Seleccione la materia:</h3>";
    container.innerHTML += `<button onclick="mostrarLeccionesLenguaje()">Lenguaje</button> `;
    container.innerHTML += `<button onclick="alert('Matemáticas próximamente')">Matemáticas</button>`;
}

function mostrarLeccionesLenguaje() {
    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = "<h3>Lecciones de Lenguaje</h3>";

    // Crear contenedor tipo grid
    const gridContainer = document.createElement("div");
    gridContainer.id = "grid-lecciones";

    container.appendChild(gridContainer);

    // Llama al backend API para obtener las lecciones desde Firestore
    fetch('https://app-estudio-backend.onrender.com/api/lecciones?materia=lenguaje')

        .then(response => response.json())
        .then(data => {
            data.forEach(item => {
                const div = document.createElement("div");
                div.classList.add("clase-card"); // Reutilizamos el diseño de las clases

                div.innerHTML = `
                    <h4>${item.contenido.titulo}</h4>
                    <p>${item.contenido.descripcion}</p>
                    ${item.contenido.contenido_html}
                `;

                gridContainer.appendChild(div);
            });
        })
        .catch(err => {
            container.innerHTML += "<p>Error al cargar las lecciones.</p>";
            console.error(err);
        });
}

// Ejecutar al cargar la página
window.onload = mostrarGradosLecciones;
