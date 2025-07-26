// Renderiza la lista de productos en tarjetas Bootstrap



function renderizarProductos(productos) {
    const container = document.getElementById("productos-container");
    const noData = document.getElementById("no-data");
    container.innerHTML = ""; // Limpia el contenido anterior

    

    if (!productos || productos.length === 0) {
        noData.classList.remove("d-none");
        return;
    }
    noData.classList.add("d-none");

    productos.forEach(producto => {
        const card = document.createElement("div");
        card.className = "col-md-4 mb-4";
        card.innerHTML = `
            <div class="card shadow-sm h-100">
                <!-- Mostrar imagen del producto -->
                
                <div class="card-body">
                    <img src="http://localhost:5000/downloads/${producto.archivo_nombre}" class="card-img-top" alt="${producto.titulo}">
                    <h5 class="card-title">${producto.titulo}</h5>
                    <p class="card-text"><strong>Precio:</strong> ${producto.precio || 'No disponible'}</p>
                    <p class="card-text"><strong>Origen:</strong> ${producto.origen || '-'}</p>
                    <p class="card-text"><strong>Estado:</strong> ${producto.estado || '-'}</p>
                    <small class="text-muted">Registrado: ${producto.fecha_registro ? producto.fecha_registro.split('T')[0] : '-'}</small>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

async function enviarHTMLAlLLM() {
    const html = document.getElementById("htmlInput").value.trim();
    const resultado = document.getElementById("llm-result");

    if (!html) {
        resultado.className = "alert alert-warning";
        resultado.textContent = "Por favor pega algún HTML antes de enviar.";
        resultado.classList.remove("d-none");
        return;
    }

    try {
        const res = await fetch("http://localhost:5000/api/llm_selector", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ html })
        });

        const data = await res.json();

        if (data.success) {
            resultado.className = "alert alert-success";
            resultado.textContent = "✅ Selectores generados correctamente. Revisa la consola.";
            console.log("✅ Selectores generados por la IA:", data.selectores);
        } else {
            resultado.className = "alert alert-danger";
            resultado.textContent = data.error || "❌ Error generando selectores.";
            console.error(data);
        }

        resultado.classList.remove("d-none");
    } catch (err) {
        resultado.className = "alert alert-danger";
        resultado.textContent = "❌ Error al conectar con la API.";
        resultado.classList.remove("d-none");
        console.error(err);
    }
}