"""
Generic OME-TIFF data handler.

This module implements the SpatialData interface for arbitrary OME-TIFF files,
providing support for any OME-compliant TIFF format.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
import xml.etree.ElementTree as ET

try:
    import tifffile
except ImportError:
    tifffile = None

from .spatial_data import SpatialData


class OMETiffData(SpatialData):
    """
    Handler for generic OME-TIFF files.
    
    Supports any OME-compliant TIFF format with multi-channel data
    and OME-XML metadata.
    
    Attributes:
        tiff_path (Path): Path to OME-TIFF file
        channels (List[str]): List of channel names
    """
    
    def __init__(self, data_path: str):
        """
        Initialize OMETiffData instance.
        
        Args:
            data_path: Path to OME-TIFF file
        """
        super().__init__(data_path, modality="ometiff")
        self.tiff_path = self.data_path
        self.channels: List[str] = []
        self._channel_data: Dict[int, np.ndarray] = {}
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata from OME-TIFF file."""
        if not tifffile:
            raise ImportError("tifffile is required for OME-TIFF data")
        
        try:
            with tifffile.TiffFile(str(self.tiff_path)) as tif:
                # Extract OME-XML metadata
                if hasattr(tif, 'ome_metadata'):
                    self.metadata['ome_xml'] = tif.ome_metadata
                
                # Extract basic information
                if hasattr(tif, 'pages') and len(tif.pages) > 0:
                    page = tif.pages[0]
                    
                    # Get image dimensions
                    self.metadata['height'] = page.shape[0]
                    self.metadata['width'] = page.shape[1]
                    self.metadata['num_channels'] = len(tif.pages)
                    self.metadata['dtype'] = str(page.dtype)
                    
                    # Extract resolution from tags
                    if hasattr(page, 'tags'):
                        if 'XResolution' in page.tags:
                            xres = page.tags['XResolution'].value
                            self.resolution = 25400.0 / xres[0]
                        if 'YResolution' in page.tags:
                            yres = page.tags['YResolution'].value
                            self.resolution = 25400.0 / yres[0]
                    
                    # Extract channel names
                    for i, p in enumerate(tif.pages):
                        if hasattr(p, 'description') and p.description:
                            try:
                                root = ET.fromstring(p.description)
                                channel_name = root.find('.//Name')
                                if channel_name is not None:
                                    self.channels.append(channel_name.text)
                                else:
                                    self.channels.append(f"Channel_{i}")
                            except:
                                self.channels.append(f"Channel_{i}")
                        else:
                            self.channels.append(f"Channel_{i}")
        
        except Exception as e:
            print(f"Warning: Could not load OME-TIFF metadata: {e}")
    
    def load_image(self, channel: Optional[int] = None) -> np.ndarray:
        """
        Load image data from OME-TIFF.
        
        Args:
            channel: Channel index to load (default: 0)
            
        Returns:
            Image as numpy array
        """
        if not tifffile:
            raise ImportError("tifffile is required for OME-TIFF data")
        
        if channel is None:
            channel = 0
        
        if channel in self._channel_data:
            return self._channel_data[channel]
        
        if not self.tiff_path.exists():
            raise FileNotFoundError(f"OME-TIFF not found: {self.tiff_path}")
        
        try:
            img = tifffile.imread(str(self.tiff_path), key=channel)
            self._channel_data[channel] = img
            return img
        except Exception as e:
            raise ValueError(f"Failed to load channel {channel}: {e}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get OME-TIFF metadata.
        
        Returns:
            Dictionary with OME-XML, dimensions, channels, etc.
        """
        return self.metadata.copy()
    
    def get_resolution(self) -> float:
        """
        Get resolution in micrometers.
        
        Returns:
            Resolution in micrometers
        """
        return self.resolution
    
    def get_channels(self) -> List[str]:
        """
        Get list of channel names.
        
        Returns:
            List of channel names
        """
        return self.channels.copy()
    
    def generate_mask(self, **kwargs) -> np.ndarray:
        """
        Generate binary mask from OME-TIFF data.
        
        Args:
            channel: Channel index to use (default: 0)
            threshold: Intensity threshold (default: auto)
            
        Returns:
            Binary mask (uint8, values 0 or 255)
        """
        import cv2
        
        channel = kwargs.get('channel', 0)
        img = self.load_image(channel=channel)
        
        # Normalize to 0-255 range
        if img.dtype == np.uint16:
            img_norm = (img / 256).astype(np.uint8)
        elif img.dtype == np.uint32:
            img_norm = (img / 65536).astype(np.uint8)
        else:
            img_norm = img.astype(np.uint8)
        
        # Apply threshold
        threshold = kwargs.get('threshold', None)
        if threshold is None:
            # Auto threshold using Otsu's method
            _, mask = cv2.threshold(img_norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            _, mask = cv2.threshold(img_norm, threshold, 255, cv2.THRESH_BINARY)
        
        return mask
    
    def validate(self) -> tuple:
        """
        Validate OME-TIFF data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, msg = super().validate()
        if not is_valid:
            return is_valid, msg
        
        if not self.tiff_path.exists():
            return False, f"OME-TIFF not found: {self.tiff_path}"
        
        if not tifffile:
            return False, "tifffile library not installed"
        
        return True, ""

