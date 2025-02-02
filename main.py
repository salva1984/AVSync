import re
import winreg
import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from requests_util import descargar_archivo


def get_desktop_path():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
        desktop = winreg.QueryValueEx(key, "Desktop")[0]
    return desktop


desktop_path = get_desktop_path()


def pop_n(stack, n):
    for i in range(n):
        stack.pop()


def limpiar_nombre_archivo(nombre, reemplazo="-"):
    """
    Reemplaza caracteres no válidos en nombres de archivos o carpetas en Windows.

    Argumentos:
    - nombre (str): Nombre original del archivo o carpeta.
    - reemplazo (str): Carácter con el que se reemplazarán los caracteres no permitidos (por defecto '_').

    Retorna:
    - str: Nombre limpio sin caracteres inválidos.
    """
    caracteres_invalidos = r'[<>:"/|?*]'  # Caracteres no permitidos en Windows
    return re.sub(caracteres_invalidos, reemplazo, nombre)


# def descargar_archivo_con_selenium(url, carpeta_destino, driver):
#     crear_dir(carpeta_destino)
#
#     nombre_archivo = get_filename(url)
#     ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
#
#     #  Extraer cookies de Selenium
#     cookies_selenium = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
#
#     #  Extraer headers (modifica si es necesario)
#     headers = {
#         "User-Agent": driver.execute_script("return navigator.userAgent;"),  # Simula el navegador
#         "Referer": driver.current_url,  # Indica de qué página vienes
#     }
#
#     try:
#         respuesta = requests.get(url, headers=headers, cookies=cookies_selenium, stream=True)
#         respuesta.raise_for_status()
#
#         with open(ruta_destino, "wb") as archivo:
#             for chunk in respuesta.iter_content(chunk_size=8192):
#                 archivo.write(chunk)
#
#         print(f"Archivo descargado en: {ruta_destino}")
#         return ruta_destino
#     except requests.exceptions.RequestException as e:
#         print(f"Error al descargar el archivo: {e}")
#         return None

# Configurar Selenium para iniciar sesión y extraer cookies
def obtener_cookies_sesion(url_login, usuario, contraseña):
    load_dotenv()
    options = Options()
    driver = webdriver.Chrome(options=options)

    driver.get(url_login)

    # Iniciar sesión (ajusta los selectores según sea necesario)
    driver.find_element(By.ID, "username").send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(contraseña)
    driver.find_element(By.NAME, "submit").click()

    # Extraer cookies
    cookies = driver.get_cookies()
    driver.quit()
    return cookies





def crear_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print("Creando dir a:" + path)


def extraer_links(links):
    urls = []
    for l in links:
        url = l.get_attribute("href")
        if url is not None and url not in urls:  # Verificar si la URL ya está en la lista
            urls.append(url)  # Agregar solo si no está
    return urls


def extraer_links_descarga(links):
    urls = []
    for l in links:
        url = l.get_attribute("href")
        if url is not None and url not in urls and 'download' in url:  # Verificar si la URL ya está en la lista
            urls.append(url)  # Agregar solo si no está
    return urls


def calcular_nivel(file):
    nivel = file.get_attribute("class").split(" ")
    for n in nivel:
        if "indent" in n:
            nivel = n
            break
    nivel = nivel.split("_")[1][0]
    return nivel


load_dotenv()

load_dotenv()
# Obtén las cookies después de iniciar sesión
cookies = obtener_cookies_sesion(
    "https://auth.espol.edu.ec/login?service=https%3A%2F%2Faulavirtual.espol.edu.ec%2Flogin%2Fcas", os.getenv("USER"),
    os.getenv("PASS"))

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
driver.get("https://aulavirtual.espol.edu.ec/courses/28459/modules")

# Obtener todos los links de modulos
marco = driver.find_element(By.ID, "context_modules")
divs = marco.find_elements(By.XPATH, "./div")

