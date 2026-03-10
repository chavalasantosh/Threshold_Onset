"""
THRESHOLD_ONSET — Phase 4: SYMBOL

Pure aliasing phase.
Creates reversible symbol mappings for persistent identities and relations.

Phase 4 adds ZERO new structure.
Removing all symbols must restore Phase 3 bit-for-bit, without recomputation.
"""

from threshold_onset.phase4.alias import assign_identity_aliases, assign_relation_aliases  # pylint: disable=import-outside-toplevel

# FIXED threshold for Phase 4 gate (non-adaptive)
# These values are external and fixed, not computed from data
MIN_PERSISTENT_IDENTITIES = 1
MIN_PERSISTENT_RELATIONS = 1


def phase4(phase2_metrics, phase3_metrics):
    """
    Phase 4 symbol pipeline (pure aliasing).
    
    Creates reversible symbol mappings for persistent identities and relations.
    Phase 4 adds ZERO new structure - only aliases.
    
    CRITICAL: Phase 4 aliases apply ONLY to frozen identities and frozen relations.
    No alias may be created for non-persistent entities.
    
    Args:
        phase2_metrics: dictionary with Phase 2 identity metrics (from multi-run)
        phase3_metrics: dictionary with Phase 3 relation metrics (from multi-run, FROZEN)
    
    Returns:
        Dictionary with symbol mappings (if gate passes), or None (if gate fails):
        - 'identity_to_symbol': dict mapping identity_hash → integer symbol
        - 'symbol_to_identity': dict mapping integer symbol → identity_hash
        - 'identity_alias_count': int
        - 'relation_to_symbol': dict mapping relation_hash → integer symbol
        - 'symbol_to_relation': dict mapping integer symbol → relation_hash
        - 'relation_alias_count': int
    """
    # Check gate
    gate_passed = _check_phase4_gate(phase2_metrics, phase3_metrics)
    
    if not gate_passed:
        return None  # Gate failed, refuse execution
    
    # Extract identity hashes from Phase 2
    # CRITICAL: Only alias persistent identities
    identity_mappings = phase2_metrics.get('identity_mappings', {})
    # Extract all unique identity hashes from identity_mappings
    identity_hashes = set(identity_mappings.values())
    
    # Extract relation hashes from Phase 3
    # CRITICAL: Only alias persistent relations
    persistent_relation_hashes = phase3_metrics.get('persistent_relation_hashes', set())
    relation_hashes = set(persistent_relation_hashes)
    
    # Assign aliases to identities
    identity_alias_result = assign_identity_aliases(identity_hashes)
    
    # Assign aliases to relations
    relation_alias_result = assign_relation_aliases(relation_hashes)
    
    # Return combined mappings
    return {
        'identity_to_symbol': identity_alias_result['identity_to_symbol'],
        'symbol_to_identity': identity_alias_result['symbol_to_identity'],
        'identity_alias_count': identity_alias_result['alias_count'],
        'relation_to_symbol': relation_alias_result['relation_to_symbol'],
        'symbol_to_relation': relation_alias_result['symbol_to_relation'],
        'relation_alias_count': relation_alias_result['alias_count']
    }


def _check_phase4_gate(phase2_metrics, phase3_metrics):
    """
    Check if Phase 4 gate criteria are met.
    
    Phase 4 must refuse execution unless ALL criteria are met:
    1. Phase 3 is frozen (not None)
    2. Phase 3 has persistent relations (≥ MIN_PERSISTENT_RELATIONS)
    3. Phase 2 has persistent identities (≥ MIN_PERSISTENT_IDENTITIES)
    
    Args:
        phase2_metrics: dictionary with Phase 2 identity metrics
        phase3_metrics: dictionary with Phase 3 relation metrics (or None if gate failed)
    
    Returns:
        True if gate passes, False if gate fails
    """
    # Criterion 1: Phase 3 is frozen (not None)
    if phase3_metrics is None:
        return False
    
    # Criterion 2: Phase 3 has persistent relations
    persistent_relation_hashes = phase3_metrics.get('persistent_relation_hashes', set())
    persistent_relations = len(persistent_relation_hashes)
    has_persistent_relations = persistent_relations >= MIN_PERSISTENT_RELATIONS
    
    # Criterion 3: Phase 2 has persistent identities
    persistent_segment_hashes = phase2_metrics.get('persistent_segment_hashes', [])
    identity_mappings = phase2_metrics.get('identity_mappings', {})
    persistent_identities = len(persistent_segment_hashes) + len(identity_mappings)
    has_persistent_identities = persistent_identities >= MIN_PERSISTENT_IDENTITIES
    
    # All three criteria must be met
    return has_persistent_relations and has_persistent_identities
