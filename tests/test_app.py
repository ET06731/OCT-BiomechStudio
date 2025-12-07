import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
from oct_biomech_studio.models import Volume, VolumeMeta


# Mock PySide6 to avoid GUI dependencies in tests
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtGui'] = MagicMock()
sys.modules['pyvista'] = MagicMock()
sys.modules['pyvistaqt'] = MagicMock()


class TestMainWindowInit(unittest.TestCase):
    """Test MainWindow initialization."""
    
    @patch('oct_biomech_studio.app.QMainWindow')
    @patch('oct_biomech_studio.app.QMenu')
    @patch('oct_biomech_studio.app.QAction')
    def test_window_initialization(self, mock_action, mock_menu, mock_main_window):
        """Test that MainWindow initializes with correct structure."""
        from oct_biomech_studio.app import MainWindow
        
        window = MainWindow()
        
        # Verify window properties
        self.assertTrue(hasattr(window, 'ref_vol'))
        self.assertTrue(hasattr(window, 'def_vol'))
        self.assertTrue(hasattr(window, 'btn_segment'))
        self.assertTrue(hasattr(window, 'btn_compute'))
        self.assertTrue(hasattr(window, 'btn_export'))
    
    @patch('oct_biomech_studio.app.QMainWindow')
    @patch('oct_biomech_studio.app.QAction')
    def test_menu_actions_created(self, mock_action, mock_main_window):
        """Test that all menu actions are created including new folder actions."""
        from oct_biomech_studio.app import MainWindow
        
        window = MainWindow()
        
        # Should have created actions for:
        # - Load Reference
        # - Load Reference (Folder) - NEW
        # - Load Deformed
        # - Load Deformed (Folder) - NEW
        # - Load Volume Pair
        # Total: 5 actions
        self.assertGreaterEqual(mock_action.call_count, 5)


class TestLoadReferenceFolder(unittest.TestCase):
    """Test the new _load_reference_folder method."""
    
    def setUp(self):
        """Set up test fixtures."""
        from oct_biomech_studio.app import MainWindow
        with patch('oct_biomech_studio.app.QMainWindow'):
            self.window = MainWindow()
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    def test_load_reference_folder_cancel(self, mock_msgbox, mock_dialog):
        """Test canceling folder selection."""
        mock_dialog.getExistingDirectory.return_value = ""
        
        self.window._load_reference_folder()
        
        # Should not show any message boxes if canceled
        mock_msgbox.information.assert_not_called()
        mock_msgbox.critical.assert_not_called()
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    @patch('oct_biomech_studio.app.load_volume')
    def test_load_reference_folder_success(self, mock_load, mock_msgbox, mock_dialog):
        """Test successful folder loading for reference."""
        import numpy as np
        
        test_path = "/test/dicom/folder"
        mock_dialog.getExistingDirectory.return_value = test_path
        
        # Create a mock volume
        meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=(1, 0, 0, 0, 1, 0, 0, 0, 1),
            shape=(10, 10, 10),
            path=test_path
        )
        mock_volume = Volume(data=np.zeros((10, 10, 10)), meta=meta)
        mock_load.return_value = mock_volume
        
        with patch.object(self.window, '_display_volume') as mock_display:
            self.window._load_reference_folder()
        
        # Assertions
        mock_load.assert_called_once_with(test_path)
        mock_msgbox.information.assert_called_once()
        mock_display.assert_called_once_with(mock_volume)
        self.assertEqual(self.window.ref_vol, mock_volume)
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    @patch('oct_biomech_studio.app.load_volume')
    def test_load_reference_folder_error(self, mock_load, mock_msgbox, mock_dialog):
        """Test error handling in folder loading."""
        mock_dialog.getExistingDirectory.return_value = "/test/folder"
        mock_load.side_effect = ValueError("No DICOM series found")
        
        self.window._load_reference_folder()
        
        mock_msgbox.critical.assert_called_once()
        args = mock_msgbox.critical.call_args[0]
        self.assertIn("Error", args)
        self.assertIn("No DICOM series found", args[-1])
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    @patch('oct_biomech_studio.app.load_volume')
    def test_load_reference_folder_import_error(self, mock_load, mock_msgbox, mock_dialog):
        """Test handling of SimpleITK import error."""
        mock_dialog.getExistingDirectory.return_value = "/test/folder"
        mock_load.side_effect = ImportError("SimpleITK is required")
        
        self.window._load_reference_folder()
        
        mock_msgbox.critical.assert_called_once()
        args = mock_msgbox.critical.call_args[0]
        self.assertIn("SimpleITK", args[-1])


