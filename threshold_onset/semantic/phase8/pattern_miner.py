"""
Pattern Mining for Constraint Discovery

Enterprise-grade pattern mining from role sequences.

CORRECTED: Global forbidden pattern comparison, prefix-match templates.
"""

import logging
from typing import List, Dict, Any, Tuple, Set
from collections import Counter

from threshold_onset.semantic.common.utils import calculate_percentile, mean

logger = logging.getLogger('threshold_onset.semantic.phase8')


def discover_role_patterns(
    role_sequences: List[List[str]],
    min_frequency: int = 3,
    max_pattern_length: int = 4
) -> Dict[Tuple[str, ...], Dict[str, Any]]:
    """
    Discover frequent role n-grams.
    
    No imported rules. Just frequency.
    
    Args:
        role_sequences: List of role sequences
        min_frequency: Minimum pattern frequency
        max_pattern_length: Maximum n-gram length
        
    Returns:
        Dictionary mapping pattern -> {frequency, length}
    """
    patterns = {}
    
    for n in range(2, max_pattern_length + 1):
        ngrams = Counter()
        for role_seq in role_sequences:
            for i in range(len(role_seq) - n + 1):
                pattern = tuple(role_seq[i:i+n])
                ngrams[pattern] += 1
        
        # Keep frequent patterns
        for pattern, freq in ngrams.items():
            if freq >= min_frequency:
                patterns[pattern] = {
                    'frequency': freq,
                    'length': n
                }
    
    logger.info(f"Discovered {len(patterns)} role patterns")
    
    return patterns


def discover_forbidden_patterns(
    role_patterns: Dict[Tuple[str, ...], Dict[str, Any]],
    edge_deltas: Dict[Tuple[str, str], Dict[str, float]],
    symbol_to_role: Dict[Any, str],
    identity_to_symbol: Dict[str, Any],
    continuation_observer: Any
) -> Set[Tuple[str, ...]]:
    """
    Discover forbidden role transitions from outcome data.
    
    CORRECTED: Compare against global distribution, not local percentile.
    
    Forbidden = high failure rate or high cost (from Phase 5 edge_deltas).
    
    Args:
        role_patterns: Discovered role patterns
        edge_deltas: Edge deltas from Phase 5
        symbol_to_role: Symbol to role mapping
        identity_to_symbol: Identity hash to symbol mapping
        continuation_observer: ContinuationObserver instance
        
    Returns:
        Set of forbidden role patterns (tuples)
    """
    forbidden = set()
    
    # Group transitions by role pattern (2-grams for now)
    role_transition_outcomes = {}
    
    for (source_hash, target_hash), delta in edge_deltas.items():
        source_symbol = identity_to_symbol.get(source_hash)
        target_symbol = identity_to_symbol.get(target_hash)
        
        if source_symbol is None or target_symbol is None:
            continue
        
        source_role = symbol_to_role.get(source_symbol, 'unclassified')
        target_role = symbol_to_role.get(target_symbol, 'unclassified')
        role_pattern = (source_role, target_role)
        
        # Use refusal_delta as failure indicator
        refusal_delta = delta.get('refusal_delta', 0.0)
        
        if role_pattern not in role_transition_outcomes:
            role_transition_outcomes[role_pattern] = []
        
        role_transition_outcomes[role_pattern].append(refusal_delta)
    
    if not role_transition_outcomes:
        logger.warning("No role transition outcomes found")
        return forbidden
    
    # CORRECTED: Compute average refusal per role_pair
    avg_refusal_per_pattern = {}
    for role_pattern, outcomes in role_transition_outcomes.items():
        if outcomes:
            avg_refusal_per_pattern[role_pattern] = mean(outcomes)
    
    # CORRECTED: Collect all averages into global list
    all_avg_refusals = list(avg_refusal_per_pattern.values())
    
    if not all_avg_refusals:
        return forbidden
    
    # CORRECTED: Compare against global 90th percentile
    global_percentile_90 = calculate_percentile(all_avg_refusals, 90)
    
    # Patterns with high average refusal_delta are forbidden
    for role_pattern, avg_refusal in avg_refusal_per_pattern.items():
        if avg_refusal > global_percentile_90:
            forbidden.add(role_pattern)
            logger.debug(
                f"Forbidden pattern: {role_pattern} "
                f"(avg_refusal={avg_refusal:.3f} > {global_percentile_90:.3f})"
            )
    
    logger.info(f"Discovered {len(forbidden)} forbidden patterns")
    
    return forbidden


def build_templates(
    role_patterns: Dict[Tuple[str, ...], Dict[str, Any]],
    forbidden_patterns: Set[Tuple[str, ...]]
) -> List[Dict[str, Any]]:
    """
    Build templates from valid role patterns.
    
    Templates = frequent patterns that are not forbidden.
    
    Args:
        role_patterns: Discovered role patterns
        forbidden_patterns: Set of forbidden patterns
        
    Returns:
        List of template dictionaries
    """
    # Filter: frequent AND not forbidden
    valid_patterns = {
        p: data for p, data in role_patterns.items()
        if p not in forbidden_patterns
    }
    
    # Sort by frequency
    sorted_patterns = sorted(
        valid_patterns.items(),
        key=lambda x: x[1]['frequency'],
        reverse=True
    )
    
    # Top patterns become templates
    templates = []
    for pattern, data in sorted_patterns[:20]:  # Top 20
        templates.append({
            'pattern': list(pattern),
            'frequency': data['frequency'],
            'length': data['length']
        })
    
    logger.info(f"Built {len(templates)} templates")
    
    return templates


def compute_prefix_match_score(
    current_role_sequence: List[str],
    template_pattern: List[str],
    window: int = 5
) -> float:
    """
    Compute prefix-match score for template continuation.
    
    CORRECTED: Prefix-match scoring guides continuation.
    
    If current role suffix matches template prefix, reward continuation.
    
    Args:
        current_role_sequence: Current role sequence (last N roles)
        template_pattern: Template pattern to match
        window: Window size for matching
        
    Returns:
        Score [0.0, 1.0] (higher = better match)
    """
    if not current_role_sequence or not template_pattern:
        return 0.0
    
    # Get last window roles
    recent_roles = current_role_sequence[-window:] if len(current_role_sequence) >= window else current_role_sequence
    
    # Check if recent roles match template prefix
    pattern_len = len(template_pattern)
    
    if len(recent_roles) < pattern_len:
        # Check if recent roles match beginning of pattern
        if recent_roles == template_pattern[:len(recent_roles)]:
            # Partial match - reward continuation
            return len(recent_roles) / pattern_len
        return 0.0
    
    # Check for exact prefix match
    for i in range(len(recent_roles) - pattern_len + 1):
        if tuple(recent_roles[i:i+pattern_len]) == tuple(template_pattern):
            # Exact match
            return 1.0
    
    # Check for suffix-prefix match (continuation)
    # If end of recent matches beginning of pattern
    for suffix_len in range(1, min(len(recent_roles), pattern_len)):
        if recent_roles[-suffix_len:] == template_pattern[:suffix_len]:
            # Partial continuation match
            return suffix_len / pattern_len
    
    return 0.0
