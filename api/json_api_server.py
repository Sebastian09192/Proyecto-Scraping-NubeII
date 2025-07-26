from flask import Flask, jsonify
import psycopg2
from dotenv import load_dotenv
import os
from flask_cors import CORS
from llm.llm_selector import llm_selector_bp
from flask import send_from_directory

# Cargar variables de entorno (.env)
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
CORS(app)
app.register_blueprint(llm_selector_bp)

def get_db_connection():
    conn = psycopg2.connect(DB_URL)
    return conn

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOWNLOADS_FOLDER = os.path.join(BASE_DIR, 'downloads')

@app.route('/downloads/<path:filename>')
def download_file(filename):
    from urllib.parse import unquote
    filename = unquote(filename)
    return send_from_directory(DOWNLOADS_FOLDER, filename)

@app.route("/api/productos", methods=["GET"])
def obtener_productos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo, precio, origen, archivo_nombre, archivo_url, hash_archivo, estado, fecha_registro, ultima_actualizacion
        FROM productos
        ORDER BY id DESC
    """)
    columnas = [desc[0] for desc in cursor.description]
    productos = []
    for fila in cursor.fetchall():
        productos.append(dict(zip(columnas, fila)))
    cursor.close()
    conn.close()
    return jsonify(productos)

@app.route("/api/", methods=["GET"])
def home():
    return jsonify({"status": "API OK", "endpoints": ["/api/productos"]})

if __name__ == "__main__":
    # Ejecuta la API en http://localhost:5000
    app.run(debug=True)