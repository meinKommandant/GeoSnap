# src/exceptions.py

class GeoSnapError(Exception):
    """Clase base para todas las excepciones de esta aplicación."""
    pass

class InputFolderMissingError(GeoSnapError):
    """Se lanza cuando la carpeta de entrada no existe."""
    def __init__(self, path):
        super().__init__(f"La carpeta de entrada no existe: {path}")

class NoImagesFoundError(GeoSnapError):
    """Se lanza cuando no hay imágenes válidas en la carpeta."""
    def __init__(self, path):
        super().__init__(f"No se encontraron imágenes (JPG/PNG) en: {path}")

class NoGPSDataError(GeoSnapError):
    """Se lanza si ninguna de las fotos procesadas tiene GPS."""
    def __init__(self):
        super().__init__("Terminado, pero no se encontraron fotos con datos GPS válidos.")

class ProcessCancelledError(GeoSnapError):
    """Se lanza cuando el usuario detiene el proceso manualmente."""
    def __init__(self):
        super().__init__("El proceso fue cancelado por el usuario.")