#!/usr/bin/env python3
"""
Refusal Signature Aggregation

Counts distinct refusal signatures across all tests.
Mechanical counting only - no interpretation.
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# pylint: disable=wrong-import-position
from integration.test_permuted import record_refusal_test
from integration.observe_refusals import record_refusals


def compute_refusal_signature(refusal):
    """
    Compute refusal signature.

    Returns tuple: (current_symbol, attempted_next_symbol, relation_exists)
    Mechanical only - no interpretation.
    """
    return (
        refusal['current_symbol'],
        refusal['attempted_next_symbol'],
        refusal['relation_exists']
    )


def aggregate_refusals_from_tests():
    """Collect refusals from all tests and aggregate signatures."""

    base_text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    all_refusals = []
    test_metadata = []

    # Test 1: Original continuation
    continuation_text1 = "Tokens become actions. Patterns become residues."
    test1 = record_refusal_test(
        test_name="original",
        base_text=base_text,
        continuation_text=continuation_text1,
        tokenization_method="word",
        permute=False
    )
    if test1 and test1['refusals']:
        all_refusals.extend(test1['refusals'])
        test_metadata.append(('original', 'word', False, len(test1['refusals'])))

    # Test 2: Permuted continuation (seed 42)
    test2 = record_refusal_test(
        test_name="permuted_seed42",
        base_text=base_text,
        continuation_text=continuation_text1,
        tokenization_method="word",
        permute=True,
        seed=42
    )
    if test2 and test2['refusals']:
        all_refusals.extend(test2['refusals'])
        test_metadata.append(('permuted_seed42', 'word', True, len(test2['refusals'])))

    # Test 3: Permuted continuation (seed 123)
    test3 = record_refusal_test(
        test_name="permuted_seed123",
        base_text=base_text,
        continuation_text=continuation_text1,
        tokenization_method="word",
        permute=True,
        seed=123
    )
    if test3 and test3['refusals']:
        all_refusals.extend(test3['refusals'])
        test_metadata.append(('permuted_seed123', 'word', True, len(test3['refusals'])))

    # Test 4: Character tokenization
    test4 = record_refusals(
        test_name="character_tokenization",
        text=base_text,
        continuation_text=continuation_text1,
        tokenization_method="character"
    )
    if test4 and test4['refusals']:
        all_refusals.extend(test4['refusals'])
        test_metadata.append(('character_tokenization', 'character', False, len(test4['refusals'])))

    # Test 5: Longer continuation
    continuation_text2 = (
        "Tokens become actions. Patterns become residues. Structure emerges "
        "naturally. Semantics emerge automatically. No embeddings needed."
    )
    test5 = record_refusals(
        test_name="longer_continuation",
        text=base_text,
        continuation_text=continuation_text2,
        tokenization_method="word"
    )
    if test5 and test5['refusals']:
        all_refusals.extend(test5['refusals'])
        test_metadata.append(('longer_continuation', 'word', False, len(test5['refusals'])))

    # Compute signatures
    signatures = []
    signature_to_refusals = defaultdict(list)

    for refusal in all_refusals:
        signature = compute_refusal_signature(refusal)
        signatures.append(signature)
        signature_to_refusals[signature].append(refusal)

    # Count distinct signatures
    signature_counts = Counter(signatures)

    return {
        'total_refusals': len(all_refusals),
        'distinct_signatures': len(signature_counts),
        'signature_counts': dict(signature_counts),
        'signature_to_refusals': dict(signature_to_refusals),
        'test_metadata': test_metadata
    }


def main():
    """Aggregate refusal signatures and report counts."""

    print("=" * 70)
    print("REFUSAL SIGNATURE AGGREGATION")
    print("=" * 70)
    print()
    print("Collecting refusals from all tests...")
    print()

    results = aggregate_refusals_from_tests()

    print("=" * 70)
    print("RAW COUNTS")
    print("=" * 70)
    print()

    # Total refusals
    print(f"Total refusals collected: {results['total_refusals']}")
    print(f"Distinct refusal signatures: {results['distinct_signatures']}")
    print()

    # Test metadata
    print("Tests run:")
    print("-" * 70)
    for test_name, tokenization, permuted, refusal_count in results['test_metadata']:
        print(f"  {test_name}: {tokenization}, permuted={permuted}, refusals={refusal_count}")
    print()

    # Signature counts
    print("Signature counts:")
    print("-" * 70)
    for signature, count in sorted(
        results['signature_counts'].items(), key=lambda x: x[1], reverse=True
    ):
        current_symbol, attempted_symbol, relation_exists = signature
        print(f"  Signature: ({current_symbol}, {attempted_symbol}, {relation_exists})")
        print(f"    Count: {count}")
        print()

    # Cross-test signature appearance
    print("=" * 70)
    print("SIGNATURE CROSS-TEST APPEARANCE")
    print("=" * 70)
    print()

    # Check which signatures appear in which tests
    for signature, refusals in results['signature_to_refusals'].items():
        current_symbol, attempted_symbol, relation_exists = signature
        print(f"Signature: ({current_symbol}, {attempted_symbol}, {relation_exists})")
        print(f"  Total occurrences: {len(refusals)}")

        # Count occurrences per test (approximate - based on step_index patterns)
        step_indices = [r['step_index'] for r in refusals]
        print(f"  Step indices: {sorted(set(step_indices))}")
        print()

    print("=" * 70)
    print("AGGREGATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
