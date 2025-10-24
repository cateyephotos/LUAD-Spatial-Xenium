"""
Image processing and mask generation utilities.

This module provides core image processing functions for spatial omics data,
including binarization, morphological operations, and mask generation.

Classes:
    ImageProcessor: Core image processing utilities
    CircleDetector: Circle detection for Visium data
    MaskGenerator: Mask generation from images
"""

from .image_processor import ImageProcessor
from .circle_detector import CircleDetector
from .mask_generator import MaskGenerator

__all__ = [
    "ImageProcessor",
    "CircleDetector",
    "MaskGenerator",
]

