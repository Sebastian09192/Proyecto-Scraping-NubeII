// URL de la API Flask (ajusta el puerto si es necesario)
const API_URL = "http://localhost:5000/api/productos";

async function obtenerProductos() {
    try {
        const resp = await fetch(API_URL);
        if (!resp.ok) throw new Error("Error en la API");
        const productos = await resp.json();
        renderizarProductos(productos);
    } catch (error) {
        document.getElementById("no-data").textContent = "No se pudieron cargar los productos. Verifica la API.";
        document.getElementById("no-data").classList.remove("d-none");
    }
}

// Cuando cargue el DOM, solicita los productos
document.addEventListener("DOMContentLoaded", obtenerProductos);