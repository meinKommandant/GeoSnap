# src/config.py
import json
from pathlib import Path

# Guardamos la configuración en la carpeta de usuario para que sea persistente
# Windows: C:\Users\TuUsuario\.fotos2kmz_settings.json
CONFIG_FILE = Path.home() / ".fotos2kmz_settings.json"

DEFAULT_CONFIG = {
    "input_dir": "",
    "output_dir": "",
    "project_name": "Mi_Reporte"
}


class ConfigManager:
    @staticmethod
    def load_config():
        """Carga la configuración desde el archivo JSON o devuelve los valores por defecto."""
        if not CONFIG_FILE.exists():
            return DEFAULT_CONFIG.copy()

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Nos aseguramos de que no falten claves si actualizamos la app
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception as e:
            print(f"⚠️ No se pudo cargar la configuración: {e}")
            return DEFAULT_CONFIG.copy()

    @staticmethod
    def save_config(input_dir, output_dir, project_name):
        """Guarda las rutas actuales en el archivo JSON."""
        data = {
            "input_dir": str(input_dir),
            "output_dir": str(output_dir),
            "project_name": str(project_name)
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error guardando configuración: {e}")