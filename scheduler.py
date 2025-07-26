from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import logging

# Configurar el logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Función que ejecuta el scraper dinámico y estático
def ejecutar_scraping():
    logging.info("Iniciando scraper estático...")
    subprocess.run(["python", "scraper/scraper_static.py"], check=True)  # Ejecuta el scraper estático
    logging.info("Scraper estático completado.")
    
    logging.info("Iniciando scraper dinámico...")
    subprocess.run(["python", "scraper/scraper_dynamic.py"], check=True)  # Ejecuta el scraper dinámico
    logging.info("Scraper dinámico completado.")

# Crear el scheduler
scheduler = BlockingScheduler()

# Programar la ejecución cada 30 minutos
scheduler.add_job(ejecutar_scraping, 'interval', minutes=30)

logging.info("Scheduler iniciado. El scraping se ejecutará cada 30 minutos.")

# Iniciar el scheduler
scheduler.start()