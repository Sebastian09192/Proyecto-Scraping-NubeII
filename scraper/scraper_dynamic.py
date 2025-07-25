from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
import traceback

# Ruta a chromedriver
CHROMEDRIVER_PATH = os.path.join("scraper", "driver", "chromedriver.exe")

options = Options()
# options.add_argument("--headless")  # Activar solo si no necesitas ver el navegador
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

os.makedirs("data", exist_ok=True)

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
wait = WebDriverWait(driver, 10)

try:
    driver.get("https://listado.mercadolibre.co.cr/laptop")

    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ui-search-layout__item")))

    for _ in range(2):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    productos = []
    items = driver.find_elements(By.CSS_SELECTOR, ".ui-search-layout__item")

    for item in items:
        try:
            # ✅ Selector correcto del título
            titulo = item.find_element(By.CSS_SELECTOR, "h3.poly-component__title-wrapper").text.strip()
            try:
                precio = item.find_element(By.CSS_SELECTOR, "span.andes-money-amount__fraction").text.strip()
                precio = f"₡{precio}"
            except:
                precio = "No disponible"

            productos.append({
                "titulo": titulo,
                "precio": precio
            })
        except Exception as e:
            print("❌ Error procesando un producto:", e)

    # Guardar en JSON
    with open("data/results_dynamic.json", "w", encoding="utf-8") as f:
        json.dump(productos, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Se guardaron {len(productos)} productos en 'data/results_dynamic.json'")

except Exception as e:
    print("❌ Error general:")
    traceback.print_exc()
    driver.save_screenshot("error_scraping.png")

finally:
    driver.quit()