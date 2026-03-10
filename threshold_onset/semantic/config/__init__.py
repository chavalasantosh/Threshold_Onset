"""
Configuration management for semantic discovery module.

Enterprise-grade configuration with validation.
"""

from threshold_onset.semantic.config.defaults import (
    DEFAULT_K,
    DEFAULT_NUM_ROLLOUTS,
    DEFAULT_MIN_FREQUENCY,
    DEFAULT_NOVELTY_WINDOW,
    DEFAULT_NUM_CLUSTERS,
    get_default_config
)
from threshold_onset.semantic.config.validation import (
    validate_config,
    ConfigError
)

__all__ = [
    'DEFAULT_K',
    'DEFAULT_NUM_ROLLOUTS',
    'DEFAULT_MIN_FREQUENCY',
    'DEFAULT_NOVELTY_WINDOW',
    'DEFAULT_NUM_CLUSTERS',
    'get_default_config',
    'validate_config',
    'ConfigError',
]
