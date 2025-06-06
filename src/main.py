import re
import os
import platform

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from file_utils import leer_archivo
from src.mainfunction import main_function


def get_desktop_path():
    system = platform.system()

    if system == "Windows":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                desktop = winreg.QueryValueEx(key, "Desktop")[0]
            return desktop
        except Exception as e:
            print(f"Error obteniendo el escritorio en Windows: {e}")
            return os.path.join(os.path.expanduser("~"), "Desktop")

    else:  # Linux, macOS, etc.
        return os.path.join(os.path.expanduser("~"), "Desktop")


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
        print(f"Creando dir en: {path}")
    else:
        print(f"Conflicto: ya existe un archivo o carpeta con el nombre '{path}'")
        # Dividimos la ruta en su directorio padre y el nombre del último componente.
        directorio_padre, nombre_actual = os.path.split(path)
        nuevo_nombre = f"Carpeta-{nombre_actual}"
        # Si directorio_padre está vacío (ruta relativa sin subcarpetas), os.path.join
        # devolverá simplemente 'Carpeta-<nombre_actual>'.
        nueva_ruta = os.path.join(directorio_padre, nuevo_nombre)
        os.makedirs(nueva_ruta)
        print(f"Creando dir en: {nueva_ruta}")


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

# Entra a un modulos de una página
if len(cursos) > 1:
    for curso in cursos:
        main_function(curso)
else:
    main_function(cursos[0])
