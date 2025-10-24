"""
Unit tests for core data abstraction layer.

Tests for SpatialData implementations and factory functions.
"""

import pytest
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import core modules
from src.core import (
    SpatialData,
    VisiumData,
    XeniumData,
    OMETiffData,
    PhenoCyclerData,
    create_spatial_data,
    detect_modality,
    list_supported_formats,
)


class TestSpatialDataAbstract:
    """Test abstract SpatialData class."""
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that SpatialData cannot be instantiated directly."""
        with pytest.raises(TypeError):
            SpatialData("/fake/path", "test")
    
    def test_spatial_data_repr(self):
        """Test string representation."""
        # Create a mock subclass
        class MockSpatialData(SpatialData):
            def load_image(self, channel=None):
                return np.zeros((100, 100))
            def get_metadata(self):
                return {}
            def get_resolution(self):
                return 1.0
            def get_channels(self):
                return ["ch1"]
            def generate_mask(self, **kwargs):
                return np.zeros((100, 100), dtype=np.uint8)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            data = MockSpatialData(tmpdir, "test")
            repr_str = repr(data)
            assert "MockSpatialData" in repr_str
            assert "test" in repr_str


class TestVisiumData:
    """Test VisiumData class."""
    
    def test_visium_initialization(self):
        """Test VisiumData initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal Visium structure
            spatial_dir = Path(tmpdir) / "spatial"
            spatial_dir.mkdir()
            
            # Create dummy image
            img_path = Path(tmpdir) / "tissue_hires_image.png"
            img_path.touch()
            
            data = VisiumData(tmpdir)
            assert data.modality == "visium"
            assert data.resolution > 0
    
    def test_visium_get_channels(self):
        """Test Visium channel retrieval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spatial_dir = Path(tmpdir) / "spatial"
            spatial_dir.mkdir()
            
            data = VisiumData(tmpdir)
            channels = data.get_channels()
            assert channels == ["H&E"]
    
    def test_visium_validate_missing_image(self):
        """Test validation with missing image."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spatial_dir = Path(tmpdir) / "spatial"
            spatial_dir.mkdir()
            
            data = VisiumData(tmpdir)
            is_valid, msg = data.validate()
            assert not is_valid
            assert "not found" in msg.lower()


class TestXeniumData:
    """Test XeniumData class."""
    
    def test_xenium_initialization(self):
        """Test XeniumData initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy TIFF file
            tiff_path = Path(tmpdir) / "image.ome.tiff"
            tiff_path.touch()
            
            # Mock tifffile
            with patch('src.core.xenium_data.tifffile') as mock_tifffile:
                mock_tif = MagicMock()
                mock_page = MagicMock()
                mock_page.shape = (100, 100)
                mock_page.description = None
                mock_tif.pages = [mock_page]
                mock_tif.ome_metadata = None
                mock_tifffile.TiffFile.return_value.__enter__.return_value = mock_tif
                
                data = XeniumData(tmpdir)
                assert data.modality == "xenium"
    
    def test_xenium_validate_missing_file(self):
        """Test validation with missing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data = XeniumData(tmpdir)
            is_valid, msg = data.validate()
            assert not is_valid


class TestOMETiffData:
    """Test OMETiffData class."""
    
    def test_ometiff_initialization(self):
        """Test OMETiffData initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tiff_path = Path(tmpdir) / "image.tiff"
            tiff_path.touch()
            
            with patch('src.core.ometiff_data.tifffile') as mock_tifffile:
                mock_tif = MagicMock()
                mock_page = MagicMock()
                mock_page.shape = (100, 100)
                mock_page.description = None
                mock_tif.pages = [mock_page]
                mock_tif.ome_metadata = None
                mock_tifffile.TiffFile.return_value.__enter__.return_value = mock_tif
                
                data = OMETiffData(str(tiff_path))
                assert data.modality == "ometiff"


class TestPhenoCyclerData:
    """Test PhenoCyclerData class."""
    
    def test_phenocycler_initialization(self):
        """Test PhenoCyclerData initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            qptiff_path = Path(tmpdir) / "image.qptiff"
            qptiff_path.touch()
            
            with patch('src.core.phenocycler_data.tifffile') as mock_tifffile:
                mock_tif = MagicMock()
                mock_series = MagicMock()
                mock_page = MagicMock()
                mock_page.shape = (100, 100)
                mock_page.description = None
                mock_series.pages = [mock_page]
                mock_tif.series = [mock_series]
                mock_tifffile.TiffFile.return_value.__enter__.return_value = mock_tif
                
                data = PhenoCyclerData(str(qptiff_path))
                assert data.modality == "phenocycler"


class TestDataFactory:
    """Test data factory functions."""
    
    def test_create_spatial_data_with_explicit_modality(self):
        """Test factory with explicit modality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spatial_dir = Path(tmpdir) / "spatial"
            spatial_dir.mkdir()
            
            data = create_spatial_data(tmpdir, modality="visium")
            assert isinstance(data, VisiumData)
    
    def test_create_spatial_data_invalid_modality(self):
        """Test factory with invalid modality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError):
                create_spatial_data(tmpdir, modality="invalid")
    
    def test_create_spatial_data_nonexistent_path(self):
        """Test factory with nonexistent path."""
        with pytest.raises(FileNotFoundError):
            create_spatial_data("/nonexistent/path")
    
    def test_detect_modality_visium(self):
        """Test modality detection for Visium."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spatial_dir = Path(tmpdir) / "spatial"
            spatial_dir.mkdir()
            
            modality = detect_modality(tmpdir)
            assert modality == "visium"
    
    def test_detect_modality_by_extension(self):
        """Test modality detection by file extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            qptiff_path = Path(tmpdir) / "image.qptiff"
            qptiff_path.touch()
            
            modality = detect_modality(str(qptiff_path))
            assert modality == "phenocycler"
    
    def test_list_supported_formats(self):
        """Test listing supported formats."""
        formats = list_supported_formats()
        assert "visium" in formats
        assert "xenium" in formats
        assert "phenocycler" in formats
        assert "ometiff" in formats
        
        for fmt in formats.values():
            assert "description" in fmt
            assert "file_types" in fmt


class TestDataCaching:
    """Test data caching functionality."""
    
    def test_image_cache_clearing(self):
        """Test image cache clearing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spatial_dir = Path(tmpdir) / "spatial"
            spatial_dir.mkdir()
            
            data = VisiumData(tmpdir)
            data._image_cache = np.zeros((100, 100))
            
            data.clear_cache()
            assert data._image_cache is None
            assert data._mask_cache is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

