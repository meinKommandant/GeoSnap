"""
Tests for main.py backend functions.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path
from threading import Event
import sys
import os
import tempfile
import shutil

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from geosnap.main import (
    process_photos_backend,
    _get_unique_path,
    _index_photos,
)
from geosnap.exceptions import (
    InputFolderMissingError,
    NoImagesFoundError,
    NoGPSDataError,
    ProcessCancelledError,
)


class TestProcessPhotosBackend:
    """Tests for the main photo processing backend."""

    def test_input_folder_missing_raises_error(self):
        """Verify InputFolderMissingError is raised when input folder doesn't exist."""
        with pytest.raises(InputFolderMissingError):
            process_photos_backend(
                input_path_str="C:/nonexistent/folder/12345",
                output_path_str="C:/temp",
                project_name_str="test"
            )

    def test_no_images_found_raises_error(self, tmp_path):
        """Verify NoImagesFoundError is raised when folder has no images."""
        # Create empty directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        with pytest.raises(NoImagesFoundError):
            process_photos_backend(
                input_path_str=str(empty_dir),
                output_path_str=str(tmp_path / "output"),
                project_name_str="test"
            )

    def test_cancellation_raises_error(self, tmp_path):
        """Verify ProcessCancelledError when stop_event is set before processing."""
        # Create directory with a dummy image file
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        (input_dir / "test.jpg").write_bytes(b'\xff\xd8\xff\xe0' + b'\x00' * 100)  # Minimal JPEG header
        
        # Create stop event that is already set
        stop_event = Event()
        stop_event.set()
        
        with pytest.raises(ProcessCancelledError):
            process_photos_backend(
                input_path_str=str(input_dir),
                output_path_str=str(tmp_path / "output"),
                project_name_str="test",
                stop_event=stop_event
            )


class TestGetUniquePath:
    """Tests for the _get_unique_path helper function."""

    def test_returns_original_if_not_exists(self, tmp_path):
        """If path doesn't exist, return it unchanged."""
        target = tmp_path / "newfile.kmz"
        result = _get_unique_path(target)
        assert result == target

    def test_adds_suffix_if_exists(self, tmp_path):
        """If path exists, add _1 suffix."""
        target = tmp_path / "existing.kmz"
        target.touch()  # Create the file
        
        result = _get_unique_path(target)
        assert result == tmp_path / "existing_1.kmz"

    def test_increments_suffix_if_multiple_exist(self, tmp_path):
        """If path_1 also exists, try _2, etc."""
        target = tmp_path / "report.kmz"
        target.touch()
        (tmp_path / "report_1.kmz").touch()
        (tmp_path / "report_2.kmz").touch()
        
        result = _get_unique_path(target)
        assert result == tmp_path / "report_3.kmz"


class TestIndexPhotos:
    """Tests for the _index_photos helper function."""

    def test_indexes_image_files(self, tmp_path):
        """Verify photos are indexed by lowercase filename."""
        # Create some test image files
        (tmp_path / "Photo1.JPG").touch()
        (tmp_path / "photo2.png").touch()
        (tmp_path / "IMAGE.HEIC").touch()
        (tmp_path / "notanimage.txt").touch()  # Should be excluded
        
        index = _index_photos(tmp_path)
        
        assert "photo1.jpg" in index
        assert "photo2.png" in index
        assert "image.heic" in index
        assert "notanimage.txt" not in index
        assert len(index) == 3

    def test_indexes_nested_directories(self, tmp_path):
        """Verify rglob finds photos in subdirectories."""
        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)
        (subdir / "nested_photo.jpg").touch()
        (tmp_path / "root_photo.png").touch()
        
        index = _index_photos(tmp_path)
        
        assert "nested_photo.jpg" in index
        assert "root_photo.png" in index
        assert len(index) == 2

    def test_empty_directory(self, tmp_path):
        """Empty directory returns empty index."""
        index = _index_photos(tmp_path)
        assert index == {}
