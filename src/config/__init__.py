"""
Configuration management system for spatial omics processing.

This module provides configuration loading and parameter management
for the spatial omics integration pipeline.

Classes:
    ConfigLoader: YAML configuration file loader
    Parameters: Parameter management and validation
"""

from .config_loader import ConfigLoader
from .defaults import DEFAULT_PARAMETERS, get_default_config

__all__ = [
    "ConfigLoader",
    "DEFAULT_PARAMETERS",
    "get_default_config",
]

