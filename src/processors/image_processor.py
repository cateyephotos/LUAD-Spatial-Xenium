"""
Core image processing utilities.

This module provides fundamental image processing operations used throughout
the spatial omics pipeline.
"""

from typing import Tuple, Optional
import numpy as np
import cv2


class ImageProcessor:
    """
    Core image processing utilities.
    
    Provides methods for image manipulation, filtering, and analysis.
    """
    
    @staticmethod
    def binarize(image: np.ndarray, threshold: Optional[int] = None, 
                 method: str = "binary") -> np.ndarray:
        """
        Binarize image using specified method.
        
        Args:
            image: Input image
            threshold: Threshold value (ignored for Otsu method)
            method: 'binary', 'otsu', or 'adaptive'
            
        Returns:
            Binary image (uint8, values 0 or 255)
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        if method == "otsu":
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == "adaptive":
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
        else:  # binary
            if threshold is None:
                threshold = 127
            _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        return binary
    
    @staticmethod
    def morphology(image: np.ndarray, operation: str = "close",
                   kernel_size: int = 5, iterations: int = 1) -> np.ndarray:
        """
        Apply morphological operations.
        
        Args:
            image: Binary image
            operation: 'open', 'close', 'dilate', 'erode', 'gradient'
            kernel_size: Size of morphological kernel
            iterations: Number of iterations
            
        Returns:
            Processed image
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        if operation == "open":
            result = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)
        elif operation == "close":
            result = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        elif operation == "dilate":
            result = cv2.dilate(image, kernel, iterations=iterations)
        elif operation == "erode":
            result = cv2.erode(image, kernel, iterations=iterations)
        elif operation == "gradient":
            result = cv2.morphologyEx(image, cv2.MORPH_GRADIENT, kernel, iterations=iterations)
        else:
            result = image
        
        return result
    
    @staticmethod
    def find_contours(image: np.ndarray, min_area: int = 100,
                      max_area: int = 1000000) -> Tuple[list, np.ndarray]:
        """
        Find contours in binary image.
        
        Args:
            image: Binary image
            min_area: Minimum contour area
            max_area: Maximum contour area
            
        Returns:
            Tuple of (filtered_contours, contour_image)
        """
        contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter by area
        filtered = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area <= area <= max_area:
                filtered.append(contour)
        
        # Create contour image
        contour_img = np.zeros_like(image)
        cv2.drawContours(contour_img, filtered, -1, 255, -1)
        
        return filtered, contour_img
    
    @staticmethod
    def normalize(image: np.ndarray, target_dtype: np.dtype = np.uint8) -> np.ndarray:
        """
        Normalize image to target data type.
        
        Args:
            image: Input image
            target_dtype: Target data type
            
        Returns:
            Normalized image
        """
        if image.dtype == target_dtype:
            return image
        
        if image.dtype == np.uint16 and target_dtype == np.uint8:
            return (image / 256).astype(np.uint8)
        elif image.dtype == np.uint32 and target_dtype == np.uint8:
            return (image / 65536).astype(np.uint8)
        elif image.dtype == np.uint8 and target_dtype == np.uint16:
            return (image * 256).astype(np.uint16)
        else:
            # Generic normalization
            img_min = image.min()
            img_max = image.max()
            if img_max > img_min:
                normalized = (image - img_min) / (img_max - img_min)
            else:
                normalized = image
            
            if target_dtype == np.uint8:
                return (normalized * 255).astype(np.uint8)
            elif target_dtype == np.uint16:
                return (normalized * 65535).astype(np.uint16)
            else:
                return normalized.astype(target_dtype)
    
    @staticmethod
    def resize(image: np.ndarray, scale: float) -> np.ndarray:
        """
        Resize image by scale factor.
        
        Args:
            image: Input image
            scale: Scale factor
            
        Returns:
            Resized image
        """
        return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    
    @staticmethod
    def rotate(image: np.ndarray, angle: float, center: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Rotate image.
        
        Args:
            image: Input image
            angle: Rotation angle in degrees
            center: Rotation center (default: image center)
            
        Returns:
            Rotated image
        """
        h, w = image.shape[:2]
        if center is None:
            center = (w // 2, h // 2)
        
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))
        
        return rotated
    
    @staticmethod
    def shift(image: np.ndarray, dx: int, dy: int) -> np.ndarray:
        """
        Shift image by (dx, dy).
        
        Args:
            image: Input image
            dx: Horizontal shift
            dy: Vertical shift
            
        Returns:
            Shifted image
        """
        h, w = image.shape[:2]
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        shifted = cv2.warpAffine(image, M, (w, h))
        
        return shifted
    
    @staticmethod
    def iou(mask1: np.ndarray, mask2: np.ndarray) -> float:
        """
        Calculate Intersection over Union (IoU).
        
        Args:
            mask1: First binary mask
            mask2: Second binary mask
            
        Returns:
            IoU value (0-1)
        """
        # Ensure same size
        h1, w1 = mask1.shape[:2]
        h2, w2 = mask2.shape[:2]
        h = min(h1, h2)
        w = min(w1, w2)
        
        m1 = mask1[:h, :w]
        m2 = mask2[:h, :w]
        
        # Binarize
        m1_bin = (m1 > 127).astype(np.uint8)
        m2_bin = (m2 > 127).astype(np.uint8)
        
        intersection = np.logical_and(m1_bin, m2_bin).sum()
        union = np.logical_or(m1_bin, m2_bin).sum()
        
        if union == 0:
            return 0.0
        
        return intersection / union

