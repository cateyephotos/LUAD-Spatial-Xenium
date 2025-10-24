"""
Core data abstraction layer for spatial omics data formats.

This module provides abstract base classes and implementations for handling
different spatial omics data formats (Visium, Xenium, PhenoCycler, Generic OME-TIFF).

Classes:
    SpatialData: Abstract base class for spatial data
    VisiumData: Implementation for Visium data
    XeniumData: Implementation for Xenium OME-TIFF data
    OMETiffData: Implementation for generic OME-TIFF data
    PhenoCyclerData: Implementation for PhenoCycler QPTIFF data

Functions:
    create_spatial_data: Factory function to create appropriate data handler
    detect_modality: Detect data modality from path
    list_supported_formats: List all supported formats
"""

from .spatial_data import SpatialData
from .visium_data import VisiumData
from .xenium_data import XeniumData
from .ometiff_data import OMETiffData
from .phenocycler_data import PhenoCyclerData
from .data_factory import create_spatial_data, detect_modality, list_supported_formats

__all__ = [
    "SpatialData",
    "VisiumData",
    "XeniumData",
    "OMETiffData",
    "PhenoCyclerData",
    "create_spatial_data",
    "detect_modality",
    "list_supported_formats",
]

