import requests
from bs4 import BeautifulSoup
import json
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Crear la carpeta data si no existe
os.makedirs("data", exist_ok=True)

# URL base del sitio
BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"
HEADERS = {"User-Agent": "Mozilla/5.0"}

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
            "rating": calificacion,
            "origen": "books.toscrape.com"
        })
    return resultados

# Recolectar datos de múltiples páginas
todos_los_libros = []
for i in range(1, 6):  # Cambia el rango si quieres más páginas
    print(f"Scrapeando página {i}...")
    libros = obtener_libros(i)
    todos_los_libros.extend(libros)

# Guardar resultados en un archivo JSON
output_file = "data/results.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(todos_los_libros, f, indent=4, ensure_ascii=False)

print(f"\nSe guardaron {len(todos_los_libros)} libros en '{output_file}'")

# Cargar variables de entorno
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def guardar_en_postgres(path_json, origen):
    try:
        with open(path_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()

        for prod in data:
            titulo = prod.get("titulo")
            precio = prod.get("precio")
            origen_val = prod.get("origen", origen)
            # Solo insertamos las columnas que existen en tu tabla
            cursor.execute("SELECT id FROM productos WHERE titulo = %s", (titulo,))
            existente = cursor.fetchone()
            if existente:
                cursor.execute("""
                    UPDATE productos SET
                        precio = %s,
                        ultima_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (precio, existente[0]))
            else:
                cursor.execute("""
                    INSERT INTO productos (titulo, precio, origen)
                    VALUES (%s, %s, %s)
                """, (titulo, precio, origen_val))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Datos de {origen} guardados en PostgreSQL.")

    except Exception as e:
        print("❌ Error al guardar en PostgreSQL:", e)

guardar_en_postgres(output_file, "estático")