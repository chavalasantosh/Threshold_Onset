#!/usr/bin/env python3
# pylint: disable=wrong-import-position,protected-access
"""
Near-Refusal Observer

Measures distance from violation:
- Which identities approach self-continuation?
- How often does system approach i → i before diverting?
- What sequences hover near refusal without triggering?

Mechanical observation only - no interpretation.
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from integration.unified_system import process_text_through_phases, tokenize_text_to_actions
from integration.continuation_observer import ContinuationObserver


def observe_near_refusals(phase4_output, phase3_metrics, phase2_metrics, continuation_tokens):
    """
    Observe sequences that approach self-transition but don't trigger it.

    Tracks:
    - Symbols that appear before a different symbol (near self-transition avoided)
    - Patterns of what follows identities that might self-repeat
    - Frequency of approaching self-transition

    Returns counts and patterns - no interpretation.
    """
    from integration.unified_system import TokenAction

    observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)

    # Convert tokens to residues
    tokens = list(continuation_tokens)
    action = TokenAction(tokens)

    # Track sequences
    symbol_sequence = []
    identity_hash_sequence = []

    # Map residues to identity hashes
    current_identity_hash = None
    current_symbol = None

    # Build sequence
    for step in range(len(tokens) * 2):  # Process tokens multiple times if needed
        if step >= len(tokens) * 2:
            break

        residue = action()
        next_identity_hash = observer._residue_to_identity_hash(residue)

        if next_identity_hash is None:
            continue

        next_symbol = observer._identity_hash_to_symbol(next_identity_hash)

        if next_symbol is None:
            continue

        # Check transition (but don't stop on refusal - just record)
        if current_identity_hash is not None:
            transition_allowed = observer._check_transition_allowed(
                current_identity_hash,
                next_identity_hash
            )

            if not transition_allowed:
                # This is a refusal - record it but continue building sequence
                pass
            else:
                # Transition allowed - add to sequence
                symbol_sequence.append(current_symbol)
                identity_hash_sequence.append(current_identity_hash)

        # Update current
        if current_identity_hash != next_identity_hash:  # Only update on change
            current_identity_hash = next_identity_hash
            current_symbol = next_symbol

    # Analyze near-refusals
    # Count: how often does symbol i appear, then symbol j (where j ≠ i)
    # This is "approaching self-transition but diverting"

    near_refusal_counts = defaultdict(int)  # (i, j) where i appears, then j appears (j ≠ i)
    symbol_follows = defaultdict(list)  # i -> [j1, j2, ...] what follows i

    for i in range(len(symbol_sequence) - 1):
        current = symbol_sequence[i]
        next_sym = symbol_sequence[i + 1]

        if current != next_sym:
            # Near-refusal: current could have self-repeated, but didn't
            near_refusal_counts[(current, next_sym)] += 1
            symbol_follows[current].append(next_sym)

    # Count self-transition attempts (symbol appears, then same symbol attempted)
    self_transition_attempts = defaultdict(int)

    # Re-analyze to find self-transition attempts
    for step in range(len(tokens) * 2):
        if step >= len(tokens) * 2:
            break

        residue = action()
        next_identity_hash = observer._residue_to_identity_hash(residue)

        if next_identity_hash is None:
            continue

        next_symbol = observer._identity_hash_to_symbol(next_identity_hash)

        if next_symbol is None:
            continue

        if current_symbol is not None:
            if current_symbol == next_symbol:
                # Self-transition attempted
                self_transition_attempts[current_symbol] += 1

        if current_identity_hash != next_identity_hash:
            current_identity_hash = next_identity_hash
            current_symbol = next_symbol

    return {
        'near_refusal_counts': dict(near_refusal_counts),
        'symbol_follows': {k: list(v) for k, v in symbol_follows.items()},
        'self_transition_attempts': dict(self_transition_attempts),
        'symbol_sequence_length': len(symbol_sequence)
    }


def main():
    """Observe near-refusals across continuation tests."""

    base_text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    continuation_text = "Tokens become actions. Patterns become residues."

    print("=" * 70)
    print("NEAR-REFUSAL OBSERVATION")
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

    print("Observing near-refusals...")
    print()

    # Observe near-refusals
    near_data = observe_near_refusals(
        results['phase4'],
        results['phase3'],
        results['phase2'],
        continuation_tokens
    )

    print("=" * 70)
    print("NEAR-REFUSAL COUNTS")
    print("=" * 70)
    print()

    print(f"Sequence length: {near_data['symbol_sequence_length']}")
    print()

    # Self-transition attempts
    print("Self-transition attempts (symbol → same symbol):")
    print("-" * 70)
    if near_data['self_transition_attempts']:
        for symbol, count in sorted(near_data['self_transition_attempts'].items()):
            print(f"  Symbol {symbol}: {count} attempts")
    else:
        print("  None observed")
    print()

    # Near-refusal patterns (what follows each symbol)
    print("Near-refusal patterns (symbol i → symbol j, where j ≠ i):")
    print("-" * 70)
    symbol_follows = near_data['symbol_follows']

    for symbol in sorted(symbol_follows.keys()):
        follows = symbol_follows[symbol]
        if follows:
            follow_counts = Counter(follows)
            print(f"  Symbol {symbol} followed by:")
            for follow_symbol, count in sorted(follow_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    → {follow_symbol}: {count} times")
    print()

    # Top near-refusal transitions
    print("Top near-refusal transitions (most frequent i → j, j ≠ i):")
    print("-" * 70)
    near_counts = near_data['near_refusal_counts']
    if near_counts:
        top_transitions = sorted(near_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for (i, j), count in top_transitions:
            print(f"  {i} → {j}: {count} occurrences")
    else:
        print("  None observed")
    print()

    print("=" * 70)
    print("OBSERVATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
