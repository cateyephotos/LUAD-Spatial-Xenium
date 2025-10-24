"""
PhenoCycler QPTIFF data handler.

This module implements the SpatialData interface for Akoya Biosciences PhenoCycler
QPTIFF files, which contain multi-channel immunofluorescence data.
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


class PhenoCyclerData(SpatialData):
    """
    Handler for Akoya Biosciences PhenoCycler QPTIFF data.
    
    PhenoCycler data consists of:
    - Multi-channel QPTIFF files
    - XML metadata in page descriptions
    - Biomarker information
    
    Attributes:
        qptiff_path (Path): Path to QPTIFF file
        channels (List[str]): List of biomarker names
        resolution_nm (float): Resolution in nanometers
    """
    
    def __init__(self, data_path: str):
        """
        Initialize PhenoCyclerData instance.
        
        Args:
            data_path: Path to QPTIFF file
        """
        super().__init__(data_path, modality="phenocycler")
        self.qptiff_path = self.data_path
        self.channels: List[str] = []
        self.resolution_nm: float = 1.0
        self._channel_data: Dict[int, np.ndarray] = {}
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata from QPTIFF file."""
        if not tifffile:
            raise ImportError("tifffile is required for PhenoCycler data")
        
        try:
            with tifffile.TiffFile(str(self.qptiff_path)) as tif:
                if hasattr(tif, 'series') and len(tif.series) > 0:
                    series = tif.series[0]
                    
                    # Get number of channels
                    self.metadata['num_channels'] = len(series.pages)
                    
                    # Extract metadata from each page
                    for i, page in enumerate(series.pages):
                        # Get image dimensions from first page
                        if i == 0:
                            self.metadata['height'] = page.shape[0]
                            self.metadata['width'] = page.shape[1]
                            self.metadata['dtype'] = str(page.dtype)
                        
                        # Extract biomarker name and resolution from XML
                        if hasattr(page, 'description') and page.description:
                            try:
                                root = ET.fromstring(page.description)
                                
                                # Extract biomarker name
                                biomarker = root.find('Biomarker')
                                if biomarker is not None:
                                    self.channels.append(biomarker.text)
                                else:
                                    self.channels.append(f"Biomarker_{i}")
                                
                                # Extract resolution (only from first page)
                                if i == 0:
                                    scan_profile = root.find('ScanProfile')
                                    if scan_profile is not None:
                                        exp_v4 = scan_profile.find('ExperimentV4')
                                        if exp_v4 is not None:
                                            res_elem = exp_v4.find('Resolution_nm')
                                            if res_elem is not None:
                                                self.resolution_nm = float(res_elem.text)
                                                # Convert nm to µm
                                                self.resolution = self.resolution_nm / 1000.0
                            
                            except Exception as e:
                                print(f"Warning: Could not parse page {i} metadata: {e}")
                                self.channels.append(f"Biomarker_{i}")
                        else:
                            self.channels.append(f"Biomarker_{i}")
        
        except Exception as e:
            print(f"Warning: Could not load PhenoCycler metadata: {e}")
    
    def load_image(self, channel: Optional[int] = None) -> np.ndarray:
        """
        Load image data from QPTIFF.
        
        Args:
            channel: Channel index to load (default: 0)
            
        Returns:
            Image as numpy array (uint16)
        """
        if not tifffile:
            raise ImportError("tifffile is required for PhenoCycler data")
        
        if channel is None:
            channel = 0
        
        if channel in self._channel_data:
            return self._channel_data[channel]
        
        if not self.qptiff_path.exists():
            raise FileNotFoundError(f"PhenoCycler QPTIFF not found: {self.qptiff_path}")
        
        try:
            img = tifffile.imread(str(self.qptiff_path), key=channel)
            self._channel_data[channel] = img
            return img
        except Exception as e:
            raise ValueError(f"Failed to load channel {channel}: {e}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get PhenoCycler metadata.
        
        Returns:
            Dictionary with biomarkers, resolution, dimensions, etc.
        """
        meta = self.metadata.copy()
        meta['resolution_nm'] = self.resolution_nm
        meta['biomarkers'] = self.channels.copy()
        return meta
    
    def get_resolution(self) -> float:
        """
        Get PhenoCycler resolution in micrometers.
        
        Returns:
            Resolution in micrometers
        """
        return self.resolution
    
    def get_channels(self) -> List[str]:
        """
        Get list of biomarker names.
        
        Returns:
            List of biomarker names
        """
        return self.channels.copy()
    
    def generate_mask(self, **kwargs) -> np.ndarray:
        """
        Generate binary mask from PhenoCycler data.
        
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
        Validate PhenoCycler data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, msg = super().validate()
        if not is_valid:
            return is_valid, msg
        
        if not self.qptiff_path.exists():
            return False, f"PhenoCycler QPTIFF not found: {self.qptiff_path}"
        
        if not tifffile:
            return False, "tifffile library not installed"
        
        return True, ""