class TestLoadDeformedFolder(unittest.TestCase):
    """Test the new _load_deformed_folder method."""
    
    def setUp(self):
        """Set up test fixtures."""
        from oct_biomech_studio.app import MainWindow
        with patch('oct_biomech_studio.app.QMainWindow'):
            self.window = MainWindow()
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    def test_load_deformed_folder_cancel(self, mock_msgbox, mock_dialog):
        """Test canceling folder selection for deformed."""
        mock_dialog.getExistingDirectory.return_value = ""
        
        self.window._load_deformed_folder()
        
        mock_msgbox.information.assert_not_called()
        mock_msgbox.critical.assert_not_called()
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    @patch('oct_biomech_studio.app.load_volume')
    def test_load_deformed_folder_success(self, mock_load, mock_msgbox, mock_dialog):
        """Test successful deformed folder loading."""
        import numpy as np
        
        test_path = "/test/deformed/dicom"
        mock_dialog.getExistingDirectory.return_value = test_path
        
        meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=(1, 0, 0, 0, 1, 0, 0, 0, 1),
            shape=(10, 10, 10),
            path=test_path
        )
        mock_volume = Volume(data=np.zeros((10, 10, 10)), meta=meta)
        mock_load.return_value = mock_volume
        
        with patch.object(self.window, '_display_volume') as mock_display:
            self.window._load_deformed_folder()
        
        mock_load.assert_called_once_with(test_path)
        mock_msgbox.information.assert_called_once()
        mock_display.assert_called_once_with(mock_volume)
        self.assertEqual(self.window.def_vol, mock_volume)
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    @patch('oct_biomech_studio.app.load_volume')
    def test_load_deformed_folder_error(self, mock_load, mock_msgbox, mock_dialog):
        """Test error handling for deformed folder."""
        mock_dialog.getExistingDirectory.return_value = "/test/folder"
        mock_load.side_effect = Exception("Read error")
        
        self.window._load_deformed_folder()
        
        mock_msgbox.critical.assert_called_once()


class TestLoadReferenceFile(unittest.TestCase):
    """Test file loading methods (modified to exclude TIFF)."""
    
    def setUp(self):
        """Set up test fixtures."""
        from oct_biomech_studio.app import MainWindow
        with patch('oct_biomech_studio.app.QMainWindow'):
            self.window = MainWindow()
    
    @patch('oct_biomech_studio.app.QFileDialog')
    def test_load_reference_file_filter(self, mock_dialog):
        """Test that file dialog has correct filter without TIFF."""
        mock_dialog.getOpenFileName.return_value = ("", "")
        
        self.window._load_reference()
        
        # Get the filter string from the call
        call_args = mock_dialog.getOpenFileName.call_args
        filter_str = call_args[0][2]
        
        # Should include NPY, NII, DICOM but NOT TIFF
        self.assertIn("*.npy", filter_str)
        self.assertIn("*.nii", filter_str)
        self.assertIn("*.dcm", filter_str)
        self.assertNotIn("*.tif", filter_str)
        self.assertNotIn("*.tiff", filter_str)
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    @patch('oct_biomech_studio.app.load_volume')
    def test_load_reference_file_success(self, mock_load, mock_msgbox, mock_dialog):
        """Test successful file loading."""
        import numpy as np
        
        test_path = "/test/volume.npy"
        mock_dialog.getOpenFileName.return_value = (test_path, "")
        
        meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=(1, 0, 0, 0, 1, 0, 0, 0, 1),
            shape=(10, 10, 10)
        )
        mock_volume = Volume(data=np.zeros((10, 10, 10)), meta=meta)
        mock_load.return_value = mock_volume
        
        with patch.object(self.window, '_display_volume'):
            self.window._load_reference()
        
        mock_load.assert_called_once_with(test_path)


