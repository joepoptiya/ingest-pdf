"""Configuration module for the ingest_pdf package."""

from functools import lru_cache
from types import SimpleNamespace
from typing import Any

from config import reload_settings as global_reload_settings

# Import the global config loader
from config import settings as global_settings


class ConfigLoader:
    """Configuration loader for backward compatibility."""

    def __init__(self, config_path: str | None = None):
        """Initialize config loader.
        
        Args:
            config_path: Path to config file (ignored, uses global config)
        """
        # For backward compatibility, but we use global config
        pass

    def stop_watcher(self) -> None:
        """Stop config watcher (placeholder for compatibility)."""
        pass


# Global config loader instance
config_loader = ConfigLoader()


def _dict_to_namespace(d: dict[str, Any]) -> SimpleNamespace:
    """Convert nested dict to SimpleNamespace for dot notation access."""
    result = SimpleNamespace()
    for key, value in d.items():
        if isinstance(value, dict):
            setattr(result, key, _dict_to_namespace(value))
        else:
            setattr(result, key, value)
    return result


@lru_cache(maxsize=1)
def get_config() -> SimpleNamespace:
    """Get the current configuration as a namespace object.
    
    Returns:
        Configuration object with dot notation access
    """
    config_dict = global_settings()
    return _dict_to_namespace(config_dict)


# Re-export global functions for compatibility
settings = global_settings
reload_settings = global_reload_settings


def reload_config() -> SimpleNamespace:
    """Reload configuration from file.
    
    Returns:
        Updated configuration object
    """
    get_config.cache_clear()
    global_reload_settings()
    return get_config()
