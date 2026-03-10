"""
THRESHOLD_ONSET — Phase 4: SYMBOL

Symbol assignment (pure aliasing).
Creates deterministic, reversible symbol mappings.

CONSTRAINT: Symbols are integers only (0, 1, 2, 3, ...).
No meaning, no ordering, no semantics.
Pure one-to-one mapping.
"""


def assign_identity_aliases(identity_hashes):
    """
    Assign integer symbols to identity hashes.
    
    Creates deterministic, reversible mappings.
    Symbols are assigned in sorted hash order (lexicographic).
    
    CRITICAL: Symbols are integers only (0, 1, 2, 3, ...).
    No letters, no tokens, no multi-letter sequences.
    
    Args:
        identity_hashes: set or list of identity hashes (strings)
    
    Returns:
        Dictionary with:
        - 'identity_to_symbol': dict mapping identity_hash → integer symbol
        - 'symbol_to_identity': dict mapping integer symbol → identity_hash
        - 'alias_count': int - number of aliases assigned
    """
    if not identity_hashes:
        return {
            'identity_to_symbol': {},
            'symbol_to_identity': {},
            'alias_count': 0
        }
    
    # Convert to sorted list for deterministic assignment
    # CRITICAL: Sort lexicographically to guarantee cross-run consistency
    sorted_hashes = sorted(identity_hashes)
    
    # Assign integer symbols sequentially: 0, 1, 2, 3, ...
    identity_to_symbol = {}
    symbol_to_identity = {}
    
    for symbol, identity_hash in enumerate(sorted_hashes):
        identity_to_symbol[identity_hash] = symbol
        symbol_to_identity[symbol] = identity_hash
    
    return {
        'identity_to_symbol': identity_to_symbol,
        'symbol_to_identity': symbol_to_identity,
        'alias_count': len(identity_to_symbol)
    }


def assign_relation_aliases(relation_hashes):
    """
    Assign integer symbols to relation hashes.
    
    Creates deterministic, reversible mappings.
    Symbols are assigned in sorted hash order (lexicographic).
    
    CRITICAL: Symbols are integers only (0, 1, 2, 3, ...).
    No letters, no tokens, no multi-letter sequences.
    
    Args:
        relation_hashes: set or list of relation hashes (strings)
    
    Returns:
        Dictionary with:
        - 'relation_to_symbol': dict mapping relation_hash → integer symbol
        - 'symbol_to_relation': dict mapping integer symbol → relation_hash
        - 'alias_count': int - number of aliases assigned
    """
    if not relation_hashes:
        return {
            'relation_to_symbol': {},
            'symbol_to_relation': {},
            'alias_count': 0
        }
    
    # Convert to sorted list for deterministic assignment
    # CRITICAL: Sort lexicographically to guarantee cross-run consistency
    sorted_hashes = sorted(relation_hashes)
    
    # Assign integer symbols sequentially: 0, 1, 2, 3, ...
    relation_to_symbol = {}
    symbol_to_relation = {}
    
    for symbol, relation_hash in enumerate(sorted_hashes):
        relation_to_symbol[relation_hash] = symbol
        symbol_to_relation[symbol] = relation_hash
    
    return {
        'relation_to_symbol': relation_to_symbol,
        'symbol_to_relation': symbol_to_relation,
        'alias_count': len(relation_to_symbol)
    }
