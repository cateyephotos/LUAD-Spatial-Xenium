"""
Default parameters for spatial omics processing.

This module defines default parameters for mask generation, alignment,
and analysis operations.
"""

from typing import Dict, Any


# Default parameters for all processing steps
DEFAULT_PARAMETERS: Dict[str, Any] = {
    # Mask Generation Parameters
    "mask_generation": {
        "binarization": {
            "threshold": 10,
            "method": "binary",  # binary, otsu, adaptive
        },
        "morphology": {
            "kernel_size": 5,
            "dilate_iterations": 1,
            "erode_iterations": 1,
            "operation": "close",  # close, open, gradient
        },
        "contour": {
            "min_area": 100,
            "max_area": 1000000,
            "approximation": "simple",
        },
        "circle_detection": {
            "method": "hough",
            "min_radius": 10,
            "max_radius": 10,
            "param1": 100,
            "param2": 30,
            "min_dist": 20,
        },
    },
    
    # Alignment Parameters
    "alignment": {
        "zoom_range": [0.8, 1.2],
        "zoom_step": 0.05,
        "shift_range": [-50, 50],
        "shift_step": 5,
        "rotation_range": [-45, 45],
        "rotation_step": 5,
        "fitness_metric": "iou",  # iou, mi, cc
        "search_strategy": "exhaustive",  # exhaustive, coarse_to_fine, gradient
    },
    
    # Analysis Parameters
    "analysis": {
        "correlation": {
            "method": "pearson",  # pearson, spearman, kendall
            "min_overlap": 0.1,
        },
        "clustering": {
            "method": "kmeans",  # kmeans, hierarchical, dbscan, leiden
            "n_clusters": 5,
            "random_state": 42,
        },
        "roi_extraction": {
            "min_size": 100,
            "max_size": 10000,
        },
    },
    
    # Data Format Specific Parameters
    "visium": {
        "image_file": "tissue_hires_image.png",
        "metadata_dir": "spatial",
    },
    
    "xenium": {
        "image_file": "image.ome.tiff",
        "default_channel": 0,
    },
    
    "phenocycler": {
        "default_channel": 0,
    },
    
    "ometiff": {
        "default_channel": 0,
    },
}


def get_default_config(modality: str = None) -> Dict[str, Any]:
    """
    Get default configuration.
    
    Args:
        modality: Optional modality to get modality-specific defaults
        
    Returns:
        Dictionary of default parameters
    """
    config = DEFAULT_PARAMETERS.copy()
    
    if modality:
        modality_lower = modality.lower()
        if modality_lower in config:
            config["modality_specific"] = config[modality_lower]
    
    return config


def update_defaults(updates: Dict[str, Any]) -> None:
    """
    Update default parameters.
    
    Args:
        updates: Dictionary of updates to apply
    """
    def deep_update(d: Dict, u: Dict) -> None:
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = d.get(k, {})
                deep_update(d[k], v)
            else:
                d[k] = v
    
    deep_update(DEFAULT_PARAMETERS, updates)

