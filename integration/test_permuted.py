#!/usr/bin/env python3
"""
Test Permuted Continuation

Same input, same tokenization, slightly permuted continuation order.
Observe how refusals change (appear/disappear/shift).
"""

import sys
from pathlib import Path
import random

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from integration.unified_system import process_text_through_phases, tokenize_text_to_actions
from integration.continuation_observer import observe_continuation_refusals


def permute_tokens(tokens, seed=42):
    """Slightly permute token order - mechanical only."""
    tokens_copy = tokens.copy()
    random.seed(seed)
    # Swap adjacent pairs (minimal permutation)
    for i in range(0, len(tokens_copy) - 1, 2):
        if random.random() > 0.5:
            tokens_copy[i], tokens_copy[i + 1] = tokens_copy[i + 1], tokens_copy[i]
    return tokens_copy


def record_refusal_test(test_name, base_text, continuation_text, tokenization_method, permute=False, seed=42):
    """Process, continue, record refusals. Facts only."""

    # Process through Phases 0-4
    results = process_text_through_phases(
        text=base_text,
        tokenization_method=tokenization_method,
        num_runs=3
    )

    if results['phase4'] is None:
        return None

    # Continue with continuation text
    _, continuation_tokens = tokenize_text_to_actions(
        continuation_text,
        tokenization_method=tokenization_method
    )

    # Permute if requested
    if permute:
        continuation_tokens = permute_tokens(continuation_tokens, seed=seed)

    # Observe continuation
    refusals = observe_continuation_refusals(
        phase4_output=results['phase4'],
        phase3_metrics=results['phase3'],
        phase2_metrics=results['phase2'],
        continuation_tokens=continuation_tokens,
        max_steps=100
    )

    return {
        'test_name': test_name,
        'refusals': refusals,
        'permuted': permute
    }


def main():
    """Run permuted continuation tests."""

    # Base text (same for all)
    base_text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    # Base continuation (same as before)
    continuation_text = "Tokens become actions. Patterns become residues."

    # Test 1: Original (no permutation)
    print("TEST 1: Original continuation")
    print("-" * 70)
    test1 = record_refusal_test(
        test_name="original",
        base_text=base_text,
        continuation_text=continuation_text,
        tokenization_method="word",
        permute=False
    )

    # Test 2: Permuted (seed 42)
    print("\nTEST 2: Permuted continuation (seed 42)")
    print("-" * 70)
    test2 = record_refusal_test(
        test_name="permuted_seed42",
        base_text=base_text,
        continuation_text=continuation_text,
        tokenization_method="word",
        permute=True,
        seed=42
    )

    # Test 3: Permuted (seed 123)
    print("\nTEST 3: Permuted continuation (seed 123)")
    print("-" * 70)
    test3 = record_refusal_test(
        test_name="permuted_seed123",
        base_text=base_text,
        continuation_text=continuation_text,
        tokenization_method="word",
        permute=True,
        seed=123
    )

    # Output: Raw refusals only
    print("\n" + "=" * 70)
    print("RAW REFUSALS - PERMUTED CONTINUATION")
    print("=" * 70)
    print()

    all_results = [test1, test2, test3]

    for result in all_results:
        if result is None:
            continue

        print(f"Test: {result['test_name']} (permuted: {result['permuted']})")
        print("-" * 70)
        refusals = result['refusals']

        if not refusals:
            print("No refusals observed.")
        else:
            print(f"Total refusals: {len(refusals)}")
            for i, refusal in enumerate(refusals, 1):
                print(f"\nRefusal {i}:")
                print(f"  step_index: {refusal['step_index']}")
                print(f"  current_symbol: {refusal['current_symbol']}")
                print(f"  attempted_next_symbol: {refusal['attempted_next_symbol']}")
                print(f"  reason_for_refusal: {refusal['reason_for_refusal']}")
                print(f"  relation_exists: {refusal['relation_exists']}")

        print()

    print("=" * 70)
    print("OBSERVATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
