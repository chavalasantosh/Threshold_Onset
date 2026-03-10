#!/usr/bin/env python3
"""
Observe Refusals - Multiple Variations

Records raw refusals only. No interpretation.
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from integration.unified_system import process_text_through_phases, tokenize_text_to_actions
from integration.continuation_observer import observe_continuation_refusals


def record_refusals(test_name, text, continuation_text, tokenization_method):
    """Process text, continue, record refusals. Facts only."""

    # Process through Phases 0-4
    results = process_text_through_phases(
        text=text,
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
        'refusals': refusals
    }


def main():
    """Run multiple tests, record refusals only."""

    # Base text (same for all tests)
    base_text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    # Test 1: Different continuation text
    print("TEST 1: Different continuation text")
    print("-" * 70)
    test1 = record_refusals(
        test_name="different_continuation",
        text=base_text,
        continuation_text="Meaning emerges from refusal. Structure constrains continuation.",
        tokenization_method="word"
    )

    # Test 2: Same continuation, different tokenization (word -> character)
    print("\nTEST 2: Same continuation, character tokenization")
    print("-" * 70)
    test2 = record_refusals(
        test_name="character_tokenization",
        text=base_text,
        continuation_text="Tokens become actions. Patterns become residues.",
        tokenization_method="character"
    )

    # Test 3: Same everything, longer continuation
    print("\nTEST 3: Same everything, longer continuation")
    print("-" * 70)
    test3 = record_refusals(
        test_name="longer_continuation",
        text=base_text,
        continuation_text="Tokens become actions. Patterns become residues. Structure emerges naturally. Semantics emerge automatically. No embeddings needed.",
        tokenization_method="word"
    )

    # Output: Raw refusals only
    print("\n" + "=" * 70)
    print("RAW REFUSALS RECORDED")
    print("=" * 70)
    print()

    all_results = [test1, test2, test3]

    for result in all_results:
        if result is None:
            continue

        print(f"Test: {result['test_name']}")
        print("-" * 70)
        refusals = result['refusals']

        if not refusals:
            print("No refusals observed.")
        else:
            print(f"Total refusals: {len(refusals)}")
            for i, refusal in enumerate(refusals[:5], 1):  # Show first 5
                print(f"\nRefusal {i}:")
                print(f"  step_index: {refusal['step_index']}")
                print(f"  current_symbol: {refusal['current_symbol']}")
                print(f"  attempted_next_symbol: {refusal['attempted_next_symbol']}")
                print(f"  reason_for_refusal: {refusal['reason_for_refusal']}")

        print()

    print("=" * 70)
    print("OBSERVATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
