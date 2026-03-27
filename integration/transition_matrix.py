#!/usr/bin/env python3
"""
Transition Permission Matrix

For all identity pairs (i → j):
- allowed (relation exists in graph)
- forbidden (no relation)
- observed (count from continuation tests)

Mechanical counting only - no interpretation.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from integration.unified_system import process_text_through_phases
from integration.continuation_observer import ContinuationObserver
from integration.refusal_signatures import aggregate_refusals_from_tests


def build_transition_matrix(phase4_output, phase3_metrics):
    """
    Build transition permission matrix.

    For each pair (i → j), record:
    - allowed: relation exists in graph (1) or not (0)
    - forbidden: relation does not exist (1) or exists (0)
    - observed: count from actual continuation tests

    Returns dictionary: {(i, j): {'allowed': 0/1, 'forbidden': 0/1, 'observed': count}}
    """
    # Get identity symbols
    symbol_to_identity = phase4_output.get('symbol_to_identity', {})
    identity_to_symbol = phase4_output.get('identity_to_symbol', {})

    # Build observer to access graph
    # Use dummy phase2_metrics - we only need graph structure
    dummy_phase2 = {'identity_mappings': {}}
    observer = ContinuationObserver(phase4_output, phase3_metrics, dummy_phase2)
    adjacency = observer.adjacency

    # Get all symbols
    symbols = sorted(symbol_to_identity.keys())

    # Build matrix
    matrix = {}

    for i in symbols:
        for j in symbols:
            # Get identity hashes
            identity_i = symbol_to_identity[i]
            identity_j = symbol_to_identity[j]

            # Check if relation exists in graph
            relation_exists = identity_j in adjacency.get(identity_i, set())

            # Record in matrix
            matrix[(i, j)] = {
                'allowed': 1 if relation_exists else 0,
                'forbidden': 0 if relation_exists else 1,
                'observed': 0  # Will be filled from tests
            }

    return matrix, symbols


def count_observed_transitions(matrix, symbols):
    """Count observed transitions and refusals from all tests."""

    # Aggregate refusals from all tests
    aggregation = aggregate_refusals_from_tests()

    # Count transitions and refusals
    transition_counts = defaultdict(int)
    refusal_counts = defaultdict(int)

    # Process all refusals
    for refusal_list in aggregation['signature_to_refusals'].values():
        for refusal in refusal_list:
            current = refusal['current_symbol']
            attempted = refusal['attempted_next_symbol']
            refusal_counts[(current, attempted)] += 1

    # For now, we only have refusal data
    # We don't have successful transition counts
    # So 'observed' will only count refusals

    for (i, j), count in refusal_counts.items():
        if (i, j) in matrix:
            # Refusals are "observed" forbidden transitions
            # But we don't track successful transitions yet
            matrix[(i, j)]['observed'] = count

    return matrix


def main():
    """Build and output transition permission matrix."""

    print("=" * 70)
    print("TRANSITION PERMISSION MATRIX")
    print("=" * 70)
    print()
    print("Building matrix from Phase 3 graph structure...")
    print()

    # Process text to get structure
    base_text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    results = process_text_through_phases(
        text=base_text,
        tokenization_method="word",
        num_runs=3
    )

    if results['phase4'] is None:
        print("Phase 4 did not complete. Cannot build matrix.")
        return

    # Build matrix
    matrix, symbols = build_transition_matrix(
        results['phase4'],
        results['phase3']
    )

    # Count observed transitions/refusals
    matrix = count_observed_transitions(matrix, symbols)

    print("=" * 70)
    print("MATRIX SUMMARY")
    print("=" * 70)
    print()

    # Count statistics
    total_pairs = len(matrix)
    allowed_pairs = sum(1 for m in matrix.values() if m['allowed'] == 1)
    forbidden_pairs = sum(1 for m in matrix.values() if m['forbidden'] == 1)
    observed_refusals = sum(1 for m in matrix.values() if m['observed'] > 0)
    total_observed_count = sum(m['observed'] for m in matrix.values())

    print(f"Total identity pairs: {total_pairs}")
    print(f"Allowed transitions: {allowed_pairs}")
    print(f"Forbidden transitions: {forbidden_pairs}")
    print(f"Pairs with observed refusals: {observed_refusals}")
    print(f"Total observed refusal count: {total_observed_count}")
    print()

    # Show matrix for pairs with observations or self-transitions
    print("=" * 70)
    print("TRANSITION MATRIX (Self-transitions and Observed)")
    print("=" * 70)
    print()
    print(f"{'i → j':<10} {'allowed':<10} {'forbidden':<12} {'observed':<10}")
    print("-" * 70)

    # Show self-transitions first
    for i in symbols:
        pair = (i, i)
        if pair in matrix:
            m = matrix[pair]
            print(f"{i} → {i:<7} {m['allowed']:<10} {m['forbidden']:<12} {m['observed']:<10}")

    print()
    print("-" * 70)
    print("Observed refusals (non-self):")
    print("-" * 70)

    # Show observed refusals (non-self)
    observed_non_self = [(pair, m) for pair, m in matrix.items()
                         if m['observed'] > 0 and pair[0] != pair[1]]

    if observed_non_self:
        for (i, j), m in sorted(observed_non_self):
            print(f"{i} → {j:<7} {m['allowed']:<10} {m['forbidden']:<12} {m['observed']:<10}")
    else:
        print("None")

    print()
    print("=" * 70)
    print("FULL MATRIX (Sample - first 10 symbols)")
    print("=" * 70)
    print()
    print(f"{'i → j':<10} {'allowed':<10} {'forbidden':<12} {'observed':<10}")
    print("-" * 70)

    # Show sample of full matrix (first 10 symbols)
    sample_symbols = symbols[:10]
    for i in sample_symbols:
        for j in sample_symbols:
            pair = (i, j)
            if pair in matrix:
                m = matrix[pair]
                if m['allowed'] == 1 or m['observed'] > 0:  # Only show allowed or observed
                    print(f"{i} → {j:<7} {m['allowed']:<10} {m['forbidden']:<12} {m['observed']:<10}")

    print()
    print("=" * 70)
    print("MATRIX COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
