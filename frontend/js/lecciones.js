// Mostrar grados al cargar la página
function mostrarGradosLecciones() {
    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = "<h3>Seleccione su grado:</h3>";

    const grados = ["Primer Grado", "Segundo Grado", "Tercer Grado", "Cuarto Grado", "Quinto Grado", "Sexto Grado", "Séptimo Grado", "Octavo Grado", "Noveno Grado"];

    grados.forEach(grado => {
        const div = document.createElement("div");
        div.innerHTML = `
            <button onclick="seleccionarGradoLecciones('${grado}')">${grado}</button><br>
            ${grado === "Primer Grado" ? "" : "<small>Próximamente</small>"}
        `;
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

    container.innerHTML += `
        <button onclick="mostrarLeccionesLenguaje()">Lenguaje</button> 
        <button onclick="alert('Matemáticas próximamente')">Matemáticas</button>
    `;
}

// Mostrar las lecciones de lenguaje (flujo mejorado)
function mostrarLeccionesLenguaje() {
    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = "<h3>Lecciones de Lenguaje</h3>";

    const gridContainer = document.createElement("div");
    gridContainer.style.display = "grid";
    gridContainer.style.gridTemplateColumns = "repeat(auto-fit, minmax(300px, 1fr))";
    gridContainer.style.gap = "20px";
    gridContainer.style.padding = "20px";

    // Llamada a la API del backend
    fetch("https://app-estudio-backend.onrender.com/api/lecciones")
        .then(response => response.json())
        .then(data => {
            data.forEach(item => {
                const leccion = item.contenido;

                // Extraer URL del EPUB del contenido_html
                const match = leccion.contenido_html.match(/href=['"]([^'"]+)['"]/);
                let epubUrl = match ? match[1] : '#';

                // Asegurar que la URL tenga ?raw=1 o ?dl=1
                if (!epubUrl.includes("?raw=1") && !epubUrl.includes("?dl=1")) {
                    epubUrl += (epubUrl.includes("?") ? "&" : "?") + "raw=1";
                }

                const card = document.createElement("div");
                card.classList.add("clase-card");

                // Botón Abrir EPUB
                const botonAbrir = document.createElement("button");
                botonAbrir.textContent = "Abrir";
                botonAbrir.onclick = () => abrirVisorEPUB(epubUrl);

                // Botón Descargar EPUB
                const linkDescarga = document.createElement("a");
                linkDescarga.href = epubUrl;
                linkDescarga.target = "_blank";
                linkDescarga.download = "";
                const botonDescarga = document.createElement("button");
                botonDescarga.textContent = "Descargar";
                linkDescarga.appendChild(botonDescarga);

                card.innerHTML = `
                    <img src="https://cdn-icons-png.flaticon.com/512/2972/2972341.png" alt="EPUB" width="100" height="100" style="object-fit: contain;">
                    <h4>${leccion.titulo}</h4>
                    <p>${leccion.descripcion}</p>
                `;

                card.appendChild(botonAbrir);
                card.appendChild(linkDescarga);

                gridContainer.appendChild(card);
            });

            container.appendChild(gridContainer);
        })
        .catch(err => {
            container.innerHTML += "<p>Error al cargar las lecciones.</p>";
            console.error(err);
        });
}

// Abrir visor de EPUB
function abrirVisorEPUB(url) {
    const finalUrl = encodeURIComponent(url);
    window.location.href = `libro.html?epub=${finalUrl}`;
}

// Ejecutar al cargar la página
window.onload = mostrarGradosLecciones;
