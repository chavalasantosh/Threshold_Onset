#!/usr/bin/env python3
# pylint: disable=wrong-import-position
"""
Scoring System

Adds frequency-based and pressure-based scoring to rank allowed paths.
Mechanical scoring only - no semantics, no learning.

Scores allowed transitions, ranks them, enables selection.
"""

import sys
from pathlib import Path
import random
from collections import Counter, defaultdict

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from integration.continuation_observer import ContinuationObserver
from integration.unified_system import TokenAction


def compute_transition_frequencies(phase4_output, phase3_metrics, phase2_metrics, token_sequences):
    """
    Compute frequency of allowed transitions from token sequences.

    Observes which transitions actually occur and how often.
    Uses ContinuationObserver internal API for residue/symbol mapping.
    Returns:
        - {(from_symbol, to_symbol): frequency_count}
        - {(prev_prev_symbol, prev_symbol, next_symbol): frequency_count} for context
    """
    # pylint: disable=protected-access
    observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)

    transition_counts = Counter()
    context_counts = Counter()  # Track 3-step sequences

    for tokens in token_sequences:
        action = TokenAction(tokens)
        current_identity_hash = None
        current_symbol = None
        prev_symbol = None
        prev_prev_symbol = None

        for _ in range(len(tokens) * 2):
            residue = action()
            next_identity_hash = observer._residue_to_identity_hash(residue)

            if next_identity_hash is None:
                continue

            next_symbol = observer._identity_hash_to_symbol(next_identity_hash)

            if next_symbol is None:
                continue

            if current_identity_hash is not None:
                # Check if transition is allowed
                transition_allowed = observer._check_transition_allowed(
                    current_identity_hash,
                    next_identity_hash
                )

                if transition_allowed:
                    # This is an allowed transition - count it
                    transition_counts[(current_symbol, next_symbol)] += 1

                    # Track 3-step context: (prev_prev, prev, next)
                    if prev_prev_symbol is not None and prev_symbol is not None:
                        context_counts[(prev_prev_symbol, prev_symbol, next_symbol)] += 1

            # Update history
            if current_identity_hash != next_identity_hash:
                prev_prev_symbol = prev_symbol
                prev_symbol = current_symbol
                current_identity_hash = next_identity_hash
                current_symbol = next_symbol

    return dict(transition_counts), dict(context_counts)


def _topology_get(data, key, default=0):
    """Get value from topology data (dict or TopologyData object)."""
    if hasattr(data, key):
        return getattr(data, key, default)
    return data.get(key, default)


def compute_pressure_scores(topology):
    """
    Compute pressure-based scores for symbols.

    Higher pressure (more self-transition attempts) = higher score.
    This represents "urgency" to escape.

    Returns: {symbol: pressure_score}
    """
    scores = {}

    for symbol, data in topology.items():
        attempts = _topology_get(data, 'self_transition_attempts')
        near_refusals = _topology_get(data, 'near_refusal_events')
        appearances = _topology_get(data, 'appearances')

        # Pressure score = attempts + normalized near-refusals
        # More attempts = higher pressure
        pressure_score = attempts + (near_refusals / max(appearances, 1))

        scores[symbol] = pressure_score

    return scores


