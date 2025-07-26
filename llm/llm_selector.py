import os
import json
from flask import Blueprint, request, jsonify
from openai import AzureOpenAI
from dotenv import load_dotenv
import re

# Configurar Flask Blueprint
llm_selector_bp = Blueprint("llm_selector", __name__)

# Cargar variables de entorno
load_dotenv()

# Configuración de Azure OpenAI
endpoint = "https://voiceflip-openai.openai.azure.com/"
deployment = "gpt-4o-mini"
api_version = "2024-12-01-preview"
api_key = os.getenv("OPENAI_API_KEY")  # Usa .env para evitar exponer la API key

# Inicializar cliente
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=endpoint,
)

# Ruta POST para recibir HTML y retornar selectores
@llm_selector_bp.route("/api/llm_selector", methods=["POST"])
def selector():
    data = request.get_json()
    html = data.get("html", "")

    if not html:
        return jsonify({"error": "HTML no proporcionado"}), 400

    prompt = f"""
Actúa como un experto en scraping. Analiza el siguiente HTML extraído de una búsqueda en MercadoLibre y genera un objeto JSON con los selectores **CSS** y **XPath** para cada uno de los siguientes campos:

- título del producto
- precio del producto
- enlace a la página del producto
- imagen del producto

La respuesta debe tener este formato exacto (**solo JSON, sin explicaciones**):

{{
  "titulo": {{
    "css": "...",
    "xpath": "..."
  }},
  "precio": {{
    "css": "...",
    "xpath": "..."
  }},
  "link": {{
    "css": "...",
    "xpath": "..."
  }},
  "imagen": {{
    "css": "...",
    "xpath": "..."
  }}
}}

HTML:
{html}
    """

    try:
        respuesta = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        contenido = respuesta.choices[0].message.content.strip()

        # Limpieza si viene con ```json ... ```
        contenido_limpio = re.sub(r"^```json\s*|\s*```$", "", contenido.strip())

        # Parsear el JSON limpio
        resultado = json.loads(contenido_limpio)

        return jsonify({"success": True, "selectores": resultado})

    except json.JSONDecodeError:
        return jsonify({"error": "La respuesta del modelo no es JSON válido", "contenido": contenido}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500