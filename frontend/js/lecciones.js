function mostrarGradosLecciones() {
    const container = document.getElementById("contenido-lecciones");
    container.innerHTML = "<h3>Seleccione su grado:</h3>";

    const grados = [
        "Primer Grado", "Segundo Grado", "Tercer Grado", "Cuarto Grado", "Quinto Grado",
        "Sexto Grado", "Séptimo Grado", "Octavo Grado", "Noveno Grado"
    ];

    grados.forEach(grado => {
        const div = document.createElement("div");
        const btn = document.createElement("button");
        btn.textContent = grado;
        btn.className = "grado-btn";
        if (grado !== "Primer Grado") {
            btn.disabled = true;
            btn.classList.add("disabled");
            const small = document.createElement("small");
            small.textContent = "Próximamente";
            div.appendChild(btn);
            div.appendChild(document.createElement("br"));
            div.appendChild(small);
        } else {
            btn.onclick = () => seleccionarGradoLeccion(grado);
            div.appendChild(btn);
        }
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

    const materias = ["Lenguaje", "Matemáticas"];
    materias.forEach(materia => {
        const btn = document.createElement("button");
        btn.textContent = materia;
        btn.className = "grado-btn materia-btn";
        btn.onclick = () => mostrarLecciones(materia.toLowerCase());
        container.appendChild(btn);
    });
}

function mostrarLecciones(materia) {
    const materiasDisponibles = ["lenguaje", "matematicas"];
    const container = document.getElementById("contenido-lecciones");

    if (!materiasDisponibles.includes(materia)) {
        container.innerHTML = "<p>Próximamente...</p>";
        return;
    }

    container.innerHTML = `<h3>Lecciones de ${materia.charAt(0).toUpperCase() + materia.slice(1)}</h3>`;

    const gridContainer = document.createElement("div");
    gridContainer.id = "grid-lecciones";
    container.appendChild(gridContainer);

    fetch(`https://app-estudio-docker.onrender.com/api/lecciones?materia=${materia}`)
        .then(response => response.json())
        .then(data => {
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
            container.innerHTML += "<p>Error al cargar las lecciones.</p>";
            console.error(err);
        });
}

function abrirVisorEPUB(url) {
    window.location.href = `libro.html?epub=${url}`;
}

window.onload = mostrarGradosLecciones;
