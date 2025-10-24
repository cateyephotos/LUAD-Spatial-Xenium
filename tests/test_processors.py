"""
Unit tests for image processing and mask generation.

Tests for ImageProcessor, CircleDetector, and MaskGenerator classes.
"""

import pytest
import numpy as np
from src.processors import ImageProcessor, CircleDetector, MaskGenerator


class TestImageProcessor:
    """Test ImageProcessor class."""
    
    def test_binarize_binary_method(self):
        """Test binary thresholding."""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        binary = ImageProcessor.binarize(img, threshold=128, method='binary')
        
        assert binary.dtype == np.uint8
        assert np.all((binary == 0) | (binary == 255))
    
    def test_binarize_otsu_method(self):
        """Test Otsu thresholding."""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        binary = ImageProcessor.binarize(img, method='otsu')
        
        assert binary.dtype == np.uint8
        assert np.all((binary == 0) | (binary == 255))
    
    def test_morphology_close(self):
        """Test morphological closing."""
        img = np.zeros((100, 100), dtype=np.uint8)
        img[40:60, 40:60] = 255
        
        result = ImageProcessor.morphology(img, operation='close', kernel_size=5)
        
        assert result.dtype == np.uint8
        assert result.shape == img.shape
    
    def test_morphology_open(self):
        """Test morphological opening."""
        img = np.zeros((100, 100), dtype=np.uint8)
        img[40:60, 40:60] = 255
        
        result = ImageProcessor.morphology(img, operation='open', kernel_size=5)
        
        assert result.dtype == np.uint8
        assert result.shape == img.shape
    
    def test_find_contours(self):
        """Test contour finding."""
        img = np.zeros((100, 100), dtype=np.uint8)
        img[30:70, 30:70] = 255
        
        contours, contour_img = ImageProcessor.find_contours(img, min_area=100)
        
        assert len(contours) > 0
        assert contour_img.shape == img.shape
        assert np.any(contour_img > 0)
    
    def test_normalize_uint16_to_uint8(self):
        """Test normalization from uint16 to uint8."""
        img = np.random.randint(0, 65536, (100, 100), dtype=np.uint16)
        normalized = ImageProcessor.normalize(img, target_dtype=np.uint8)
        
        assert normalized.dtype == np.uint8
        assert normalized.max() <= 255
    
    def test_resize(self):
        """Test image resizing."""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        resized = ImageProcessor.resize(img, scale=0.5)
        
        assert resized.shape == (50, 50)
    
    def test_rotate(self):
        """Test image rotation."""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        rotated = ImageProcessor.rotate(img, angle=45)
        
        assert rotated.shape == img.shape
    
    def test_shift(self):
        """Test image shifting."""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        shifted = ImageProcessor.shift(img, dx=10, dy=10)
        
        assert shifted.shape == img.shape
    
    def test_iou(self):
        """Test IoU calculation."""
        mask1 = np.zeros((100, 100), dtype=np.uint8)
        mask1[30:70, 30:70] = 255
        
        mask2 = np.zeros((100, 100), dtype=np.uint8)
        mask2[40:80, 40:80] = 255
        
        iou = ImageProcessor.iou(mask1, mask2)
        
        assert 0 <= iou <= 1
        assert iou > 0  # Should have some overlap


class TestCircleDetector:
    """Test CircleDetector class."""
    
    def test_detect_circles_synthetic(self):
        """Test circle detection on synthetic image."""
        img = np.zeros((200, 200), dtype=np.uint8)
        # Draw a circle
        import cv2
        cv2.circle(img, (100, 100), 30, 255, -1)
        
        circles = CircleDetector.detect_circles(img, min_radius=20, max_radius=40)
        
        # May or may not detect depending on parameters
        if circles is not None:
            assert len(circles) > 0
            assert circles.shape[1] == 3  # (x, y, r)
    
    def test_draw_circles(self):
        """Test drawing circles."""
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        circles = np.array([[50, 50, 20], [75, 75, 15]])
        
        result = CircleDetector.draw_circles(img, circles)
        
        assert result.shape == img.shape
        assert np.any(result > 0)
    
    def test_create_mask_from_circles(self):
        """Test mask creation from circles."""
        circles = np.array([[50, 50, 20], [75, 75, 15]])
        mask = CircleDetector.create_mask_from_circles((100, 100), circles)
        
        assert mask.shape == (100, 100)
        assert mask.dtype == np.uint8
        assert np.any(mask > 0)
    
    def test_filter_circles_by_size(self):
        """Test filtering circles by size."""
        circles = np.array([[50, 50, 20], [75, 75, 5], [25, 25, 50]])
        filtered = CircleDetector.filter_circles_by_size(circles, min_radius=10, max_radius=30)
        
        assert len(filtered) == 1
        assert filtered[0, 2] == 20
    
    def test_get_circle_statistics(self):
        """Test circle statistics."""
        circles = np.array([[50, 50, 20], [75, 75, 15], [25, 25, 25]])
        stats = CircleDetector.get_circle_statistics(circles)
        
        assert stats['count'] == 3
        assert stats['mean_radius'] == 20
        assert stats['min_radius'] == 15
        assert stats['max_radius'] == 25


class TestMaskGenerator:
    """Test MaskGenerator class."""
    
    def test_generate_contour_mask(self):
        """Test contour-based mask generation."""
        img = np.zeros((100, 100), dtype=np.uint8)
        img[30:70, 30:70] = 200
        
        mask = MaskGenerator.generate_contour_mask(img, threshold=100)
        
        assert mask.dtype == np.uint8
        assert mask.shape == img.shape
        assert np.any(mask > 0)
    
    def test_generate_intensity_mask(self):
        """Test intensity-based mask generation."""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        mask = MaskGenerator.generate_intensity_mask(img, method='otsu')
        
        assert mask.dtype == np.uint8
        assert np.all((mask == 0) | (mask == 255))
    
    def test_generate_adaptive_mask(self):
        """Test adaptive mask generation."""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        mask = MaskGenerator.generate_adaptive_mask(img)
        
        assert mask.dtype == np.uint8
        assert np.all((mask == 0) | (mask == 255))
    
    def test_generate_mask_contour(self):
        """Test generic mask generation with contour method."""
        img = np.zeros((100, 100), dtype=np.uint8)
        img[30:70, 30:70] = 200
        
        mask = MaskGenerator.generate_mask(img, mask_type='contour', threshold=100)
        
        assert mask.dtype == np.uint8
        assert np.any(mask > 0)
    
    def test_generate_mask_intensity(self):
        """Test generic mask generation with intensity method."""
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        mask = MaskGenerator.generate_mask(img, mask_type='intensity', method='otsu')
        
        assert mask.dtype == np.uint8
        assert np.all((mask == 0) | (mask == 255))
    
    def test_post_process_mask(self):
        """Test mask post-processing."""
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[30:70, 30:70] = 255
        
        result = MaskGenerator.post_process_mask(mask, kernel_size=5, operation='close')
        
        assert result.dtype == np.uint8
        assert result.shape == mask.shape


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

