import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from fotos2kmz.extractor import GPSPhotoExtractor
from fotos2kmz.models import PhotoMetadata

class TestGPSPhotoExtractor:
    @pytest.fixture
    def extractor(self):
        return GPSPhotoExtractor()

    @patch('extractor.Image.open')
    def test_extract_metadata_with_valid_gps(self, mock_open, extractor):
        # Mock image and EXIF data
        mock_img = MagicMock()
        mock_open.return_value = mock_img
        
        # EXIF data with GPS (Tag 34853)
        # 1=LatRef, 2=Lat, 3=LonRef, 4=Lon, 6=Alt
        gps_info = {
            1: 'N',
            2: (40.0, 0.0, 0.0),
            3: 'W',
            4: (3.0, 0.0, 0.0),
            6: 100.0
        }
        
        mock_img._getexif.return_value = {
            34853: gps_info,
            36867: '2023:01:01 12:00:00' # DateTimeOriginal
        }

        metadata = extractor.extract_metadata(Path("dummy.jpg"))

        assert isinstance(metadata, PhotoMetadata)
        assert metadata.has_gps is True
        assert metadata.coordinates.latitude == 40.0
        assert metadata.coordinates.longitude == -3.0 # West is negative
        assert metadata.coordinates.altitude == 100.0

    @patch('extractor.Image.open')
    def test_extract_metadata_no_gps(self, mock_open, extractor):
        mock_img = MagicMock()
        mock_open.return_value = mock_img
        
        # EXIF without GPS
        mock_img._getexif.return_value = {
            36867: '2023:01:01 12:00:00'
        }

        metadata = extractor.extract_metadata(Path("dummy.jpg"))

        assert isinstance(metadata, PhotoMetadata)
        assert metadata.has_gps is False
        assert metadata.coordinates is None

    @patch('extractor.Image.open')
    def test_extract_metadata_zero_coordinates(self, mock_open, extractor):
        # Test for the safety check we added
        mock_img = MagicMock()
        mock_open.return_value = mock_img
        
        gps_info = {
            1: 'N',
            2: (0.0, 0.0, 0.0),
            3: 'E',
            4: (0.0, 0.0, 0.0),
            6: 0.0
        }
        
        mock_img._getexif.return_value = {
            34853: gps_info
        }

        metadata = extractor.extract_metadata(Path("dummy.jpg"))

        assert metadata.has_gps is False
        assert metadata.coordinates is None
