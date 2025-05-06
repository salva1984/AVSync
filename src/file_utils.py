def leer_archivo():
    with open("datos.txt", "r") as archivo:
        data = []
        for linea in archivo:
            data.append(linea.split("=")[1].strip("\n"))
            print(linea.split("="))
    return data
