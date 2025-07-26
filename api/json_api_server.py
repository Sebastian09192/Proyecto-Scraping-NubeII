from flask import Flask, jsonify
import psycopg2
from dotenv import load_dotenv
import os
from flask_cors import CORS

# Cargar variables de entorno (.env)
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = psycopg2.connect(DB_URL)
    return conn

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