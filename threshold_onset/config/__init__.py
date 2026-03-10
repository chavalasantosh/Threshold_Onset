"""
THRESHOLD_ONSET — Configuration Management

Load config from JSON file with environment overrides.
"""

from .loader import load_config, get_config

__all__ = ["load_config", "get_config"]
