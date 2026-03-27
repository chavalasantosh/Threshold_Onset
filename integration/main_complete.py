#!/usr/bin/env python3
"""
Complete Unified System: threshold_onset <-> santok

End-to-end pipeline:
1. Tokenization (santok)
2. Structure Emergence (threshold_onset Phases 0-4)
3. Continuation Observation
4. Escape Topology Measurement
5. Topology Clustering

कार्य (kārya) happens before ज्ञान (jñāna)
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
# Use internal pip-installed modules: santok, santek, somaya
# These are our own projects: pip install santok, pip install santek, pip install somaya

# Import all components
from integration.unified_system import process_text_through_phases, tokenize_text_to_actions
from integration.continuation_observer import observe_continuation_refusals
from integration.escape_topology import measure_escape_topology


def run_complete_pipeline(text, continuation_text=None, tokenization_method="word", num_runs=3):
    """
    Run complete end-to-end pipeline.

    Args:
        text: Input text for structure emergence
        continuation_text: Text for continuation observation (if None, uses same as text)
        tokenization_method: Tokenization method
        num_runs: Number of runs for multi-run persistence

    Returns:
        Complete results dictionary
    """
    print("=" * 70)
    print("COMPLETE UNIFIED SYSTEM")
    print("कार्य (kārya) happens before ज्ञान (jñāna)")
    print("=" * 70)
    print()

    # ========================================================================
    # PHASE 1: TOKENIZATION (santok)
    # ========================================================================
    print("PHASE 1: TOKENIZATION (santok)")
    print("-" * 70)
    _, tokens = tokenize_text_to_actions(text, tokenization_method)
    print(f"Tokens generated: {len(tokens)}")
    print(f"Sample tokens: {tokens[:10]}")
    print()

    # ========================================================================
    # PHASE 2: STRUCTURE EMERGENCE (threshold_onset Phases 0-4)
    # ========================================================================
    print("PHASE 2: STRUCTURE EMERGENCE (threshold_onset)")
    print("-" * 70)
    results = process_text_through_phases(
        text=text,
        tokenization_method=tokenization_method,
        num_runs=num_runs
    )

    if results['phase4'] is None:
        print("Phase 4 did not complete. Cannot continue.")
        return None

    print()
    print("Structure emergence complete.")
    print(f"  Identity aliases: {results['phase4']['identity_alias_count']}")
    print(f"  Relation aliases: {results['phase4']['relation_alias_count']}")
    print()

    # ========================================================================
    # PHASE 3: CONTINUATION OBSERVATION
    # ========================================================================
    print("PHASE 3: CONTINUATION OBSERVATION")
    print("-" * 70)

    if continuation_text is None:
        continuation_text = text

    _, continuation_tokens = tokenize_text_to_actions(
        continuation_text,
        tokenization_method=tokenization_method
    )

    print(f"Continuation tokens: {len(continuation_tokens)}")

    # Observe continuation refusals
    refusals = observe_continuation_refusals(
        phase4_output=results['phase4'],
        phase3_metrics=results['phase3'],
        phase2_metrics=results['phase2'],
        continuation_tokens=continuation_tokens,
        max_steps=100
    )

    print(f"Refusals observed: {len(refusals)}")
    if refusals:
        print("First refusal:")
        r = refusals[0]
        print(f"  Step: {r['step_index']}, Current: {r['current_symbol']}, "
              f"Attempted: {r['attempted_next_symbol']}, Reason: {r['reason_for_refusal']}")
    print()

    # ========================================================================
    # PHASE 4: ESCAPE TOPOLOGY MEASUREMENT
    # ========================================================================
    print("PHASE 4: ESCAPE TOPOLOGY MEASUREMENT")
    print("-" * 70)

    topology = measure_escape_topology(
        results['phase4'],
        results['phase3'],
        results['phase2'],
        continuation_tokens,
        max_steps=200
    )

    print(f"Identities observed: {len(topology)}")

    symbols_with_attempts = [s for s, d in topology.items() if d['self_transition_attempts'] > 0]
    total_attempts = sum(d['self_transition_attempts'] for d in topology.values())
    avg_escape_paths = (
        sum(d['distinct_escape_paths'] for d in topology.values()) / len(topology)
        if topology else 0
    )

    print(f"Symbols with self-transition attempts: {len(symbols_with_attempts)}")
    print(f"Total self-transition attempts: {total_attempts}")
    print(f"Average escape paths: {avg_escape_paths:.2f}")
    print()

    # ========================================================================
    # PHASE 5: TOPOLOGY CLUSTERING
    # ========================================================================
    print("PHASE 5: TOPOLOGY CLUSTERING")
    print("-" * 70)

    clusters = cluster_by_topology(topology)

    print(f"Clusters identified: {len(clusters)}")
    for cluster_name, members in sorted(clusters.items()):
        print(f"  {cluster_name}: {len(members)} identities")
    print()

    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("=" * 70)
    print("COMPLETE PIPELINE SUMMARY")
    print("=" * 70)
    print()

    print("Structure:")
    print(f"  Identities: {results['phase4']['identity_alias_count']}")
    print(f"  Relations: {results['phase4']['relation_alias_count']}")
    print()

    print("Continuation:")
    print(f"  Refusals observed: {len(refusals)}")
    all_self = all(
        r['current_symbol'] == r['attempted_next_symbol'] for r in refusals
    )
    print(f"  All refusals are self-transitions: {all_self}")
    print()

    print("Topology:")
    print(f"  Identities measured: {len(topology)}")
    print(f"  Average escape paths: {avg_escape_paths:.2f}")
    print(f"  Symbols under pressure: {len(symbols_with_attempts)}")
    print()

    print("Clusters:")
    print(f"  Total clusters: {len(clusters)}")
    for cluster_name, members in sorted(clusters.items()):
        print(f"    {cluster_name}: {len(members)}")
    print()

    print("=" * 70)
    print("PIPELINE COMPLETE")
    print("=" * 70)
    print()
    print("Key Result:")
    print("  Structure → Constraint → Refusal → Necessity → Organization")
    print("  No meaning added. No labels. No interpretation.")
    print("  Difference emerges from topology, not semantics.")
    print()

    return {
        'structure': results,
        'refusals': refusals,
        'topology': topology,
        'clusters': clusters
    }


def cluster_by_topology(topology):
    """Cluster identities by escape topology characteristics."""
    clusters = defaultdict(list)

    for symbol, data in topology.items():
        # Pressure classification
        attempts = data['self_transition_attempts']
        near_refusals = data['near_refusal_events']

        if attempts > 0:
            pressure_level = 'high'
        elif near_refusals > 5:
            pressure_level = 'medium'
        else:
            pressure_level = 'low'

        # Freedom classification
        escape_paths = data['distinct_escape_paths']
        concentration = data['escape_concentration']

        if escape_paths >= 3:
            freedom_level = 'high'
        elif escape_paths == 2:
            freedom_level = 'medium'
        else:
            freedom_level = 'low'

        # Concentration classification
        if concentration == 1.0:
            concentration_type = 'concentrated'
        elif concentration < 0.5:
            concentration_type = 'distributed'
        else:
            concentration_type = 'mixed'

        # Create cluster key
        cluster_key = f"{pressure_level}_pressure_{freedom_level}_freedom_{concentration_type}"

        clusters[cluster_key].append({
            'symbol': symbol,
            'attempts': attempts,
            'near_refusals': near_refusals,
            'escape_paths': escape_paths,
            'concentration': concentration,
            'escape_targets': list(data['escape_paths'].keys())
        })

    return dict(clusters)


def main():
    """Main entry point for complete system."""

    # Example usage
    text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    continuation_text = "Tokens become actions. Patterns become residues."

    results = run_complete_pipeline(
        text=text,
        continuation_text=continuation_text,
        tokenization_method="word",
        num_runs=3
    )

    if results:
        print("\nComplete results available in returned dictionary.")
        print("Keys: 'structure', 'refusals', 'topology', 'clusters'")


if __name__ == "__main__":
    main()
