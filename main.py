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


# Configurar Selenium para iniciar sesión y extraer cookies
def obtener_cookies_sesion(driver, url_login, usuario, contraseña):
    driver.get(url_login)

    # Iniciar sesión (ajusta los selectores según sea necesario)
    driver.find_element(By.ID, "username").send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(contraseña)
    driver.find_element(By.NAME, "submit").click()

    # Extraer cookies
    cookies = driver.get_cookies()
    return cookies


def crear_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print("Creando dir a:" + path)


def crear_dir_force(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
        print("Creando dir a:" + path)
    else:
        print(f'Conflicto de carpeta-archivo con el mismo nombre en {path}')
        path = path.split('\\')
        path[-1] = 'Carpeta-' + path[-1]
        path = "\\".join(path)
        os.makedirs(path)


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
desktop_path = get_desktop_path()
chrome_options = Options()
chrome_options.add_argument("--headless")  # Activar el modo headless
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)
cookies = obtener_cookies_sesion(driver,
                                 "https://auth.espol.edu.ec/login?service=https%3A%2F%2Faulavirtual.espol.edu.ec%2Flogin%2Fcas",
                                 os.getenv("USER"),
                                 os.getenv("PASS"))

driver.get("https://auth.espol.edu.ec/login?service=https%3A%2F%2Faulavirtual.espol.edu.ec%2Flogin%2Fcas")

# Entra a un modulos de una página
driver.get("https://aulavirtual.espol.edu.ec/courses/28459/modules")

# Obtener todos los links de modulos
marco = driver.find_element(By.ID, "context_modules")
divs = marco.find_elements(By.XPATH, "./div")

# No se puede iterar sobre divs directamente...
l_divs = []

for div in divs:
    # Obtenemos la ruta raiz
    raiz = desktop_path + "\\" + limpiar_nombre_archivo(driver.title) + "\\" + limpiar_nombre_archivo(
        div.get_attribute("aria-label"))

    # Get all the "content" of the div
    contenido = WebDriverWait(div, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".ig-list.items.context_module_items"))
    )
    archivos = contenido.find_elements(By.XPATH, "./li")

    # Get relevant information about files
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

    # Add a dict with the root and all the files (not all the files have a link)
    l_divs.append({
        'raiz': raiz,
        'archivos': l_archivos,

    })

archivos_no_descargados = []

for ldiv in l_divs:
    raiz = ldiv['raiz']
    archivos = ldiv['archivos']
    print(f'Procesando div: {raiz}')
    crear_dir(raiz)

    stack = []
    for index, archivo in enumerate(archivos):
        driver.implicitly_wait(1)  # Espera implícita de 5 segundos

        nombre_archivo = archivo["nombre"]
        nivel = archivo["nivel"]
        enlace = archivo["link"]

        print(f"Nom archivo:{nombre_archivo}")
        print(f"Nivel: {nivel}")

        try:
            siguiente_archivo = archivos[index + 1]
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
                if enlace:
                    if links:  # idk
                        if len(links) > 1:
                            crear_dir(ruta_actual)
                            for link in links:
                                # descargar_archivo_con_selenium(link, ruta_actual,driver)
                                descargar_archivo(link, ruta_actual, cookies, archivos_no_descargados)
                        else:
                            # descargar_archivo_con_selenium(links.pop(), raiz,driver)
                            descargar_archivo(links.pop(), raiz, cookies, archivos_no_descargados)
            else:
                ruta_actual = stack[-1] + "\\" + nombre_archivo
                stack.append(ruta_actual)
                if enlace:
                    if len(links) > 1:
                        crear_dir(ruta_actual)
                        for link in links:
                            # descargar_archivo_con_selenium(link, ruta_actual,driver)
                            descargar_archivo(link, ruta_actual, cookies, archivos_no_descargados)
                    else:
                        if len(links) > 0:
                            # descargar_archivo_con_selenium(links.pop(), stack[-2],driver)
                            descargar_archivo(links.pop(), stack[-2], cookies, archivos_no_descargados)
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
                    print(f"El siguiente archivo: {siguiente_archivo['nombre']} contiene links.")
                    if len(stack) == 0:
                        ruta_actual = raiz + "\\" + nombre_archivo
                        stack.append(ruta_actual)
                    else:
                        ruta_actual = stack[-1] + "\\" + nombre_archivo
                        stack.append(ruta_actual)
                    crear_dir(ruta_actual)
                else:
                    print(f"El siguiente archivo: {siguiente_archivo['nombre']} es un separador.")

if len(archivos_no_descargados) > 0:
    print("\n" + "=" * 50)
    print("!!! ADVERTENCIA: HAY ARCHIVOS NO DESCARGADOS !!!")
    for i in archivos_no_descargados:
        print(i)
    print("=" * 50 + "\n")