def compute_input_order_boost(tokens, symbol_to_token):
    """
    Boost transitions that match consecutive pairs (and trigrams) in the input.
    Pure input structure - no external data. Favors natural word order.
    Returns: {(from_symbol, to_symbol): boost_amount}
    """
    boost = defaultdict(float)
    if not tokens or not symbol_to_token:
        return dict(boost)

    # token -> list of symbols (one token can map to multiple symbols)
    token_to_symbols = defaultdict(list)
    for sym, tok in symbol_to_token.items():
        token_to_symbols[tok].append(sym)

    # Input bigrams: consecutive pairs (strong boost for natural flow)
    for i in range(len(tokens) - 1):
        t1, t2 = tokens[i], tokens[i+1]
        s1_list = token_to_symbols.get(t1, [])
        s2_list = token_to_symbols.get(t2, [])
        for s1 in s1_list:
            for s2 in s2_list:
                if s1 != s2:
                    # Stronger boost for early bigrams (preserve sentence start)
                    early_bonus = 2.0 if i < 5 else 1.0
                    boost[(s1, s2)] += 5.0 * early_bonus

    # Input trigrams (continuity)
    for i in range(len(tokens) - 2):
        t1, t2, t3 = tokens[i], tokens[i+1], tokens[i+2]
        for s1 in token_to_symbols.get(t1, []):
            for s2 in token_to_symbols.get(t2, []):
                for s3 in token_to_symbols.get(t3, []):
                    if s2 not in (s1, s3):
                        boost[(s1, s2)] += 2.0
                        boost[(s2, s3)] += 2.0

    # Input 4-grams and 5-grams (longer coherence)
    for i in range(len(tokens) - 3):
        t1, t2, t3, t4 = tokens[i], tokens[i+1], tokens[i+2], tokens[i+3]
        for s1 in token_to_symbols.get(t1, []):
            for s2 in token_to_symbols.get(t2, []):
                for s3 in token_to_symbols.get(t3, []):
                    for s4 in token_to_symbols.get(t4, []):
                        if s2 not in (s1, s3) and s3 not in (s2, s4):
                            boost[(s1, s2)] += 1.0
                            boost[(s2, s3)] += 1.0
                            boost[(s3, s4)] += 1.0

    for i in range(len(tokens) - 4):
        t1, t2, t3, t4, t5 = tokens[i], tokens[i+1], tokens[i+2], tokens[i+3], tokens[i+4]
        for s1 in token_to_symbols.get(t1, []):
            for s2 in token_to_symbols.get(t2, []):
                for s3 in token_to_symbols.get(t3, []):
                    for s4 in token_to_symbols.get(t4, []):
                        for s5 in token_to_symbols.get(t5, []):
                            if len({s1, s2, s3, s4, s5}) >= 4:
                                boost[(s1, s2)] += 0.5
                                boost[(s2, s3)] += 0.5
                                boost[(s3, s4)] += 0.5
                                boost[(s4, s5)] += 0.5

    return dict(boost)


def score_allowed_paths(
    phase4_output, phase3_metrics, phase2_metrics, topology, token_sequences,
    learner=None, symbol_to_token=None
):
    """
    Score all allowed paths using frequency, pressure, context, and input-order boost.

    CONTRACT: path_scores[(from_symbol, to_symbol)] is always a float (scalar).
    Metadata (like context_counts) is stored under special string keys prefixed with '_'.

    When symbol_to_token is provided, transitions matching input word order get a boost
    (no 3rd party - purely from input structure).

    Returns:
        dict: path_scores with structure:
            - {(from_symbol, to_symbol): float} for all allowed transitions
            - {'_context_counts': dict} for context metadata (filtered during iteration)
    """
    # Get transition frequencies and context counts
    frequencies, context_counts = compute_transition_frequencies(
        phase4_output, phase3_metrics, phase2_metrics, token_sequences
    )

    # Input-order boost (consecutive pairs in input = more natural flow)
    input_boost = {}
    if symbol_to_token and token_sequences:
        tokens = token_sequences[0] if token_sequences else []
        input_boost = compute_input_order_boost(tokens, symbol_to_token)

    # Get pressure scores
    pressure_scores = compute_pressure_scores(topology)

    # Build graph of allowed transitions
    observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)

    symbol_to_identity = phase4_output.get('symbol_to_identity', {})
    identity_to_symbol = phase4_output.get('identity_to_symbol', {})

    # Score all allowed transitions
    # CONTRACT: All entries with tuple keys (from, to) must be float scalars
    path_scores = {}

    for from_symbol, from_identity in symbol_to_identity.items():
        # Get all allowed transitions from this symbol
        allowed_targets = observer.adjacency.get(from_identity, set())

        for to_identity in allowed_targets:
            to_symbol = identity_to_symbol.get(to_identity)

            if to_symbol is None:
                continue

            # Compute base score
            # Base: frequency of this transition
            frequency = frequencies.get((from_symbol, to_symbol), 0)

            # Bonus: pressure of source symbol (higher pressure = prefer this path)
            pressure = pressure_scores.get(from_symbol, 0)

            # Learned bias (if learner provided)
            learned_bias = 0.0
            if learner is not None:
                learned_bias = learner.bias((from_symbol, to_symbol))

            # Input-order boost: consecutive pairs in input = more natural
            order_boost = input_boost.get((from_symbol, to_symbol), 0.0)

            # Combined base score - ALWAYS store as float (scalar)
            final_score = float(frequency + (pressure * 0.1) + learned_bias + order_boost)

            path_scores[(from_symbol, to_symbol)] = final_score

    # Store context_counts as metadata under special key (filtered during iteration)
    path_scores['_context_counts'] = context_counts

    return path_scores


