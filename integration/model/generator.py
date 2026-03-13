"""
Canonical generation: anchor-from-prompt, cycle control, clean refusal.

- Anchor: last prompt symbol that exists in the learned graph (has an outgoing edge).
- Cycle control: deterministic penalties for repeated 2-grams and 3-grams in one generation.
- No fallback to global-best-edge; caller refuses when unanchored.

Stdlib only. Used by integration.model.santek_base.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# Type alias for path_scores (int,int) -> float
PathScores = Dict[Tuple[int, int], float]

# Defaults for V1 cycle control
RECENCY_WINDOW = 6
RECENCY_PENALTY = 0.30
BIGRAM_PENALTY = 0.20
TRIGRAM_PENALTY = 0.35


def _sources_in_graph(path_scores: PathScores) -> set:
    """Set of symbols that have at least one outgoing edge (excluding self-loop)."""
    return {fr for (fr, to) in path_scores if fr != to}


def last_connected_anchor(
    prompt_symbols: List[int],
    path_scores: PathScores,
) -> Tuple[List[int], Optional[int]]:
    """
    Return (connected_prefix, anchor) for the prompt.

    connected_prefix = longest prefix of prompt_symbols ending at a symbol that
    has an outgoing edge in path_scores. anchor = that last symbol.
    If no symbol in the prompt is in the graph, returns ([], None).
    """
    in_graph = _sources_in_graph(path_scores)
    if not in_graph:
        return [], None
    last_anchor_idx: Optional[int] = None
    for i, s in enumerate(prompt_symbols):
        if s in in_graph:
            last_anchor_idx = i
    if last_anchor_idx is None:
        return [], None
    prefix = list(prompt_symbols[: last_anchor_idx + 1])
    return prefix, prefix[-1]


def is_anchored(prompt_symbols: List[int], path_scores: PathScores) -> bool:
    """True if at least one prompt symbol has an outgoing edge in the graph."""
    _, anchor = last_connected_anchor(prompt_symbols, path_scores)
    return anchor is not None


def generate_symbols_with_cycle_control(
    start_seq: List[int],
    path_scores: PathScores,
    length: int,
    recency_window: int = RECENCY_WINDOW,
    recency_penalty: float = RECENCY_PENALTY,
    bigram_penalty: float = BIGRAM_PENALTY,
    trigram_penalty: float = TRIGRAM_PENALTY,
) -> List[int]:
    """
    Extend sequence by greedy argmax on path_scores with deterministic cycle control.

    - Recency: same symbol repeated in recent window (existing behavior).
    - Bigram: (current, next) repeated in recent bigrams → extra penalty.
    - Trigram: (prev, current, next) repeated in recent trigrams → extra penalty.

    Stops when no valid outgoing edge. No self-transitions.
    """
    seq = list(start_seq)
    if not seq:
        return seq

    for _ in range(length):
        current = seq[-1]
        recent = seq[-recency_window:] if len(seq) >= recency_window else seq
        start_b = max(0, len(seq) - 1 - recency_window)
        recent_bigrams = [(seq[i], seq[i + 1]) for i in range(start_b, len(seq) - 1)]
        start_t = max(0, len(seq) - 2 - recency_window)
        recent_trigrams = [(seq[i], seq[i + 1], seq[i + 2]) for i in range(start_t, len(seq) - 2)]

        candidates: List[Tuple[float, int]] = []
        for (fr, to), score in path_scores.items():
            if fr != current or to == current:
                continue
            penalty = recency_penalty * recent.count(to)
            if len(seq) >= 1:
                bigram = (current, to)
                penalty += bigram_penalty * recent_bigrams.count(bigram)
            if len(seq) >= 2:
                trigram = (seq[-2], current, to)
                penalty += trigram_penalty * recent_trigrams.count(trigram)
            candidates.append((score - penalty, to))

        if not candidates:
            break
        candidates.sort(key=lambda x: x[0], reverse=True)
        seq.append(candidates[0][1])

    return seq


def symbols_to_text(symbols: List[int], vocab: Dict[int, str]) -> str:
    """Decode symbol sequence to text; skip unknown; dedupe consecutive same token."""
    tokens: List[str] = []
    prev: Optional[str] = None
    for sym in symbols:
        tok = vocab.get(sym)
        if tok and tok != prev:
            tokens.append(tok)
            prev = tok
    return " ".join(tokens)
