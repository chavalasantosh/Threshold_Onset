"""
THRESHOLD_ONSET — Phase 4 Freeze Validation Test

Tests Phase 4 (SYMBOL) for freeze-worthiness:
1. Determinism: Same inputs → same alias tables
2. Reversibility: Removing Phase 4 → Phase 3 restored bit-for-bit
3. Immutability: Aliases never change once assigned
4. Gate determinism: Gate never flakes

CRITICAL: Output shows only counts, never symbol values. 
"""

import sys
import os
import copy

# Add threshold_onset package to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
threshold_onset_dir = os.path.join(project_root, 'threshold_onset')
sys.path.insert(0, threshold_onset_dir)
sys.path.insert(0, project_root)  # For main.py imports


def run_main_capture_output():
    """
    Run integration pipeline via API and capture metrics.
    Uses integration.run_complete.run() directly (no subprocess).
    
    Returns:
        Dictionary with phase metrics or None if execution failed
    """
    try:
        from integration.run_complete import run, PipelineConfig  # pylint: disable=import-outside-toplevel

        cfg = PipelineConfig.from_project()
        cfg.show_tui = False
        result = run(
            text_override="The quick brown fox jumps.",
            cfg=cfg,
            return_result=True,
            return_model_state=True,
        )

        if result is None:
            return None

        # Build metrics from PipelineResult
        phase3_metrics = (result.model_state or {}).get("phase3_metrics", {})
        metrics = {
            "phase2_identity_mappings": result.identity_count,
            "phase3_persistent_relations": result.relation_count,
            "phase3_stability_ratio": phase3_metrics.get(
                "stability_ratio",
                1.0 if result.relation_count > 0 else 0.0,
            ),
            "phase4_identity_alias_count": result.identity_count,
            "phase4_relation_alias_count": result.relation_count,
            "phase4_gate_failed": not result.succeeded,
        }
        return metrics

    except Exception as e:
        print(f"Error running pipeline: {e}")
        return None


def test_determinism(num_iterations=5):
    """
    Test 1: Determinism
    Same inputs → same alias tables
    
    CRITICAL: Phase 4 determinism must be tested with FIXED Phase 2/3 inputs.
    We run Phase 0-3 once to get fixed inputs, then test Phase 4 multiple times
    with those same inputs.
    """
    print("=" * 70)
    print("TEST 1: DETERMINISM")
    print("=" * 70)
    print()
    print("Step 1: Run Phase 0-3 once to get fixed inputs...")
    print()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

    from tests.phase_test_helpers import (  # pylint: disable=import-outside-toplevel
        run_phase0_finite,
        run_phase1,
        run_phase2_multi_run,
        run_phase3_multi_run,
    )

    # Setup: Run Phase 0-3 to get fixed inputs
    NUM_RUNS = 5
    residue_sequences = []
    phase1_metrics_list = []
    
    for run_idx in range(NUM_RUNS):
        residues = run_phase0_finite()
        phase1_metrics = run_phase1(residues)
        residue_sequences.append(residues)
        phase1_metrics_list.append(phase1_metrics)
    
    phase2_metrics = run_phase2_multi_run(residue_sequences, phase1_metrics_list)
    phase3_metrics = run_phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)
    
    assert phase2_metrics is not None and phase3_metrics is not None, "Could not get fixed Phase 2/3 inputs"
    
    print("  Fixed inputs obtained:")
    print(f"    Persistent identities: {len(phase2_metrics.get('identity_mappings', {}))}")
    print(f"    Persistent relations: {len(phase3_metrics.get('persistent_relation_hashes', set()))}")
    print()
    
    print(f"Step 2: Run Phase 4 {num_iterations} times with SAME fixed inputs...")
    print()
    
    # Now test Phase 4 determinism with fixed inputs
    from threshold_onset.phase4.phase4 import phase4  # pylint: disable=import-outside-toplevel,import-error
    
    results = []
    for i in range(num_iterations):
        print(f"  Iteration {i+1}/{num_iterations}...", end=' ', flush=True)
        symbol_metrics = phase4(phase2_metrics, phase3_metrics)
        assert symbol_metrics is not None, "Phase 4 gate failed"
        results.append(symbol_metrics)
        print("OK")
    
    print()
    
    # Extract counts
    identity_counts = [r['identity_alias_count'] for r in results]
    relation_counts = [r['relation_alias_count'] for r in results]
    
    # Check if all counts are identical
    identity_deterministic = len(set(identity_counts)) == 1
    relation_deterministic = len(set(relation_counts)) == 1
    
    print("  Results:")
    print(f"    Identity alias counts: {identity_counts}")
    print(f"    Relation alias counts: {relation_counts}")
    print()
    
    if identity_deterministic and relation_deterministic:
        print("  [PASS] All alias counts are identical across runs")
        print("         (Phase 4 is deterministic with fixed inputs)")
        print()
    else:
        print("  [FAIL] Alias counts vary across runs")
        if not identity_deterministic:
            print(f"    Identity counts differ: {set(identity_counts)}")
        if not relation_deterministic:
            print(f"    Relation counts differ: {set(relation_counts)}")
        print()
    assert identity_deterministic and relation_deterministic, "Phase 4 must be deterministic"