def rank_paths_from_symbol(from_symbol, path_scores):
    """
    Rank all allowed paths from a given symbol.

    CONTRACT: Filters out metadata keys (strings starting with '_') to ensure
    only tuple-keyed float values are processed.

    Returns: List of (to_symbol, score) tuples, sorted by score (descending)
    """
    # Filter: Only tuple keys (from, to) with float values
    # Exclude metadata keys like '_context_counts' (string keys)
    actual_path_scores = {k: v for k, v in path_scores.items()
                         if isinstance(k, tuple) and len(k) == 2}

    # CONTRACT: all tuple-keyed values must be scalar floats (no dicts)
    for (f, t), v in actual_path_scores.items():
        assert isinstance(v, float), (
            f"path_scores[({f!r}, {t!r})]: expected float, got {type(v).__name__}"
        )

    paths_from = [(to_symbol, score)
                  for (f, to_symbol), score in actual_path_scores.items()
                  if f == from_symbol]

    # Sort by score descending (scores are guaranteed to be floats)
    paths_from.sort(key=lambda x: x[1], reverse=True)

    return paths_from


def choose_next_path(from_symbol, path_scores, method="highest_score"):
    """
    Choose next path from a symbol based on scoring.

    Args:
        from_symbol: Current symbol
        path_scores: Dictionary of path scores
        method: "highest_score" (deterministic) or "weighted_random" (probabilistic)

    Returns:
        to_symbol or None if no allowed paths
    """
    ranked = rank_paths_from_symbol(from_symbol, path_scores)

    if not ranked:
        return None

    if method == "highest_score":
        # Deterministic: choose highest score
        return ranked[0][0]

    if method == "weighted_random":
        # Probabilistic: choose based on score weights
        symbols = [s for s, _ in ranked]
        scores = [s for _, s in ranked]

        # Normalize scores to probabilities
        total_score = sum(scores)
        if total_score == 0:
            # All scores zero - uniform random
            return random.choice(symbols)

        probabilities = [s / total_score for s in scores]

        # Weighted random choice
        return random.choices(symbols, weights=probabilities, k=1)[0]

    # Default: highest score
    return ranked[0][0]


def main():
    """Test scoring system."""
    from integration.unified_system import process_text_through_phases, tokenize_text_to_actions
    from integration.escape_topology import measure_escape_topology

    text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    continuation_text = "Tokens become actions. Patterns become residues."

    # Process through phases
    results = process_text_through_phases(
        text=text,
        tokenization_method="word",
        num_runs=3
    )

    if results['phase4'] is None:
        print("Phase 4 did not complete.")
        return

    # Measure topology
    _, continuation_tokens = tokenize_text_to_actions(continuation_text, "word")
    topology = measure_escape_topology(
        results['phase4'],
        results['phase3'],
        results['phase2'],
        continuation_tokens
    )

    # Get token sequences for frequency computation
    token_sequences = [results['tokens']]

    # Score paths
    path_scores = score_allowed_paths(
        results['phase4'],
        results['phase3'],
        results['phase2'],
        topology,
        token_sequences
    )

    print("=" * 70)
    print("PATH SCORING")
    print("=" * 70)
    print()

    # Filter out special keys like '_context_counts' before counting/sorting
    actual_path_scores = {k: v for k, v in path_scores.items()
                         if isinstance(k, tuple) and len(k) == 2}

    print(f"Total scored paths: {len(actual_path_scores)}")
    print()

    # Show top scored paths
    print("Top scored paths:")
    top_paths = sorted(actual_path_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    for (from_sym, to_sym), score in top_paths:
        print(f"  {from_sym} → {to_sym}: {score:.4f}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
