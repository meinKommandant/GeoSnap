import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from geosnap.config import ConfigManager, DEFAULT_CONFIG


class TestConfigManagerLoadConfig:
    """Tests for ConfigManager.load_config()"""

    def test_returns_default_when_no_file(self, tmp_path):
        """Test that default config is returned when file doesn't exist."""
        with patch("geosnap.config.CONFIG_FILE", tmp_path / "nonexistent.json"):
            config = ConfigManager.load_config()
            assert config == DEFAULT_CONFIG

    def test_loads_existing_config(self, tmp_path):
        """Test that existing config file is loaded correctly."""
        config_file = tmp_path / "settings.json"
        test_config = {"input_dir": "/test/path", "project_name": "TestProject"}
        config_file.write_text(json.dumps(test_config))

        with patch("geosnap.config.CONFIG_FILE", config_file):
            config = ConfigManager.load_config()
            assert config["input_dir"] == "/test/path"
            assert config["project_name"] == "TestProject"
            # Should also have defaults merged in
            assert "thumbnail_size" in config

    def test_handles_invalid_json(self, tmp_path):
        """Test that invalid JSON returns default config."""
        config_file = tmp_path / "settings.json"
        config_file.write_text("{ invalid json }")

        with patch("geosnap.config.CONFIG_FILE", config_file):
            config = ConfigManager.load_config()
            assert config == DEFAULT_CONFIG


class TestConfigManagerSaveConfig:
    """Tests for ConfigManager.save_config()"""

    def test_saves_input_dir(self, tmp_path):
        """Test that input_dir is saved correctly."""
        config_file = tmp_path / "settings.json"

        with patch("geosnap.config.CONFIG_FILE", config_file):
            ConfigManager.save_config(input_dir="/new/input")
            saved = json.loads(config_file.read_text())
            assert saved["input_dir"] == "/new/input"

    def test_saves_output_dir(self, tmp_path):
        """Test that output_dir is saved correctly."""
        config_file = tmp_path / "settings.json"

        with patch("geosnap.config.CONFIG_FILE", config_file):
            ConfigManager.save_config(output_dir="/new/output")
            saved = json.loads(config_file.read_text())
            assert saved["output_dir"] == "/new/output"

    def test_saves_project_name(self, tmp_path):
        """Test that project_name is saved correctly."""
        config_file = tmp_path / "settings.json"

        with patch("geosnap.config.CONFIG_FILE", config_file):
            ConfigManager.save_config(project_name="NewProject")
            saved = json.loads(config_file.read_text())
            assert saved["project_name"] == "NewProject"

    def test_preserves_existing_values(self, tmp_path):
        """Test that existing values are preserved when updating."""
        config_file = tmp_path / "settings.json"
        initial = {"input_dir": "/old/path", "output_dir": "/out"}
        config_file.write_text(json.dumps(initial))

        with patch("geosnap.config.CONFIG_FILE", config_file):
            ConfigManager.save_config(project_name="Updated")
            saved = json.loads(config_file.read_text())
            assert saved["input_dir"] == "/old/path"  # Preserved
            assert saved["project_name"] == "Updated"  # Updated


class TestConfigManagerUpdateSettings:
    """Tests for ConfigManager.update_settings()"""

    def test_updates_thumbnail_size(self, tmp_path):
        """Test that thumbnail_size is updated."""
        config_file = tmp_path / "settings.json"
        config_file.write_text(json.dumps(DEFAULT_CONFIG))

        with patch("geosnap.config.CONFIG_FILE", config_file):
            ConfigManager.update_settings({"thumbnail_size": 1200})
            saved = json.loads(config_file.read_text())
            assert saved["thumbnail_size"] == 1200

    def test_updates_jpeg_quality(self, tmp_path):
        """Test that jpeg_quality is updated."""
        config_file = tmp_path / "settings.json"
        config_file.write_text(json.dumps(DEFAULT_CONFIG))

        with patch("geosnap.config.CONFIG_FILE", config_file):
            ConfigManager.update_settings({"jpeg_quality": 90})
            saved = json.loads(config_file.read_text())
            assert saved["jpeg_quality"] == 90

    def test_ignores_non_settings_keys(self, tmp_path):
        """Test that non-settings keys are ignored."""
        config_file = tmp_path / "settings.json"
        config_file.write_text(json.dumps(DEFAULT_CONFIG))

        with patch("geosnap.config.CONFIG_FILE", config_file):
            ConfigManager.update_settings({"input_dir": "/should/not/change"})
            saved = json.loads(config_file.read_text())
            assert saved["input_dir"] == ""  # Should remain default


class TestConfigManagerProfiles:
    """Tests for profile management functions."""

    def test_list_profiles_empty(self, tmp_path):
        """Test list_profiles returns empty list when no profiles."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()

        with patch("geosnap.config.PROFILES_DIR", profiles_dir):
            profiles = ConfigManager.list_profiles()
            assert profiles == []

    def test_list_profiles_returns_names(self, tmp_path):
        """Test list_profiles returns profile names without extension."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        (profiles_dir / "work.json").write_text("{}")
        (profiles_dir / "personal.json").write_text("{}")

        with patch("geosnap.config.PROFILES_DIR", profiles_dir):
            profiles = ConfigManager.list_profiles()
            assert set(profiles) == {"work", "personal"}

    def test_save_profile(self, tmp_path):
        """Test save_profile creates a profile file."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()

        with patch("geosnap.config.PROFILES_DIR", profiles_dir):
            ConfigManager.save_profile("test_profile", {"key": "value"})
            profile_file = profiles_dir / "test_profile.json"
            assert profile_file.exists()
            saved = json.loads(profile_file.read_text())
            assert saved["key"] == "value"

    def test_load_profile_existing(self, tmp_path):
        """Test load_profile loads existing profile."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        (profiles_dir / "myprofile.json").write_text(json.dumps({"input_dir": "/profile/path"}))

        with patch("geosnap.config.PROFILES_DIR", profiles_dir):
            config = ConfigManager.load_profile("myprofile")
            assert config["input_dir"] == "/profile/path"

    def test_load_profile_nonexistent(self, tmp_path):
        """Test load_profile returns default for missing profile."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()

        with patch("geosnap.config.PROFILES_DIR", profiles_dir):
            config = ConfigManager.load_profile("nonexistent")
            assert config == DEFAULT_CONFIG

    def test_delete_profile(self, tmp_path):
        """Test delete_profile removes profile file."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        profile_file = profiles_dir / "todelete.json"
        profile_file.write_text("{}")

        with patch("geosnap.config.PROFILES_DIR", profiles_dir):
            result = ConfigManager.delete_profile("todelete")
            assert result is True
            assert not profile_file.exists()

    def test_delete_profile_nonexistent(self, tmp_path):
        """Test delete_profile returns False for missing profile."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()

        with patch("geosnap.config.PROFILES_DIR", profiles_dir):
            result = ConfigManager.delete_profile("nonexistent")
            assert result is False
