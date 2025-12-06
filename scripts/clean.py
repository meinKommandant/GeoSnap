import shutil
import os
from pathlib import Path


def limpiar_proyecto():
    # Definir la raíz del proyecto
    root = Path.cwd()

    # SECURITY: Verify we are in the GeoSnap project root before deleting anything
    required_markers = [
        root / "src",
        root / "geosnap_app.py",
        root / "pyproject.toml",
    ]

    missing = [str(m) for m in required_markers if not m.exists()]
    if missing:
        print("❌ ERROR DE SEGURIDAD: No estás en la raíz del proyecto GeoSnap.")
        print(f"   Directorio actual: {root}")
        print(f"   Archivos/carpetas no encontrados: {', '.join(missing)}")
        print("   Abortando limpieza para evitar borrar archivos incorrectos.")
        return

    # 1. Directorios a eliminar completamente (Carpetas generadas por PyInstaller y Python)
    directorios_a_borrar = [
        root / "build",
        root / "dist",
        root / "__pycache__",
        root / "src" / "__pycache__",
        root / "output" / "temp_thumbnails",
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
