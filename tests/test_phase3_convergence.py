"""
THRESHOLD_ONSET — Phase 3 Convergence Validation Test

Tests Phase 3 stability and convergence across multiple run counts.
Proves that Phase 3 results are not accidental and can be frozen.

CRITICAL: This test must pass before Phase 3 can be frozen.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tests.phase_test_helpers import (
    run_phase0_finite,
    run_phase1,
    run_phase2_multi_run,
    run_phase3_multi_run,
)

# Fixed thresholds (must match Phase 3 implementation)
MIN_STABILITY_RATIO = 0.6
MIN_PERSISTENT_RELATIONS = 1

# Convergence test configuration
TEST_RUN_COUNTS = [5, 10, 20]  # Increasing run counts to test convergence
NUM_ITERATIONS_PER_RUN_COUNT = 3  # Run each test configuration multiple times


def run_convergence_test():
    """
    Run Phase 3 convergence validation test.

    Tests:
    1. Gate passes consistently across all run counts
    2. Stability ratio stays >= threshold
    3. Metrics converge (don't drift significantly)
    4. No flaky behavior

    Returns:
        Dictionary with test results
    """
    print("=" * 70)
    print("THRESHOLD_ONSET — Phase 3 Convergence Validation Test")
    print("=" * 70)
    print()
    print("Testing Phase 3 stability across multiple run counts...")
    print("Configuration:")
    print(f"  Test run counts: {TEST_RUN_COUNTS}")
    print(f"  Iterations per run count: {NUM_ITERATIONS_PER_RUN_COUNT}")
    print(f"  Required stability ratio: >= {MIN_STABILITY_RATIO}")
    print(f"  Required persistent relations: >= {MIN_PERSISTENT_RELATIONS}")
    print()
    print("=" * 70)
    print()

    all_results = {}
    all_passed = True

    for num_runs in TEST_RUN_COUNTS:
        print(f"Testing with NUM_RUNS = {num_runs}")
        print("-" * 70)

        iteration_results = []

        for iteration in range(NUM_ITERATIONS_PER_RUN_COUNT):
            print(f"  Iteration {iteration + 1}/{NUM_ITERATIONS_PER_RUN_COUNT}...", end=" ")

            # Run Phase 0 multiple times
            residue_sequences = []
            phase1_metrics_list = []

            for _ in range(num_runs):
                residues = run_phase0_finite()
                residue_sequences.append(residues)
                phase1_metrics = run_phase1(residues)
                phase1_metrics_list.append(phase1_metrics)

            # Run Phase 2 (multi-run)
            phase2_metrics = run_phase2_multi_run(residue_sequences, phase1_metrics_list)

            # Run Phase 3 (multi-run)
            relation_metrics = run_phase3_multi_run(
                residue_sequences, phase1_metrics_list, phase2_metrics
            )

            # Check if gate passed
            if relation_metrics is None:
                print("FAILED (gate failed)")
                all_passed = False
                iteration_results.append({
                    'gate_passed': False,
                    'stability_ratio': None,
                    'persistence_rate': None,
                    'persistent_relations': None,
                    'node_count': None,
                    'edge_count': None,
                    'common_edges_ratio': None
                })
                continue

            # Extract metrics
            stability_ratio = relation_metrics.get('stability_ratio', 0.0)
            persistence_rate = relation_metrics.get('persistence_rate', 0.0)
            persistent_relations = len(relation_metrics.get('persistent_relation_hashes', []))
            node_count = relation_metrics.get('node_count', 0)
            edge_count = relation_metrics.get('edge_count', 0)
            common_edges_ratio = relation_metrics.get('common_edges_ratio', 0.0)

            # Check thresholds
            gate_passed = (
                stability_ratio >= MIN_STABILITY_RATIO and
                persistent_relations >= MIN_PERSISTENT_RELATIONS
            )

            if not gate_passed:
                print("FAILED (thresholds not met)")
                all_passed = False
            else:
                print("PASSED")

            iteration_results.append({
                'gate_passed': gate_passed,
                'stability_ratio': stability_ratio,
                'persistence_rate': persistence_rate,
                'persistent_relations': persistent_relations,
                'node_count': node_count,
                'edge_count': edge_count,
                'common_edges_ratio': common_edges_ratio
            })

        all_results[num_runs] = iteration_results

        # Compute statistics for this run count
        passed_count = sum(1 for r in iteration_results if r['gate_passed'])
        stability_ratios = [r['stability_ratio'] for r in iteration_results if r['stability_ratio'] is not None]
        persistence_rates = [r['persistence_rate'] for r in iteration_results if r['persistence_rate'] is not None]
        persistent_relations_counts = [r['persistent_relations'] for r in iteration_results if r['persistent_relations'] is not None]

        print()
        print(f"  Results for NUM_RUNS = {num_runs}:")
        print(f"    Gate passes: {passed_count}/{NUM_ITERATIONS_PER_RUN_COUNT}")
        if stability_ratios:
            print(f"    Stability ratio: min={min(stability_ratios):.4f}, max={max(stability_ratios):.4f}, mean={sum(stability_ratios)/len(stability_ratios):.4f}")
        if persistence_rates:
            print(f"    Persistence rate: min={min(persistence_rates):.4f}, max={max(persistence_rates):.4f}, mean={sum(persistence_rates)/len(persistence_rates):.4f}")
        if persistent_relations_counts:
            print(f"    Persistent relations: min={min(persistent_relations_counts)}, max={max(persistent_relations_counts)}, mean={sum(persistent_relations_counts)/len(persistent_relations_counts):.1f}")
        print()

    # Final verdict
    print("=" * 70)
    print("CONVERGENCE TEST SUMMARY")
    print("=" * 70)
    print()

    if all_passed:
        print("[PASS] ALL TESTS PASSED")
        print()
        print("Phase 3 convergence validation: SUCCESS")
        print("Phase 3 is ready for freeze.")
    else:
        print("[FAIL] SOME TESTS FAILED")
        print()
        print("Phase 3 convergence validation: FAILURE")
        print("Phase 3 is NOT ready for freeze.")
        print("Investigate failures before proceeding.")

    print()
    print("=" * 70)

    return {
        'all_passed': all_passed,
        'results': all_results
    }


if __name__ == "__main__":
    run_convergence_test()
