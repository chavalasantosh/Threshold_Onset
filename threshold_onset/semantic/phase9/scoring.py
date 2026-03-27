"""
Scoring Functions for Fluency Generation

Enterprise-grade scoring with stability, template, and novelty components.

CORRECTED: Experience table (not "learner"), prefix-match templates.
"""

import logging
from typing import Dict, Any, Tuple, List, Optional

from threshold_onset.semantic.common.types import ConsequenceVector
from threshold_onset.semantic.common.utils import mean

logger = logging.getLogger('threshold_onset.semantic.phase9')


def calculate_stability_score(
    transition: Tuple[str, str],
    consequence_field: Any  # ConsequenceField
) -> float:
    """
    Calculate stability score from consequence field.
    
    Score = w1 * survival + w2 * (1/entropy) + w3 * (1 - refusal_rate)
    
    Args:
        transition: (source_hash, target_hash) tuple
        consequence_field: ConsequenceField from Phase 5
        
    Returns:
        Stability score [0.0, 1.0]
    """
    source_hash, target_hash = transition
    
    source_vector = consequence_field.identity_vectors.get(source_hash, {})
    target_vector = consequence_field.identity_vectors.get(target_hash, {})
    
    if not target_vector:
        return 0.0
    
    # Component 1: Survival
    survival = target_vector.get('survival', 0.0)
    
    # Component 2: Entropy reduction (inverse)
    entropy = target_vector.get('entropy', 1.0)
    entropy_reduction = 1.0 / (1.0 + entropy)
    
    # Component 3: Refusal distance
    refusal_rate = target_vector.get('near_refusal_rate', 0.0)
    refusal_distance = 1.0 - refusal_rate
    
    # Combined stability score
    stability = (
        survival * 0.4 +
        entropy_reduction * 0.3 +
        refusal_distance * 0.3
    )
    
    return stability


def calculate_novelty_penalty(
    symbol: int,
    recent_sequence: List[int],
    window: int = 5
) -> float:
    """
    Penalize repeating recent symbols.
    
    Prevents collapse into loops.
    
    Args:
        symbol: Symbol to check
        recent_sequence: Recent symbol sequence
        window: Window size for repetition check
        
    Returns:
        Novelty penalty [0.0, 1.0] (higher = more penalty)
    """
    if len(recent_sequence) < window:
        return 0.0
    
    recent = recent_sequence[-window:]
    repeat_count = recent.count(symbol)
    
    penalty = repeat_count / window
    return penalty


def calculate_experience_bias(
    transition: Tuple[int, int],
    experience_table: Dict[Tuple[int, int], float]
) -> float:
    """
    Calculate experience-based bias from experience table.
    
    CORRECTED: Experience table (not "learner").
    Deterministic update rule, derived from consequence deltas.
    
    Args:
        transition: (source_symbol, target_symbol) tuple
        experience_table: Experience table mapping transition -> bias
        
    Returns:
        Experience bias [-1.0, 1.0]
    """
    return experience_table.get(transition, 0.0)
