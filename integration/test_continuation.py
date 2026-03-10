#!/usr/bin/env python3
"""
Test Continuation Observer

Minimal test: one input, observe one refusal.

No theory. Just observation.
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

from integration.unified_system import process_text_through_phases
from integration.continuation_observer import observe_continuation_refusals


def main():
    """Run one test: process text, continue, observe refusal."""

    # Fixed input (one text, one test)
    text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    print("=" * 70)
    print("CONTINUATION OBSERVER TEST")
    print("=" * 70)
    print()
    print("Processing text through Phases 0-4...")
    print()

    # Process through all phases
    results = process_text_through_phases(
        text=text,
        tokenization_method="word",
        num_runs=3  # Small number for testing
    )

    # Check if all phases completed
    if results['phase4'] is None:
        print("Phase 4 did not complete. Cannot observe continuation.")
        return

    print()
    print("=" * 70)
    print("OBSERVING CONTINUATION")
    print("=" * 70)
    print()

    # Continue with same text (simulating continuation after Phase 4)
    from integration.unified_system import tokenize_text_to_actions

    continuation_text = "Tokens become actions. Patterns become residues."
    _, continuation_tokens = tokenize_text_to_actions(
        continuation_text,
        tokenization_method="word"
    )

    print(f"Continuation tokens: {len(continuation_tokens)}")
    print(f"Sample: {continuation_tokens[:5]}")
    print()

    # Observe continuation
    refusals = observe_continuation_refusals(
        phase4_output=results['phase4'],
        phase3_metrics=results['phase3'],
        phase2_metrics=results['phase2'],
        continuation_tokens=continuation_tokens,
        max_steps=50
    )

    print("=" * 70)
    print("REFUSALS OBSERVED")
    print("=" * 70)
    print()

    if not refusals:
        print("No refusals observed.")
        print("This could mean:")
        print("  - All continuations were allowed")
        print("  - Or structure is too loose to constrain")
    else:
        print(f"Total refusals: {len(refusals)}")
        print()
        print("First refusal:")
        print("-" * 70)
        refusal = refusals[0]
        print(f"Step index: {refusal['step_index']}")
        print(f"Current symbol: {refusal['current_symbol']}")
        print(f"Attempted next symbol: {refusal['attempted_next_symbol']}")
        print(f"Reason for refusal: {refusal['reason_for_refusal']}")
        print("-" * 70)

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
