from selenium import webdriver
from selenium.webdriver.common.by import By

from src.mainfunction import main_function
from src.selenium_utils import obtener_cookies_sesion
from src.utils import get_config

config = get_config()
correo = config["correo"]
password = config['password']
cursos = config['cursos']
driver_config = config['driver_config']
driver = webdriver.Chrome(options=driver_config)
driver.get("https://auth.espol.edu.ec/login?service=https%3A%2F%2Faulavirtual.espol.edu.ec%2Flogin%2Fcas")

# Iniciar sesión (ajusta los selectores según sea necesario)
driver.find_element(By.ID, "username").send_keys(correo)
driver.find_element(By.ID, "password").send_keys(password)
driver.find_element(By.NAME, "submit").click()

cookies = obtener_cookies_sesion(driver)

# Entra a un modulos de una página
if len(cursos) > 1:
    for curso in cursos:
        main_function(curso,driver,cookies)
else:
    main_function(cursos[0],driver,cookies)

driver.quit()
