import os

import requests

from main import limpiar_nombre_archivo


def obtener_nombre_archivo(url, cookies=None):
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}  # Simula un navegador

    # Si tienes cookies, pásalas
    if cookies:
        cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    else:
        cookies_dict = {}

    # Realizar una petición HEAD para obtener solo los headers
    respuesta = session.head(url, cookies=cookies_dict, allow_redirects=True)

    # Revisar si el header 'Content-Disposition' está presente
    if "Content-Disposition" in respuesta.headers:
        content_disposition = respuesta.headers["Content-Disposition"]
        if "filename=" in content_disposition:
            nombre_archivo = content_disposition.split("filename=")[-1].strip('";')
            return nombre_archivo

    # Si no hay Content-Disposition, intenta con la URL
    return url.split("/")[-1]  # Última parte de la URL como nombre alternativo

def descargar_archivo(url_descarga, carpeta_destino, cookies):
    session = requests.Session()

    # Agregar cookies a la sesión de requests
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # Extraer el nombre del archivo desde la URL
    nombre_archivo = obtener_nombre_archivo(url_descarga, cookies)
    nombre_archivo = limpiar_nombre_archivo(nombre_archivo)
    ruta_destino = os.path.join(carpeta_destino, nombre_archivo)

    try:
        respuesta = session.get(url_descarga, stream=True)
        respuesta.raise_for_status()

        with open(ruta_destino, "wb") as archivo:
            for chunk in respuesta.iter_content(chunk_size=8192):
                archivo.write(chunk)

        print(f"Archivo descargado en: {ruta_destino}")
        return ruta_destino
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar el archivo: {e}")
        return None
