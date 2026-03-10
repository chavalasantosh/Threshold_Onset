"""
Configuration validation.

Enterprise-grade config validation.
"""

from typing import Dict, Any
from threshold_onset.semantic.common.exceptions import SemanticDiscoveryError


class ConfigError(SemanticDiscoveryError):
    """Configuration error."""
    pass


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration dict
        
    Raises:
        ConfigError: If config is invalid
    """
    if not isinstance(config, dict):
        raise ConfigError(f"config must be dict, got {type(config)}")
    
    # Validate phase5 config
    if 'phase5' in config:
        phase5 = config['phase5']
        if 'k' in phase5:
            k = phase5['k']
            if not isinstance(k, int) or k < 1 or k > 20:
                raise ConfigError(f"phase5.k must be int in [1, 20], got {k}")
        
        if 'num_rollouts' in phase5:
            nr = phase5['num_rollouts']
            if not isinstance(nr, int) or nr < 1 or nr > 10000:
                raise ConfigError(
                    f"phase5.num_rollouts must be int in [1, 10000], got {nr}"
                )
    
    # Validate phase6 config
    if 'phase6' in config:
        phase6 = config['phase6']
        if 'num_clusters' in phase6 and phase6['num_clusters'] is not None:
            nc = phase6['num_clusters']
            if not isinstance(nc, int) or nc < 2:
                raise ConfigError(
                    f"phase6.num_clusters must be int >= 2 or None, got {nc}"
                )
    
    # Validate phase9 config
    if 'phase9' in config:
        phase9 = config['phase9']
        weights = [
            phase9.get('stability_weight', 0.4),
            phase9.get('template_weight', 0.3),
            phase9.get('bias_weight', 0.2),
            phase9.get('novelty_weight', 0.1),
        ]
        total = sum(weights)
        if abs(total - 1.0) > 0.01:  # Allow small floating point error
            raise ConfigError(
                f"phase9 weights must sum to 1.0, got {total}"
            )
