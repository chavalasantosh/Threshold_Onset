#!/usr/bin/env python3
# pylint: disable=wrong-import-position
"""
Identity Permission Profile

Counts allowed vs refused self-transitions for each identity symbol.
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


def compute_permission_profile(phase4_output, phase3_metrics, phase2_metrics):
    """
    Compute permission profile for each identity symbol.

    For each symbol, count:
    - allowed self-transitions (relation exists in graph)
    - refused self-transitions (relation does not exist)

    Returns dictionary mapping symbol -> (allowed_count, refused_count)
    """
    observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)

    # Get all identity symbols
    symbol_to_identity = phase4_output.get('symbol_to_identity', {})

    # Get graph structure
    adjacency = observer.adjacency

    # Count permissions per symbol
    permission_profile = {}

    for symbol, identity_hash in symbol_to_identity.items():
        # Check if self-transition is allowed (relation exists)
        relation_exists = identity_hash in adjacency.get(identity_hash, set())

        # For now, we only know refused count from observed refusals
        # We need to check all possible self-transitions

        # Check if self-loop exists in graph
        self_loop_exists = relation_exists

        # Initialize counts
        allowed_count = 0
        refused_count = 0

        if self_loop_exists:
            allowed_count = 1  # Self-transition is allowed
        else:
            refused_count = 1  # Self-transition is refused (structural)

        permission_profile[symbol] = {
            'allowed': allowed_count,
            'refused': refused_count,
            'identity_hash': identity_hash,
            'self_loop_exists': self_loop_exists
        }

    return permission_profile


def count_observed_refusals_per_symbol():
    """Count observed refusals per symbol from all tests."""

    base_text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    # Process once to get structure
    results = process_text_through_phases(
        text=base_text,
        tokenization_method="word",
        num_runs=3
    )

    if results['phase4'] is None:
        return None

    # Get permission profile
    profile = compute_permission_profile(
        results['phase4'],
        results['phase3'],
        results['phase2']
    )

    # Count observed refusals per symbol
    aggregation = aggregate_refusals_from_tests()

    # Count refusals per symbol
    symbol_refusal_counts = defaultdict(int)

    for refusals in aggregation['signature_to_refusals'].values():
        for r in refusals:
            symbol_refusal_counts[r['current_symbol']] += 1

    # Update profile with observed counts
    for symbol, data in profile.items():
        data['observed_refusals'] = symbol_refusal_counts.get(symbol, 0)

    return profile


def main():
    """Compute and report permission profiles."""

    print("=" * 70)
    print("IDENTITY PERMISSION PROFILE")
    print("=" * 70)
    print()
    print("Computing allowed vs refused self-transitions per identity...")
    print()

    profile = count_observed_refusals_per_symbol()

    if profile is None:
        print("Could not compute profile.")
        return

    print("=" * 70)
    print("RAW COUNTS PER IDENTITY SYMBOL")
    print("=" * 70)
    print()

    # Sort by symbol for readability
    sorted_symbols = sorted(profile.keys())

    for symbol in sorted_symbols:
        data = profile[symbol]
        print(f"Symbol {symbol}:")
        print(f"  Allowed self-transitions: {data['allowed']}")
        print(f"  Refused self-transitions (structural): {data['refused']}")
        print(f"  Observed refusals: {data.get('observed_refusals', 0)}")
        print(f"  Self-loop exists in graph: {data['self_loop_exists']}")
        print()

    # Summary counts
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()

    total_allowed = sum(p['allowed'] for p in profile.values())
    total_refused_structural = sum(p['refused'] for p in profile.values())
    total_observed = sum(p.get('observed_refusals', 0) for p in profile.values())

    symbols_with_self_loops = sum(1 for p in profile.values() if p['self_loop_exists'])
    symbols_without_self_loops = len(profile) - symbols_with_self_loops

    print(f"Total identity symbols: {len(profile)}")
    print(f"Symbols with self-loops (allowed): {symbols_with_self_loops}")
    print(f"Symbols without self-loops (refused): {symbols_without_self_loops}")
    print(f"Total allowed self-transitions: {total_allowed}")
    print(f"Total refused self-transitions (structural): {total_refused_structural}")
    print(f"Total observed refusals: {total_observed}")
    print()

    print("=" * 70)
    print("PROFILE COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
