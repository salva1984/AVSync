import re
import time
import winreg
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from file_utils import leer_archivo
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
    caracteres_invalidos = r'[<>:"/|?*]'  # Caracteres no permitidos en Windows
    return re.sub(caracteres_invalidos, reemplazo, nombre)


# Configurar Selenium para iniciar sesión y extraer cookies
def obtener_cookies_sesion(driver, url_login, usuario, password):
    driver.get(url_login)

    # Iniciar sesión (ajusta los selectores según sea necesario)
    driver.find_element(By.ID, "username").send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(password)
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


datos = leer_archivo()
correo = datos[0]
password = datos[1]
cursos = datos[2].split(",")
desktop_path = get_desktop_path()
chrome_options = Options()
chrome_options.add_experimental_option('detach', True)
# chrome_options.add_argument("--headless")  # Activar el modo headless
# chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=chrome_options)
cookies = obtener_cookies_sesion(driver,
                                 "https://auth.espol.edu.ec/login?service=https%3A%2F%2Faulavirtual.espol.edu.ec%2Flogin%2Fcas",
                                 correo,
                                 password)


def main_function(curso):
    driver.get(curso)
    boton_expandir = driver.find_element(By.ID, 'expand_collapse_all')
    if boton_expandir.get_attribute('aria-expanded') == 'true':
        boton_expandir.click()
        time.sleep(0.5)
        boton_expandir.click()
    else:
        boton_expandir.click()
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

                # Si no hay elementos en el stack (carpeta raiz)
                if len(stack) == 0:
                    ruta_actual = raiz + "\\" + nombre_archivo
                    stack.append(ruta_actual)

                    if enlace:
                        if links:  # idk
                            if len(links) > 1: # Si hay mas de un enlace (documento) en la pagina...
                                crear_dir(ruta_actual) # Crea una carpeta
                                for link in links: # Y descarga los archivos adentro
                                    descargar_archivo(link, ruta_actual, cookies, archivos_no_descargados)
                            else: # Si solo tiene un archivo
                                descargar_archivo(links.pop(), raiz, cookies, archivos_no_descargados)
                else: # Si estas debajo de alguna carpeta
                    ruta_actual = stack[-1] + "\\" + nombre_archivo # Recupera la ruta de la carpeta padre
                    stack.append(ruta_actual) # Agrega esta ruta en caso de que pueda ser una carpeta que contenga mas carpetas
                    if enlace:
                        if len(links) > 1:
                            crear_dir(ruta_actual)
                            for link in links: # Descarga los archivos en la carpeta creada
                                descargar_archivo(link, ruta_actual, cookies, archivos_no_descargados)
                        else:
                            if len(links) > 0: # Si solo tiene un archivo
                                descargar_archivo(links.pop(), stack[-2], cookies, archivos_no_descargados)
                                # stack[-2] es la ruta padre de este archivo, stack[-1] es este archivo
                if siguiente_archivo: #Si el siguiente archivo NO es un separador
                    if siguiente_archivo["nivel"] > nivel: # Si el siguiente "archivo" es un hijo de el actual
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
        with open("archivos_no_descargados.txt", "w") as f:
            f.write("=" * 50 + "\n")
            f.write("!!! ADVERTENCIA: HAY ARCHIVOS NO DESCARGADOS !!!\n")
            for i in archivos_no_descargados:
                f.write(f"{i}\n")
            f.write("=" * 50 + "\n")

        print("\n[!] Algunos archivos no se pudieron descargar.")
        print("[!] Revisa el archivo 'archivos_no_descargados.txt' para más detalles.\n")


# Entra a un modulos de una página
if len(cursos) > 1:
    for curso in cursos:
        main_function(curso)
else:
    main_function(cursos)
