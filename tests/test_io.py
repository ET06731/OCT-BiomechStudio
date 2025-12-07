import unittest
from unittest.mock import Mock, patch, MagicMock, call
import tempfile
import shutil
from pathlib import Path
from oct_biomech_studio.io import load_volume, load_volume_pair, load_segmentation, _default_meta, _identity_direction
from oct_biomech_studio.models import Volume, VolumeMeta, Segmentation, VolumePair


class TestIdentityDirection(unittest.TestCase):
    """Test the _identity_direction helper function."""
    
    def test_identity_direction_returns_tuple(self):
        result = _identity_direction()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 9)
    
    def test_identity_direction_values(self):
        result = _identity_direction()
        expected = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        self.assertEqual(result, expected)
    
    def test_identity_direction_immutable(self):
        """Ensure the function returns a tuple (immutable)."""
        result = _identity_direction()
        with self.assertRaises(TypeError):
            result[0] = 2.0


class TestDefaultMeta(unittest.TestCase):
    """Test the _default_meta helper function."""
    
    def test_default_meta_basic(self):
        shape = (10, 20, 30)
        path = "/test/path.npy"
        meta = _default_meta(shape, path)
        
        self.assertIsInstance(meta, VolumeMeta)
        self.assertEqual(meta.shape, shape)
        self.assertEqual(meta.path, path)
        self.assertEqual(meta.origin, (0.0, 0.0, 0.0))
        self.assertEqual(meta.spacing, (1.0, 1.0, 1.0))
    
    def test_default_meta_direction(self):
        meta = _default_meta((5, 5, 5), "test.npy")
        self.assertEqual(meta.direction, _identity_direction())
    
    def test_default_meta_various_shapes(self):
        """Test with different shape tuples."""
        shapes = [(1, 1, 1), (100, 200, 300), (512, 512, 128)]
        for shape in shapes:
            meta = _default_meta(shape, "test.npy")
            self.assertEqual(meta.shape, shape)


class TestLoadVolumeDirectory(unittest.TestCase):
    """Test DICOM directory loading functionality (new feature)."""
    
    @patch('oct_biomech_studio.io.Path')
    @patch('oct_biomech_studio.io.sitk')
    def test_load_dicom_directory_success(self, mock_sitk, mock_path_cls):
        """Test successful DICOM directory loading."""
        # Setup mocks
        mock_path = Mock()
        mock_path.is_dir.return_value = True
        mock_path_cls.return_value = mock_path
        
        mock_reader = Mock()
        mock_sitk.ImageSeriesReader.return_value = mock_reader
        mock_reader.GetGDCMSeriesFileNames.return_value = ['file1.dcm', 'file2.dcm']
        
        mock_img = Mock()
        mock_reader.Execute.return_value = mock_img
        mock_img.GetOrigin.return_value = (1.0, 2.0, 3.0)
        mock_img.GetSpacing.return_value = (0.5, 0.5, 1.0)
        mock_img.GetDirection.return_value = (1, 0, 0, 0, 1, 0, 0, 0, 1)
        
        import numpy as np
        mock_arr = np.zeros((10, 20, 30))
        mock_sitk.GetArrayFromImage.return_value = mock_arr
        
        # Execute
        result = load_volume('/test/dicom_dir')
        
        # Assert
        self.assertIsInstance(result, Volume)
        self.assertEqual(result.meta.shape, (10, 20, 30))
        self.assertEqual(result.meta.origin, (1.0, 2.0, 3.0))
        self.assertEqual(result.meta.spacing, (0.5, 0.5, 1.0))
        mock_reader.SetFileNames.assert_called_once_with(['file1.dcm', 'file2.dcm'])
        mock_reader.Execute.assert_called_once()
    
    @patch('oct_biomech_studio.io.Path')
    @patch('oct_biomech_studio.io.sitk')
    def test_load_dicom_directory_empty(self, mock_sitk, mock_path_cls):
        """Test loading directory with no DICOM files."""
        mock_path = Mock()
        mock_path.is_dir.return_value = True
        mock_path_cls.return_value = mock_path
        
        mock_reader = Mock()
        mock_sitk.ImageSeriesReader.return_value = mock_reader
        mock_reader.GetGDCMSeriesFileNames.return_value = []
        
        with self.assertRaises(ValueError) as context:
            load_volume('/test/empty_dir')
        
        self.assertIn("No DICOM series found", str(context.exception))
    
    @patch('oct_biomech_studio.io.Path')
    def test_load_dicom_directory_no_simpleitk(self, mock_path_cls):
        """Test error when SimpleITK is not available."""
        mock_path = Mock()
        mock_path.is_dir.return_value = True
        mock_path_cls.return_value = mock_path
        
        with patch.dict('sys.modules', {'SimpleITK': None}):
            with self.assertRaises(ImportError) as context:
                load_volume('/test/dicom_dir')
            
            self.assertIn("SimpleITK is required", str(context.exception))
    
    @patch('oct_biomech_studio.io.Path')
    @patch('oct_biomech_studio.io.sitk')
    def test_load_dicom_directory_metadata_extraction(self, mock_sitk, mock_path_cls):
        """Test that metadata is correctly extracted from DICOM series."""
        mock_path = Mock()
        mock_path.is_dir.return_value = True
        mock_path.name = "test_series"
        mock_path_cls.return_value = mock_path
        
        mock_reader = Mock()
        mock_sitk.ImageSeriesReader.return_value = mock_reader
        mock_reader.GetGDCMSeriesFileNames.return_value = ['f1.dcm']
        
        mock_img = Mock()
        mock_reader.Execute.return_value = mock_img
        
        # Test with specific metadata values
        test_origin = (10.5, 20.5, 30.5)
        test_spacing = (0.25, 0.25, 2.0)
        test_direction = (1, 0, 0, 0, -1, 0, 0, 0, 1)
        
        mock_img.GetOrigin.return_value = test_origin
        mock_img.GetSpacing.return_value = test_spacing
        mock_img.GetDirection.return_value = test_direction
        
        import numpy as np
        mock_arr = np.zeros((5, 10, 15))
        mock_sitk.GetArrayFromImage.return_value = mock_arr
        
        result = load_volume('/test/dicom_dir')
        
        self.assertEqual(result.meta.origin, test_origin)
        self.assertEqual(result.meta.spacing, test_spacing)
        self.assertEqual(result.meta.direction, tuple(test_direction))


