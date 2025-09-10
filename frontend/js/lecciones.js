// Mostrar selección de grados al cargar la página
function mostrarGradosLecciones() {
    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = "<h3>Seleccione su grado:</h3>";

    const grados = [
        "Primer Grado", "Segundo Grado", "Tercer Grado", "Cuarto Grado", "Quinto Grado",
        "Sexto Grado", "Séptimo Grado", "Octavo Grado", "Noveno Grado"
    ];

    grados.forEach(grado => {
        const btn = document.createElement("button");
        btn.textContent = grado;
        btn.className = "grado-btn";

        if (grado !== "Primer Grado") {
            btn.disabled = true;
            btn.classList.add("disabled");
        } else {
            btn.onclick = () => seleccionarGradoLeccion(grado);
        }

        container.appendChild(btn);
    });
}

function seleccionarGradoLeccion(grado) {
    if (grado !== "Primer Grado") {
        alert("Contenido disponible próximamente");
        return;
    }

    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = "<h3>Seleccione la materia:</h3>";

    const materias = [
        { nombre: "Lenguaje", slug: "lenguaje" },
        { nombre: "Matemáticas", slug: "matematicas" }
    ];

    materias.forEach(materia => {
        const btn = document.createElement("button");
        btn.textContent = materia.nombre;
        btn.className = "grado-btn materia-btn";
        btn.onclick = () => mostrarLecciones(materia.slug);
        container.appendChild(btn);
    });
}

function mostrarLecciones(materiaSlug) {
    const container = document.getElementById("contenido-lecciones");
    const materiaNombre = materiaSlug === "matematicas" ? "Matemáticas" : "Lenguaje";

    container.innerHTML = `<h3>Lecciones de ${materiaNombre}</h3>`;

    const gridContainer = document.createElement("div");
    gridContainer.id = "grid-lecciones";
    container.appendChild(gridContainer);

    fetch(`https://app-estudio-docker.onrender.com/api/lecciones?materia=${materiaSlug}`)
        .then(response => {
            if (!response.ok) throw new Error("Error en la respuesta del servidor");
            return response.json();
        })
        .then(data => {
            gridContainer.innerHTML = "";
            data.forEach(item => {
                const leccion = item.contenido;

                let epubUrl = '#';
                if (leccion.contenido_html.startsWith('http')) {
                    epubUrl = leccion.contenido_html.trim();
                } else {
                    const match = leccion.contenido_html.match(/href=['"](.*?)['"]/);
                    epubUrl = match ? match[1] : '#';
                }

                const card = document.createElement("div");
                card.classList.add("clase-card");

                card.innerHTML = `
                    <img src="https://cdn-icons-png.flaticon.com/512/2972/2972341.png" alt="EPUB" width="100" height="100" style="object-fit: contain;">
                    <h4>${leccion.titulo}</h4>
                    <p>${leccion.descripcion}</p>
                    <button onclick="abrirVisorEPUB('${encodeURIComponent(epubUrl)}')">Abrir</button>
                    <a href="${epubUrl}" target="_blank" download><button>Descargar</button></a>
                `;

                gridContainer.appendChild(card);
            });
        })
        .catch(err => {
            const errorMsg = document.createElement("p");
            errorMsg.textContent = "Error al cargar las lecciones.";
            container.appendChild(errorMsg);
            console.error(err);
        });
}

// Abrir visor EPUB
function abrirVisorEPUB(url) {
    window.location.href = `libro.html?epub=${url}`;
}

// Ejecutar al cargar la página
window.onload = mostrarGradosLecciones;
