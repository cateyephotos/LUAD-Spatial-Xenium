"""
Abstract base class for spatial omics data.

This module defines the SpatialData abstract base class that all spatial data
format implementations must inherit from. It provides a unified interface for
loading, processing, and analyzing spatial omics data from different sources.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import numpy as np


class SpatialData(ABC):
    """
    Abstract base class for spatial omics data.
    
    All spatial data format implementations (Visium, Xenium, PhenoCycler, etc.)
    must inherit from this class and implement the required abstract methods.
    
    Attributes:
        data_path (Path): Path to the data file or directory
        modality (str): Data modality (e.g., 'visium', 'xenium', 'phenocycler')
        metadata (Dict): Metadata extracted from the data
        resolution (float): Physical resolution in micrometers
    """
    
    def __init__(self, data_path: str, modality: str):
        """
        Initialize SpatialData instance.
        
        Args:
            data_path: Path to data file or directory
            modality: Data modality identifier
        """
        self.data_path = Path(data_path)
        self.modality = modality
        self.metadata: Dict[str, Any] = {}
        self.resolution: float = 1.0
        self._image_cache: Optional[np.ndarray] = None
        self._mask_cache: Optional[np.ndarray] = None
    
    @abstractmethod
    def load_image(self, channel: Optional[int] = None) -> np.ndarray:
        """
        Load image data from the data source.
        
        Args:
            channel: Optional channel index for multi-channel data
            
        Returns:
            Image as numpy array (uint8 or uint16)
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Extract and return metadata from the data source.
        
        Returns:
            Dictionary containing metadata (resolution, channels, dimensions, etc.)
        """
        pass
    
    @abstractmethod
    def get_resolution(self) -> float:
        """
        Get physical resolution in micrometers.
        
        Returns:
            Resolution in micrometers
        """
        pass
    
    @abstractmethod
    def get_channels(self) -> List[str]:
        """
        Get list of available channels.
        
        Returns:
            List of channel names or identifiers
        """
        pass
    
    @abstractmethod
    def generate_mask(self, **kwargs) -> np.ndarray:
        """
        Generate binary mask from the data.
        
        Args:
            **kwargs: Format-specific parameters for mask generation
            
        Returns:
            Binary mask as numpy array (uint8, values 0 or 255)
        """
        pass
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate that the data source is accessible and valid.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.data_path.exists():
            return False, f"Data path does not exist: {self.data_path}"
        return True, ""
    
    def clear_cache(self) -> None:
        """Clear cached image and mask data."""
        self._image_cache = None
        self._mask_cache = None
    
    def get_image_shape(self) -> Tuple[int, int]:
        """
        Get image dimensions (height, width).
        
        Returns:
            Tuple of (height, width)
        """
        img = self.load_image()
        return img.shape[:2]
    
    def get_image_dtype(self) -> np.dtype:
        """
        Get image data type.
        
        Returns:
            NumPy dtype of image data
        """
        img = self.load_image()
        return img.dtype
    
    def __repr__(self) -> str:
        """String representation of SpatialData instance."""
        return (
            f"{self.__class__.__name__}("
            f"modality='{self.modality}', "
            f"path='{self.data_path}', "
            f"resolution={self.resolution}µm)"
        )

