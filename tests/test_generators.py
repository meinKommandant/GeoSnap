import pytest
from unittest.mock import MagicMock
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from fotos2kmz.generators import ExcelReportGenerator
from fotos2kmz.models import PhotoMetadata, GPSCoordinates

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
