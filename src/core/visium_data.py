"""
Visium spatial transcriptomics data handler.

This module implements the SpatialData interface for 10x Genomics Visium data,
which consists of H&E images and SpaceRanger output files.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import numpy as np
import cv2
from .spatial_data import SpatialData


class VisiumData(SpatialData):
    """
    Handler for 10x Genomics Visium spatial transcriptomics data.
    
    Visium data consists of:
    - H&E image (PNG)
    - SpaceRanger output (JSON, CSV files)
    - Tissue positions and fiducial markers
    
    Attributes:
        image_path (Path): Path to H&E image file
        metadata_dir (Path): Directory containing SpaceRanger output
    """
    
    def __init__(self, data_path: str, image_filename: str = "tissue_hires_image.png"):
        """
        Initialize VisiumData instance.
        
        Args:
            data_path: Path to Visium data directory
            image_filename: Name of H&E image file (default: tissue_hires_image.png)
        """
        super().__init__(data_path, modality="visium")
        self.image_path = self.data_path / image_filename
        self.metadata_dir = self.data_path / "spatial"
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata from SpaceRanger output files."""
        try:
            # Load scale factors
            scalefactors_file = self.metadata_dir / "scalefactors_json.json"
            if scalefactors_file.exists():
                with open(scalefactors_file, 'r') as f:
                    scalefactors = json.load(f)
                    self.metadata['scalefactors'] = scalefactors
                    
                    # Extract resolution
                    if 'tissue_hires_scalef' in scalefactors:
                        self.resolution = 1.0 / scalefactors['tissue_hires_scalef']
            
            # Load tissue positions
            tissue_positions_file = self.metadata_dir / "tissue_positions_list.csv"
            if tissue_positions_file.exists():
                self.metadata['tissue_positions_file'] = str(tissue_positions_file)
            
            # Load fiducial positions
            fiducial_file = self.metadata_dir / "fiducial_positions_list.txt"
            if fiducial_file.exists():
                self.metadata['fiducial_positions_file'] = str(fiducial_file)
        
        except Exception as e:
            print(f"Warning: Could not load Visium metadata: {e}")
    
    def load_image(self, channel: Optional[int] = None) -> np.ndarray:
        """
        Load H&E image.
        
        Args:
            channel: Ignored for Visium (single-channel H&E)
            
        Returns:
            Image as numpy array (BGR format from OpenCV)
        """
        if self._image_cache is not None:
            return self._image_cache
        
        if not self.image_path.exists():
            raise FileNotFoundError(f"Visium image not found: {self.image_path}")
        
        img = cv2.imread(str(self.image_path))
        if img is None:
            raise ValueError(f"Failed to load image: {self.image_path}")
        
        self._image_cache = img
        return img
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get Visium metadata.
        
        Returns:
            Dictionary with scalefactors, tissue positions, etc.
        """
        return self.metadata.copy()
    
    def get_resolution(self) -> float:
        """
        Get Visium resolution in micrometers.
        
        Returns:
            Resolution in micrometers
        """
        return self.resolution
    
    def get_channels(self) -> List[str]:
        """
        Get available channels (H&E only).
        
        Returns:
            List with single channel name
        """
        return ["H&E"]
    
    def generate_mask(self, **kwargs) -> np.ndarray:
        """
        Generate binary mask from H&E image using circle detection.
        
        Args:
            threshold: Binary threshold (default: 10)
            min_radius: Minimum circle radius (default: 10)
            max_radius: Maximum circle radius (default: 10)
            
        Returns:
            Binary mask (uint8, values 0 or 255)
        """
        img = self.load_image()
        
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Apply threshold
        threshold = kwargs.get('threshold', 10)
        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        # Create mask
        mask = np.zeros_like(binary)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw contours on mask
        cv2.drawContours(mask, contours, -1, 255, -1)
        
        return mask
    
    def validate(self) -> tuple:
        """
        Validate Visium data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, msg = super().validate()
        if not is_valid:
            return is_valid, msg
        
        if not self.image_path.exists():
            return False, f"H&E image not found: {self.image_path}"
        
        if not self.metadata_dir.exists():
            return False, f"Metadata directory not found: {self.metadata_dir}"
        
        return True, ""

