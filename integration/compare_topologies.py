#!/usr/bin/env python3
# pylint: disable=wrong-import-position,too-many-locals,too-many-branches,too-many-statements
"""
Compare Escape Topologies Across Inputs

Measures escape topology for different texts and compares:
- Which features remain invariant
- Which features vary

Mechanical comparison only - no interpretation.
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from integration.unified_system import process_text_through_phases, tokenize_text_to_actions
from integration.escape_topology import measure_escape_topology


def compare_topologies():
    """Compare escape topologies across different inputs."""

    # Different test inputs
    test_cases = [
        {
            'name': 'philosophy',
            'text': """
            Action before knowledge.
            Function stabilizes before meaning appears.
            Structure emerges before language exists.
            """,
            'continuation': "Tokens become actions. Patterns become residues.",
            'tokenization': 'word'
        },
        {
            'name': 'technical',
            'text': """
            Code compiles before execution.
            Syntax checks before runtime.
            Types validate before execution.
            """,
            'continuation': "Functions define before calling. Variables declare before use.",
            'tokenization': 'word'
        },
        {
            'name': 'literary',
            'text': """
            The moon rises over mountains.
            Stars twinkle in dark sky.
            Waves crash on shore.
            """,
            'continuation': "Wind whispers through trees. Birds sing at dawn.",
            'tokenization': 'word'
        },
        {
            'name': 'short',
            'text': 'Hello world. Hello again.',
            'continuation': 'Goodbye world. Goodbye again.',
            'tokenization': 'word'
        }
    ]

    all_topologies = {}

    print("=" * 70)
    print("ESCAPE TOPOLOGY COMPARISON")
    print("=" * 70)
    print()

    # Measure topology for each input
    for test_case in test_cases:
        print(f"Measuring: {test_case['name']}")
        print("-" * 70)

        try:
            # Process through phases
            results = process_text_through_phases(
                text=test_case['text'],
                tokenization_method=test_case['tokenization'],
                num_runs=3
            )

            if results['phase4'] is None:
                print(f"  Phase 4 did not complete for {test_case['name']}")
                continue

            # Continue with continuation text
            _, continuation_tokens = tokenize_text_to_actions(
                test_case['continuation'],
                tokenization_method=test_case['tokenization']
            )

            # Measure topology
            topology = measure_escape_topology(
                results['phase4'],
                results['phase3'],
                results['phase2'],
                continuation_tokens,
                max_steps=200
            )

            all_topologies[test_case['name']] = topology

            # Quick summary
            symbols_with_attempts = [
                s for s, d in topology.items() if d['self_transition_attempts'] > 0
            ]
            total_attempts = sum(d['self_transition_attempts'] for d in topology.values())
            avg_escape_paths = (
                sum(d['distinct_escape_paths'] for d in topology.values()) / len(topology)
                if topology else 0
            )

            print(f"  Symbols observed: {len(topology)}")
            print(f"  Symbols with self-transition attempts: {len(symbols_with_attempts)}")
            print(f"  Total self-transition attempts: {total_attempts}")
            print(f"  Average escape paths: {avg_escape_paths:.2f}")
            print()

        except (ImportError, KeyError, TypeError, ValueError) as e:
            print(f"  Error: {e}")
            print()

    # Compare topologies
    print("=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)
    print()

    if len(all_topologies) < 2:
        print("Need at least 2 topologies to compare.")
        return

    # Extract metrics for comparison
    comparison_metrics = {}

    for name, topology in all_topologies.items():
        metrics = {
            'total_symbols': len(topology),
            'symbols_with_attempts': len([
                s for s, d in topology.items() if d['self_transition_attempts'] > 0
            ]),
            'total_attempts': sum(d['self_transition_attempts'] for d in topology.values()),
            'total_escape_paths': sum(d['distinct_escape_paths'] for d in topology.values()),
            'avg_escape_paths': (
                sum(d['distinct_escape_paths'] for d in topology.values()) / len(topology)
                if topology else 0
            ),
            'avg_concentration': (
                sum(d['escape_concentration'] for d in topology.values()) / len(topology)
                if topology else 0
            ),
            'max_attempts': max(
                (d['self_transition_attempts'] for d in topology.values()), default=0
            ),
            'max_escape_paths': max(
                (d['distinct_escape_paths'] for d in topology.values()), default=0
            )
        }
        comparison_metrics[name] = metrics

    # Report metrics
    print("METRICS PER INPUT:")
    print("-" * 70)
    for name, metrics in comparison_metrics.items():
        print(f"{name}:")
        print(f"  Total symbols: {metrics['total_symbols']}")
        print(f"  Symbols with attempts: {metrics['symbols_with_attempts']}")
        print(f"  Total attempts: {metrics['total_attempts']}")
        print(f"  Average escape paths: {metrics['avg_escape_paths']:.2f}")
        print(f"  Average concentration: {metrics['avg_concentration']:.4f}")
        print(f"  Max attempts (single symbol): {metrics['max_attempts']}")
        print(f"  Max escape paths (single symbol): {metrics['max_escape_paths']}")
        print()

    # Identify invariants vs variations
    print("=" * 70)
    print("INVARIANTS VS VARIATIONS")
    print("=" * 70)
    print()

    # Check which metrics are consistent (invariant) vs vary
    metric_names = [
        'total_symbols', 'symbols_with_attempts', 'total_attempts',
        'avg_escape_paths', 'avg_concentration', 'max_attempts', 'max_escape_paths'
    ]

    invariants = []
    variations = []

    for metric_name in metric_names:
        values = [metrics[metric_name] for metrics in comparison_metrics.values()]

        # Check if all values are the same (invariant)
        if len(set(values)) == 1:
            invariants.append((metric_name, values[0]))
        else:
            variations.append((metric_name, values))

    print("INVARIANTS (same across all inputs):")
    print("-" * 70)
    if invariants:
        for metric_name, value in invariants:
            print(f"  {metric_name}: {value}")
    else:
        print("  None found")
    print()

    print("VARIATIONS (different across inputs):")
    print("-" * 70)
    if variations:
        for metric_name, values in variations:
            value_dict = dict(zip(comparison_metrics.keys(), values))
            print(f"  {metric_name}:")
            for name, val in value_dict.items():
                print(f"    {name}: {val}")
    else:
        print("  None found")
    print()

    # Structural patterns
    print("=" * 70)
    print("STRUCTURAL PATTERNS")
    print("=" * 70)
    print()

    # Check if all inputs have at least one symbol with self-transition attempts
    all_have_attempts = all(
        any(d['self_transition_attempts'] > 0 for d in topo.values())
        for topo in all_topologies.values()
    )

    # Check if all inputs have symbols with concentrated escape (concentration = 1.0)
    all_have_concentrated = all(
        any(d['escape_concentration'] == 1.0 for d in topology.values())
        for topology in all_topologies.values()
    )

    print(f"All inputs have self-transition attempts: {all_have_attempts}")
    print(f"All inputs have concentrated escape paths: {all_have_concentrated}")
    print()

    print("=" * 70)
    print("COMPARISON COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    compare_topologies()
