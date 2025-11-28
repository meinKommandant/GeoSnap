import logging
from PIL import Image, ExifTags
import pillow_heif
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

# Register HEIF opener
pillow_heif.register_heif_opener()

# IMPORTANTE: Importación directa (sin 'src.')
from .models import PhotoMetadata, GPSCoordinates

# Configurar logger
logger = logging.getLogger(__name__)

class GPSPhotoExtractor:
    def extract_metadata(self, file_path: Path) -> PhotoMetadata:
        """
        Lee una imagen y extrae sus metadatos y coordenadas GPS convertidas.
        """
        try:
            image = Image.open(file_path)

            # 1. Obtener datos EXIF crudos
            raw_exif = image._getexif()

            if not raw_exif:
                logger.warning(f"No EXIF data found for {file_path.name}")
                return PhotoMetadata(file_path.name, str(file_path), None, None)

            # 2. Mapear etiquetas
            exif_data = {
                ExifTags.TAGS.get(k, k): v
                for k, v in raw_exif.items()
            }

            # 3. Buscar datos GPS (ID 34853)
            gps_info = raw_exif.get(34853)

            timestamp = self._get_date(exif_data)

            gps_coords = None
            if gps_info:
                try:
                    gps_coords = self._get_lat_lon(gps_info)
                    # Validar coordenadas 0.0, 0.0 (error de señal GPS)
                    if gps_coords and gps_coords.latitude == 0.0 and gps_coords.longitude == 0.0:
                        logger.warning(f"GPS coordinates are (0.0, 0.0) for {file_path.name}. Treating as no GPS.")
                        gps_coords = None
                except Exception as e:
                    logger.warning(f"Error parsing GPS info for {file_path.name}: {e}")
                    gps_coords = None
            else:
                logger.debug(f"No GPS info found for {file_path.name}")

            return PhotoMetadata(
                filename=file_path.name,
                filepath=str(file_path),
                timestamp=timestamp,
                coordinates=gps_coords
            )

        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path.name}: {e}")
            return PhotoMetadata(file_path.name, str(file_path), None, None)

    def _get_date(self, exif_data: Dict[str, Any]) -> Optional[datetime]:
        date_str = exif_data.get('DateTimeOriginal') or exif_data.get('DateTime')
        if date_str and isinstance(date_str, str):
            try:
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            except ValueError:
                logger.warning(f"Invalid date format: {date_str}")
                return None
        return None

    def _get_lat_lon(self, gps_info: Dict[int, Any]) -> Optional[GPSCoordinates]:
        # Mapeo de tags GPS usando ExifTags.GPSTAGS si fuera necesario, 
        # pero los IDs son estándar: 1=LatRef, 2=Lat, 3=LonRef, 4=Lon, 6=Alt
        
        lat_dms = gps_info.get(2)
        lat_ref = gps_info.get(1)
        lon_dms = gps_info.get(4)
        lon_ref = gps_info.get(3)
        alt = gps_info.get(6, 0.0)

        if lat_dms and lat_ref and lon_dms and lon_ref:
            lat = self._to_decimal(lat_dms, lat_ref)
            lon = self._to_decimal(lon_dms, lon_ref)

            # Solo si lat y lon son válidos
            if lat is not None and lon is not None:
                if isinstance(alt, tuple):
                    try:
                        alt = float(alt[0]) / float(alt[1])
                    except (ZeroDivisionError, IndexError, ValueError):
                        alt = 0.0
                
                # Asegurar que alt es float
                try:
                    alt = float(alt)
                except (ValueError, TypeError):
                    alt = 0.0

                return GPSCoordinates(lat, lon, alt)
        return None

    def _to_decimal(self, dms_tuple: Tuple[Any, Any, Any], ref: str) -> Optional[float]:
        try:
            d = float(dms_tuple[0])
            m = float(dms_tuple[1])
            s = float(dms_tuple[2])

            decimal = d + (m / 60.0) + (s / 3600.0)

            if ref.upper() in ['S', 'W']:
                decimal = -decimal
            return decimal
        except Exception as e:
            logger.warning(f"Error converting DMS to decimal: {dms_tuple} {ref} - {e}")
            return None