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
                    <img src="../downloads/${producto.archivo_nombre}" class="card-img-top" alt="${producto.titulo}">
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