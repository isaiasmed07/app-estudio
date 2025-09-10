// Mostrar selección de grados al cargar la página
function mostrarGrados() {
    const grados = [
        "Primer Grado", "Segundo Grado", "Tercer Grado", "Cuarto Grado",
        "Quinto Grado", "Sexto Grado", "Séptimo Grado", "Octavo Grado", "Noveno Grado"
    ];
    const container = document.getElementById("contenido");
    container.innerHTML = "<h3>Seleccione su grado:</h3>";

    grados.forEach(grado => {
        const btn = document.createElement("button");
        btn.textContent = grado;
        btn.className = "grado-btn";

        if (grado !== "Primer Grado") {
            btn.disabled = true;
            btn.classList.add("disabled");
        } else {
            btn.onclick = () => seleccionarGrado(grado);
        }

        container.appendChild(btn);
    });
}

function seleccionarGrado(grado) {
    if (grado !== "Primer Grado") {
        alert("Contenido disponible próximamente");
        return;
    }

    const container = document.getElementById("contenido");
    container.innerHTML = "<h3>Seleccione la materia:</h3>";

    const materias = [
        { nombre: "Lenguaje", slug: "lenguaje" },
        { nombre: "Matemáticas", slug: "matematicas" }
    ];

    materias.forEach(materia => {
        const btn = document.createElement("button");
        btn.textContent = materia.nombre;
        btn.className = "grado-btn materia-btn";
        btn.onclick = () => mostrarClases(materia.slug);
        container.appendChild(btn);
    });
}

function mostrarClases(materiaSlug) {
    const materiaNombre = materiaSlug === "matematicas" ? "Matemáticas" : "Lenguaje";
    const container = document.getElementById("contenido");
    container.innerHTML = `<h3>Clases de ${materiaNombre}</h3>`;

    const gridContainer = document.createElement("div");
    gridContainer.id = "grid-clases";
    container.appendChild(gridContainer);

    fetch(`https://app-estudio-docker.onrender.com/api/listar-videos?materia=${materiaSlug}`)
        .then(response => {
            if (!response.ok) throw new Error("Error en la respuesta del servidor");
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
            const errorMsg = document.createElement("p");
            errorMsg.textContent = `Error al cargar las clases de ${materiaNombre}.`;
            container.appendChild(errorMsg);
            console.error(err);
        });
}

// Ejecutar al cargar la página
window.onload = mostrarGrados;
