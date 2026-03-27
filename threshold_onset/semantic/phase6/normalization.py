"""
Vector Normalization for Clustering

Enterprise-grade normalization utilities.
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger('threshold_onset.semantic.phase6')


def normalize_vectors(
    identity_vectors: Dict[str, Dict[str, float]]
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, float]]]:
    """
    Normalize consequence vectors for clustering.
    
    Each component normalized to [0, 1] range.
    
    Args:
        identity_vectors: Dictionary mapping identity_hash -> ConsequenceVector
        
    Returns:
        Tuple of (normalized_vectors, ranges)
        - normalized_vectors: Dictionary mapping identity_hash -> normalized vector
        - ranges: Dictionary mapping component -> {min, max}
    """
    if not identity_vectors:
        return {}, {}
    
    # Collect all values per component
    components = {
        'out_degree': [],
        'k_reach': [],
        'survival': [],
        'entropy': [],
        'escape_concentration': [],
        'near_refusal_rate': [],
        'dead_end_risk': []
    }
    
    for vector in identity_vectors.values():
        for key in components:
            if key in vector:
                components[key].append(vector[key])
    
    # Compute min/max for normalization
    ranges = {}
    for key, values in components.items():
        if values:
            ranges[key] = {
                'min': min(values),
                'max': max(values)
            }
        else:
            ranges[key] = {'min': 0.0, 'max': 1.0}
    
    # Normalize
    normalized = {}
    for identity_hash, vector in identity_vectors.items():
        normalized[identity_hash] = {}
        for key in components:
            value = vector.get(key, 0.0)
            min_val = ranges[key]['min']
            max_val = ranges[key]['max']
            
            if max_val > min_val:
                normalized[identity_hash][key] = (value - min_val) / (max_val - min_val)
            else:
                normalized[identity_hash][key] = 0.0
    
    logger.info(f"Normalized {len(normalized)} vectors")
    
    return normalized, ranges
