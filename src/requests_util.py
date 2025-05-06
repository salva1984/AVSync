import os
import time
import requests




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

def descargar_archivo(url_descarga, carpeta_destino, cookies, archivos_no_descargados, intentos_max=3):
    from main import limpiar_nombre_archivo
    session = requests.Session()

    # Agregar cookies a la sesión de requests
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # Intentar obtener el nombre del archivo
    try:
        nombre_archivo = obtener_nombre_archivo(url_descarga, cookies)
        if not nombre_archivo:
            raise ValueError("No se pudo obtener el nombre del archivo.")
    except Exception as e:
        print(f"Error al obtener el nombre del archivo: {e}")
        archivos_no_descargados.append(url_descarga)
        return None

    # Limpiar y formatear el nombre del archivo
    nombre_archivo = limpiar_nombre_archivo(nombre_archivo)
    ext = f"({nombre_archivo.split('.')[-1].upper()}) "
    nombre_archivo = ext + nombre_archivo
    ruta_destino = os.path.join(carpeta_destino, nombre_archivo)

    if os.path.exists(ruta_destino):
        print(f"El archivo {nombre_archivo} ya existe en {carpeta_destino}. Omitiendo descarga.")
        return ruta_destino

    # Intentos de descarga
    for intento in range(intentos_max):
        try:
            respuesta = session.get(url_descarga, stream=True, timeout=10)
            respuesta.raise_for_status()

            # Guardar el archivo en la ruta de destino
            with open(ruta_destino, "wb") as archivo:
                for chunk in respuesta.iter_content(chunk_size=8192):
                    archivo.write(chunk)

            print(f"Archivo descargado en: {ruta_destino}")
            return ruta_destino

        except requests.exceptions.ConnectTimeout:
            print(f"Intento {intento + 1}/{intentos_max}: Tiempo de espera agotado para {url_descarga}.")
        except requests.exceptions.RequestException as e:
            print(f"Intento {intento + 1}/{intentos_max}: Error al descargar {url_descarga}: {e}")

        # Esperar antes de reintentar
        time.sleep(5 * (intento + 1))

    print(f"No se pudo descargar el archivo después de {intentos_max} intentos: {url_descarga}")
    archivos_no_descargados.append(url_descarga)
    return None
