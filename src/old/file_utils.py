import os
import platform
import re


def leer_archivo():
    with open("datos.txt", "r") as archivo:
        data = []
        for linea in archivo:
            data.append(linea.split("=")[1].strip("\n"))
            # print(linea.split("="))
    return data


def limpiar_nombre_archivo(nombre, reemplazo="-"):
    caracteres_invalidos = r'[<>:"/|?*]'  # Caracteres no permitidos en Windows
    return re.sub(caracteres_invalidos, reemplazo, nombre)


def crear_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print("Creando dir a:" + path)

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