class TestLoadDeformedFile(unittest.TestCase):
    """Test deformed file loading (modified to exclude TIFF)."""
    
    def setUp(self):
        """Set up test fixtures."""
        from oct_biomech_studio.app import MainWindow
        with patch('oct_biomech_studio.app.QMainWindow'):
            self.window = MainWindow()
    
    @patch('oct_biomech_studio.app.QFileDialog')
    def test_load_deformed_file_filter(self, mock_dialog):
        """Test that deformed file dialog excludes TIFF."""
        mock_dialog.getOpenFileName.return_value = ("", "")
        
        self.window._load_deformed()
        
        call_args = mock_dialog.getOpenFileName.call_args
        filter_str = call_args[0][2]
        
        self.assertIn("*.npy", filter_str)
        self.assertIn("*.nii", filter_str)
        self.assertIn("*.dcm", filter_str)
        self.assertNotIn("*.tif", filter_str)
        self.assertNotIn("*.tiff", filter_str)


class TestLoadVolumePair(unittest.TestCase):
    """Test volume pair loading (updated file filters)."""
    
    def setUp(self):
        """Set up test fixtures."""
        from oct_biomech_studio.app import MainWindow
        with patch('oct_biomech_studio.app.QMainWindow'):
            self.window = MainWindow()
    
    @patch('oct_biomech_studio.app.QFileDialog')
    def test_load_volume_pair_filters(self, mock_dialog):
        """Test that volume pair dialogs exclude TIFF."""
        mock_dialog.getOpenFileName.return_value = ("", "")
        
        self.window._load_volume_pair()
        
        # Should be called twice (reference and deformed)
        self.assertEqual(mock_dialog.getOpenFileName.call_count, 2)
        
        # Check both calls exclude TIFF
        for call_obj in mock_dialog.getOpenFileName.call_args_list:
            filter_str = call_obj[0][2]
            self.assertNotIn("*.tif", filter_str)
            self.assertNotIn("*.tiff", filter_str)
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    def test_load_volume_pair_cancel_reference(self, mock_msgbox, mock_dialog):
        """Test canceling at reference selection."""
        mock_dialog.getOpenFileName.return_value = ("", "")
        
        self.window._load_volume_pair()
        
        # Should only call once (for reference) before returning
        self.assertEqual(mock_dialog.getOpenFileName.call_count, 1)
        mock_msgbox.information.assert_not_called()
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    def test_load_volume_pair_cancel_deformed(self, mock_msgbox, mock_dialog):
        """Test canceling at deformed selection."""
        mock_dialog.getOpenFileName.side_effect = [
            ("/test/ref.npy", ""),
            ("", "")  # Cancel on deformed
        ]
        
        self.window._load_volume_pair()
        
        # Should call twice but not proceed
        self.assertEqual(mock_dialog.getOpenFileName.call_count, 2)
        mock_msgbox.information.assert_not_called()


