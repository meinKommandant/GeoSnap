import pytest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime
import tempfile
import shutil
import math

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from geosnap.generators import ExcelReportGenerator, KmzReportGenerator
from geosnap.models import PhotoMetadata, GPSCoordinates

class TestExcelReportGenerator:
    def test_create_workbook(self):
        generator = ExcelReportGenerator()
        assert generator.wb is not None
        assert generator.ws.title == "Listado de Fotos"

    def test_add_row(self):
        generator = ExcelReportGenerator()
        
        metadata = PhotoMetadata(
            filename="test.jpg",
            filepath="/path/to/test.jpg",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            coordinates=GPSCoordinates(40.0, -3.0, 100.0)
        )
        
        generator.add_row(2, 1, metadata, 100.0)
        
        # Check values in cells
        assert generator.ws['B2'].value == 1
        assert generator.ws['C2'].value == "test.jpg"
        assert generator.ws['E2'].value == "2023-01-01 12:00:00"
        assert generator.ws['F2'].value == 40.0
        assert generator.ws['G2'].value == -3.0
        assert generator.ws['H2'].value == 100.0

    def test_add_row_no_gps_shows_empty_coords(self):
        """Test that 0,0 coordinates (no-GPS marker) show as empty strings."""
        generator = ExcelReportGenerator()
        
        metadata = PhotoMetadata(
            filename="no_gps.jpg",
            filepath="/path/to/no_gps.jpg",
            timestamp=datetime(2023, 1, 1, 12, 0, 0),
            coordinates=GPSCoordinates(0.0, 0.0, 0.0)  # No-GPS marker
        )
        
        generator.add_row(2, 1, metadata, 0.0)
        
        # Lat/Lon/Alt should be empty for no-GPS photos
        assert generator.ws['F2'].value == ""
        assert generator.ws['G2'].value == ""
        assert generator.ws['H2'].value == ""


class TestKmzReportGenerator:
    @pytest.fixture
    def temp_thumbs_dir(self, tmp_path):
        """Create a temporary thumbnails directory."""
        thumbs_dir = tmp_path / "thumbs"
        yield thumbs_dir
        # Cleanup
        if thumbs_dir.exists():
            shutil.rmtree(thumbs_dir)

    def test_calculate_dest_point_north(self, temp_thumbs_dir):
        """Test arrow destination calculation heading north (0°)."""
        generator = KmzReportGenerator(temp_thumbs_dir)
        
        # Starting at equator, heading north
        lat, lon = 0.0, 0.0
        dist_m = 1000  # 1km
        bearing = 0  # North
        
        dest_lat, dest_lon = generator._calculate_dest_point(lat, lon, dist_m, bearing)
        
        # Should move north (higher latitude), same longitude
        assert dest_lat > lat
        assert abs(dest_lon - lon) < 0.0001  # Longitude should be nearly unchanged

    def test_calculate_dest_point_east(self, temp_thumbs_dir):
        """Test arrow destination calculation heading east (90°)."""
        generator = KmzReportGenerator(temp_thumbs_dir)
        
        lat, lon = 0.0, 0.0
        dist_m = 1000
        bearing = 90  # East
        
        dest_lat, dest_lon = generator._calculate_dest_point(lat, lon, dist_m, bearing)
        
        # Should move east (higher longitude), same latitude
        assert abs(dest_lat - lat) < 0.0001
        assert dest_lon > lon

    def test_calculate_dest_point_south(self, temp_thumbs_dir):
        """Test arrow destination calculation heading south (180°)."""
        generator = KmzReportGenerator(temp_thumbs_dir)
        
        lat, lon = 10.0, 10.0
        dist_m = 1000
        bearing = 180  # South
        
        dest_lat, dest_lon = generator._calculate_dest_point(lat, lon, dist_m, bearing)
        
        # Should move south (lower latitude)
        assert dest_lat < lat

    def test_thumbs_dir_created(self, temp_thumbs_dir):
        """Test that thumbs directory is created on init."""
        generator = KmzReportGenerator(temp_thumbs_dir)
        assert temp_thumbs_dir.exists()

    def test_cleanup_removes_thumbs_dir(self, temp_thumbs_dir):
        """Test that cleanup removes the thumbnails directory."""
        generator = KmzReportGenerator(temp_thumbs_dir)
        assert temp_thumbs_dir.exists()
        
        generator.cleanup()
        assert not temp_thumbs_dir.exists()

