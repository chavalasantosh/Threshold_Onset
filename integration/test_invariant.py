#!/usr/bin/env python3
"""
Test Invariant: No Self-Transition Law

Test if "no self-transition" law holds across:
- Different texts
- Different domains
- Different tokenization granularities

Mechanical checking only - no interpretation.
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from integration.unified_system import process_text_through_phases
from integration.transition_matrix import build_transition_matrix


def test_no_self_transition_law(phase4_output, phase3_metrics):
    """
    Check if no self-transition law holds.

    Returns:
        - all_self_forbidden: True if all self-transitions are forbidden
        - self_transition_count: Number of self-transitions
        - forbidden_count: Number of forbidden self-transitions
    """
    matrix, symbols = build_transition_matrix(phase4_output, phase3_metrics)

    # Check self-transitions
    self_transitions = [(i, i) for i in symbols]
    forbidden_self = sum(1 for pair in self_transitions
                         if pair in matrix and matrix[pair]['forbidden'] == 1)

    all_self_forbidden = forbidden_self == len(self_transitions)

    return {
        'all_self_forbidden': all_self_forbidden,
        'self_transition_count': len(self_transitions),
        'forbidden_count': forbidden_self,
        'total_symbols': len(symbols)
    }


def main():
    """Test invariant across different inputs."""

    # Test inputs - different texts, domains, styles
    test_cases = [
        {
            'name': 'original_philosophy',
            'text': """
            Action before knowledge.
            Function stabilizes before meaning appears.
            Structure emerges before language exists.
            """,
            'tokenization': 'word'
        },
        {
            'name': 'technical_programming',
            'text': """
            Code compiles before execution.
            Syntax checks before runtime.
            Types validate before execution.
            Functions define before calling.
            """,
            'tokenization': 'word'
        },
        {
            'name': 'literary_text',
            'text': """
            The moon rises over mountains.
            Stars twinkle in dark sky.
            Waves crash on shore.
            Wind whispers through trees.
            """,
            'tokenization': 'word'
        },
        {
            'name': 'character_tokenization',
            'text': """
            Action before knowledge.
            Structure emerges naturally.
            """,
            'tokenization': 'character'
        },
        {
            'name': 'grammar_tokenization',
            'text': """
            Function stabilizes. Meaning appears. Language exists.
            Tokens become actions. Patterns become residues.
            """,
            'tokenization': 'grammar'
        },
        {
            'name': 'short_text',
            'text': 'Hello world. Hello again.',
            'tokenization': 'word'
        }
    ]

    print("=" * 70)
    print("TESTING INVARIANT: NO SELF-TRANSITION LAW")
    print("=" * 70)
    print()
    print("Testing across different texts and tokenizations...")
    print()

    results = []

    for test_case in test_cases:
        print(f"Test: {test_case['name']}")
        print(f"  Text: {test_case['text'][:50]}...")
        print(f"  Tokenization: {test_case['tokenization']}")
        print("-" * 70)

        try:
            # Process through phases
            phase_results = process_text_through_phases(
                text=test_case['text'],
                tokenization_method=test_case['tokenization'],
                num_runs=3
            )

            if phase_results['phase4'] is None:
                print(f"  Status: Phase 4 did not complete")
                results.append({
                    'name': test_case['name'],
                    'status': 'phase4_failed',
                    'result': None
                })
                print()
                continue

            # Test invariant
            invariant_result = test_no_self_transition_law(
                phase_results['phase4'],
                phase_results['phase3']
            )

            results.append({
                'name': test_case['name'],
                'status': 'success',
                'result': invariant_result
            })

            print(f"  Total symbols: {invariant_result['total_symbols']}")
            print(f"  Self-transitions: {invariant_result['self_transition_count']}")
            print(f"  Forbidden self-transitions: {invariant_result['forbidden_count']}")
            print(f"  All self-transitions forbidden: {invariant_result['all_self_forbidden']}")
            print()

        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                'name': test_case['name'],
                'status': 'error',
                'error': str(e)
            })
            print()

    # Summary
    print("=" * 70)
    print("INVARIANT TEST SUMMARY")
    print("=" * 70)
    print()

    successful_tests = [r for r in results if r['status'] == 'success']
    invariant_holds = [r for r in successful_tests if r['result']['all_self_forbidden']]
    invariant_breaks = [r for r in successful_tests if not r['result']['all_self_forbidden']]

    print(f"Total tests: {len(test_cases)}")
    print(f"Successful tests: {len(successful_tests)}")
    print(f"Invariant holds: {len(invariant_holds)}")
    print(f"Invariant breaks: {len(invariant_breaks)}")
    print()

    if invariant_holds:
        print("Tests where invariant HOLDS:")
        print("-" * 70)
        for r in invariant_holds:
            print(f"  {r['name']}: {r['result']['forbidden_count']}/{r['result']['self_transition_count']} self-transitions forbidden")
        print()

    if invariant_breaks:
        print("Tests where invariant BREAKS:")
        print("-" * 70)
        for r in invariant_breaks:
            print(f"  {r['name']}: {r['result']['forbidden_count']}/{r['result']['self_transition_count']} self-transitions forbidden")
        print()

    # Final verdict
    print("=" * 70)
    if len(invariant_holds) == len(successful_tests) and len(successful_tests) > 0:
        print("INVARIANT HOLDS: All self-transitions are forbidden in all tests")
    elif len(invariant_breaks) > 0:
        print("INVARIANT BREAKS: Some tests show allowed self-transitions")
    else:
        print("INSUFFICIENT DATA: Cannot determine")
    print("=" * 70)


if __name__ == "__main__":
    main()
