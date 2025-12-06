# src/main.py
import logging
from PIL import UnidentifiedImageError
from logging.handlers import RotatingFileHandler
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional
from threading import Event

# --- IMPORTS ---
from .extractor import GPSPhotoExtractor
from .models import GPSCoordinates
from .generators import ExcelReportGenerator, KmzReportGenerator, WordReportGenerator
from .importer import ExcelImporter
from .exceptions import InputFolderMissingError, NoImagesFoundError, NoGPSDataError, ProcessCancelledError
from .constants import IMAGE_EXTENSIONS, IMAGE_EXTENSIONS_SET

# Configure logger
log_dir = Path.home() / ".geosnap_logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def process_photos_backend(
    input_path_str: str,
    output_path_str: str,
    project_name_str: str,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
    stop_event: Optional[Event] = None,
    include_no_gps: bool = False,
) -> str:
    """
    Robust backend that raises controlled exceptions on error.
    """
    logger.info("Starting backend process")

    # 1. Validar rutas
    INPUT_DIR = Path(input_path_str)
    OUTPUT_DIR = Path(output_path_str)
    THUMBS_DIR = OUTPUT_DIR / "temp_thumbnails"

    if not INPUT_DIR.exists():
        # Raise exception instead of returning string
        raise InputFolderMissingError(INPUT_DIR)

    # Base name
    base_name = project_name_str.strip() or "reporte_completo"
    base_name = base_name.replace(".kmz", "").replace(".xlsx", "")
    # 3. GET IMAGES
    # Supported extensions definition (includes HEIC/HEIF)
    extensions = IMAGE_EXTENSIONS
    # File search
    raw_files = []
    for ext in extensions:
        raw_files.extend(INPUT_DIR.glob(ext))
    image_files = sorted(list(set(raw_files)))
    total_files = len(image_files)

    if total_files == 0:
        # Raise specific exception
        raise NoImagesFoundError(INPUT_DIR)

    logger.info(f"Found {total_files} images to process")

    processed_count = 0
    valid_photos = []

    # 2. INITIALIZE ENGINES
    extractor = GPSPhotoExtractor()
    excel_gen = ExcelReportGenerator()
    kmz_gen = KmzReportGenerator(THUMBS_DIR)

    # 4. PARALLEL PROCESSING
    with ThreadPoolExecutor() as executor:
        future_to_index = {
            executor.submit(extractor.extract_metadata, img_path): i for i, img_path in enumerate(image_files)
        }

        for i, future in enumerate(as_completed(future_to_index)):
            # Cancellation check with exception
            if stop_event and stop_event.is_set():
                logger.info("Cancellation detected during extraction phase")
                raise ProcessCancelledError()

            index = future_to_index[future]
            img_path = image_files[index]

            try:
                metadata = future.result()
                if metadata.has_gps:
                    valid_photos.append((index, metadata, img_path))
                elif include_no_gps:
                    # Create dummy coordinates if none exist
                    if metadata.coordinates is None:
                        metadata.coordinates = GPSCoordinates(0.0, 0.0, 0.0)
                    valid_photos.append((index, metadata, img_path))
            except UnidentifiedImageError:
                logger.error(f"Error: La imagen {img_path.name} está corrupta o no es válida.")
            except Exception as e:
                logger.error(f"Error procesando {img_path.name}: {e}")

            if progress_callback:
                progress_callback(i + 1, total_files, f"Analyzing: {img_path.name}")

    valid_photos.sort(key=lambda x: x[0])

    # 5. REPORT GENERATION
    total_valid = len(valid_photos)

    # Validate we have useful photos BEFORE generating empty reports
    if total_valid == 0:
        raise NoGPSDataError(total_files, str(INPUT_DIR))

    for i, (_, metadata, img_path) in enumerate(valid_photos):
        if stop_event and stop_event.is_set():
            raise ProcessCancelledError()

        if progress_callback:
            progress_callback(i, total_valid, f"Generating report: {metadata.filename}")

        numero_orden = i + 1
        val_alt = float(f"{metadata.coordinates.altitude:.2f}")

        excel_gen.add_row(i + 2, numero_orden, metadata, val_alt)
        kmz_gen.add_point(numero_orden, metadata, img_path, val_alt)

    processed_count = total_valid

    if progress_callback:
        progress_callback(total_files, total_files, "Saving files...")

    # 6. SAVE
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    kmz_path = OUTPUT_DIR / f"{base_name}.kmz"
    xlsx_path = OUTPUT_DIR / f"{base_name}.xlsx"

    kmz_gen.save(kmz_path)
    excel_gen.save(xlsx_path)
    kmz_gen.cleanup()

    logger.info(f"Process completed. {processed_count} photos processed.")
    # Success return is still a string or could be a Result object,
    # but since it's the "happy path", returning the final message is fine.
    return f"SUCCESS!\nProcessed: {processed_count} photos.\nGenerated:\n- {kmz_path.name}\n- {xlsx_path.name}"


