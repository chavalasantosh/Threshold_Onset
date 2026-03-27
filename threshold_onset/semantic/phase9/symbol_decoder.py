"""
Symbol Decoder

Structural inversion: symbol → identity → residue → token.

No heuristics. No probability. Pure backward walk through structure.
Token → residue → identity → symbol (forward).
Symbol → identity → residue → token (reverse).

Space: O(|symbols| + |identity| + |vocab|)
Time: O(n) build, O(1) decode per symbol.
"""

import hashlib
import logging
import re
from typing import Dict, List, Tuple, Any

logger = logging.getLogger('threshold_onset.semantic.phase9.symbol_decoder')


def _hash_segment(segment: Tuple[float, ...]) -> str:
    """Same as Phase 2 identity._hash_segment. Internal only."""
    segment_bytes = str(segment).encode('utf-8')
    return hashlib.md5(segment_bytes).hexdigest()


def _token_to_residue(token: str) -> float:
    """Same as TokenAction. Internal only."""
    token_bytes = token.encode('utf-8')
    hash_obj = hashlib.sha256(token_bytes)
    hash_int = int(hash_obj.hexdigest()[:8], 16)
    return float(hash_int % 10000) / 10000.0


def build_structural_decoder(
    tokens: List[str],
    residue_sequences: List[List[float]],
    phase2_metrics: Dict[str, Any],
    phase4_metrics: Dict[str, Any],
) -> Dict[int, str]:
    """
    Build symbol → token map by structural inversion.

    Process:
    1. residue → token: from tokens and TokenAction hash (store first occurrence)
    2. identity → residues: from residue_sequences + identity_mappings (segment hash → segment)
    3. symbol → identity: from phase4
    4. symbol → token: symbol → identity → first residue → token

    Args:
        tokens: Original token strings from tokenization
        residue_sequences: Residue sequences from Phase 0 (one per run)
        phase2_metrics: Phase 2 output (identity_mappings, etc.)
        phase4_metrics: Phase 4 output (symbol_to_identity, identity_to_symbol)

    Returns:
        Dict mapping symbol (int) → token string
    """
    identity_mappings = phase2_metrics.get('identity_mappings', {})
    symbol_to_identity = phase4_metrics.get('symbol_to_identity', {})

    if not phase2_metrics or not phase4_metrics:
        return {}
    if not identity_mappings or not symbol_to_identity:
        return {}

    # 1. residue → token (first occurrence wins)
    residue_to_token: Dict[float, str] = {}
    for token in tokens:
        residue = _token_to_residue(token)
        if residue not in residue_to_token:
            residue_to_token[residue] = token

    # 2. identity → residues (from segments in residue_sequences)
    identity_to_residues: Dict[str, List[float]] = {}
    SEGMENT_WINDOW = 2

    for residues in residue_sequences:
        for i in range(len(residues) - SEGMENT_WINDOW + 1):
            segment = tuple(residues[i:i + SEGMENT_WINDOW])
            segment_hash = _hash_segment(segment)
            if segment_hash in identity_mappings:
                identity_hash = identity_mappings[segment_hash]
                if identity_hash not in identity_to_residues:
                    identity_to_residues[identity_hash] = []
                for r in segment:
                    if r not in identity_to_residues[identity_hash]:
                        identity_to_residues[identity_hash].append(r)

    # 3. symbol → token: symbol → identity → first residue → token
    symbol_to_token: Dict[int, str] = {}
    fallback = "<UNK>"

    for symbol, identity_hash in symbol_to_identity.items():
        residues = identity_to_residues.get(identity_hash)
        if not residues:
            symbol_to_token[symbol] = fallback
            continue
        token = None
        for residue in residues:
            if residue in residue_to_token:
                token = residue_to_token[residue]
                break
        symbol_to_token[symbol] = token if token else fallback

    logger.info(
        "Structural decoder built: %d symbols, %d identity→residue, %d residue→token",
        len(symbol_to_token),
        len(identity_to_residues),
        len(residue_to_token),
    )
    return symbol_to_token


def decode_symbol_sequence(
    symbol_sequence: List[int],
    symbol_to_token: Dict[int, str],
    skip_unk: bool = True,
    unk_placeholder: str = "<UNK>",
) -> str:
    """
    Decode symbol sequence to text.

    Args:
        symbol_sequence: List of symbol IDs
        symbol_to_token: Map from symbol → token
        skip_unk: If True, skip <UNK> tokens in output
        unk_placeholder: Token to use for unknown symbols

    Returns:
        Space-joined token string
    """
    tokens = []
    for symbol in symbol_sequence:
        token = symbol_to_token.get(symbol, unk_placeholder)
        if skip_unk and token == unk_placeholder:
            continue
        tokens.append(token)
    text = " ".join(tokens)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


def get_decoder_stats(symbol_to_token: Dict[int, str]) -> Dict[str, int]:
    """
    Return decoder statistics (unk count, mapped count).

    Args:
        symbol_to_token: Map from symbol → token

    Returns:
        Dict with 'mapped', 'unk', 'total'
    """
    unk = sum(1 for t in symbol_to_token.values() if t == "<UNK>")
    mapped = len(symbol_to_token) - unk
    return {'mapped': mapped, 'unk': unk, 'total': len(symbol_to_token)}