class TestLoadVolumeNPY(unittest.TestCase):
    """Test NPY file loading."""
    
    def test_load_npy_volume_success(self):
        """Test loading a valid NPY volume."""
        import numpy as np
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.npy"
            arr = np.random.rand(10, 20, 30).astype(np.float32)
            np.save(str(path), arr)
            
            result = load_volume(str(path))
            
            self.assertIsInstance(result, Volume)
            self.assertEqual(result.data.shape, (10, 20, 30))
            self.assertEqual(result.meta.shape, (10, 20, 30))
    
    def test_load_npy_invalid_dimensions(self):
        """Test error when NPY array is not 3D."""
        import numpy as np
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test 2D array
            path = Path(tmpdir) / "test2d.npy"
            arr = np.random.rand(10, 20)
            np.save(str(path), arr)
            
            with self.assertRaises(ValueError) as context:
                load_volume(str(path))
            self.assertIn("must be 3D", str(context.exception))
            
            # Test 4D array
            path = Path(tmpdir) / "test4d.npy"
            arr = np.random.rand(10, 20, 30, 5)
            np.save(str(path), arr)
            
            with self.assertRaises(ValueError) as context:
                load_volume(str(path))
            self.assertIn("must be 3D", str(context.exception))
    
    def test_load_npy_uses_default_metadata(self):
        """Test that NPY files get default metadata."""
        import numpy as np
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.npy"
            arr = np.random.rand(5, 10, 15)
            np.save(str(path), arr)
            
            result = load_volume(str(path))
            
            self.assertEqual(result.meta.origin, (0.0, 0.0, 0.0))
            self.assertEqual(result.meta.spacing, (1.0, 1.0, 1.0))
            self.assertEqual(result.meta.direction, _identity_direction())


class TestLoadVolumeNIfTI(unittest.TestCase):
    """Test NIfTI file loading."""
    
    @patch('oct_biomech_studio.io.sitk')
    def test_load_nii_volume(self, mock_sitk):
        """Test loading .nii file."""
        mock_img = Mock()
        mock_sitk.ReadImage.return_value = mock_img
        
        import numpy as np
        mock_arr = np.zeros((10, 20, 30))
        mock_sitk.GetArrayFromImage.return_value = mock_arr
        
        mock_img.GetOrigin.return_value = (0, 0, 0)
        mock_img.GetSpacing.return_value = (1, 1, 1)
        mock_img.GetDirection.return_value = (1, 0, 0, 0, 1, 0, 0, 0, 1)
        
        result = load_volume('/test/volume.nii')
        
        self.assertIsInstance(result, Volume)
        mock_sitk.ReadImage.assert_called_once_with('/test/volume.nii')
    
    @patch('oct_biomech_studio.io.sitk')
    def test_load_nii_gz_volume(self, mock_sitk):
        """Test loading .nii.gz file."""
        mock_img = Mock()
        mock_sitk.ReadImage.return_value = mock_img
        
        import numpy as np
        mock_arr = np.zeros((10, 20, 30))
        mock_sitk.GetArrayFromImage.return_value = mock_arr
        
        mock_img.GetOrigin.return_value = (0, 0, 0)
        mock_img.GetSpacing.return_value = (1, 1, 1)
        mock_img.GetDirection.return_value = (1, 0, 0, 0, 1, 0, 0, 0, 1)
        
        result = load_volume('/test/volume.nii.gz')
        
        self.assertIsInstance(result, Volume)
        mock_sitk.ReadImage.assert_called_once_with('/test/volume.nii.gz')
    
    @patch('oct_biomech_studio.io.sitk', None)
    def test_load_nii_no_simpleitk(self):
        """Test error when SimpleITK not available for NIfTI."""
        with self.assertRaises(ImportError) as context:
            load_volume('/test/volume.nii')
        self.assertIn("SimpleITK is required", str(context.exception))


