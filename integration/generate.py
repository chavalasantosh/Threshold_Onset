#!/usr/bin/env python3
"""
Generation Module

Generates symbol sequences using constraint-aware decoding.

This is the core generation loop:
- Use constraint graph (Phase 3 relations)
- Score allowed paths (frequency + pressure)
- Select next symbol deterministically or probabilistically
- Generate sequences without self-repetition
"""

import math
import random
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from integration.continuation_observer import ContinuationObserver


def _classify_transition_outcome(
    observer,
    current_identity,
    next_identity,
    next_symbol,
    recent_symbols,
):
    """Classify transition outcome for learner feedback."""
    if current_identity is None or next_identity is None:
        return "dead_end"

    allowed_from_current = observer.adjacency.get(current_identity, set())
    if next_identity not in allowed_from_current:
        return "refusal"

    if not observer.adjacency.get(next_identity, set()):
        return "dead_end"

    if next_symbol in recent_symbols[-3:]:
        return "loop"

    return "ok"


def generate_sequence(
    start_symbol,
    steps,
    phase4_output,
    phase3_metrics,
    phase2_metrics,
    path_scores,
    method="highest_score",
    temperature=0.7,
    learner=None
):
    """
    Generate a symbol sequence using constraint-aware decoding.

    Args:
        start_symbol: Starting symbol (int)
        steps: Number of steps to generate
        phase4_output: Phase 4 metrics (symbol mappings)
        phase3_metrics: Phase 3 metrics (relation graph)
        phase2_metrics: Phase 2 metrics (identity mappings)
        path_scores: Dictionary of {(from_symbol, to_symbol): score}
        method: "highest_score" (deterministic) or "weighted_random" (probabilistic)

    Returns:
        List of symbols [start_symbol, ...]
    """
    observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)

    symbol_to_identity = phase4_output.get('symbol_to_identity', {})
    identity_to_symbol = phase4_output.get('identity_to_symbol', {})

    # Initialize sequence with 2-step memory
    sequence = [start_symbol]
    current_symbol = start_symbol
    prev_symbol = None  # Previous symbol (1 step back)
    prev_prev_symbol = None  # Symbol 2 steps back

    # Check if start symbol exists
    if current_symbol not in symbol_to_identity:
        return sequence

    current_identity = symbol_to_identity[current_symbol]

    for _ in range(steps):
        # Get allowed next identities from graph
        allowed_identities = observer.adjacency.get(current_identity, set())

        if not allowed_identities:
            # No allowed transitions - stop
            break

        # Convert to symbols
        allowed_symbols = []
        for identity in allowed_identities:
            symbol = identity_to_symbol.get(identity)
            if symbol is not None:
                allowed_symbols.append(symbol)

        if not allowed_symbols:
            break

        # Score and choose next symbol (with 2-3 step context + repetition penalty)
        recent_symbols = sequence[-6:] if len(sequence) >= 6 else sequence  # Last 6 for penalty
        next_symbol = _choose_next_from_allowed(
            current_symbol,
            allowed_symbols,
            path_scores,
            method,
            temperature,
            prev_prev_symbol,
            prev_symbol,
            recent_symbols  # Repetition penalty: avoid recently used
        )

        if next_symbol is None:
            break

        # Avoid self-repetition (enforce universal law)
        if next_symbol == current_symbol:
            next_symbol = _choose_next_from_allowed(
                current_symbol,
                [s for s in allowed_symbols if s != current_symbol],
                path_scores,
                method,
                temperature,
                prev_prev_symbol,
                prev_symbol,
                recent_symbols
            )
            if next_symbol is None:
                break

        # Observe transition for learning
        transition = (current_symbol, next_symbol)
        if learner is not None:
            next_identity = symbol_to_identity.get(next_symbol)
            outcome = _classify_transition_outcome(
                observer,
                current_identity,
                next_identity,
                next_symbol,
                recent_symbols,
            )
            learner.observe(transition, outcome)

        # Update with memory
        sequence.append(next_symbol)
        prev_prev_symbol = prev_symbol
        prev_symbol = current_symbol
        current_symbol = next_symbol
        current_identity = symbol_to_identity.get(current_symbol)

        if current_identity is None:
            break

    return sequence