def test_gate_determinism(num_iterations=5):
    """
    Test 2: Gate Determinism
    Gate never flakes - always passes when Phase 3 frozen, always fails when not.
    """
    print("=" * 70)
    print("TEST 2: GATE DETERMINISM")
    print("=" * 70)
    print()
    print(f"Running Phase 4 {num_iterations} times to check gate consistency...")
    print()
    
    results = []
    for i in range(num_iterations):
        print(f"  Iteration {i+1}/{num_iterations}...", end=' ', flush=True)
        metrics = run_main_capture_output()
        assert metrics is not None, "Pipeline failed"
        results.append(metrics)
        print("OK")
    
    print()
    
    # Check gate consistency
    gate_results = [r.get('phase4_gate_failed', True) for r in results]
    
    assert gate_results, "No gate results collected"
    
    # With stable frozen upstream phases, gate should pass every time.
    gate_consistent = len(set(gate_results)) == 1
    gate_always_passes = all(not failed for failed in gate_results)
    
    print("  Results:")
    print(f"    Gate failed: {gate_results}")
    print()
    
    if gate_consistent and gate_always_passes:
        gate_status = "FAILED" if gate_results[0] else "PASSED"
        print(f"  [PASS] Gate consistently {gate_status}")
        print()
    else:
        print("  [FAIL] Gate behavior is inconsistent")
        print()
    assert gate_consistent, "Gate must be deterministic"
    assert gate_always_passes, "Gate should pass when upstream phases are frozen"


def test_reversibility():
    """
    Test 3: Reversibility
    Removing Phase 4 → Phase 3 restored bit-for-bit
    
    This test verifies that Phase 4 doesn't modify Phase 3 outputs.
    We compare Phase 3 metrics before and after Phase 4 execution.
    """
    print("=" * 70)
    print("TEST 3: REVERSIBILITY")
    print("=" * 70)
    print()
    print("Testing that Phase 4 doesn't modify Phase 3 structure...")
    print()
    
    from tests.phase_test_helpers import (  # pylint: disable=import-outside-toplevel
        run_phase0_finite,
        run_phase1,
        run_phase2_multi_run,
        run_phase3_multi_run,
    )
    from threshold_onset.phase4.phase4 import phase4  # pylint: disable=import-outside-toplevel,import-error

    residue_sequences = []
    phase1_metrics_list = []
    for _ in range(5):
        residues = run_phase0_finite()
        phase1_metrics = run_phase1(residues)
        residue_sequences.append(residues)
        phase1_metrics_list.append(phase1_metrics)

    phase2_metrics = run_phase2_multi_run(residue_sequences, phase1_metrics_list)
    phase3_metrics = run_phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)
    assert phase2_metrics is not None and phase3_metrics is not None, "Could not build fixed Phase 2/3 inputs"

    phase3_before = copy.deepcopy(phase3_metrics)
    print("  Running Phase 4 with fixed inputs...", end=' ', flush=True)
    symbol_metrics = phase4(phase2_metrics, phase3_metrics)
    assert symbol_metrics is not None, "Phase 4 gate failed"
    print("OK")

    assert phase3_metrics == phase3_before, "Phase 4 mutated Phase 3 metrics"
    print("  [PASS] Phase 4 is read-only - Phase 3 metrics are bit-for-bit unchanged")
    print()


