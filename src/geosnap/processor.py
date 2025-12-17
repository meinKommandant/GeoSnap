"""
Photo processor module for GeoSnap.

This module contains the PhotoProcessor class which handles:
- Scanning for image files
- Parallel metadata extraction using ThreadPoolExecutor
- GPS validation and No-GPS handling
- Photo sorting and filtering
"""

import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event
from typing import Callable, List, Optional, Tuple

from PIL import UnidentifiedImageError

from .extractor import GPSPhotoExtractor
from .models import PhotoMetadata, GPSCoordinates
from .constants import IMAGE_EXTENSIONS
from .exceptions import NoImagesFoundError, ProcessCancelledError

logger = logging.getLogger(__name__)


class PhotoProcessor:
    """Handles photo scanning, parallel extraction, and metadata processing.

    This class encapsulates the logic for:
    - Scanning directories for supported image files
    - Parallel metadata extraction using ThreadPoolExecutor
    - Handling photos with and without GPS data
    - Creating dummy coordinates for No-GPS photos when requested

    Attributes:
        input_dir: Path to the directory containing photos.
        include_no_gps: Whether to include photos without GPS data.
        progress_callback: Optional callback for progress updates.
        stop_event: Optional threading event for cancellation.
    """

    def __init__(
        self,
        input_dir: Path,
        include_no_gps: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        stop_event: Optional[Event] = None,
    ) -> None:
        """Initialize the PhotoProcessor.

        Args:
            input_dir: Path to the directory containing photos to process.
            include_no_gps: If True, include photos without GPS coordinates
                           by assigning dummy (0, 0, 0) coordinates.
            progress_callback: Optional callback function receiving
                              (current, total, message) for progress updates.
            stop_event: Optional threading.Event for graceful cancellation.
        """
        self.input_dir = input_dir
        self.include_no_gps = include_no_gps
        self.progress_callback = progress_callback
        self.stop_event = stop_event
        self._extractor = GPSPhotoExtractor()

    def scan_files(self) -> List[Path]:
        """Scan the input directory for supported image files.

        Searches for files matching IMAGE_EXTENSIONS patterns in the input
        directory (non-recursive).

        Returns:
            Sorted list of unique Path objects for found image files.

        Raises:
            NoImagesFoundError: If no supported image files are found.
        """
        raw_files: List[Path] = []
        for ext in IMAGE_EXTENSIONS:
            raw_files.extend(self.input_dir.glob(ext))

        image_files = sorted(list(set(raw_files)))
        total_files = len(image_files)

        if total_files == 0:
            raise NoImagesFoundError(self.input_dir)

        logger.info(f"Found {total_files} images to process")
        return image_files

    def process(self) -> List[Tuple[int, PhotoMetadata, Path]]:
        """Process all photos in the input directory.

        Scans for image files, extracts metadata in parallel using
        ThreadPoolExecutor, and filters/processes based on GPS availability.

        Returns:
            List of tuples (original_index, metadata, file_path) sorted by
            original index. Only includes photos with valid GPS data, or
            all photos with dummy coordinates if include_no_gps is True.

        Raises:
            NoImagesFoundError: If no supported image files are found.
            ProcessCancelledError: If stop_event is set during processing.
        """
        image_files = self.scan_files()
        total_files = len(image_files)
        valid_photos: List[Tuple[int, PhotoMetadata, Path]] = []

        with ThreadPoolExecutor() as executor:
            future_to_index = {
                executor.submit(self._extractor.extract_metadata, img_path): i
                for i, img_path in enumerate(image_files)
            }

            for i, future in enumerate(as_completed(future_to_index)):
                # Check for cancellation
                if self.stop_event and self.stop_event.is_set():
                    logger.info("Cancellation detected during extraction phase")
                    raise ProcessCancelledError()

                index = future_to_index[future]
                img_path = image_files[index]

                try:
                    metadata = future.result()
                    if metadata.has_gps:
                        valid_photos.append((index, metadata, img_path))
                    elif self.include_no_gps:
                        # Create dummy coordinates if none exist
                        if metadata.coordinates is None:
                            metadata.coordinates = GPSCoordinates(0.0, 0.0, 0.0)
                        valid_photos.append((index, metadata, img_path))
                except UnidentifiedImageError:
                    logger.error(
                        f"Error: Image {img_path.name} is corrupt or invalid."
                    )
                except Exception as e:
                    logger.error(f"Error processing {img_path.name}: {e}")

                if self.progress_callback:
                    self.progress_callback(
                        i + 1, total_files, f"Analyzing: {img_path.name}"
                    )

        # Sort by original index to maintain file order
        valid_photos.sort(key=lambda x: x[0])
        return valid_photos

    def get_total_files(self) -> int:
        """Get the count of image files without processing them.

        Returns:
            Number of image files found in input directory.

        Raises:
            NoImagesFoundError: If no supported image files are found.
        """
        return len(self.scan_files())
