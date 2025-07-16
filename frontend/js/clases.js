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
    container.innerHTML += `<button onclick="mostrarMatematicas()">Matemáticas</button>`;
}

function mostrarLenguaje() {
    cargarClases('Lenguaje', 'https://dl.dropboxusercontent.com/scl/fi/fqnqwpyr0301spia0f9n4/CLASES.json?rlkey=m103vmfupjd7zsia4gx97t2oz&st=zwnqkqo9');
}

function mostrarMatematicas() {
    cargarClases('Matemáticas', 'https://dl.dropboxusercontent.com/scl/fi/p2rf3hamf2x2sra1gq3xv/Matematicas.json?rlkey=3z96dye0mmlojetm4wdbzp5tj&st=myvd4y7m');
}

function cargarClases(materia, jsonUrl) {
    const container = document.getElementById("contenido");
    container.innerHTML = `<h3>Clases de ${materia}</h3>`;

    const gridContainer = document.createElement("div");
    gridContainer.id = "grid-clases";

    container.appendChild(gridContainer);

    fetch(jsonUrl)
        .then(response => response.json())
        .then(data => {
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