class TestLoadVolumeDICOM(unittest.TestCase):
    """Test DICOM file loading."""
    
    @patch('oct_biomech_studio.io.Path')
    @patch('oct_biomech_studio.io.sitk')
    def test_load_dcm_file(self, mock_sitk, mock_path_cls):
        """Test loading single DICOM file."""
        mock_path = Mock()
        mock_path.is_dir.return_value = False
        mock_path.suffix.lower.return_value = '.dcm'
        mock_path_cls.return_value = mock_path
        
        mock_img = Mock()
        mock_sitk.ReadImage.return_value = mock_img
        
        import numpy as np
        mock_arr = np.zeros((10, 20, 30))
        mock_sitk.GetArrayFromImage.return_value = mock_arr
        
        mock_img.GetOrigin.return_value = (0, 0, 0)
        mock_img.GetSpacing.return_value = (1, 1, 1)
        mock_img.GetDirection.return_value = (1, 0, 0, 0, 1, 0, 0, 0, 1)
        
        result = load_volume('/test/image.dcm')
        
        self.assertIsInstance(result, Volume)
    
    @patch('oct_biomech_studio.io.Path')
    @patch('oct_biomech_studio.io.sitk', None)
    def test_load_dcm_no_simpleitk(self, mock_path_cls):
        """Test error when SimpleITK not available for DICOM."""
        mock_path = Mock()
        mock_path.is_dir.return_value = False
        mock_path.suffix.lower.return_value = '.dcm'
        mock_path_cls.return_value = mock_path
        
        with self.assertRaises(ImportError) as context:
            load_volume('/test/image.dcm')
        self.assertIn("SimpleITK is required", str(context.exception))


class TestLoadVolumeUnsupportedFormat(unittest.TestCase):
    """Test handling of unsupported file formats."""
    
    @patch('oct_biomech_studio.io.Path')
    def test_unsupported_extension(self, mock_path_cls):
        """Test that unsupported formats raise NotImplementedError."""
        mock_path = Mock()
        mock_path.is_dir.return_value = False
        mock_path.suffix.lower.return_value = '.txt'
        mock_path_cls.return_value = mock_path
        
        with self.assertRaises(NotImplementedError) as context:
            load_volume('/test/file.txt')
        self.assertIn("unsupported format", str(context.exception))
    
    @patch('oct_biomech_studio.io.Path')
    def test_tiff_removed(self, mock_path_cls):
        """Test that TIFF support has been removed."""
        mock_path = Mock()
        mock_path.is_dir.return_value = False
        mock_path.suffix.lower.return_value = '.tif'
        mock_path_cls.return_value = mock_path
        
        with self.assertRaises(NotImplementedError):
            load_volume('/test/file.tif')
        
        # Also test .tiff extension
        mock_path.suffix.lower.return_value = '.tiff'
        with self.assertRaises(NotImplementedError):
            load_volume('/test/file.tiff')


class TestLoadSegmentation(unittest.TestCase):
    """Test segmentation loading."""
    
    def test_load_segmentation_npy(self):
        """Test loading segmentation from NPY file."""
        import numpy as np
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "seg.npy"
            arr = np.random.randint(0, 6, (10, 20, 30), dtype=np.uint8)
            np.save(str(path), arr)
            
            result = load_segmentation(str(path))
            
            self.assertIsInstance(result, Segmentation)
            self.assertEqual(result.labels.shape, (10, 20, 30))
    
    def test_load_segmentation_invalid_dimensions(self):
        """Test error for non-3D segmentation."""
        import numpy as np
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "seg2d.npy"
            arr = np.random.randint(0, 6, (10, 20))
            np.save(str(path), arr)
            
            with self.assertRaises(ValueError) as context:
                load_segmentation(str(path))
            self.assertIn("must be 3D", str(context.exception))
    
    @patch('oct_biomech_studio.io.sitk')
    def test_load_segmentation_nii(self, mock_sitk):
        """Test loading segmentation from NIfTI."""
        mock_img = Mock()
        mock_sitk.ReadImage.return_value = mock_img
        
        import numpy as np
        mock_arr = np.zeros((10, 20, 30), dtype=np.uint8)
        mock_sitk.GetArrayFromImage.return_value = mock_arr
        
        mock_img.GetOrigin.return_value = (0, 0, 0)
        mock_img.GetSpacing.return_value = (1, 1, 1)
        mock_img.GetDirection.return_value = (1, 0, 0, 0, 1, 0, 0, 0, 1)
        
        result = load_segmentation('/test/seg.nii')
        
        self.assertIsInstance(result, Segmentation)