def test_immutability(num_iterations=3):
    """
    Test 4: Immutability
    Aliases never change once assigned.
    
    This test verifies that Phase 4 produces identical mappings
    when given the same inputs multiple times.
    """
    print("=" * 70)
    print("TEST 4: IMMUTABILITY")
    print("=" * 70)
    print()
    print("Step 1: Get fixed Phase 2/3 inputs...")
    print()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

    from tests.phase_test_helpers import (  # pylint: disable=import-outside-toplevel
        run_phase0_finite,
        run_phase1,
        run_phase2_multi_run,
        run_phase3_multi_run,
    )

    NUM_RUNS = 5
    residue_sequences = []
    phase1_metrics_list = []
    
    for run_idx in range(NUM_RUNS):
        residues = run_phase0_finite()
        phase1_metrics = run_phase1(residues)
        residue_sequences.append(residues)
        phase1_metrics_list.append(phase1_metrics)
    
    phase2_metrics = run_phase2_multi_run(residue_sequences, phase1_metrics_list)
    phase3_metrics = run_phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)
    
    assert phase2_metrics is not None and phase3_metrics is not None, "Could not get fixed Phase 2/3 inputs"
    
    print(f"Step 2: Run Phase 4 {num_iterations} times with SAME inputs...")
    print()
    
    # Test immutability with fixed inputs
    from threshold_onset.phase4.phase4 import phase4  # pylint: disable=import-outside-toplevel,import-error
    
    results = []
    for i in range(num_iterations):
        print(f"  Iteration {i+1}/{num_iterations}...", end=' ', flush=True)
        symbol_metrics = phase4(phase2_metrics, phase3_metrics)
        assert symbol_metrics is not None, "Phase 4 gate failed"
        results.append(symbol_metrics)
        print("OK")
    
    print()
    
    # Extract counts and verify mappings are identical
    identity_counts = [r['identity_alias_count'] for r in results]
    relation_counts = [r['relation_alias_count'] for r in results]
    
    # Check if counts are identical (immutable)
    identity_immutable = len(set(identity_counts)) == 1
    relation_immutable = len(set(relation_counts)) == 1
    
    # Also verify mappings are identical
    identity_mappings_identical = all(
        r['identity_to_symbol'] == results[0]['identity_to_symbol']
        for r in results
    )
    relation_mappings_identical = all(
        r['relation_to_symbol'] == results[0]['relation_to_symbol']
        for r in results
    )
    
    print("  Results:")
    print(f"    Identity alias counts: {identity_counts}")
    print(f"    Relation alias counts: {relation_counts}")
    print()
    
    if identity_immutable and relation_immutable and identity_mappings_identical and relation_mappings_identical:
        print("  [PASS] Alias counts and mappings are immutable across runs")
        print("         (Same inputs -> same outputs, always)")
        print()
    else:
        print("  [FAIL] Aliases changed across runs")
        if not identity_immutable:
            print(f"    Identity counts differ: {set(identity_counts)}")
        if not relation_immutable:
            print(f"    Relation counts differ: {set(relation_counts)}")
        if not identity_mappings_identical:
            print("    Identity mappings differ")
        if not relation_mappings_identical:
            print("    Relation mappings differ")
        print()
    assert identity_immutable and relation_immutable and identity_mappings_identical and relation_mappings_identical, (
        "Phase 4 aliases must be immutable"
    )


def run_freeze_validation():
    """
    Run all Phase 4 freeze validation tests.
    """
    print("=" * 70)
    print("PHASE 4 FREEZE VALIDATION TEST")
    print("=" * 70)
    print()
    
    all_tests_passed = True
    
    test1_passed = test2_passed = test3_passed = test4_passed = True
    try:
        test_determinism(num_iterations=5)
    except AssertionError:
        test1_passed = False
    try:
        test_gate_determinism(num_iterations=5)
    except AssertionError:
        test2_passed = False
    try:
        test_reversibility()
    except AssertionError:
        test3_passed = False
    try:
        test_immutability(num_iterations=3)
    except AssertionError:
        test4_passed = False
    all_tests_passed = test1_passed and test2_passed and test3_passed and test4_passed
    
    # Summary
    print("=" * 70)
    print("PHASE 4 FREEZE VALIDATION SUMMARY")
    print("=" * 70)
    print()
    print("Test Results:")
    print(f"  Test 1 (Determinism):        {'[PASS]' if test1_passed else '[FAIL]'}")
    print(f"  Test 2 (Gate Determinism):   {'[PASS]' if test2_passed else '[FAIL]'}")
    print(f"  Test 3 (Reversibility):     {'[PASS]' if test3_passed else '[FAIL]'}")
    print(f"  Test 4 (Immutability):     {'[PASS]' if test4_passed else '[FAIL]'}")
    print()
    
    if all_tests_passed:
        print("[PASS] ALL TESTS PASSED")
        print("Phase 4 freeze validation: SUCCESS")
        print("Phase 4 is ready for freeze.")
    else:
        print("[FAIL] SOME TESTS FAILED")
        print("Phase 4 is NOT ready for freeze.")
    print()
    print("=" * 70)
    
    return all_tests_passed


if __name__ == "__main__":
    success = run_freeze_validation()
    sys.exit(0 if success else 1)
