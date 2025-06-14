# AVSync
<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white" />
  <img src="https://img.shields.io/badge/Canvas_LMS-E34F26?style=for-the-badge&logo=canvas&logoColor=white" />
</p>

Herramienta en Python para descargar automáticamente todos los archivos (PDF, DOCX, PPTX, etc.) de un curso en Aula Virtual (Canvas) y organizarlos en carpetas según la jerarquía de módulos.

Ideal para estudiantes que quieren respaldar su material de clase sin tener que descargar archivo por archivo manualmente.

---
## 🚀 Características

- ✅ Autenticación automática en Aula Virtual (Canvas)

- ✅ Descarga de archivos desde múltiples cursos

- ✅ Preservación de la estructura jerárquica de archivos
  
- ✅ Guardado en carpetas organizadas en el escritorio del usuario

- ⚙️ Soporte para múltiples tipos de archivos comunes (PDF, DOCX, PPTX, etc.)

## 🛠️ Tecnologías

- Python 3.11

- Selenium WebDriver

- Web scraping con XPath, CSS Selector

- Sistema de archivos local (os, pathlib)

## 🧩 Estructura del Proyecto

```
AVSync/
├── src/                       # Código fuente principal
│   ├── main.py                # Script principal
│   ├── mainfunction.py        # Función principal de ejecución
│   ├── selenium_utils.py      # Funciones relacionadas con Selenium
│   ├── file_utils.py          # Funciones para manejo de archivos y directorios
│   ├── requests_util.py       # Funciones auxiliares para requests
│   ├── utils.py               # Utilidades generales
│   └── datos.txt              # Archivo de credenciales y enlaces
├── requirements.txt           # Dependencias del proyecto
├── README.md                  # Este archivo
├── .gitignore                 # Archivos y carpetas ignoradas por Git
```

## ⚙️ Instalación

1. Clona el repositorio

   ```bash
   git clone https://github.com/tuusuario/AVSync.git
   cd AVSync
   ```

2. Crea y activa un entorno virtual (opcional pero recomendado)

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Instala las dependencias

   ```bash
   pip install -r requirements.txt
   ```

4. Crea el archivo `datos.txt` en la carpeta `src/` con el siguiente formato:

   ```txt
   user=tu_usuario
   pass=tu_contraseña
   cursos=https://aulavirtual.edu.ec/curso1Paginademodulo,https://aulavirtual.edu.ec/curso2Paginademodulo
   ```

## ▶️ Uso

```bash
python src/main.py
```

El script iniciará un navegador, iniciará sesión y descargará todos los archivos en carpetas estructuradas dentro del escritorio.

## ✅ Ejemplo de Código

```python
# src/main.py
from mainfunction import ejecutar_descarga

ejecutar_descarga("src/datos.txt")
```

## 🪪 Licencia

Este proyecto está bajo la licencia MIT.


