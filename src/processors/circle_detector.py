"""
Circle detection for Visium fiducial markers.

This module provides circle detection utilities specifically for identifying
Visium fiducial markers in H&E images.
"""

from typing import List, Tuple, Optional
import numpy as np
import cv2


class CircleDetector:
    """
    Detect circles in images using Hough Circle Transform.
    
    Primarily used for detecting Visium fiducial markers in H&E images.
    """
    
    @staticmethod
    def detect_circles(image: np.ndarray, 
                      min_radius: int = 10,
                      max_radius: int = 10,
                      param1: int = 100,
                      param2: int = 30,
                      min_dist: int = 20) -> Optional[np.ndarray]:
        """
        Detect circles using Hough Circle Transform.
        
        Args:
            image: Input image (grayscale or BGR)
            min_radius: Minimum circle radius
            max_radius: Maximum circle radius
            param1: Upper threshold for Canny edge detection
            param2: Accumulator threshold for circle center
            min_dist: Minimum distance between circle centers
            
        Returns:
            Array of detected circles (x, y, radius) or None if no circles found
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=min_dist,
            param1=param1,
            param2=param2,
            minRadius=min_radius,
            maxRadius=max_radius
        )
        
        if circles is None:
            return None
        
        # Convert to integer coordinates
        circles = np.uint16(np.around(circles))
        return circles[0]
    
    @staticmethod
    def draw_circles(image: np.ndarray, circles: np.ndarray,
                    color: Tuple[int, int, int] = (0, 255, 0),
                    thickness: int = 2) -> np.ndarray:
        """
        Draw detected circles on image.
        
        Args:
            image: Input image
            circles: Array of circles (x, y, radius)
            color: Circle color (BGR)
            thickness: Line thickness
            
        Returns:
            Image with drawn circles
        """
        result = image.copy()
        
        for (x, y, r) in circles:
            # Draw circle outline
            cv2.circle(result, (x, y), r, color, thickness)
            # Draw center
            cv2.circle(result, (x, y), 2, color, -1)
        
        return result
    
    @staticmethod
    def create_mask_from_circles(image_shape: Tuple[int, int],
                                circles: np.ndarray) -> np.ndarray:
        """
        Create binary mask from detected circles.
        
        Args:
            image_shape: Shape of output mask (height, width)
            circles: Array of circles (x, y, radius)
            
        Returns:
            Binary mask with circles filled
        """
        mask = np.zeros(image_shape, dtype=np.uint8)
        
        for (x, y, r) in circles:
            cv2.circle(mask, (x, y), r, 255, -1)
        
        return mask
    
    @staticmethod
    def filter_circles_by_size(circles: np.ndarray,
                              min_radius: int = 5,
                              max_radius: int = 50) -> np.ndarray:
        """
        Filter circles by radius.
        
        Args:
            circles: Array of circles (x, y, radius)
            min_radius: Minimum radius
            max_radius: Maximum radius
            
        Returns:
            Filtered circles
        """
        if circles is None or len(circles) == 0:
            return None
        
        filtered = []
        for (x, y, r) in circles:
            if min_radius <= r <= max_radius:
                filtered.append([x, y, r])
        
        if len(filtered) == 0:
            return None
        
        return np.array(filtered)
    
    @staticmethod
    def filter_circles_by_distance(circles: np.ndarray,
                                  min_distance: int = 20) -> np.ndarray:
        """
        Filter overlapping circles by distance.
        
        Args:
            circles: Array of circles (x, y, radius)
            min_distance: Minimum distance between circle centers
            
        Returns:
            Filtered circles
        """
        if circles is None or len(circles) <= 1:
            return circles
        
        filtered = [circles[0]]
        
        for i in range(1, len(circles)):
            x1, y1, r1 = circles[i]
            is_valid = True
            
            for x2, y2, r2 in filtered:
                dist = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                if dist < min_distance:
                    is_valid = False
                    break
            
            if is_valid:
                filtered.append(circles[i])
        
        return np.array(filtered)
    
    @staticmethod
    def get_circle_statistics(circles: np.ndarray) -> dict:
        """
        Get statistics about detected circles.
        
        Args:
            circles: Array of circles (x, y, radius)
            
        Returns:
            Dictionary with statistics
        """
        if circles is None or len(circles) == 0:
            return {
                "count": 0,
                "mean_radius": 0,
                "min_radius": 0,
                "max_radius": 0,
            }
        
        radii = circles[:, 2]
        
        return {
            "count": len(circles),
            "mean_radius": float(np.mean(radii)),
            "min_radius": float(np.min(radii)),
            "max_radius": float(np.max(radii)),
            "std_radius": float(np.std(radii)),
        }

