import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys
import os

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from geosnap.main import process_photos_backend
from geosnap.models import PhotoMetadata, GPSCoordinates
from geosnap.exceptions import NoGPSDataError

class TestNoGPSFeature(unittest.TestCase):
    def setUp(self):
        self.input_dir = Path("dummy_input")
        self.output_dir = Path("dummy_output")
        self.project_name = "TestProject"

    @patch('geosnap.main.as_completed')
    @patch('geosnap.main.Path')
    @patch('geosnap.main.GPSPhotoExtractor')
    @patch('geosnap.main.ExcelReportGenerator')
    @patch('geosnap.main.KmzReportGenerator')
    @patch('geosnap.main.ThreadPoolExecutor')
    def test_process_with_options(self, mock_executor, mock_kmz_gen, mock_excel_gen, mock_extractor_cls, mock_path, mock_as_completed):
        # Setup common mocks
        mock_input_path = MagicMock()
        mock_input_path.exists.return_value = True
        
        mock_file1 = MagicMock()
        mock_file1.name = "photo_gps.jpg"
        # Make mocks comparable for sorted()
        mock_file1.__lt__ = lambda self, other: self.name < other.name
        
        mock_file2 = MagicMock()
        mock_file2.name = "photo_no_gps.jpg"
        mock_file2.__lt__ = lambda self, other: self.name < other.name
        
        # Mock glob to return files when called with extensions
        # The code calls glob for each extension.
        # We can just make the first call return our files and others empty
        mock_input_path.glob.side_effect = [[mock_file1, mock_file2]] + [[]]*10

        mock_path.return_value = mock_input_path
        
        # Mock Extractor results
        meta_gps = PhotoMetadata(
            filename="photo_gps.jpg",
            filepath="path/to/photo_gps.jpg",
            timestamp=None,
            coordinates=GPSCoordinates(10.0, 20.0, 100.0)
        )
        meta_no_gps = PhotoMetadata(
            filename="photo_no_gps.jpg",
            filepath="path/to/photo_no_gps.jpg",
            timestamp=None,
            coordinates=None
        )

        mock_future1 = MagicMock()
        mock_future1.result.return_value = meta_gps
        mock_future2 = MagicMock()
        mock_future2.result.return_value = meta_no_gps
        
        # Map futures to indices as the code does: future_to_index
        # The code does: future_to_index = { executor.submit(...): i ... }
        # We need to mock executor.submit to return our futures
        mock_executor_instance = mock_executor.return_value
        mock_executor_instance.__enter__.return_value = mock_executor_instance
        mock_executor_instance.submit.side_effect = [mock_future1, mock_future2]
        
        mock_as_completed.return_value = [mock_future1, mock_future2]

        # --- TEST CASE 1: include_no_gps = True ---
        print("Testing include_no_gps=True...")
        result = process_photos_backend(
            str(self.input_dir), str(self.output_dir), self.project_name,
            include_no_gps=True
        )
        
        # Verify both photos were added to report
        # We check calls to excel_gen.add_row or kmz_gen.add_point
        mock_excel_instance = mock_excel_gen.return_value
        self.assertEqual(mock_excel_instance.add_row.call_count, 2, "Should process 2 photos when include_no_gps=True")
        
        # Verify the second photo has 0,0 coordinates
        # args: row_idx, numero_orden, metadata, val_alt
        # call_args_list[1] is the second call (sorted order: gps, no_gps)
        # Wait, sorted order depends on names. "photo_gps.jpg" < "photo_no_gps.jpg"
        # So index 0 is gps, index 1 is no_gps.
        
        # Check calls. Note that process_photos_backend sorts valid_photos by index.
        # Index comes from enumerate(image_files).
        # image_files is sorted.
        # So index 0 -> photo_gps, index 1 -> photo_no_gps.
        
        args, _ = mock_excel_instance.add_row.call_args_list[1]
        metadata_arg = args[2]
        self.assertEqual(metadata_arg.filename, "photo_no_gps.jpg")
        self.assertEqual(metadata_arg.coordinates.latitude, 0.0)
        self.assertEqual(metadata_arg.coordinates.longitude, 0.0)

        # --- TEST CASE 2: include_no_gps = False ---
        print("Testing include_no_gps=False...")
        # Reset mocks
        mock_excel_instance.reset_mock()
        
        # Create FRESH metadata objects because the previous run mutated them!
        meta_gps_2 = PhotoMetadata(
            filename="photo_gps.jpg",
            filepath="path/to/photo_gps.jpg",
            timestamp=None,
            coordinates=GPSCoordinates(10.0, 20.0, 100.0)
        )
        meta_no_gps_2 = PhotoMetadata(
            filename="photo_no_gps.jpg",
            filepath="path/to/photo_no_gps.jpg",
            timestamp=None,
            coordinates=None
        )
        
        mock_future1_2 = MagicMock()
        mock_future1_2.result.return_value = meta_gps_2
        mock_future2_2 = MagicMock()
        mock_future2_2.result.return_value = meta_no_gps_2

        mock_executor_instance.submit.side_effect = [mock_future1_2, mock_future2_2]
        mock_as_completed.return_value = [mock_future1_2, mock_future2_2]
        
        # Reset glob side effect for the second run
        mock_input_path.glob.side_effect = [[mock_file1, mock_file2]] + [[]]*20
        
        result = process_photos_backend(
            str(self.input_dir), str(self.output_dir), self.project_name,
            include_no_gps=False
        )
        
        # Verify only 1 photo was added
        self.assertEqual(mock_excel_instance.add_row.call_count, 1, "Should process 1 photo when include_no_gps=False")
        args, _ = mock_excel_instance.add_row.call_args_list[0]
        self.assertEqual(args[2].filename, "photo_gps.jpg")

if __name__ == '__main__':
    unittest.main()
