import sys
from pathlib import Path
# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

import pytest
from unittest.mock import MagicMock, patch
from geosnap.importer import ExcelImporter
from geosnap.models import PhotoMetadata

# Helper to create a mock cell
def mock_cell(value, column):
    cell = MagicMock()
    cell.value = value
    cell.column = column
    return cell

# Helper to mock a worksheet
def mock_worksheet(rows_data):
    ws = MagicMock()
    # Mock iterating over rows (for header mapping which iterates ws[1])
    # ws[1] should return a list of cells for the first row
    header_cells = [mock_cell(val, i+1) for i, val in enumerate(rows_data[0])]
    ws.__getitem__.side_effect = lambda key: header_cells if key == 1 else None
    
    # Mock max_row
    ws.max_row = len(rows_data)
    
    # Mock cell access by row/column
    def get_cell(row, column, value=None):
        # row is 1-based, data is 0-based
        if 1 <= row <= len(rows_data):
            row_data = rows_data[row-1]
            if 1 <= column <= len(row_data):
                return mock_cell(row_data[column-1], column)
        return mock_cell(None, column)

    ws.cell.side_effect = get_cell
    return ws

@pytest.fixture
def importer():
    return ExcelImporter()

@patch("geosnap.importer.openpyxl.load_workbook")
def test_parse_excel_valid(mock_load_workbook, importer):
    # Setup mock data
    # Row 1: Headers
    # Row 2: Valid Data
    rows = [
        ["Archivo", "Latitud", "Longitud", "Altitud", "Azimut"],
        ["foto1.jpg", 10.5, -75.2, 100, 45.5],
        ["foto2.png", "20,5", "-80,1", "50", "180"]
    ]
    
    mock_wb = MagicMock()
    mock_ws = mock_worksheet(rows)
    mock_wb.active = mock_ws
    mock_load_workbook.return_value = mock_wb
    
    results = importer.parse_excel("dummy.xlsx")
    
    assert len(results) == 2
    
    # Check first item
    p1 = results[0]
    assert p1.filename == "foto1.jpg"
    assert p1.coordinates.latitude == 10.5
    assert p1.coordinates.longitude == -75.2
    assert p1.coordinates.altitude == 100.0
    assert p1.coordinates.azimuth == 45.5
    
    # Check second item (string parsing)
    p2 = results[1]
    assert p2.filename == "foto2.png"
    assert p2.coordinates.latitude == 20.5
    assert p2.coordinates.longitude == -80.1
    assert p2.coordinates.altitude == 50.0
    assert p2.coordinates.azimuth == 180.0

@patch("geosnap.importer.openpyxl.load_workbook")
def test_parse_missing_critical_columns(mock_load_workbook, importer):
    # Missing 'Latitud'
    rows = [
        ["Archivo", "Longitud"],
        ["foto1.jpg", -75.2]
    ]
    
    mock_wb = MagicMock()
    mock_ws = mock_worksheet(rows)
    mock_wb.active = mock_ws
    mock_load_workbook.return_value = mock_wb
    
    with pytest.raises(ValueError, match="Missing critical columns"):
        importer.parse_excel("dummy.xlsx")

@patch("geosnap.importer.openpyxl.load_workbook")
def test_parse_invalid_coordinates(mock_load_workbook, importer):
    # Row 2 has invalid lat/lon, should be skipped
    rows = [
        ["Archivo", "Latitud", "Longitud"],
        ["valid.jpg", 10.0, 20.0],
        ["invalid.jpg", "bad_lat", 20.0],
        ["missing.jpg", None, 20.0]
    ]
    
    mock_wb = MagicMock()
    mock_ws = mock_worksheet(rows)
    mock_wb.active = mock_ws
    mock_load_workbook.return_value = mock_wb
    
    results = importer.parse_excel("dummy.xlsx")
    
    assert len(results) == 1
    assert results[0].filename == "valid.jpg"

@patch("geosnap.importer.openpyxl.load_workbook")
def test_parse_headers_case_insensitive(mock_load_workbook, importer):
    # Case insensitive matching and aliases
    rows = [
        ["FILE", "lat", "Lng", "Rumbo"],
        ["foto1.jpg", 10.0, 20.0, 90]
    ]
    
    mock_wb = MagicMock()
    mock_ws = mock_worksheet(rows)
    mock_wb.active = mock_ws
    mock_load_workbook.return_value = mock_wb
    
    results = importer.parse_excel("dummy.xlsx")
    
    assert len(results) == 1
    p1 = results[0]
    assert p1.filename == "foto1.jpg"
    assert p1.coordinates.latitude == 10.0
    assert p1.coordinates.longitude == 20.0
    assert p1.coordinates.azimuth == 90.0
