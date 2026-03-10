"""
Default configuration values.

Enterprise-grade configuration management.
"""

from typing import Dict, Any


# Phase 5: Consequence Field
DEFAULT_K = 5  # k-step reachability horizon
DEFAULT_NUM_ROLLOUTS = 100  # Rollouts per identity
DEFAULT_MAX_STEPS = 50  # Maximum steps per rollout

# Phase 6: Meaning Discovery
DEFAULT_NUM_CLUSTERS = None  # Auto-detect from data
DEFAULT_SIMILARITY_THRESHOLD = 0.7  # For clustering

# Phase 7: Role Emergence
DEFAULT_PERCENTILE_HIGH = 75  # High threshold percentile
DEFAULT_PERCENTILE_LOW = 25  # Low threshold percentile

# Phase 8: Constraint Discovery
DEFAULT_MIN_FREQUENCY = 3  # Minimum pattern frequency
DEFAULT_MAX_PATTERN_LENGTH = 4  # Maximum n-gram length

# Phase 9: Fluency Generator
DEFAULT_NOVELTY_WINDOW = 5  # Novelty penalty window
DEFAULT_STABILITY_WEIGHT = 0.4  # Stability score weight
DEFAULT_TEMPLATE_WEIGHT = 0.3  # Template score weight
DEFAULT_BIAS_WEIGHT = 0.2  # Learned bias weight
DEFAULT_NOVELTY_WEIGHT = 0.1  # Novelty penalty weight


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration dictionary.
    
    Returns:
        Default configuration dict
    """
    return {
        'phase5': {
            'k': DEFAULT_K,
            'num_rollouts': DEFAULT_NUM_ROLLOUTS,
            'max_steps': DEFAULT_MAX_STEPS,
        },
        'phase6': {
            'num_clusters': DEFAULT_NUM_CLUSTERS,
            'similarity_threshold': DEFAULT_SIMILARITY_THRESHOLD,
        },
        'phase7': {
            'percentile_high': DEFAULT_PERCENTILE_HIGH,
            'percentile_low': DEFAULT_PERCENTILE_LOW,
        },
        'phase8': {
            'min_frequency': DEFAULT_MIN_FREQUENCY,
            'max_pattern_length': DEFAULT_MAX_PATTERN_LENGTH,
        },
        'phase9': {
            'novelty_window': DEFAULT_NOVELTY_WINDOW,
            'stability_weight': DEFAULT_STABILITY_WEIGHT,
            'template_weight': DEFAULT_TEMPLATE_WEIGHT,
            'bias_weight': DEFAULT_BIAS_WEIGHT,
            'novelty_weight': DEFAULT_NOVELTY_WEIGHT,
        },
    }
