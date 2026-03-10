#!/usr/bin/env python3
# pylint: disable=wrong-import-position,too-many-locals,too-many-branches,too-many-statements
"""
Escape Topology Measurement

For each symbol i:
- How often does it attempt self-transition?
- How often does it get near refusal?
- How many distinct escape paths does it have?
- How concentrated are those paths?

Measures degrees of freedom under constraint.
Mechanical measurement only - no interpretation.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import math

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from integration.unified_system import (
    process_text_through_phases,
    tokenize_text_to_actions,
    TokenAction,
)
from integration.continuation_observer import ContinuationObserver


def measure_escape_topology(
    phase4_output, phase3_metrics, phase2_metrics, continuation_tokens, max_steps=200
):
    """
    Measure escape topology for each symbol.

    For each symbol i:
    - self_transition_attempts: count of i → i attempts
    - appearances: count of times symbol i appears
    - escape_paths: dict of j → count (what follows i when i ≠ j)
    - distinct_escape_paths: number of distinct symbols that follow i
    - escape_concentration: concentration metric of escape paths

    Returns dict: symbol → topology data
    """
    observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)

    # Convert tokens to residues
    tokens = list(continuation_tokens)
    action = TokenAction(tokens)

    # Track topology data per symbol
    topology = defaultdict(lambda: {
        'self_transition_attempts': 0,
        'appearances': 0,
        'escape_paths': Counter(),
        'near_refusal_events': 0  # Times when i appears and could self-repeat
    })

    # Build sequence and analyze
    current_identity_hash = None
    current_symbol = None
    symbol_sequence = []

    for step in range(max_steps):
        if step >= len(tokens) * 3:  # Allow multiple passes
            break

        residue = action()
        next_identity_hash = observer._residue_to_identity_hash(residue)  # pylint: disable=protected-access

        if next_identity_hash is None:
            continue

        next_symbol = observer._identity_hash_to_symbol(next_identity_hash)  # pylint: disable=protected-access

        if next_symbol is None:
            continue

        # Record appearance
        topology[next_symbol]['appearances'] += 1

        # Check transitions
        if current_symbol is not None:
            # Near-refusal event: current symbol appeared, now something follows
            topology[current_symbol]['near_refusal_events'] += 1

            if current_symbol == next_symbol:
                # Self-transition attempted
                topology[current_symbol]['self_transition_attempts'] += 1
            else:
                # Escape path: current → next (different symbol)
                topology[current_symbol]['escape_paths'][next_symbol] += 1

        # Update current
        if current_identity_hash != next_identity_hash:
            current_identity_hash = next_identity_hash
            current_symbol = next_symbol
            symbol_sequence.append(next_symbol)

    # Compute topology metrics for each symbol
    for symbol in topology:
        data = topology[symbol]

        # Distinct escape paths
        data['distinct_escape_paths'] = len(data['escape_paths'])

        # Escape concentration (entropy-based)
        total_escapes = sum(data['escape_paths'].values())
        if total_escapes > 0:
            # Compute entropy (higher entropy = less concentrated)
            probabilities = [count / total_escapes for count in data['escape_paths'].values()]
            entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in probabilities)
            n_paths = len(data['escape_paths'])
            max_entropy = math.log2(n_paths) if n_paths > 1 else 0

            # Concentration = 1 - normalized entropy (1 = fully concentrated, 0 = uniform)
            if max_entropy > 0:
                data['escape_concentration'] = 1 - (entropy / max_entropy)
            else:
                data['escape_concentration'] = 1.0 if total_escapes > 0 else 0.0
        else:
            data['escape_concentration'] = 0.0

    return dict(topology)


def main():
    """Measure and report escape topology."""

    base_text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    continuation_text = "Tokens become actions. Patterns become residues."

    print("=" * 70)
    print("ESCAPE TOPOLOGY MEASUREMENT")
    print("=" * 70)
    print()

    # Process through phases
    results = process_text_through_phases(
        text=base_text,
        tokenization_method="word",
        num_runs=3
    )

    if results['phase4'] is None:
        print("Phase 4 did not complete.")
        return

    # Continue with continuation text
    _, continuation_tokens = tokenize_text_to_actions(
        continuation_text,
        tokenization_method="word"
    )

    print("Measuring escape topology...")
    print()

    # Measure topology
    topology = measure_escape_topology(
        results['phase4'],
        results['phase3'],
        results['phase2'],
        continuation_tokens,
        max_steps=200
    )

    print("=" * 70)
    print("ESCAPE TOPOLOGY RESULTS")
    print("=" * 70)
    print()

    # Summary statistics
    symbols_with_attempts = [s for s, d in topology.items() if d['self_transition_attempts'] > 0]
    symbols_with_escapes = [s for s, d in topology.items() if len(d['escape_paths']) > 0]

    print(f"Total symbols observed: {len(topology)}")
    print(f"Symbols with self-transition attempts: {len(symbols_with_attempts)}")
    print(f"Symbols with escape paths: {len(symbols_with_escapes)}")
    print()

    # Per-symbol topology
    print("=" * 70)
    print("PER-SYMBOL TOPOLOGY")
    print("=" * 70)
    print()

    # Sort by self-transition attempts (descending)
    sorted_symbols = sorted(topology.items(),
                           key=lambda x: (x[1]['self_transition_attempts'],
                                         len(x[1]['escape_paths'])),
                           reverse=True)

    for symbol, data in sorted_symbols:
        if data['appearances'] == 0:
            continue

        print(f"Symbol {symbol}:")
        print(f"  Appearances: {data['appearances']}")
        print(f"  Self-transition attempts: {data['self_transition_attempts']}")
        print(f"  Near-refusal events: {data['near_refusal_events']}")
        print(f"  Distinct escape paths: {data['distinct_escape_paths']}")
        print(f"  Escape concentration: {data['escape_concentration']:.4f}")

        if data['escape_paths']:
            print("  Escape paths:")
            # Show top 3 escape paths
            top_paths = data['escape_paths'].most_common(3)
            for escape_symbol, count in top_paths:
                print(f"    → {escape_symbol}: {count} times")
        else:
            print("  Escape paths: none")

        print()

    # Statistics
    print("=" * 70)
    print("TOPOLOGY STATISTICS")
    print("=" * 70)
    print()

    all_attempts = [d['self_transition_attempts'] for d in topology.values()]
    all_distinct_paths = [
        d['distinct_escape_paths'] for d in topology.values()
        if d['distinct_escape_paths'] > 0
    ]
    all_concentrations = [
        d['escape_concentration'] for d in topology.values()
        if d['escape_concentration'] > 0
    ]

    if all_attempts:
        min_a, max_a, total_a = min(all_attempts), max(all_attempts), sum(all_attempts)
        print(f"Self-transition attempts: min={min_a}, max={max_a}, total={total_a}")

    if all_distinct_paths:
        min_p, max_p = min(all_distinct_paths), max(all_distinct_paths)
        avg = sum(all_distinct_paths) / len(all_distinct_paths)
        print(f"Distinct escape paths: min={min_p}, max={max_p}, avg={avg:.2f}")

    if all_concentrations:
        min_c, max_c = min(all_concentrations), max(all_concentrations)
        avg = sum(all_concentrations) / len(all_concentrations)
        print(f"Escape concentration: min={min_c:.4f}, max={max_c:.4f}, avg={avg:.4f}")

    print()
    print("=" * 70)
    print("MEASUREMENT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
