# 📸 Fotos2KMZ: Generador de Reportes Geo-Referenciados

> **Convierte tus fotos geoetiquetadas en reportes visuales (KMZ) y tabulados (Excel) en segundos.**

**Fotos2KMZ** es una aplicación de escritorio desarrollada en Python que procesa lotes de imágenes, extrae sus metadatos GPS y genera automáticamente archivos compatibles con Google Earth y hojas de cálculo detalladas.

---

## 🚀 Características Principales

* **🗺️ Generación de KMZ "Portátil":** Crea archivos `.kmz` con las miniaturas de las fotos **incrustadas**. Esto permite enviar el archivo por correo y visualizar las fotos en el mapa sin necesidad de adjuntar las imágenes originales.
* **📊 Reportes en Excel:** Genera una hoja de cálculo (`.xlsx`) con formato profesional, incluyendo bordes y encabezados, lista para entregar.
* **🖥️ Interfaz Gráfica (GUI):** Fácil de usar, sin necesidad de tocar código. Selecciona carpetas y procesa.
* **⚡ Procesamiento Paralelo:** Utiliza *hilos* (threading) para leer y extraer metadatos de múltiples imágenes simultáneamente, mejorando la velocidad.
* **🔄 Auto-Rotación:** Detecta la orientación EXIF para asegurar que las fotos verticales se muestren correctamente.
* **🧹 Utilidades de Limpieza:** Incluye scripts para limpiar archivos temporales y compilaciones previas.

---

## 🛠️ Requisitos e Instalación

### Prerrequisitos
* Python 3.8 o superior.
* Entorno virtual (recomendado).

### Instalación para Desarrollo

1.  **Clonar o descargar el repositorio**:
    ```bash
    git clone <url-del-repo>
    cd fotos2kmz
    ```

2.  **Crear y activar un entorno virtual**:
    * *Windows*:
        ```bash
        py -m venv venv
        .\venv\Scripts\activate
        ```
    * *macOS/Linux*:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

---

##  ▶️ Cómo Ejecutar

### Opción 1: Desde Código Fuente
Para abrir la interfaz gráfica:

```bash
py src/gui.py