# --- Helpers and backend: Phase 1 - Reverse Mode Backend ---
def _get_unique_path(path: Path) -> Path:
    """If path exists, returns path with incremental suffix _1, _2, ..."""
    if not path.exists():
        return path
    base = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 1
    while True:
        candidate = parent / f"{base}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def _index_photos(base_dir: Path) -> dict:
    """Creates an index by filename (lowercase) -> full path."""
    exts = IMAGE_EXTENSIONS_SET
    index: dict[str, Path] = {}
    for p in base_dir.rglob("*"):
        if p.is_file() and p.suffix in exts:
            index[p.name.lower()] = p
    return index


def process_excel_to_kmz_backend(
    excel_path_str: str,
    photos_source_dir_str: str,
    output_path_str: str,
    project_name_str: str,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
    stop_event: Optional[Event] = None,
    generate_word: bool = False,
) -> str:
    """
    Generates a KMZ from an existing Excel file (Source of Truth).
    Optionally generates a Word report if generate_word is True.
    - Uses a file index for O(1) lookups.
    - Handles duplicate output names automatically.
    """
    logger.info("Starting reverse process from Excel")

    from datetime import datetime
    import os

    EXCEL_PATH = Path(excel_path_str)
    PHOTOS_DIR = Path(photos_source_dir_str)
    OUTPUT_DIR = Path(output_path_str)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if stop_event and stop_event.is_set():
        raise ProcessCancelledError()

    # 1. Importar metadatos desde Excel
    importer = ExcelImporter()
    metadata_list = importer.parse_excel(EXCEL_PATH)

    total_items = len(metadata_list)
    if total_items == 0:
        raise NoGPSDataError(0, str(EXCEL_PATH))

    # 1.b Sort by sequence_id (Nº column) to respect user-defined order
    def _sort_key(m):
        """Extract numeric value from sequence_id for proper sorting."""
        if m.sequence_id is None:
            return float("inf")  # Items without number go to the end
        try:
            return int(m.sequence_id)
        except ValueError:
            return float("inf")

    metadata_list.sort(key=_sort_key)
    logger.info(f"Sorted {total_items} items by sequence_id (Nº)")

    # 2. Generate photo index
    if progress_callback:
        progress_callback(0, total_items, "Indexing photos...")
    index = _index_photos(PHOTOS_DIR)

    # 3. Calculate unique output path
    base_name = (project_name_str or "reporte_desde_excel").strip()
    base_name = base_name.replace(".kmz", "")
    THUMBS_DIR = OUTPUT_DIR / "temp_thumbnails"
    kmz_target = OUTPUT_DIR / f"{base_name}.kmz"
    kmz_path_unique = _get_unique_path(kmz_target)

    # 4. Inicializar generador KMZ
    kmz_gen = KmzReportGenerator(THUMBS_DIR)

    # 4.b Initialize Word generator if requested
    word_gen = None
    docx_path_unique = None
    if generate_word:
        docx_target = OUTPUT_DIR / f"{base_name}.docx"
        docx_path_unique = _get_unique_path(docx_target)
        word_gen = WordReportGenerator()

    # 5. Iterar metadatos
    for i, metadata in enumerate(metadata_list):
        if stop_event and stop_event.is_set():
            kmz_gen.cleanup()
            raise ProcessCancelledError()

        filename_key = metadata.filename.strip().lower()
        img_path = index.get(filename_key)
        if img_path is None:
            logger.warning(f"Photo {metadata.filename} not found in source directory: {PHOTOS_DIR}")
            if progress_callback:
                progress_callback(i + 1, total_items, f"Not found: {metadata.filename}")
            continue

        # Resolver filepath en el objeto metadata
        metadata.filepath = str(img_path)

        # If no date, try from file system
        if metadata.timestamp is None:
            try:
                ts = os.path.getmtime(img_path)
                metadata.timestamp = datetime.fromtimestamp(ts)
            except Exception:
                pass

        altitude_val = 0.0
        if metadata.coordinates and metadata.coordinates.altitude is not None:
            try:
                altitude_val = float(metadata.coordinates.altitude)
            except Exception:
                altitude_val = 0.0

        numero_orden = i + 1
        kmz_gen.add_point(numero_orden, metadata, img_path, altitude_val)

        # Add to Word report if enabled
        if word_gen is not None:
            word_gen.add_photo(numero_orden, metadata, img_path)

        if progress_callback:
            progress_callback(i + 1, total_items, f"Added: {metadata.filename}")

    # 6. Save KMZ
    kmz_gen.save(kmz_path_unique)
    kmz_gen.cleanup()

    # 6.b Save Word report if enabled
    if word_gen is not None and docx_path_unique is not None:
        word_gen.save(docx_path_unique)
        return f"SUCCESS! KMZ generated at: {kmz_path_unique}\nWord report generated at: {docx_path_unique}"

    return f"SUCCESS! KMZ generated from Excel at: {kmz_path_unique}"
