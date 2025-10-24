"""
Mask generation from images.

This module provides utilities for generating binary masks from various
image types and data formats.
"""

from typing import Optional, Dict, Any
import numpy as np
from .image_processor import ImageProcessor
from .circle_detector import CircleDetector


class MaskGenerator:
    """
    Generate binary masks from images.
    
    Supports multiple mask generation strategies for different data types.
    """
    
    @staticmethod
    def generate_visium_mask(image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Generate mask for Visium H&E image.
        
        Uses circle detection to identify fiducial markers.
        
        Args:
            image: H&E image
            **kwargs: Parameters (threshold, min_radius, max_radius, etc.)
            
        Returns:
            Binary mask
        """
        # Get parameters
        threshold = kwargs.get('threshold', 10)
        min_radius = kwargs.get('min_radius', 10)
        max_radius = kwargs.get('max_radius', 10)
        param1 = kwargs.get('param1', 100)
        param2 = kwargs.get('param2', 30)
        min_dist = kwargs.get('min_dist', 20)
        
        # Convert to grayscale
        if len(image.shape) == 3:
            import cv2
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Detect circles
        circles = CircleDetector.detect_circles(
            gray,
            min_radius=min_radius,
            max_radius=max_radius,
            param1=param1,
            param2=param2,
            min_dist=min_dist
        )
        
        if circles is None or len(circles) == 0:
            # Fallback to contour-based mask
            return MaskGenerator.generate_contour_mask(image, threshold=threshold)
        
        # Create mask from circles
        mask = CircleDetector.create_mask_from_circles(gray.shape, circles)
        
        return mask
    
    @staticmethod
    def generate_contour_mask(image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Generate mask using contour detection.
        
        Args:
            image: Input image
            **kwargs: Parameters (threshold, min_area, max_area, etc.)
            
        Returns:
            Binary mask
        """
        # Get parameters
        threshold = kwargs.get('threshold', 10)
        min_area = kwargs.get('min_area', 100)
        max_area = kwargs.get('max_area', 1000000)
        kernel_size = kwargs.get('kernel_size', 5)
        dilate_iter = kwargs.get('dilate_iterations', 1)
        erode_iter = kwargs.get('erode_iterations', 1)
        
        # Binarize
        binary = ImageProcessor.binarize(image, threshold=threshold, method='binary')
        
        # Morphological operations
        binary = ImageProcessor.morphology(binary, operation='close',
                                          kernel_size=kernel_size,
                                          iterations=dilate_iter)
        
        # Find contours
        contours, mask = ImageProcessor.find_contours(binary, min_area=min_area,
                                                      max_area=max_area)
        
        return mask
    
    @staticmethod
    def generate_intensity_mask(image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Generate mask using intensity thresholding.
        
        Used for fluorescence images (Xenium, PhenoCycler).
        
        Args:
            image: Input image
            **kwargs: Parameters (threshold, method, etc.)
            
        Returns:
            Binary mask
        """
        # Get parameters
        threshold = kwargs.get('threshold', None)
        method = kwargs.get('method', 'otsu')
        
        # Normalize if needed
        if image.dtype == np.uint16:
            image = ImageProcessor.normalize(image, target_dtype=np.uint8)
        
        # Binarize
        binary = ImageProcessor.binarize(image, threshold=threshold, method=method)
        
        return binary
    
    @staticmethod
    def generate_adaptive_mask(image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Generate mask using adaptive thresholding.
        
        Args:
            image: Input image
            **kwargs: Parameters (kernel_size, etc.)
            
        Returns:
            Binary mask
        """
        # Get parameters
        kernel_size = kwargs.get('kernel_size', 11)
        
        # Normalize if needed
        if image.dtype == np.uint16:
            image = ImageProcessor.normalize(image, target_dtype=np.uint8)
        
        # Convert to grayscale
        if len(image.shape) == 3:
            import cv2
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Adaptive threshold
        binary = ImageProcessor.binarize(gray, method='adaptive')
        
        return binary
    
    @staticmethod
    def generate_mask(image: np.ndarray, mask_type: str = 'contour',
                     **kwargs) -> np.ndarray:
        """
        Generate mask using specified method.
        
        Args:
            image: Input image
            mask_type: Type of mask ('visium', 'contour', 'intensity', 'adaptive')
            **kwargs: Method-specific parameters
            
        Returns:
            Binary mask
        """
        if mask_type == 'visium':
            return MaskGenerator.generate_visium_mask(image, **kwargs)
        elif mask_type == 'contour':
            return MaskGenerator.generate_contour_mask(image, **kwargs)
        elif mask_type == 'intensity':
            return MaskGenerator.generate_intensity_mask(image, **kwargs)
        elif mask_type == 'adaptive':
            return MaskGenerator.generate_adaptive_mask(image, **kwargs)
        else:
            raise ValueError(f"Unknown mask type: {mask_type}")
    
    @staticmethod
    def post_process_mask(mask: np.ndarray, **kwargs) -> np.ndarray:
        """
        Post-process mask with morphological operations.
        
        Args:
            mask: Binary mask
            **kwargs: Parameters (kernel_size, dilate_iterations, erode_iterations)
            
        Returns:
            Post-processed mask
        """
        # Get parameters
        kernel_size = kwargs.get('kernel_size', 5)
        dilate_iter = kwargs.get('dilate_iterations', 1)
        erode_iter = kwargs.get('erode_iterations', 1)
        operation = kwargs.get('operation', 'close')
        
        # Apply morphological operations
        result = ImageProcessor.morphology(mask, operation=operation,
                                          kernel_size=kernel_size,
                                          iterations=max(dilate_iter, erode_iter))
        
        return result