class TestDisplayVolume(unittest.TestCase):
    """Test volume display functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        from oct_biomech_studio.app import MainWindow
        with patch('oct_biomech_studio.app.QMainWindow'):
            self.window = MainWindow()
            # Mock the plotter
            self.window.plotter = Mock()
    
    @patch('oct_biomech_studio.app.pv')
    @patch('oct_biomech_studio.app.QMessageBox')
    def test_display_volume_success(self, mock_msgbox, mock_pv):
        """Test successful volume display."""
        import numpy as np
        
        meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=(1, 0, 0, 0, 1, 0, 0, 0, 1),
            shape=(10, 10, 10)
        )
        volume = Volume(data=np.zeros((10, 10, 10)), meta=meta)
        
        mock_grid = Mock()
        mock_pv.UniformGrid.return_value = mock_grid
        
        with patch.object(self.window, '_build_surface_actors'):
            self.window._display_volume(volume)
        
        # Verify PyVista calls
        mock_pv.UniformGrid.assert_called_once()
        self.window.plotter.clear.assert_called_once()
        self.window.plotter.add_volume.assert_called_once()
        self.window.plotter.reset_camera.assert_called_once()
    
    @patch('oct_biomech_studio.app.pv')
    @patch('oct_biomech_studio.app.QMessageBox')
    def test_display_volume_error(self, mock_msgbox, mock_pv):
        """Test error handling in display."""
        import numpy as np
        
        meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=(1, 0, 0, 0, 1, 0, 0, 0, 1),
            shape=(10, 10, 10)
        )
        volume = Volume(data=np.zeros((10, 10, 10)), meta=meta)
        
        mock_pv.UniformGrid.side_effect = Exception("PyVista error")
        
        self.window._display_volume(volume)
        
        mock_msgbox.critical.assert_called_once()


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios combining multiple features."""
    
    def setUp(self):
        """Set up test fixtures."""
        from oct_biomech_studio.app import MainWindow
        with patch('oct_biomech_studio.app.QMainWindow'):
            self.window = MainWindow()
            self.window.plotter = Mock()
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    @patch('oct_biomech_studio.app.load_volume')
    def test_load_reference_then_deformed_folders(self, mock_load, mock_msgbox, mock_dialog):
        """Test loading reference and deformed from folders sequentially."""
        import numpy as np
        
        # Setup mocks for two folder selections
        mock_dialog.getExistingDirectory.side_effect = [
            "/test/ref_folder",
            "/test/def_folder"
        ]
        
        ref_meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=(1, 0, 0, 0, 1, 0, 0, 0, 1),
            shape=(10, 10, 10)
        )
        def_meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=(1, 0, 0, 0, 1, 0, 0, 0, 1),
            shape=(10, 10, 10)
        )
        
        ref_vol = Volume(data=np.zeros((10, 10, 10)), meta=ref_meta)
        def_vol = Volume(data=np.zeros((10, 10, 10)), meta=def_meta)
        
        mock_load.side_effect = [ref_vol, def_vol]
        
        with patch.object(self.window, '_display_volume'):
            # Load reference folder
            self.window._load_reference_folder()
            self.assertEqual(self.window.ref_vol, ref_vol)
            
            # Load deformed folder
            self.window._load_deformed_folder()
            self.assertEqual(self.window.def_vol, def_vol)
        
        # Verify both were loaded
        self.assertEqual(mock_load.call_count, 2)
        self.assertEqual(mock_msgbox.information.call_count, 2)


class TestErrorRecovery(unittest.TestCase):
    """Test error recovery and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        from oct_biomech_studio.app import MainWindow
        with patch('oct_biomech_studio.app.QMainWindow'):
            self.window = MainWindow()
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    @patch('oct_biomech_studio.app.load_volume')
    def test_multiple_failed_loads(self, mock_load, mock_msgbox, mock_dialog):
        """Test that multiple failed loads are handled gracefully."""
        mock_dialog.getExistingDirectory.return_value = "/test/folder"
        mock_load.side_effect = ValueError("Invalid data")
        
        # Try loading multiple times
        self.window._load_reference_folder()
        self.window._load_deformed_folder()
        
        # Each should show an error
        self.assertEqual(mock_msgbox.critical.call_count, 2)
        
        # Window should still be in valid state
        self.assertIsNotNone(self.window)
    
    @patch('oct_biomech_studio.app.QFileDialog')
    @patch('oct_biomech_studio.app.QMessageBox')
    @patch('oct_biomech_studio.app.load_volume')
    def test_load_after_previous_error(self, mock_load, mock_msgbox, mock_dialog):
        """Test that loading works after a previous error."""
        import numpy as np
        
        mock_dialog.getExistingDirectory.side_effect = [
            "/test/bad_folder",
            "/test/good_folder"
        ]
        
        # First call fails, second succeeds
        meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=(1, 0, 0, 0, 1, 0, 0, 0, 1),
            shape=(5, 5, 5)
        )
        good_vol = Volume(data=np.zeros((5, 5, 5)), meta=meta)
        
        mock_load.side_effect = [
            ValueError("Bad data"),
            good_vol
        ]
        
        with patch.object(self.window, '_display_volume'):
            # First attempt fails
            self.window._load_reference_folder()
            mock_msgbox.critical.assert_called_once()
            
            # Second attempt succeeds
            mock_msgbox.reset_mock()
            self.window._load_reference_folder()
            mock_msgbox.information.assert_called_once()
            self.assertEqual(self.window.ref_vol, good_vol)


if __name__ == "__main__":
    unittest.main()