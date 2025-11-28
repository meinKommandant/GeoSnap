import shutil
import os
from pathlib import Path


def limpiar_proyecto():
    # Definir la raíz del proyecto
    root = Path.cwd()

    # 1. Directorios a eliminar completamente (Carpetas generadas por PyInstaller y Python)
    directorios_a_borrar = [
        root / "build",
        root / "dist",
        root / "__pycache__",
        root / "src" / "__pycache__",
        root / "output" / "temp_thumbnails"
    ]

    # 2. Patrones de archivos a borrar recursivamente
    # IMPORTANTE: He quitado "*.spec" de aquí para proteger tu configuración de compilación.
    patrones = ["*.pyc", "*.pyo"]

    print(f"🧹 Iniciando limpieza en: {root}")

    # --- FASE 1: Borrar carpetas ---
    for carpeta in directorios_a_borrar:
        if carpeta.exists():
            try:
                shutil.rmtree(carpeta)
                print(f"✅ Carpeta eliminada: {carpeta.name}/")
            except Exception as e:
                print(f"❌ Error borrando carpeta {carpeta.name}: {e}")

    # --- FASE 2: Borrar archivos sueltos (RECURSIVO) ---
    # Esto busca en todas las subcarpetas archivos que coincidan con los patrones
    count_files = 0
    for patron in patrones:
        for archivo in root.rglob(patron):
            # Evitamos borrar cosas dentro de 'venv' por si acaso, aunque rglob suele ser seguro
            if "venv" not in str(archivo) and "env" not in str(archivo):
                try:
                    os.remove(archivo)
                    count_files += 1
                except Exception as e:
                    print(f"⚠️ No se pudo borrar {archivo.name}: {e}")

    if count_files > 0:
        print(f"✅ Se eliminaron {count_files} archivos temporales ({', '.join(patrones)}).")

    print("✨ Limpieza terminada.")


if __name__ == "__main__":
    limpiar_proyecto()