class TestLoadVolumePair(unittest.TestCase):
    """Test volume pair loading."""
    
    @patch('oct_biomech_studio.io.load_volume')
    def test_load_volume_pair_success(self, mock_load_volume):
        """Test loading a volume pair."""
        import numpy as np
        
        ref_meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=_identity_direction(),
            shape=(10, 10, 10)
        )
        def_meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=_identity_direction(),
            shape=(10, 10, 10)
        )
        
        ref_vol = Volume(data=np.zeros((10, 10, 10)), meta=ref_meta)
        def_vol = Volume(data=np.zeros((10, 10, 10)), meta=def_meta)
        
        mock_load_volume.side_effect = [ref_vol, def_vol]
        
        result = load_volume_pair('/ref.npy', '/def.npy')
        
        self.assertIsInstance(result, VolumePair)
        self.assertEqual(result.reference, ref_vol)
        self.assertEqual(result.deformed, def_vol)
        self.assertEqual(mock_load_volume.call_count, 2)
    
    @patch('oct_biomech_studio.io.load_volume')
    def test_load_volume_pair_calls_order(self, mock_load_volume):
        """Test that reference is loaded before deformed."""
        import numpy as np
        
        meta = VolumeMeta(
            origin=(0, 0, 0),
            spacing=(1, 1, 1),
            direction=_identity_direction(),
            shape=(5, 5, 5)
        )
        vol = Volume(data=np.zeros((5, 5, 5)), meta=meta)
        mock_load_volume.return_value = vol
        
        load_volume_pair('/path/ref.npy', '/path/def.npy')
        
        calls = mock_load_volume.call_args_list
        self.assertEqual(calls[0], call('/path/ref.npy'))
        self.assertEqual(calls[1], call('/path/def.npy'))


class TestLoadVolumeEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    @patch('oct_biomech_studio.io.Path')
    def test_load_volume_with_dots_in_name(self, mock_path_cls):
        """Test handling of filenames with multiple dots."""
        mock_path = Mock()
        mock_path.is_dir.return_value = False
        mock_path.name = "volume.scan.001.nii.gz"
        mock_path.suffix.lower.return_value = '.gz'
        mock_path_cls.return_value = mock_path
        
        # Should recognize .nii.gz pattern
        with patch('oct_biomech_studio.io.sitk') as mock_sitk:
            mock_img = Mock()
            mock_sitk.ReadImage.return_value = mock_img
            import numpy as np
            mock_sitk.GetArrayFromImage.return_value = np.zeros((5, 5, 5))
            mock_img.GetOrigin.return_value = (0, 0, 0)
            mock_img.GetSpacing.return_value = (1, 1, 1)
            mock_img.GetDirection.return_value = (1, 0, 0, 0, 1, 0, 0, 0, 1)
            
            result = load_volume('/test/volume.scan.001.nii.gz')
            self.assertIsInstance(result, Volume)
    
    @patch('oct_biomech_studio.io.Path')
    @patch('oct_biomech_studio.io.sitk')
    def test_load_volume_preserves_path_info(self, mock_sitk, mock_path_cls):
        """Test that the path information is preserved in metadata."""
        test_path = "/absolute/path/to/volume.dcm"
        
        mock_path = Mock()
        mock_path.is_dir.return_value = False
        mock_path.suffix.lower.return_value = '.dcm'
        mock_path_cls.return_value = mock_path
        
        mock_img = Mock()
        mock_sitk.ReadImage.return_value = mock_img
        
        import numpy as np
        mock_sitk.GetArrayFromImage.return_value = np.zeros((5, 5, 5))
        mock_img.GetOrigin.return_value = (0, 0, 0)
        mock_img.GetSpacing.return_value = (1, 1, 1)
        mock_img.GetDirection.return_value = (1, 0, 0, 0, 1, 0, 0, 0, 1)
        
        result = load_volume(test_path)
        
        # Path should be preserved in metadata
        self.assertIsNotNone(result.meta.path)


if __name__ == "__main__":
    unittest.main()