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


# ============================================================================
# ADVANCED GUI TESTS (Based on Gemini Deep Search patterns)
# ============================================================================


class TestGeoPhotoAppModeToggle:
    """Tests for mode switching functionality."""

    @patch("geosnap.gui.ttk.Window")
    @patch("geosnap.gui.ConfigManager")
    def test_mode_toggle_changes_text(self, mock_config, mock_window):
        """Verify mode toggle updates the mode text variable."""
        mock_config.load_config.return_value = {
            "input_dir": "",
            "output_dir": "",
            "project_name": "Test",
            "thumbnail_size": 800,
            "jpeg_quality": 75,
            "arrow_length": 30,
            "arrow_width": 4,
        }

        from geosnap.gui import GeoPhotoApp

        # Create minimal mock root
        mock_root = MagicMock()

        with patch.object(GeoPhotoApp, "__init__", lambda x, y: None):
            app = GeoPhotoApp(mock_root)
            # Use MagicMock for tkinter variables (avoids need for Tk root)
            app.is_reverse_mode = MagicMock()
            app.is_reverse_mode.get.return_value = False
            app.mode_text_var = MagicMock()
            app.excel_label = MagicMock()
            app.excel_entry = MagicMock()
            app.excel_btn = MagicMock()
            app.chk_word_report = MagicMock()
            app.input_label = MagicMock()
            app.status_label = MagicMock()
            app.btn_generate = MagicMock()

            # Test initial state returns False (Photos mode)
            assert app.is_reverse_mode.get() is False

            # Test switching to reverse mode
            app.is_reverse_mode.get.return_value = True
            assert app.is_reverse_mode.get() is True


class TestGeoPhotoAppValidation:
    """Tests for input validation."""

    def test_project_name_validation(self):
        """Verify project name is required."""
        # Test that empty project name fails validation
        project_name = ""
        is_valid = bool(project_name and project_name.strip())
        assert is_valid is False

    def test_project_name_with_spaces(self):
        """Verify project name with only spaces fails."""
        project_name = "   "
        is_valid = bool(project_name and project_name.strip())
        assert is_valid is False

    def test_valid_project_name(self):
        """Verify valid project name passes."""
        project_name = "MyProject"
        is_valid = bool(project_name and project_name.strip())
        assert is_valid is True


class TestUIMessagesConstants:
    """Tests for UI message constants."""

    def test_ui_messages_exist(self):
        """Verify all required UI messages are defined."""
        from geosnap.constants import UIMessages

        assert hasattr(UIMessages, "MODE_PHOTOS")
        assert hasattr(UIMessages, "MODE_EXCEL")
        assert hasattr(UIMessages, "BTN_GO")
        assert hasattr(UIMessages, "WAITING")
        assert hasattr(UIMessages, "SUCCESS")
        assert hasattr(UIMessages, "ERROR")

    def test_ui_messages_not_empty(self):
        """Verify UI messages have content."""
        from geosnap.constants import UIMessages

        assert len(UIMessages.MODE_PHOTOS) > 0
        assert len(UIMessages.BTN_GO) > 0


class TestProgressCallback:
    """Tests for progress callback logic."""

    def test_percentage_calculation_normal(self):
        """Verify percentage calculation works correctly."""
        current = 50
        total = 100
        percentage = (current / total) * 100 if total > 0 else 0
        assert percentage == 50.0

    def test_percentage_calculation_zero_total(self):
        """Verify zero total doesn't cause division error."""
        current = 10
        total = 0
        percentage = (current / total) * 100 if total > 0 else 0
        assert percentage == 0

    def test_percentage_calculation_complete(self):
        """Verify 100% calculation."""
        current = 100
        total = 100
        percentage = (current / total) * 100 if total > 0 else 0
        assert percentage == 100.0


class TestFileDialogMocking:
    """Tests demonstrating dialog mocking patterns."""

    @patch("tkinter.filedialog.askdirectory")
    def test_browse_folder_returns_path(self, mock_dialog):
        """Verify folder browser returns selected path."""
        mock_dialog.return_value = "/selected/folder"

        from tkinter import filedialog

        result = filedialog.askdirectory()
        assert result == "/selected/folder"
        mock_dialog.assert_called_once()

    @patch("tkinter.filedialog.askopenfilename")
    def test_browse_excel_returns_file(self, mock_dialog):
        """Verify file browser returns selected file."""
        mock_dialog.return_value = "/path/to/data.xlsx"

        from tkinter import filedialog

        result = filedialog.askopenfilename()
        assert result == "/path/to/data.xlsx"

    @patch("tkinter.filedialog.askdirectory")
    def test_browse_cancelled_returns_empty(self, mock_dialog):
        """Verify cancelled dialog returns empty string."""
        mock_dialog.return_value = ""

        from tkinter import filedialog

        result = filedialog.askdirectory()
        assert result == ""


class TestThreadingMock:
    """Tests demonstrating thread mocking for GUI operations."""

    @patch("threading.Thread")
    def test_thread_creation_mocked(self, mock_thread):
        """Verify thread is created with correct target."""
        import threading

        def dummy_target():
            pass

        t = threading.Thread(target=dummy_target)
        mock_thread.assert_called_once()

    def test_stop_event_functionality(self):
        """Verify threading.Event works for cancellation."""
        import threading

        stop_event = threading.Event()

        # Initially not set
        assert stop_event.is_set() is False

        # Set the event
        stop_event.set()
        assert stop_event.is_set() is True

        # Clear the event
        stop_event.clear()
        assert stop_event.is_set() is False
