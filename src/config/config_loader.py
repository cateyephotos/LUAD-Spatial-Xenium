"""
Configuration loader for YAML-based parameter files.

This module provides utilities for loading and managing configuration
from YAML files.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json

try:
    import yaml
except ImportError:
    yaml = None

from .defaults import DEFAULT_PARAMETERS, get_default_config


class ConfigLoader:
    """
    Load and manage configuration from YAML files.
    
    Attributes:
        config_path (Path): Path to configuration file
        config (Dict): Loaded configuration
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigLoader.
        
        Args:
            config_path: Optional path to YAML configuration file
        """
        self.config_path = Path(config_path) if config_path else None
        self.config: Dict[str, Any] = get_default_config()
        
        if self.config_path and self.config_path.exists():
            self.load_yaml(str(self.config_path))
    
    def load_yaml(self, filepath: str) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            filepath: Path to YAML file
            
        Raises:
            ImportError: If PyYAML is not installed
            FileNotFoundError: If file does not exist
            ValueError: If YAML is invalid
        """
        if not yaml:
            raise ImportError("PyYAML is required. Install with: pip install pyyaml")
        
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                loaded_config = yaml.safe_load(f)
            
            if loaded_config:
                self._deep_update(self.config, loaded_config)
        
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {filepath}: {e}")
    
    def load_json(self, filepath: str) -> None:
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If JSON is invalid
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                loaded_config = json.load(f)
            
            if loaded_config:
                self._deep_update(self.config, loaded_config)
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}")
    
    def save_yaml(self, filepath: str) -> None:
        """
        Save configuration to YAML file.
        
        Args:
            filepath: Path to save YAML file
            
        Raises:
            ImportError: If PyYAML is not installed
        """
        if not yaml:
            raise ImportError("PyYAML is required. Install with: pip install pyyaml")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def save_json(self, filepath: str) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Key path (e.g., 'alignment.zoom_range')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot-notation key.
        
        Args:
            key: Key path (e.g., 'alignment.zoom_range')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get entire configuration.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = get_default_config()
    
    @staticmethod
    def _deep_update(d: Dict, u: Dict) -> None:
        """
        Recursively update dictionary.
        
        Args:
            d: Dictionary to update
            u: Dictionary with updates
        """
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = d.get(k, {})
                ConfigLoader._deep_update(d[k], v)
            else:
                d[k] = v

