function mostrarLeccionesLenguaje() {
    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = "<h3>Lecciones de Lenguaje</h3>";

    const gridContainer = document.createElement("div");
    gridContainer.style.display = "grid";
    gridContainer.style.gridTemplateColumns = "repeat(auto-fit, minmax(300px, 1fr))";
    gridContainer.style.gap = "20px";
    gridContainer.style.padding = "20px";

    // Cargar lecciones desde tu API en Render
    fetch("https://app-estudio-backend.onrender.com/api/lecciones")
        .then(response => response.json())
        .then(data => {
            data.forEach(item => {
                const leccion = item.contenido;

                // Extraer la URL del EPUB correctamente
                const match = leccion.contenido_html.match(/href=['"]([^'"]+)['"]/);
                let epubUrl = match ? match[1] : '#';

                // Asegurar que sea enlace directo (Dropbox raw o dl=1)
                if (!epubUrl.includes("?raw=1") && !epubUrl.includes("?dl=1")) {
                    epubUrl += (epubUrl.includes("?") ? "&" : "?") + "raw=1";
                }

                const card = document.createElement("div");
                card.classList.add("clase-card");

                // Crear botón de abrir visor sin problemas de comillas
                const botonAbrir = document.createElement("button");
                botonAbrir.textContent = "Abrir";
                botonAbrir.onclick = () => abrirVisorEPUB(epubUrl);

                // Crear botón de descarga
                const linkDescarga = document.createElement("a");
                linkDescarga.href = epubUrl;
                linkDescarga.target = "_blank";
                linkDescarga.download = "";
                const botonDescarga = document.createElement("button");
                botonDescarga.textContent = "Descargar";
                linkDescarga.appendChild(botonDescarga);

                // Construir la tarjeta
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

// Función para abrir el visor EPUB
function abrirVisorEPUB(url) {
    const finalUrl = encodeURIComponent(url);
    window.location.href = `libro.html?epub=${finalUrl}`;
}
