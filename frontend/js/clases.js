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
    fetch('https://www.dropbox.com/scl/fi/0l8771dlvmlfstde4rtwn/CLASES.json?rlkey=dc0p3bzg4x5anncrv8yiusjvq&st=xohmcz3h&dl=1')
        .then(response => response.json())
        .then(data => {
            data.forEach(item => {
                const div = document.createElement("div");
                div.innerHTML = `
                    <h4>${item.titulo}</h4>
                    <iframe width="300" height="200" src="${item.url.replace("watch?v=", "embed/")}" frameborder="0" allowfullscreen></iframe>
                    <br><br>
                `;
                container.appendChild(div);
            });
        })
        .catch(err => {
            container.innerHTML += "<p>Error al cargar las clases.</p>";
            console.error(err);
        });
}

// Ejecutar cuando cargue la página
window.onload = mostrarGrados;
