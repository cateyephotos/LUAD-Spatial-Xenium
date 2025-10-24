"""
Factory for creating appropriate SpatialData instances.

This module provides a factory function to automatically detect and instantiate
the correct SpatialData subclass based on file type or explicit modality.
"""

from pathlib import Path
from typing import Optional, Union
from .spatial_data import SpatialData
from .visium_data import VisiumData
from .xenium_data import XeniumData
from .ometiff_data import OMETiffData
from .phenocycler_data import PhenoCyclerData


def create_spatial_data(
    data_path: str,
    modality: Optional[str] = None,
    **kwargs
) -> SpatialData:
    """
    Factory function to create appropriate SpatialData instance.
    
    Automatically detects data format based on file extension or modality.
    
    Args:
        data_path: Path to data file or directory
        modality: Optional modality hint ('visium', 'xenium', 'phenocycler', 'ometiff')
        **kwargs: Additional arguments passed to the data class
        
    Returns:
        Appropriate SpatialData subclass instance
        
    Raises:
        ValueError: If data format cannot be determined or is unsupported
        FileNotFoundError: If data path does not exist
    """
    data_path = Path(data_path)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data path does not exist: {data_path}")
    
    # If modality is explicitly provided, use it
    if modality:
        modality = modality.lower()
        
        if modality == "visium":
            return VisiumData(str(data_path), **kwargs)
        elif modality == "xenium":
            return XeniumData(str(data_path), **kwargs)
        elif modality == "phenocycler":
            return PhenoCyclerData(str(data_path), **kwargs)
        elif modality == "ometiff":
            return OMETiffData(str(data_path), **kwargs)
        else:
            raise ValueError(f"Unknown modality: {modality}")
    
    # Auto-detect based on file extension
    if data_path.is_file():
        suffix = data_path.suffix.lower()
        
        if suffix in [".qptiff", ".qptif"]:
            return PhenoCyclerData(str(data_path), **kwargs)
        elif suffix in [".tiff", ".tif", ".ome.tiff", ".ome.tif"]:
            # Try to determine if it's Xenium or generic OME-TIFF
            # For now, treat as generic OME-TIFF
            return OMETiffData(str(data_path), **kwargs)
        elif suffix in [".png", ".jpg", ".jpeg"]:
            # Likely Visium H&E image
            return VisiumData(str(data_path), **kwargs)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    # Auto-detect based on directory structure
    elif data_path.is_dir():
        # Check for Visium structure
        if (data_path / "spatial").exists():
            return VisiumData(str(data_path), **kwargs)
        
        # Check for OME-TIFF files
        tiff_files = list(data_path.glob("*.ome.tiff")) + \
                     list(data_path.glob("*.ome.tif")) + \
                     list(data_path.glob("*.tiff")) + \
                     list(data_path.glob("*.tif"))
        
        if tiff_files:
            # Check if it's QPTIFF (PhenoCycler)
            qptiff_files = list(data_path.glob("*.qptiff")) + \
                          list(data_path.glob("*.qptif"))
            
            if qptiff_files:
                return PhenoCyclerData(str(qptiff_files[0]), **kwargs)
            else:
                return OMETiffData(str(tiff_files[0]), **kwargs)
        
        raise ValueError(f"Could not determine data format in directory: {data_path}")
    
    else:
        raise ValueError(f"Invalid data path: {data_path}")


def detect_modality(data_path: str) -> str:
    """
    Detect data modality from path.
    
    Args:
        data_path: Path to data file or directory
        
    Returns:
        Detected modality string
        
    Raises:
        ValueError: If modality cannot be determined
    """
    data_path = Path(data_path)
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data path does not exist: {data_path}")
    
    if data_path.is_file():
        suffix = data_path.suffix.lower()
        
        if suffix in [".qptiff", ".qptif"]:
            return "phenocycler"
        elif suffix in [".tiff", ".tif", ".ome.tiff", ".ome.tif"]:
            return "ometiff"
        elif suffix in [".png", ".jpg", ".jpeg"]:
            return "visium"
    
    elif data_path.is_dir():
        if (data_path / "spatial").exists():
            return "visium"
        
        tiff_files = list(data_path.glob("*.qptiff")) + \
                     list(data_path.glob("*.qptif"))
        if tiff_files:
            return "phenocycler"
        
        tiff_files = list(data_path.glob("*.ome.tiff")) + \
                     list(data_path.glob("*.ome.tif")) + \
                     list(data_path.glob("*.tiff")) + \
                     list(data_path.glob("*.tif"))
        if tiff_files:
            return "ometiff"
    
    raise ValueError(f"Could not determine modality for: {data_path}")


def list_supported_formats() -> dict:
    """
    List all supported data formats.
    
    Returns:
        Dictionary with format information
    """
    return {
        "visium": {
            "description": "10x Genomics Visium spatial transcriptomics",
            "file_types": [".png", ".jpg"],
            "directory_structure": "Requires 'spatial' subdirectory",
        },
        "xenium": {
            "description": "10x Genomics Xenium spatial omics",
            "file_types": [".ome.tiff", ".ome.tif"],
            "directory_structure": "Single OME-TIFF file",
        },
        "phenocycler": {
            "description": "Akoya Biosciences PhenoCycler multiplexed immunofluorescence",
            "file_types": [".qptiff", ".qptif"],
            "directory_structure": "Single QPTIFF file",
        },
        "ometiff": {
            "description": "Generic OME-TIFF format",
            "file_types": [".tiff", ".tif"],
            "directory_structure": "Single OME-TIFF file",
        },
    }

