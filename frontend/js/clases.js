// Mostrar selección de grados al cargar la página
function mostrarGrados() {
    const grados = [
        "Primer Grado", "Segundo Grado", "Tercer Grado", "Cuarto Grado",
        "Quinto Grado", "Sexto Grado", "Séptimo Grado", "Octavo Grado", "Noveno Grado"
    ];
    const container = document.getElementById("contenido");
    container.innerHTML = "<h3>Seleccione su grado:</h3>";

    grados.forEach(grado => {
        const div = document.createElement("div");
        div.innerHTML = `<button onclick="seleccionarGrado('${grado}')">${grado}</button><br>${
            grado === "Primer Grado" ? "" : "<small>Próximamente</small>"
        }`;
        container.appendChild(div);
    });
}

function seleccionarGrado(grado) {
    if (grado !== "Primer Grado") {
        alert("Contenido disponible próximamente");
        return;
    }

    const container = document.getElementById("contenido");
    container.innerHTML = "<h3>Seleccione la materia:</h3>";
    container.innerHTML += `<button onclick="mostrarClases('lenguaje')">Lenguaje</button> `;
    container.innerHTML += `<button onclick="mostrarClases('matematicas')">Matemáticas</button>`;
}

function mostrarClases(materia) {
    const container = document.getElementById("contenido");
    container.innerHTML = `<h3>Clases de ${materia.charAt(0).toUpperCase() + materia.slice(1)}</h3>`;

    const gridContainer = document.createElement("div");
    gridContainer.id = "grid-clases";
    container.appendChild(gridContainer);

    // Llamada al backend para obtener el JSON desde Dropbox (ruta nueva)
    fetch(`https://app-estudio-docker.onrender.com/api/listar-videos?materia=${materia}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error en la respuesta del servidor");
            }
            return response.json();
        })
        .then(data => {
            gridContainer.innerHTML = "";
            data.forEach(item => {
                const div = document.createElement("div");
                div.classList.add("clase-card");

                let embedUrl = "";
                if (item.url.includes("list=")) {
                    const listaID = item.url.split("list=")[1];
                    embedUrl = `https://www.youtube.com/embed/videoseries?list=${listaID}`;
                } else {
                    embedUrl = item.url.replace("watch?v=", "embed/");
                }

                div.innerHTML = `
                    <h4>${item.titulo}</h4>
                    <iframe src="${embedUrl}" frameborder="0" allowfullscreen></iframe>
                `;
                gridContainer.appendChild(div);
            });
        })
        .catch(err => {
            container.innerHTML += `<p>Error al cargar las clases de ${materia}.</p>`;
            console.error(err);
        });
}

// Ejecutar cuando cargue la página
window.onload = mostrarGrados;
