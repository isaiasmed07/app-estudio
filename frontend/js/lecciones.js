function mostrarGradosLecciones() {
    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = "<h3>Seleccione su grado:</h3>";

    const grados = ["Primer Grado", "Segundo Grado", "Tercer Grado", "Cuarto Grado", "Quinto Grado", "Sexto Grado", "Séptimo Grado", "Octavo Grado", "Noveno Grado"];

    grados.forEach(grado => {
        const div = document.createElement("div");
        div.innerHTML = `
            <button onclick="seleccionarGradoLeccion('${grado}')">${grado}</button>
            <br>${grado === "Primer Grado" ? "" : "<small>Próximamente</small>"}
        `;
        container.appendChild(div);
    });
}

function seleccionarGradoLeccion(grado) {
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

    const gridContainer = document.createElement("div");
    gridContainer.style.display = "grid";
    gridContainer.style.gridTemplateColumns = "repeat(auto-fit, minmax(300px, 1fr))";
    gridContainer.style.gap = "20px";
    gridContainer.style.padding = "20px";

    fetch("https://app-estudio-docker.onrender.com/api/lecciones?materia=lenguaje")
        .then(response => response.json())
        .then(data => {
            data.forEach(item => {
                const leccion = item.contenido;

                const match = leccion.contenido_html.match(/href='(.*?)'/);
                const epubUrl = match ? match[1] : '#';

                const card = document.createElement("div");
                card.classList.add("clase-card");

                card.innerHTML = `
                    <img src="https://cdn-icons-png.flaticon.com/512/2972/2972341.png" alt="EPUB" width="100" height="100" style="object-fit: contain;">
                    <h4>${leccion.titulo}</h4>
                    <p>${leccion.descripcion}</p>
                    <button onclick="descargarYabrirEPUB('${encodeURIComponent(epubUrl)}')">Abrir</button>
                    <a href="${epubUrl}" target="_blank" download><button>Descargar</button></a>
                `;

                gridContainer.appendChild(card);
            });

            container.appendChild(gridContainer);
        })
        .catch(err => {
            container.innerHTML += "<p>Error al cargar las lecciones.</p>";
            console.error(err);
        });
}

// Nuevo método para descargar y abrir el EPUB evitando CORS
async function descargarYabrirEPUB(epubUrl) {
    const decodedUrl = decodeURIComponent(epubUrl);

    try {
        const response = await fetch(decodedUrl);
        const blob = await response.blob();

        const blobUrl = URL.createObjectURL(blob);

        window.location.href = `libro.html?blob=${encodeURIComponent(blobUrl)}`;
    } catch (err) {
        console.error("Error al descargar el EPUB:", err);
        alert("Hubo un problema al abrir el archivo.");
    }
}

// Ejecutar al cargar la página
window.onload = mostrarGradosLecciones;
