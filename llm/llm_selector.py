import os
from openai import AzureOpenAI
import json
from dotenv import load_dotenv

# 1. Cargar configuración de Azure OpenAI desde .env
load_dotenv()
endpoint = "https://voiceflip-openai.openai.azure.com/"
model_name = "gpt-4o-mini"
deployment = "gpt-4o-mini"
api_version = "2024-12-01-preview"
api_key = os.getenv("OPENAI_API_KEY")  # Debes poner tu key aquí

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=api_key,
)

# 2. Fragmento de HTML de ejemplo (puedes cambiarlo por el HTML real que scrapeas)
with open("llm/html_ejemplo.html", "r", encoding="utf-8") as f:
    html_code = f.read()

# 3. Prompt para el LLM
prompt = (
    "Dado el siguiente HTML, genera SOLO el selector CSS necesario para extraer el **título del producto**. "
    "No des explicación, responde solo con el selector CSS correcto para Selenium/BeautifulSoup.\n\n"
    "HTML:\n"
    + html_code
)

# 4. Llamada a Azure OpenAI
response = client.chat.completions.create(
    model=deployment,
    messages=[
        {"role": "system", "content": "Eres un experto en scraping y selectores CSS/XPath."},
        {"role": "user", "content": prompt},
    ],
    max_tokens=100
)
selector = response.choices[0].message.content.strip()
print("Selector sugerido por la IA:", selector)

# 5. Guardar el resultado en un archivo
with open("data/llm_selectors.json", "w", encoding="utf-8") as out_f:
    json.dump({"selector_titulo": selector}, out_f, ensure_ascii=False, indent=4)
print("Selector guardado en data/llm_selectors.json")