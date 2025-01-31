import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

def extraer_links(links):
    urls = []
    for l in links:
        url = l.get_attribute("href")
        if url is not None and url not in urls:  # Verificar si la URL ya está en la lista
            urls.append(url)  # Agregar solo si no está
    return urls

load_dotenv()

driver = webdriver.Chrome()
# carga la pagina
driver.get("https://auth.espol.edu.ec/login?service=https%3A%2F%2Faulavirtual.espol.edu.ec%2Flogin%2Fcas")

# escribe el usuario
usuario_box = driver.find_element(By.ID, "username")
usuario_box.send_keys(os.getenv("USER"))

# Escribe la contraseña
password_box = driver.find_element(By.ID, "password")
password_box.send_keys(os.getenv("PASS"))

# Da click en inicar sesion
iniciar_sesion = driver.find_element(By.NAME, "submit")
iniciar_sesion.click()

# Entra a un modulos de una página
driver.get("https://aulavirtual.espol.edu.ec/courses/27829/modules")

# Obtener todos los links de modulos
marco = driver.find_element(By.ID, "context_modules")
links = marco.find_elements(By.TAG_NAME, "a")

# poner las urls
urls = extraer_links(links)

# visitar las urls y agregar a sub_urls
sub_urls = []
for url in urls:
    print(f"Visitando url: {url}")  # Mostrar la URL que se va a visitar
    driver.get(url)
    marco = driver.find_element(By.ID, "content")
    links = marco.find_elements(By.TAG_NAME, "a")

    for l in links:
        url = l.get_attribute("href")
        if url is not None and url not in urls and "download" in url:  # Verificar si la URL ya está en la lista
            sub_urls.append(url)  # Agregar solo si no está

    print(sub_urls)


time.sleep(2)
