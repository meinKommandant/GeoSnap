import simplekml

# --- Main Configuration ---
IMAGE_EXTENSIONS = ["*.jpg", "*.jpeg", "*.JPG", "*.JPEG", "*.png", "*.heic", "*.HEIC", "*.heif", "*.HEIF"]

# Extensions set for O(1) lookup
IMAGE_EXTENSIONS_SET = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".JPG", ".JPEG", ".PNG", ".HEIC", ".HEIF"}

# --- Excel Generation ---
EXCEL_HEADERS = {
    "B1": "Nº",
    "C1": "Archivo",
    "D1": "DESCRIPCIÓN",
    "E1": "Fecha",
    "F1": "Latitud",
    "G1": "Longitud",
    "H1": "Altitud [m]",
    "I1": "Rumbo [°]",
}

COLUMN_WIDTHS = {"A": 3, "B": 8, "C": 30, "D": 50, "E": 22, "F": 15, "G": 15, "H": 12, "I": 10}

# --- KML Generation ---
KML_CAMERA_ICON = "http://maps.google.com/mapfiles/kml/pal4/icon46.png"
ARROW_COLOR = simplekml.Color.yellow
ARROW_WIDTH = 4
ARROW_MAIN_AXIS_LENGTH = 30
ARROW_WING_LENGTH = 8
ARROW_WING_ANGLE = 150

# --- GUI Configuration ---
APP_TITLE = "GeoSnap"
APP_SIZE = "700x650"
APP_MIN_SIZE = (600, 500)


class UIMessages:
    WAITING = "Esperando..."
    PROCESSING = "Procesando..."
    STARTING = "Iniciando..."
    CANCELLING = "Cancelando..."
    CANCELLED = "⛔ Cancelado."
    SUCCESS = "✅ Listo."
    WARNING = "⚠️ Alerta."
    ERROR = "❌ Error."
    MODE_PHOTOS = "Modo: FOTOS ➔ KMZ + EXCEL"
    MODE_EXCEL = "Modo: EXCEL ➔ KMZ"
    STATUS_PHOTOS = "Listo."
    STATUS_EXCEL = "Modo Reconstrucción: Selecciona Excel y Fotos."
    BTN_GO = "GO"
