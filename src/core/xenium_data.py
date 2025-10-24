"""
Xenium spatial omics data handler.

This module implements the SpatialData interface for 10x Genomics Xenium data,
which consists of multi-channel OME-TIFF files with subcellular resolution.
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


class XeniumData(SpatialData):
    """
    Handler for 10x Genomics Xenium spatial omics data.
    
    Xenium data consists of:
    - Multi-channel OME-TIFF files
    - OME-XML metadata in TIFF tags
    - Subcellular resolution (~0.5 µm)
    
    Attributes:
        tiff_path (Path): Path to OME-TIFF file
        channels (List[str]): List of channel names
    """
    
    def __init__(self, data_path: str, filename: str = "image.ome.tiff"):
        """
        Initialize XeniumData instance.
        
        Args:
            data_path: Path to Xenium data directory or file
            filename: Name of OME-TIFF file (default: image.ome.tiff)
        """
        super().__init__(data_path, modality="xenium")
        
        # Handle both file and directory paths
        if self.data_path.is_file():
            self.tiff_path = self.data_path
        else:
            self.tiff_path = self.data_path / filename
        
        self.channels: List[str] = []
        self._channel_data: Dict[int, np.ndarray] = {}
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata from OME-TIFF file."""
        if not tifffile:
            raise ImportError("tifffile is required for Xenium data. Install with: pip install tifffile")
        
        try:
            with tifffile.TiffFile(str(self.tiff_path)) as tif:
                # Extract OME-XML metadata
                if hasattr(tif, 'ome_metadata'):
                    self.metadata['ome_xml'] = tif.ome_metadata
                
                # Extract channel information
                if hasattr(tif, 'pages') and len(tif.pages) > 0:
                    page = tif.pages[0]
                    
                    # Get image dimensions
                    self.metadata['height'] = page.shape[0]
                    self.metadata['width'] = page.shape[1]
                    self.metadata['num_channels'] = len(tif.pages)
                    
                    # Extract resolution from tags
                    if hasattr(page, 'tags'):
                        if 'XResolution' in page.tags:
                            xres = page.tags['XResolution'].value
                            # Convert from pixels/inch to µm/pixel
                            self.resolution = 25400.0 / xres[0]
                        if 'YResolution' in page.tags:
                            yres = page.tags['YResolution'].value
                            self.resolution = 25400.0 / yres[0]
                    
                    # Extract channel names from descriptions
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
            print(f"Warning: Could not load Xenium metadata: {e}")
            self.channels = [f"Channel_{i}" for i in range(10)]  # Default channels
    
    def load_image(self, channel: Optional[int] = None) -> np.ndarray:
        """
        Load image data from OME-TIFF.
        
        Args:
            channel: Channel index to load (default: 0)
            
        Returns:
            Image as numpy array (uint16 or uint8)
        """
        if not tifffile:
            raise ImportError("tifffile is required for Xenium data")
        
        if channel is None:
            channel = 0
        
        if channel in self._channel_data:
            return self._channel_data[channel]
        
        if not self.tiff_path.exists():
            raise FileNotFoundError(f"Xenium TIFF not found: {self.tiff_path}")
        
        try:
            img = tifffile.imread(str(self.tiff_path), key=channel)
            self._channel_data[channel] = img
            return img
        except Exception as e:
            raise ValueError(f"Failed to load channel {channel}: {e}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get Xenium metadata.
        
        Returns:
            Dictionary with OME-XML, dimensions, channels, etc.
        """
        return self.metadata.copy()
    
    def get_resolution(self) -> float:
        """
        Get Xenium resolution in micrometers.
        
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
        Generate binary mask from Xenium data using intensity thresholding.
        
        Args:
            channel: Channel index to use (default: 0)
            threshold: Intensity threshold (default: auto)
            
        Returns:
            Binary mask (uint8, values 0 or 255)
        """
        channel = kwargs.get('channel', 0)
        img = self.load_image(channel=channel)
        
        # Normalize to 0-255 range
        if img.dtype == np.uint16:
            img_norm = (img / 256).astype(np.uint8)
        else:
            img_norm = img
        
        # Apply threshold
        threshold = kwargs.get('threshold', None)
        if threshold is None:
            # Auto threshold using Otsu's method
            import cv2
            _, mask = cv2.threshold(img_norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            import cv2
            _, mask = cv2.threshold(img_norm, threshold, 255, cv2.THRESH_BINARY)
        
        return mask
    
    def validate(self) -> tuple:
        """
        Validate Xenium data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, msg = super().validate()
        if not is_valid:
            return is_valid, msg
        
        if not self.tiff_path.exists():
            return False, f"Xenium TIFF not found: {self.tiff_path}"
        
        if not tifffile:
            return False, "tifffile library not installed"
        
        return True, ""

