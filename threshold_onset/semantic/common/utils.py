"""
Utility functions for semantic discovery module.

Enterprise-grade utility functions with full type hints.
"""

import math
from typing import List, Dict, Any
from collections import Counter


def calculate_entropy(values: List[Any]) -> float:
    """
    Calculate entropy of a distribution.
    
    Args:
        values: List of values (can be any hashable type)
        
    Returns:
        Entropy value (bits)
    """
    if not values:
        return 0.0
    
    counts = Counter(values)
    total = len(values)
    
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    
    return entropy


def calculate_entropy_from_options(num_options: int) -> float:
    """
    Calculate entropy from number of options (uniform distribution).
    
    Args:
        num_options: Number of options
        
    Returns:
        Entropy value (bits)
    """
    if num_options <= 0:
        return 0.0
    
    if num_options == 1:
        return 0.0
    
    # Uniform distribution: H = log2(n)
    return math.log2(num_options)


def calculate_entropy_from_counts(counts: List[int]) -> float:
    """
    Calculate Shannon entropy from transition counts (empirical distribution).
    
    This is the CORRECTED version that uses actual observed frequencies,
    not uniform assumption.
    
    Args:
        counts: List of transition counts
        
    Returns:
        Entropy in bits
    """
    if not counts:
        return 0.0
    
    total = sum(counts)
    if total == 0:
        return 0.0
    
    entropy = 0.0
    for count in counts:
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    
    return entropy


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculate percentile value from list.
    
    Args:
        values: List of numeric values
        percentile: Percentile (0-100)
        
    Returns:
        Percentile value
    """
    if not values:
        raise ValueError("Cannot calculate percentile of empty list")
    
    if percentile < 0 or percentile > 100:
        raise ValueError(f"percentile must be in [0, 100], got {percentile}")
    
    sorted_values = sorted(values)
    index = (percentile / 100.0) * (len(sorted_values) - 1)
    
    if index.is_integer():
        return sorted_values[int(index)]
    else:
        lower = sorted_values[int(index)]
        upper = sorted_values[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))


def normalize_vector(vector: Dict[str, float], ranges: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Normalize vector components to [0, 1] range.
    
    Args:
        vector: Vector to normalize
        ranges: Min/max ranges for each component
        
    Returns:
        Normalized vector
    """
    normalized = {}
    
    for key, value in vector.items():
        if key in ranges:
            min_val = ranges[key]['min']
            max_val = ranges[key]['max']
            
            if max_val > min_val:
                normalized[key] = (value - min_val) / (max_val - min_val)
            else:
                normalized[key] = 0.0
        else:
            normalized[key] = value
    
    return normalized


def calculate_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score [0.0, 1.0]
    """
    # Get common keys
    keys = set(vec1.keys()) & set(vec2.keys())
    
    if not keys:
        return 0.0
    
    # Calculate dot product and magnitudes
    dot_product = sum(vec1[k] * vec2[k] for k in keys)
    mag1 = math.sqrt(sum(vec1[k] ** 2 for k in keys))
    mag2 = math.sqrt(sum(vec2[k] ** 2 for k in keys))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    similarity = dot_product / (mag1 * mag2)
    
    # Clamp to [0, 1] (should already be, but safety)
    return max(0.0, min(1.0, similarity))


def mean(values: List[float]) -> float:
    """Calculate mean of values."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def variance(values: List[float]) -> float:
    """Calculate variance of values."""
    if not values:
        return 0.0
    
    m = mean(values)
    squared_diffs = [(v - m) ** 2 for v in values]
    return mean(squared_diffs)
