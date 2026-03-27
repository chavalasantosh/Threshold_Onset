"""
THRESHOLD_ONSET — Phase 4: SYMBOL

Symbol assignment (pure aliasing).
Creates deterministic, reversible symbol mappings.

CONSTRAINT: Symbols are integers only (0, 1, 2, 3, ...).
No meaning, no ordering, no semantics.
Pure one-to-one mapping.
"""


def _assign_aliases(hashes, identity_key, symbol_key):
    """
    Generic helper: assign sequential integer symbols to a collection of hashes.

    Sorts lexicographically for cross-run determinism, then enumerates.

    Args:
        hashes: set or list of hash strings
        identity_key: name for the forward mapping in the returned dict
        symbol_key:   name for the reverse mapping in the returned dict

    Returns:
        Dictionary with identity_key, symbol_key, and 'alias_count'.
    """
    if not hashes:
        return {identity_key: {}, symbol_key: {}, 'alias_count': 0}

    sorted_hashes = sorted(hashes)
    forward = {}
    reverse = {}
    for symbol, h in enumerate(sorted_hashes):
        forward[h] = symbol
        reverse[symbol] = h

    return {identity_key: forward, symbol_key: reverse, 'alias_count': len(forward)}


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
        - 'identity_to_symbol': dict mapping identity_hash -> integer symbol
        - 'symbol_to_identity': dict mapping integer symbol -> identity_hash
        - 'alias_count': int - number of aliases assigned
    """
    return _assign_aliases(identity_hashes, 'identity_to_symbol', 'symbol_to_identity')


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
        - 'relation_to_symbol': dict mapping relation_hash -> integer symbol
        - 'symbol_to_relation': dict mapping integer symbol -> relation_hash
        - 'alias_count': int - number of aliases assigned
    """
    return _assign_aliases(relation_hashes, 'relation_to_symbol', 'symbol_to_relation')
