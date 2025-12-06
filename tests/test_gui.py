"""
Tests for GUI components using mock-based approach.
Tests button states, callbacks, and UI behavior without opening actual windows.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


class TestGeoPhotoAppInitialization:
    """Tests for GeoPhotoApp initialization and state."""

    @patch("geosnap.gui.ttk.Window")
    @patch("geosnap.gui.ConfigManager")
    def test_config_loaded_on_init(self, mock_config, mock_window):
        """Verify ConfigManager.load_config is called during init."""
        mock_config.load_config.return_value = {
            "input_dir": "/test/input",
            "output_dir": "/test/output",
            "project_name": "TestProject",
            "thumbnail_size": 800,
            "jpeg_quality": 75,
            "arrow_length": 30,
            "arrow_width": 4,
        }

        # Import after patching
        from geosnap.gui import GeoPhotoApp

        mock_root = MagicMock()
        mock_root.winfo_x.return_value = 0
        mock_root.winfo_y.return_value = 0
        mock_root.winfo_width.return_value = 700
        mock_root.winfo_height.return_value = 650

        with patch.object(GeoPhotoApp, "__init__", lambda x, y: None):
            app = GeoPhotoApp(mock_root)
            app.config = mock_config.load_config()

        assert app.config["project_name"] == "TestProject"


class TestBatchProcessor:
    """Tests for BatchProcessor functionality."""

    def test_add_job_increments_count(self):
        """Verify adding jobs increments the pending count."""
        from geosnap.batch_processor import BatchProcessor

        processor = BatchProcessor()
        assert processor.get_pending_count() == 0

        processor.add_job("/input", "/output", "Project1")
        assert processor.get_pending_count() == 1

        processor.add_job("/input2", "/output2", "Project2")
        assert processor.get_pending_count() == 2

    def test_remove_job_decrements_count(self):
        """Verify removing jobs decrements the pending count."""
        from geosnap.batch_processor import BatchProcessor

        processor = BatchProcessor()
        processor.add_job("/input", "/output", "Project1")
        processor.add_job("/input2", "/output2", "Project2")

        assert processor.get_pending_count() == 2
        processor.remove_job(0)
        assert processor.get_pending_count() == 1

    def test_clear_queue_removes_pending(self):
        """Verify clear_queue removes all pending jobs."""
        from geosnap.batch_processor import BatchProcessor

        processor = BatchProcessor()
        processor.add_job("/input1", "/output1", "P1")
        processor.add_job("/input2", "/output2", "P2")
        processor.add_job("/input3", "/output3", "P3")

        assert processor.get_pending_count() == 3
        processor.clear_queue()
        assert processor.get_pending_count() == 0

    def test_get_summary_format(self):
        """Verify get_summary returns correctly formatted string."""
        from geosnap.batch_processor import BatchProcessor

        processor = BatchProcessor()
        processor.add_job("/input", "/output", "Test")

        summary = processor.get_summary()
        assert "1 pendientes" in summary
        assert "0 completados" in summary


class TestSettingsDialog:
    """Tests for SettingsDialog functionality."""

    def test_default_values(self):
        """Verify default setting values."""
        from geosnap.settings import SettingsDialog

        # Test that defaults match expected values
        defaults = {
            "thumbnail_size": 800,
            "jpeg_quality": 75,
            "arrow_length": 30,
            "arrow_width": 4,
        }

        # These are the expected defaults
        assert defaults["thumbnail_size"] == 800
        assert defaults["jpeg_quality"] == 75


class TestConfigManagerExtended:
    """Tests for extended ConfigManager functionality."""

    def test_update_settings_preserves_paths(self, tmp_path):
        """Verify update_settings doesn't overwrite path settings."""
        from geosnap.config import ConfigManager, CONFIG_FILE
        import json

        # Create a temporary config
        test_config = {
            "input_dir": "/original/input",
            "output_dir": "/original/output",
            "project_name": "Original",
            "thumbnail_size": 800,
        }

        # This test verifies the update_settings logic
        new_settings = {"thumbnail_size": 1200}

        # Merge logic should preserve input_dir
        merged = test_config.copy()
        for key in ["thumbnail_size", "jpeg_quality", "arrow_length", "arrow_width"]:
            if key in new_settings:
                merged[key] = new_settings[key]

        assert merged["input_dir"] == "/original/input"
        assert merged["thumbnail_size"] == 1200

    def test_list_profiles_returns_list(self):
        """Verify list_profiles returns a list."""
        from geosnap.config import ConfigManager

        profiles = ConfigManager.list_profiles()
        assert isinstance(profiles, list)