def _choose_next_from_allowed(
    from_symbol,
    allowed_symbols,
    path_scores,
    method,
    temperature=0.7,
    prev_prev_symbol=None,
    prev_symbol=None,
    recent_symbols=None,
):
    """Choose next symbol using scoring with temperature, context, and repetition penalty."""
    if not allowed_symbols:
        return None

    recent_symbols = recent_symbols or []

    # Extract context_counts if available
    context_counts = path_scores.get('_context_counts', {})

    # Get scores for allowed paths
    scored_paths = []
    for to_symbol in allowed_symbols:
        score = path_scores.get((from_symbol, to_symbol), 0.0)

        # Repetition penalty: penalize symbols used recently (our own logic)
        if to_symbol in recent_symbols:
            idx = recent_symbols.index(to_symbol)
            dist = len(recent_symbols) - idx  # How recent (1 = just used)
            penalty = 0.3 ** dist  # Stronger for more recent
            score *= (1.0 - penalty)

        # Context-conditioned scoring: reward continuity, penalize loops
        if prev_prev_symbol is not None and prev_symbol is not None:
            # Check 3-step context: (prev_prev, prev, next)
            context_key = (prev_prev_symbol, prev_symbol, to_symbol)
            context_freq = context_counts.get(context_key, 0)

            # Reward if this 3-step sequence was observed (continuity)
            if context_freq > 0:
                score *= (1.0 + context_freq * 0.1)  # Boost for observed continuity

            # Strong penalty for going back 2 steps (ping-pong loop)
            if to_symbol == prev_prev_symbol:
                score *= 0.2

        # Additional penalty: avoid immediate return to previous symbol
        if prev_symbol is not None and to_symbol == prev_symbol:
            score *= 0.3  # Penalty for immediate repeat

        scored_paths.append((to_symbol, score))

    # Sort by score descending
    scored_paths.sort(key=lambda x: x[1], reverse=True)

    if method == "highest_score":
        # Deterministic: choose highest score
        return scored_paths[0][0] if scored_paths else None

    if method == "weighted_random" or temperature != 1.0:
        # Probabilistic: weighted random based on temperature-scaled scores
        symbols = [s for s, _ in scored_paths]
        scores = [max(s, 0.0) for _, s in scored_paths]  # Ensure non-negative

        # Apply temperature scaling with overflow guard (log-sum-exp stable softmax)
        if temperature > 0:
            scaled_scores = [s / temperature for s in scores]
            # Stable softmax: subtract max before exp to prevent overflow
            max_s = max(scaled_scores) if scaled_scores else 0.0
            exp_scores = [math.exp(min(s - max_s, 700.0)) for s in scaled_scores]
            total = sum(exp_scores)
            if total > 0:
                probabilities = [e / total for e in exp_scores]
            else:
                probabilities = [1.0 / len(symbols)] * len(symbols)
        else:
            # Temperature = 0: deterministic (highest score)
            return scored_paths[0][0] if scored_paths else None

        # Weighted random choice
        return random.choices(symbols, weights=probabilities, k=1)[0]

    # Default: highest score
    return scored_paths[0][0] if scored_paths else None


def generate_multiple_seeds(
    seed_symbols,
    steps_per_seed,
    phase4_output,
    phase3_metrics,
    phase2_metrics,
    path_scores,
    method="highest_score"
):
    """Generate sequences from multiple starting symbols."""
    sequences = {}

    for seed in seed_symbols:
        seq = generate_sequence(
            seed,
            steps_per_seed,
            phase4_output,
            phase3_metrics,
            phase2_metrics,
            path_scores,
            method
        )
        sequences[seed] = seq

    return sequences


if __name__ == "__main__":
    # Test generation.
    print("=" * 70)
    print("SYMBOL SEQUENCE GENERATION")
    print("=" * 70)
    print()
    print("This module generates sequences using constraint-aware decoding.")
    print("Run from run_complete.py or main_complete.py to see full pipeline.")
    print()
