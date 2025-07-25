import requests
from bs4 import BeautifulSoup
import json
import os

# Crear la carpeta data si no existe
os.makedirs("data", exist_ok=True)

# URL base del sitio
BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Función para obtener los datos de una página
def obtener_libros(pagina):
    url = BASE_URL.format(pagina)
    respuesta = requests.get(url, headers=HEADERS)

    if respuesta.status_code != 200:
        print(f"Error al acceder a la página {pagina}")
        return []

    soup = BeautifulSoup(respuesta.text, "html.parser")
    libros = soup.select("article.product_pod")

    resultados = []
    for libro in libros:
        titulo = libro.h3.a["title"]
        precio = libro.select_one(".price_color").text.strip()
        calificacion = libro.select_one("p.star-rating")["class"][1]  # Ej: "Three", "One", etc.

        resultados.append({
            "titulo": titulo,
            "precio": precio,
            "rating": calificacion
        })

    return resultados

# Recolectar datos de múltiples páginas
todos_los_libros = []
for i in range(1, 6):  # Puedes aumentar el rango para más páginas
    print(f"Scrapeando página {i}...")
    libros = obtener_libros(i)
    todos_los_libros.extend(libros)

# Guardar resultados en un archivo JSON
output_file = "data/results.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(todos_los_libros, f, indent=4, ensure_ascii=False)

print(f"\nSe guardaron {len(todos_los_libros)} libros en '{output_file}'")