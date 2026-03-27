#!/usr/bin/env python3
"""
Surface Realization Layer (Surface Adapter v0)

Maps symbols back to text tokens for readable output.

SURFACE ADAPTER v0 CONTRACT:
- Deterministic: Same inputs → same outputs. Tie-breaking by sorted token string.
- No smoothing: No grammar fixes, no fluency heuristics, no probabilistic adjustments.
- Purpose: "Make paths readable, not intelligent."

This is the surface layer that makes the system "talk".
"""

from collections import Counter, defaultdict


def is_valid_surface_token(tok):
    """Check if token is valid for surface generation (content tokens only)."""
    t = tok.strip()
    if not t:
        return False
    # Reject punctuation-only tokens
    if all(c in ".,;:!?-\"'()[]{}" for c in t):
        return False
    # Reject pure whitespace
    if not t or t.isspace():
        return False
    return True


def build_symbol_to_token_mapping(
    tokens,
    phase4_output,
    phase2_metrics,
    phase0_residues_by_run,
    token_to_residue_map=None
):
    """
    Build mapping from symbols to the most frequent token(s) associated with that symbol.

    Process:
    1. Track which tokens produced which residues in each run
    2. Map residues → identities (via Phase 2)
    3. Map identities → symbols (via Phase 4)
    4. For each symbol, find most frequent associated token(s)

    Returns:
        {symbol: most_frequent_token_string}
    """
    identity_to_symbol = phase4_output.get('identity_to_symbol', {})
    symbol_to_identity = phase4_output.get('symbol_to_identity', {})

    # Build residue → identity mapping (from Phase 2)
    persistent_segment_hashes = phase2_metrics.get('persistent_segment_hashes', [])
    identity_mappings = phase2_metrics.get('identity_mappings', {})

    # Track token → residue → identity → symbol
    # For each run, track which token produced which residue

    # Build token → symbol associations
    token_to_symbols = defaultdict(list)

    # Get identity list for residue → identity mapping
    identity_hashes = set()
    if persistent_segment_hashes:
        for seg_hash in persistent_segment_hashes:
            if seg_hash in identity_mappings:
                identity_hashes.add(identity_mappings[seg_hash])
    identity_hashes.update(identity_mappings.values())
    identity_list = list(identity_hashes) if identity_hashes else []

    # Use direct token_to_residue_map if provided (more reliable)
    if token_to_residue_map:
        # Direct mapping: token → residue → identity → symbol
        for token_str, residue in token_to_residue_map.items():
            if identity_list:
                residue_int = int(abs(residue * 10000)) % len(identity_list)
                identity_hash = identity_list[residue_int]
                symbol = identity_to_symbol.get(identity_hash)
                if symbol is not None:
                    token_to_symbols[token_str].append(symbol)
    else:
        # Fallback: reconstruct from residues (original method)
        for run_idx, residues in enumerate(phase0_residues_by_run):
            if run_idx == 0:
                # Map residues to identities
                residue_to_identity = {}
                for _, residue in enumerate(residues):
                    if identity_list:
                        residue_int = int(abs(residue * 10000)) % len(identity_list)
                        identity_hash = identity_list[residue_int]
                        residue_to_identity[residue] = identity_hash

                # Try to match residues to tokens (approximate)
                for step, residue in enumerate(residues):
                    if residue in residue_to_identity:
                        identity_hash = residue_to_identity[residue]
                        symbol = identity_to_symbol.get(identity_hash)
                        if symbol is not None:
                            # Approximate token index
                            token_idx = min(step // 2, len(tokens) - 1)
                            if token_idx < len(tokens):
                                token_str = tokens[token_idx]
                                token_to_symbols[token_str].append(symbol)

    # Build final mapping: symbol → most frequent token
    symbol_to_token = {}

    # Count token frequency per symbol
    symbol_token_counts = defaultdict(Counter)
    for token_str, symbols in token_to_symbols.items():
        for symbol in symbols:
            symbol_token_counts[symbol][token_str] += 1

    # Assign most frequent VALID token to each symbol (deterministic tie-break)
    for symbol in sorted(symbol_to_identity.keys()):
        if symbol in symbol_token_counts and symbol_token_counts[symbol]:
            # most_common() can ties - use (count, token_str) for deterministic pick
            token_freqs = symbol_token_counts[symbol].most_common()
            token_freqs_sorted = sorted(token_freqs, key=lambda x: (-x[1], x[0]))

            # Pick first valid surface token (deterministic)
            valid_token = None
            for token_str, _count in token_freqs_sorted:
                if is_valid_surface_token(token_str):
                    valid_token = token_str
                    break

            if valid_token:
                symbol_to_token[symbol] = valid_token
            elif token_freqs_sorted:
                token_str = token_freqs_sorted[0][0]
                cleaned = token_str.strip()
                cleaned = ''.join(c for c in cleaned if c.isprintable() or c.isspace())
                if cleaned and not cleaned.isspace():
                    symbol_to_token[symbol] = cleaned
                else:
                    symbol_to_token[symbol] = "<UNK>"
            else:
                symbol_to_token[symbol] = "<UNK>"
        else:
            symbol_to_token[symbol] = "<UNK>"

    return symbol_to_token


def _is_sentence_end(token):
    """Our own rule: token ends with sentence-ending punctuation."""
    if not token or len(token) < 2:
        return False
    return token.rstrip()[-1] in ".!?"


def symbols_to_text(symbol_sequence, symbol_to_token, insert_sentence_breaks=False):
    """
    Convert symbol sequence to space-joined text.

    No smoothing. No grammar. Skip <UNK> only.
    When insert_sentence_breaks=True, add newline after sentence-ending tokens.

    Args:
        symbol_sequence: List of symbol IDs
        symbol_to_token: Map symbol → token string
        insert_sentence_breaks: If True, newline after tokens ending in .!?

    Returns:
        Space-joined token string (with optional newlines)
    """
    tokens = []
    for i, symbol in enumerate(symbol_sequence):
        token = symbol_to_token.get(symbol, "<UNK>")
        if token != "<UNK>":
            tokens.append(token)
            if insert_sentence_breaks and _is_sentence_end(token) and i < len(symbol_sequence) - 1:
                tokens.append("\n")
    result = " ".join(tokens)
    return result.replace(" \n ", "\n").replace("\n ", "\n")


def generate_text_sequence(
    start_symbol,
    steps,
    phase4_output,
    phase3_metrics,
    phase2_metrics,
    path_scores,
    symbol_to_token,
    method="highest_score"
):
    """
    Generate a text sequence (not just symbols).

    Uses generate_sequence internally, then converts symbols to tokens.
    """
    from integration.generate import generate_sequence

    symbol_seq = generate_sequence(
        start_symbol,
        steps,
        phase4_output,
        phase3_metrics,
        phase2_metrics,
        path_scores,
        method
    )

    text = symbols_to_text(symbol_seq, symbol_to_token)

    return text, symbol_seq
