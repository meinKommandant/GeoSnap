import os
from PIL import Image, ExifTags

# --- CONFIGURACIÓN DE LA RUTA ---
# Usamos r"" para que Windows lea bien las barras
carpeta = os.path.join(os.getcwd(), "input")

# --- CAMBIO: SOLICITUD INTERACTIVA ---
print(f"📂 Carpeta de búsqueda: {carpeta}")
# Solicitamos al usuario que escriba el nombre del archivo
nombre_archivo = input("✍️  Introduce el nombre del archivo (ej. foto.jpg): ").strip()

# Esto une la carpeta y el archivo correctamente
ruta_completa = os.path.join(carpeta, nombre_archivo)


def obtener_metadatos(ruta):
    print(f"\n--- Procesando archivo en: {ruta} ---")

    try:
        img = Image.open(ruta)
        exif_data = img._getexif()

        if not exif_data:
            print("❌ La imagen se abrió, pero NO tiene metadatos EXIF.")
            return

        print("✅ Metadatos encontrados. Buscando datos de orientación y GPS...\n")

        # Banderas para saber si encontramos algo
        found_gps = False

        for tag_id in exif_data:
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            data = exif_data.get(tag_id)

            # 1. Orientación de la imagen (Rotación)
            if tag == 'Orientation':
                print(f"📷 Orientación (Rotación): {data} (1=Normal)")

            # 2. Datos GPS
            if tag == 'GPSInfo':
                found_gps = True
                print("\n🌍 --- DATOS GPS ---")

                gps_tags = {}
                for key in data.keys():
                    decode_name = ExifTags.GPSTAGS.get(key, key)
                    gps_tags[decode_name] = data[key]

                # Dirección de la brújula (Azimut)
                img_direction = gps_tags.get('GPSImgDirection')
                img_ref = gps_tags.get('GPSImgDirectionRef')

                if img_direction:
                    print(f"🧭 Dirección de la cámara (Azimut): {img_direction} grados")
                    print(f"   Referencia: {img_ref} (M=Magnético, T=Verdadero/Geográfico)")
                else:
                    print("⚠️ Hay coordenadas GPS, pero NO se grabó la dirección (brújula).")

                # Coordenadas (Latitud/Longitud)
                lat = gps_tags.get('GPSLatitude')
                lon = gps_tags.get('GPSLongitude')
                print(f"📍 Latitud (raw): {lat}")
                print(f"📍 Longitud (raw): {lon}")

        if not found_gps:
            print("\n❌ No se encontraron datos GPS en la imagen.")

    except FileNotFoundError:
        print("\n❌ ERROR: No encuentro el archivo.")
        print("👉 Verifica que el nombre sea exacto y que el archivo esté dentro de la carpeta 'input'.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")


# --- EJECUCIÓN ---
if nombre_archivo:
    obtener_metadatos(ruta_completa)
else:
    print("⚠️ No has escrito ningún nombre de archivo. Finalizando.")