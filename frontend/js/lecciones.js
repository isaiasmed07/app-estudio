// Mostrar selección de grados al cargar la página
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
    container.innerHTML += `<button onclick="mostrarLecciones('Lenguaje')">Lenguaje</button> `;
    container.innerHTML += `<button onclick="mostrarLecciones('Matemáticas')">Matemáticas</button>`;
}

function mostrarLecciones(materia) {
    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = `<h3>Lecciones de ${materia}</h3>`;

    const gridContainer = document.createElement("div");
    gridContainer.id = "grid-lecciones";

    container.appendChild(gridContainer);

    fetch('https://app-estudio-backend.onrender.com/api/lecciones') // Cambia al dominio correcto si es necesario
        .then(response => response.json())
        .then(data => {
            // Filtrar por materia si es necesario (opcional)
            data.forEach(item => {
                const div = document.createElement("div");
                div.classList.add("leccion-card");

                div.innerHTML = `
                    <h4>${item.contenido.titulo}</h4>
                    <p>${item.contenido.descripcion}</p>
                    <button onclick="verLeccion('${item.id}')">Ver lección</button>
                `;
                gridContainer.appendChild(div);
            });
        })
        .catch(err => {
            container.innerHTML += "<p>Error al cargar las lecciones.</p>";
            console.error(err);
        });
}

function verLeccion(id) {
    window.location.href = `leccion.html?id=${id}`;
}

// Ejecutar al cargar la página
window.onload = mostrarGradosLecciones;
