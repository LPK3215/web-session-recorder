"""Configuration Manager for loading and managing YAML configuration files."""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Singleton configuration manager for loading YAML files."""
    
    _instance: Optional['ConfigManager'] = None
    _configs: Dict[str, Dict[str, Any]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all_configs()
        return cls._instance
    
    def _load_all_configs(self) -> None:
        """Load all configuration files from config/ directory."""
        # Get the backend directory (parent of app/)
        backend_dir = Path(__file__).parent.parent.parent
        config_dir = backend_dir / "config"
        if not config_dir.exists():
            raise FileNotFoundError(f"Configuration directory not found: {config_dir}")
        
        config_files = [
            "app.yaml",
            "browser.yaml",
            "recorder.yaml",
            "locators.yaml"
        ]
        
        for file_name in config_files:
            file_path = config_dir / file_name
            if file_path.exists():
                self._configs[file_name.replace('.yaml', '')] = self._load_yaml(file_path)
                logger.info(f"Loaded configuration: {file_name}")
            else:
                logger.warning(f"Configuration file not found: {file_name}")
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse a YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
                return content if content is not None else {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    def get(self, config_name: str, key_path: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            key_path: Dot-separated path to nested key (e.g., "server.host")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if config_name not in self._configs:
            logger.warning(f"Configuration not found: {config_name}")
            return default
        
        config = self._configs[config_name]
        
        if key_path is None:
            return config
        
        # Navigate nested keys
        keys = key_path.split('.')
        value = config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded configurations."""
        return self._configs.copy()
    
    def reload(self) -> None:
        """Reload all configuration files."""
        self._configs.clear()
        self._load_all_configs()
        logger.info("All configurations reloaded")
    
    def save_config(self, config_name: str, content: str) -> bool:
        """
        Save configuration content to file.
        
        Args:
            config_name: Name of config file (without .yaml extension)
            content: YAML content as string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate YAML syntax
            parsed = yaml.safe_load(content)
            if parsed is None:
                parsed = {}
            
            # Write to file
            backend_dir = Path(__file__).parent.parent.parent
            config_dir = backend_dir / "config"
            file_path = config_dir / f"{config_name}.yaml"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update in-memory config
            self._configs[config_name] = parsed
            logger.info(f"Configuration saved: {config_name}.yaml")
            return True
            
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML syntax: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False


# Global config instance
config = ConfigManager()
