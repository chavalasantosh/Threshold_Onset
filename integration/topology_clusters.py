#!/usr/bin/env python3
"""
Cluster Identities by Escape Topology

Groups identities by their escape topology characteristics:
- Pressure (self-transition attempts, near-refusal events)
- Freedom (distinct escape paths, escape concentration)
- Escape patterns (where they escape to)

Mechanical clustering only - no interpretation.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Add paths
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from integration.unified_system import process_text_through_phases, tokenize_text_to_actions
from integration.escape_topology import measure_escape_topology


def cluster_by_topology(topology):
    """
    Cluster identities by escape topology characteristics.

    Groups by:
    - Pressure level (high/medium/low based on attempts and near-refusal events)
    - Freedom level (high/medium/low based on escape paths and concentration)
    - Escape pattern (where they escape to)

    Returns clusters as dict: cluster_name -> [symbols]
    """
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
    """Cluster identities by escape topology."""

    base_text = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    continuation_text = "Tokens become actions. Patterns become residues."

    print("=" * 70)
    print("TOPOLOGY CLUSTERING")
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

    print("Measuring escape topology...")
    print()

    # Measure topology
    topology = measure_escape_topology(
        results['phase4'],
        results['phase3'],
        results['phase2'],
        continuation_tokens,
        max_steps=200
    )

    print("Clustering by topology...")
    print()

    # Cluster identities
    clusters = cluster_by_topology(topology)

    print("=" * 70)
    print("TOPOLOGY CLUSTERS")
    print("=" * 70)
    print()

    # Report clusters
    for cluster_name, members in sorted(clusters.items()):
        print(f"Cluster: {cluster_name}")
        print(f"  Members: {len(members)}")
        print("-" * 70)

        for member in members:
            print(f"  Symbol {member['symbol']}:")
            print(f"    Self-transition attempts: {member['attempts']}")
            print(f"    Near-refusal events: {member['near_refusals']}")
            print(f"    Escape paths: {member['escape_paths']}")
            print(f"    Concentration: {member['concentration']:.4f}")
            if member['escape_targets']:
                print(f"    Escapes to: {member['escape_targets']}")
            print()

    # Summary
    print("=" * 70)
    print("CLUSTER SUMMARY")
    print("=" * 70)
    print()

    print(f"Total clusters: {len(clusters)}")
    print(f"Total identities: {sum(len(members) for members in clusters.values())}")
    print()

    # Cluster sizes
    print("Cluster sizes:")
    for cluster_name, members in sorted(clusters.items()):
        print(f"  {cluster_name}: {len(members)} identities")

    print()
    print("=" * 70)
    print("CLUSTERING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
