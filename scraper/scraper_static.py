import requests
from bs4 import BeautifulSoup
import json
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import hashlib

# Crear carpetas si no existen
os.makedirs("data", exist_ok=True)
os.makedirs("downloads", exist_ok=True)
os.makedirs("logs", exist_ok=True)

def log_mensaje(msg):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("logs/scraper.log", "a", encoding="utf-8") as logf:
        logf.write(f"[{fecha}] {msg}\n")

BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"
BOOKS_BASE = "http://books.toscrape.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# =========== FUNCIONES DE UTILIDAD ==============

def calcular_hash_archivo(path):
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def registrar_archivo_en_json(info, path_json):
    archivos = []
    if os.path.exists(path_json):
        with open(path_json, "r", encoding="utf-8") as f:
            try:
                archivos = json.load(f)
            except:
                archivos = []
    archivos.append(info)
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(archivos, f, indent=4, ensure_ascii=False)

def registrar_evento(evento, path_json="data/events.json"):
    eventos = []
    if os.path.exists(path_json):
        with open(path_json, "r", encoding="utf-8") as f:
            try:
                eventos = json.load(f)
            except:
                eventos = []
    eventos.append(evento)
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(eventos, f, indent=4, ensure_ascii=False)

# =========== SCRAPING Y DESCARGA ==============

def obtener_libros(pagina):
    url = BASE_URL.format(pagina)
    respuesta = requests.get(url, headers=HEADERS)
    if respuesta.status_code != 200:
        print(f"Error al acceder a la página {pagina}")
        log_mensaje(f"Error al acceder a la página {pagina}")
        return []

    soup = BeautifulSoup(respuesta.text, "html.parser")
    libros = soup.select("article.product_pod")
    resultados = []
    for libro in libros:
        titulo = libro.h3.a["title"]
        precio = libro.select_one(".price_color").text.strip()
        calificacion = libro.select_one("p.star-rating")["class"][1]
        img_tag = libro.select_one("img")
        img_src = img_tag["src"].replace("../", "")
        img_url = BOOKS_BASE + img_src

        nombre_archivo = titulo.replace(" ", "_").replace("/", "_") + ".jpg"
        path_archivo = os.path.join("downloads", nombre_archivo)
        try:
            img_resp = requests.get(img_url)
            with open(path_archivo, "wb") as img_f:
                img_f.write(img_resp.content)
            hash_img = calcular_hash_archivo(path_archivo)
            info_archivo = {
                "titulo": titulo,
                "archivo_nombre": nombre_archivo,
                "archivo_url": img_url,
                "hash_archivo": hash_img,
                "descargado_en": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "origen": "books.toscrape.com"
            }
            registrar_archivo_en_json(info_archivo, "data/files.json")
            # Registra evento de descarga
            evento_archivo = {
                "title": "Archivo descargado",
                "descripcion": f"Descargado: {nombre_archivo}",
                "tipo": "archivo_descargado",
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "archivo_nombre": nombre_archivo,
                "archivo_url": img_url,
                "hash_archivo": hash_img
            }
            registrar_evento(evento_archivo)
            log_mensaje(f"Imagen descargada y registrada: {nombre_archivo}")
        except Exception as e:
            print(f"Error al descargar imagen de {titulo}: {e}")
            log_mensaje(f"Error al descargar imagen de {titulo}: {e}")
            nombre_archivo = ""
            img_url = ""
            hash_img = ""

        resultados.append({
            "titulo": titulo,
            "precio": precio,
            "rating": calificacion,
            "origen": "books.toscrape.com",
            "archivo_nombre": nombre_archivo,
            "archivo_url": img_url,
            "hash_archivo": hash_img
        })
    return resultados

# =========== RECOLECTA DATOS ==============

log_mensaje("==== Ejecución de scraper estático iniciada ====")

todos_los_libros = []
for i in range(1, 6):
    log_mensaje(f"Scrapeando página {i}...")
    print(f"Scrapeando página {i}...")
    libros = obtener_libros(i)
    todos_los_libros.extend(libros)

# Guardar resultados en un archivo JSON
output_file = "frontend/data/results.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(todos_los_libros, f, indent=4, ensure_ascii=False)

msg_final = f"Se guardaron {len(todos_los_libros)} libros en '{output_file}'"
print(f"\n{msg_final}")
log_mensaje(msg_final)

# Evento de scraping completado
evento_scraping = {
    "title": "Scraping estático ejecutado",
    "descripcion": f"Se recolectaron {len(todos_los_libros)} libros.",
    "tipo": "scraping_estatico",
    "fecha": datetime.now().strftime("%Y-%m-%d"),
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "detalle": output_file
}
registrar_evento(evento_scraping)
log_mensaje("Evento de scraping registrado en events.json.")

# =========== GUARDA EN POSTGRES ==============
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
            archivo_nombre = prod.get("archivo_nombre", None)
            archivo_url = prod.get("archivo_url", None)
            hash_archivo = prod.get("hash_archivo", None)
            cursor.execute("SELECT id FROM productos WHERE titulo = %s", (titulo,))
            existente = cursor.fetchone()
            if existente:
                cursor.execute("""
                    UPDATE productos SET
                        precio = %s,
                        archivo_nombre = %s,
                        archivo_url = %s,
                        hash_archivo = %s,
                        ultima_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (precio, archivo_nombre, archivo_url, hash_archivo, existente[0]))
            else:
                cursor.execute("""
                    INSERT INTO productos (titulo, precio, origen, archivo_nombre, archivo_url, hash_archivo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (titulo, precio, origen_val, archivo_nombre, archivo_url, hash_archivo))
        conn.commit()
        cursor.close()
        conn.close()
        log_mensaje(f"✅ Datos de {origen} guardados en PostgreSQL.")
        print(f"✅ Datos de {origen} guardados en PostgreSQL.")
    except Exception as e:
        log_mensaje(f"❌ Error al guardar en PostgreSQL: {e}")
        print("❌ Error al guardar en PostgreSQL:", e)

guardar_en_postgres(output_file, "estático")
log_mensaje("==== Ejecución de scraper estático finalizada ====")