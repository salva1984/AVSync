from selenium.webdriver.chrome.options import Options

from src.file_utils import leer_archivo, get_desktop_path


def pop_n(stack, n):
    for i in range(n):
        stack.pop()


def get_config():
    datos = leer_archivo()
    correo = datos[0]
    password = datos[1]
    cursos = datos[2].split(",")
    desktop_path = get_desktop_path()
    chrome_options = Options()
    chrome_options.add_experimental_option('detach', True)
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-gpu")


    return {
        "correo": correo,
        "password": password,
        "cursos": cursos,
        "desktop_path": desktop_path,
        "driver_config": chrome_options
    }
