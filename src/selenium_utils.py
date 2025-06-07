from selenium.webdriver.common.by import By


def obtener_cookies_sesion(driver):
    # Extraer cookies
    cookies = driver.get_cookies()
    return cookies

def extraer_links_descarga(links):
    urls = []
    for l in links:
        url = l.get_attribute("href")
        if url is not None and url not in urls and 'download' in url:  # Verificar si la URL ya está en la lista
            urls.append(url)  # Agregar solo si no está
    return urls
