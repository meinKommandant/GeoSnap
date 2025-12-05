# src/config.py
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

# Configure logger
logger = logging.getLogger(__name__)

# Config paths
CONFIG_DIR = Path.home() / ".geosnap"
CONFIG_FILE = CONFIG_DIR / "settings.json"
PROFILES_DIR = CONFIG_DIR / "profiles"

# Ensure config directories exist
CONFIG_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)

DEFAULT_CONFIG = {
    "input_dir": "",
    "output_dir": "",
    "project_name": "Mi_Reporte",
    # New settings
    "thumbnail_size": 800,
    "jpeg_quality": 75,
    "arrow_length": 30,
    "arrow_width": 4,
}


class ConfigManager:
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Carga la configuración desde el archivo JSON o devuelve los valores por defecto."""
        if not CONFIG_FILE.exists():
            return DEFAULT_CONFIG.copy()

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge with defaults to handle new keys
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception as e:
            logger.warning(f"No se pudo cargar la configuración: {e}")
            return DEFAULT_CONFIG.copy()

    @staticmethod
    def save_config(input_dir: str = "", output_dir: str = "", project_name: str = "", **kwargs) -> None:
        """Guarda la configuración completa en el archivo JSON."""
        # Load existing config first
        current = ConfigManager.load_config()

        # Update with provided values
        if input_dir:
            current["input_dir"] = str(input_dir)
        if output_dir:
            current["output_dir"] = str(output_dir)
        if project_name:
            current["project_name"] = str(project_name)

        # Update any additional settings
        current.update(kwargs)

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=4)
        except Exception as e:
            logger.warning(f"Error guardando configuración: {e}")

    @staticmethod
    def update_settings(settings: Dict[str, Any]) -> None:
        """Update only processing settings (not paths)."""
        current = ConfigManager.load_config()
        for key in ["thumbnail_size", "jpeg_quality", "arrow_length", "arrow_width"]:
            if key in settings:
                current[key] = settings[key]

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=4)
        except Exception as e:
            logger.warning(f"Error guardando ajustes: {e}")

    # --- Profile Management ---
    @staticmethod
    def list_profiles() -> List[str]:
        """List all saved profile names."""
        return [p.stem for p in PROFILES_DIR.glob("*.json")]

    @staticmethod
    def save_profile(name: str, config: Dict[str, Any]) -> None:
        """Save current config as a named profile."""
        profile_path = PROFILES_DIR / f"{name}.json"
        try:
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            logger.info(f"Perfil guardado: {name}")
        except Exception as e:
            logger.warning(f"Error guardando perfil: {e}")

    @staticmethod
    def load_profile(name: str) -> Dict[str, Any]:
        """Load a named profile."""
        profile_path = PROFILES_DIR / f"{name}.json"
        if not profile_path.exists():
            logger.warning(f"Perfil no encontrado: {name}")
            return DEFAULT_CONFIG.copy()

        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception as e:
            logger.warning(f"Error cargando perfil: {e}")
            return DEFAULT_CONFIG.copy()

    @staticmethod
    def delete_profile(name: str) -> bool:
        """Delete a named profile."""
        profile_path = PROFILES_DIR / f"{name}.json"
        try:
            if profile_path.exists():
                profile_path.unlink()
                return True
        except Exception as e:
            logger.warning(f"Error eliminando perfil: {e}")
        return False