for div in divs:
    raiz = div.get_attribute("aria-label")
    raiz = limpiar_nombre_archivo(raiz)
    print(raiz)
    raiz = desktop_path + "\\" + limpiar_nombre_archivo(driver.title) + "\\" + raiz
    crear_dir(raiz)

    contenido = WebDriverWait(div, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ig-list.items.context_module_items"))
    )

    stack = []

    archivos = contenido.find_elements(By.XPATH, "./li")

    # No se puede iterar sobre archivos directamente, al cambiar de página todos los webElements se convierten en Stale.
    l_archivos = []
    for archivo in archivos:
        nombre_archivo = limpiar_nombre_archivo(archivo.text.split("\n")[1])
        nivel = calcular_nivel(archivo)
        try:
            link = archivo.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            link = None
        l_archivos.append({
            "nombre": nombre_archivo,
            "nivel": nivel,
            "link": link,
        })

    for index, archivo in enumerate(l_archivos):
        driver.implicitly_wait(1)  # Espera implícita de 5 segundos

        nombre_archivo = archivo["nombre"]
        nivel = archivo["nivel"]
        enlace = archivo["link"]

        print(f"Nom archivo:{nombre_archivo}")
        print(f"Nivel: {nivel}")

        try:
            siguiente_archivo = l_archivos[index + 1]
        except:
            siguiente_archivo = None
        # Enlaces con contenido

        if enlace:
            driver.get(enlace)
            marco = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            links = marco.find_elements(By.TAG_NAME, "a")
            links = extraer_links_descarga(links)

            if len(stack) == 0:
                ruta_actual = raiz + "\\" + nombre_archivo
                stack.append(ruta_actual)
                if len(links) > 1:
                    crear_dir(ruta_actual)
                    for link in links:
                        # descargar_archivo_con_selenium(link, ruta_actual,driver)
                        descargar_archivo(link, ruta_actual, cookies)
                else:
                    # descargar_archivo_con_selenium(links.pop(), raiz,driver)
                    descargar_archivo(links.pop(), raiz, cookies)
            else:
                ruta_actual = stack[-1] + "\\" + nombre_archivo
                stack.append(ruta_actual)
                if enlace:
                    if len(links) > 1:
                        crear_dir(ruta_actual)
                        for link in links:
                            # descargar_archivo_con_selenium(link, ruta_actual,driver)
                            descargar_archivo(link, ruta_actual, cookies)
                    else:
                        if len(links) > 0:
                            # descargar_archivo_con_selenium(links.pop(), stack[-2],driver)
                            descargar_archivo(links.pop(), raiz, cookies)
            if siguiente_archivo:
                if siguiente_archivo["nivel"] > nivel:
                    crear_dir(ruta_actual)

                # Verificar si estan en el mismo lugar:
                if siguiente_archivo["nivel"] == nivel:
                    print(f"siguiente archivo en el mismo nivel")
                    stack.pop()

                # Verificar si el siguiente no es hijo del anterior
                if siguiente_archivo["nivel"] < nivel:
                    dif = int(nivel) - int(siguiente_archivo["nivel"])
                    pop_n(stack, dif + 1)
        else:
            print(f"{nombre_archivo} es un separador.")

            if siguiente_archivo:
                if siguiente_archivo["link"]:
                    if len(stack) == 0:
                        ruta_actual = raiz + "\\" + nombre_archivo
                        stack.append(ruta_actual)
                    else:
                        ruta_actual = stack[-1] + "\\" + nombre_archivo
                        stack.append(ruta_actual)
                    crear_dir(ruta_actual)
                else:
                    print(f"{siguiente_archivo['nombre']} es un divisor.")

# links = marco.find_elements(By.TAG_NAME, "a")
#
# # poner las urls
# urls = extraer_links(links)
#
# # visitar las urls y agregar a sub_urls
# sub_urls = []
# for url in urls:
#     print(f"Visitando url: {url}")  # Mostrar la URL que se va a visitar
#     driver.get(url)
#     marco = driver.find_element(By.ID, "content")
#     links = marco.find_elements(By.TAG_NAME, "a")
#
#     for l in links:
#         url = l.get_attribute("href")
#         if url is not None and url not in urls and "download" in url:  # Verificar si la URL ya está en la lista
#             sub_urls.append(url)  # Agregar solo si no está
#
#     print(sub_urls)
#
# time.sleep(2)
