import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

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



time.sleep(2)
