"""
Caching Utilities for Streamlit Application

Provides decorators and utilities for caching expensive operations.
Separates data caching from resource caching for optimal performance.

Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md - Caching Strategy
"""

import streamlit as st
from functools import wraps
from typing import Callable, Any, Optional
import hashlib


# ============================================================================
# DATA CACHING DECORATORS
# ============================================================================

def cache_image_data(func: Callable) -> Callable:
    """
    Cache expensive image loading operations.
    
    Use @cache_image_data for:
    - Loading TIFF/PNG files
    - Image preprocessing
    - Mask generation
    
    Invalidates when function arguments change.
    
    Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md - @st.cache_data
    """
    @st.cache_data
    def cached_func(*args, **kwargs):
        return func(*args, **kwargs)
    return cached_func


def cache_computation(func: Callable) -> Callable:
    """
    Cache expensive computational operations.
    
    Use @cache_computation for:
    - Alignment calculations
    - Correlation analysis
    - Clustering operations
    
    Invalidates when function arguments change.
    """
    @st.cache_data
    def cached_func(*args, **kwargs):
        return func(*args, **kwargs)
    return cached_func


# ============================================================================
# RESOURCE CACHING DECORATORS
# ============================================================================

def cache_model(func: Callable) -> Callable:
    """
    Cache global resources like ML models.
    
    Use @cache_model for:
    - ML model initialization
    - Database connections
    - Configuration loaders
    
    Never invalidates (persists for app lifetime).
    
    Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md - @st.cache_resource
    """
    @st.cache_resource
    def cached_func(*args, **kwargs):
        return func(*args, **kwargs)
    return cached_func


# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

def clear_all_caches() -> None:
    """Clear all Streamlit caches."""
    st.cache_data.clear()
    st.cache_resource.clear()


def clear_data_cache() -> None:
    """Clear only data cache (not resource cache)."""
    st.cache_data.clear()


def clear_resource_cache() -> None:
    """Clear only resource cache (not data cache)."""
    st.cache_resource.clear()


# ============================================================================
# CACHE STATISTICS
# ============================================================================

def get_cache_info() -> dict:
    """
    Get information about current cache state.
    
    Returns:
        dict: Cache statistics
    """
    return {
        "data_cache_info": "Use st.cache_data.clear() to clear",
        "resource_cache_info": "Use st.cache_resource.clear() to clear",
    }


# ============================================================================
# EXAMPLE CACHED FUNCTIONS
# ============================================================================

@st.cache_data
def load_image_file(filepath: str) -> Optional[Any]:
    """
    Load image file with caching.
    
    Args:
        filepath: Path to image file
        
    Returns:
        Image array or None if error
        
    Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md - File Upload
    """
    try:
        import cv2
        return cv2.imread(filepath)
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None


@st.cache_data
def load_tiff_file(filepath: str) -> Optional[Any]:
    """
    Load TIFF file with caching.
    
    Args:
        filepath: Path to TIFF file
        
    Returns:
        TIFF array or None if error
    """
    try:
        import tifffile
        with tifffile.TiffFile(filepath) as tif:
            return tif.asarray()
    except Exception as e:
        st.error(f"Error loading TIFF: {str(e)}")
        return None


@st.cache_resource
def init_config_loader():
    """
    Initialize configuration loader (cached resource).
    
    Returns:
        ConfigLoader instance
    """
    # Placeholder for actual config loader
    class ConfigLoader:
        def __init__(self):
            self.config = {}
        
        def load(self, filepath):
            # Load configuration from file
            pass
    
    return ConfigLoader()


# ============================================================================
# CACHE DECORATORS FOR COMMON OPERATIONS
# ============================================================================

def cached_mask_generation(func: Callable) -> Callable:
    """
    Decorator for cached mask generation.
    
    Use for expensive mask generation operations.
    """
    @st.cache_data
    def cached_func(*args, **kwargs):
        return func(*args, **kwargs)
    return cached_func


def cached_alignment(func: Callable) -> Callable:
    """
    Decorator for cached alignment operations.
    
    Use for expensive alignment calculations.
    """
    @st.cache_data
    def cached_func(*args, **kwargs):
        return func(*args, **kwargs)
    return cached_func


def cached_analysis(func: Callable) -> Callable:
    """
    Decorator for cached analysis operations.
    
    Use for expensive analysis calculations.
    """
    @st.cache_data
    def cached_func(*args, **kwargs):
        return func(*args, **kwargs)
    return cached_func


# ============================================================================
# CACHE INVALIDATION UTILITIES
# ============================================================================

def invalidate_cache_for_new_project() -> None:
    """
    Invalidate caches when starting a new project.
    
    Clears data cache but keeps resource cache.
    """
    st.cache_data.clear()


def invalidate_cache_for_new_parameters() -> None:
    """
    Invalidate caches when parameters change.
    
    Clears data cache but keeps resource cache.
    """
    st.cache_data.clear()


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

def get_cache_performance_tips() -> str:
    """
    Get performance optimization tips.
    
    Returns:
        str: Performance tips
    """
    return """
    **Cache Performance Tips:**
    
    1. Use @st.cache_data for expensive data operations
    2. Use @st.cache_resource for global resources
    3. Use forms to batch widget updates
    4. Avoid caching user-specific data
    5. Clear caches when starting new projects
    6. Monitor cache hits vs misses
    7. Use session state for workflow state
    
    Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md
    """

