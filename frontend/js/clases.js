// Mostrar selección de grados al cargar la página
function mostrarGrados() {
    const grados = ["Primer Grado", "Segundo Grado", "Tercer Grado", "Cuarto Grado", "Quinto Grado", "Sexto Grado", "Séptimo Grado", "Octavo Grado", "Noveno Grado"];
    const container = document.getElementById("contenido");
    container.innerHTML = "<h3>Seleccione su grado:</h3>";

    grados.forEach(grado => {
        const div = document.createElement("div");
        div.innerHTML = `<button onclick="seleccionarGrado('${grado}')">${grado}</button><br>${grado === "Primer Grado" ? "" : "<small>Próximamente</small>"}`;
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
    container.innerHTML += `<button onclick="mostrarLenguaje()">Lenguaje</button> `;
    container.innerHTML += `<button onclick="alert('Matemáticas próximamente')">Matemáticas</button>`;
}

function mostrarLenguaje() {
    const container = document.getElementById("contenido");
    container.innerHTML = "<h3>Clases de Lenguaje</h3>";

    // Cargar JSON desde Dropbox
    fetch('https://dl.dropboxusercontent.com/scl/fi/fqnqwpyr0301spia0f9n4/CLASES.json?rlkey=m103vmfupjd7zsia4gx97t2oz&st=zwnqkqo9')
        .then(response => response.json())
        .then(data => {

            // Crear contenedor tipo grid
            const gridContainer = document.createElement("div");
            gridContainer.style.display = "grid";
            gridContainer.style.gridTemplateColumns = "repeat(auto-fit, minmax(360px, 1fr))";
            gridContainer.style.gap = "20px";
            gridContainer.style.padding = "20px";

            data.forEach(item => {
                const div = document.createElement("div");
                div.classList.add("clase-card");

                let embedUrl = "";

                // Verifica si es un curso (lista de reproducción) o un video normal
                if (item.url.includes("list=")) {
                    const listaID = item.url.split("list=")[1];
                    embedUrl = `https://www.youtube.com/embed/videoseries?list=${listaID}`;
                } else {
                    embedUrl = item.url.replace("watch?v=", "embed/");
                }

                div.innerHTML = `
                    <h4>${item.titulo}</h4>
                    <iframe width="360" height="202" src="${embedUrl}" frameborder="0" allowfullscreen></iframe>
                `;
                gridContainer.appendChild(div);
            });

            container.appendChild(gridContainer);
        })
        .catch(err => {
            container.innerHTML += "<p>Error al cargar las clases.</p>";
            console.error(err);
        });
}

// Ejecutar cuando cargue la página
window.onload = mostrarGrados;
