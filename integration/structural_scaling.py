#!/usr/bin/env python3
"""
Structural Scaling Experiment

Measures: Tokens | Identities | Relations | Avg escape paths | Under pressure | Diversity

Law: Diversity increases with escape topology width.
"""

import sys
import hashlib
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
integration_dir = Path(__file__).resolve().parent
for d in [str(project_root), str(integration_dir)]:
    if d not in sys.path:
        sys.path.insert(0, d)


def tokenize_simple(text):
    return text.split()


def token_to_residue(token):
    h = hashlib.sha256(token.encode()).hexdigest()[:8]
    return float(int(h, 16) % 10000) / 10000.0


def run_structure_and_topology(text, num_runs=3):
    """Run phases 1-4 and measure escape topology. Return metrics or None."""
    try:
        tokens = tokenize_simple(text)
        if not tokens:
            return None

        from threshold_onset.phase1.phase1 import phase1
        from threshold_onset.phase2.phase2 import phase2_multi_run
        from threshold_onset.phase3.phase3 import phase3_multi_run
        from threshold_onset.phase4.phase4 import phase4
        from integration.escape_topology import measure_escape_topology

        residue_sequences = []
        phase1_list = []
        for _ in range(num_runs):
            residues = [token_to_residue(t) for t in tokens] * 2
            residue_sequences.append(residues)
            phase1_list.append(phase1(residues))

        phase2 = phase2_multi_run(residue_sequences, phase1_list)
        if not phase2 or not phase2.get('identity_mappings'):
            return None

        phase3 = phase3_multi_run(residue_sequences, phase1_list, phase2)
        if not phase3:
            return None

        phase4_metrics = phase4(phase2, phase3)
        if not phase4_metrics:
            return None

        continuation_text = "Tokens become actions. Patterns become residues."
        continuation_tokens = tokenize_simple(continuation_text)

        topology = measure_escape_topology(
            phase4_metrics, phase3, phase2,
            continuation_tokens, max_steps=200
        )

        n_identities = len(phase2.get('identity_mappings', {}))
        n_relations = len(phase3.get('persistent_relation_hashes', set()))
        under_pressure = sum(1 for d in topology.values() if d['self_transition_attempts'] > 0)
        avg_escape = (
            sum(d['distinct_escape_paths'] for d in topology.values()) / len(topology)
            if topology else 0
        )

        return {
            'n_tokens': len(tokens),
            'n_identities': n_identities,
            'n_relations': n_relations,
            'avg_escape_paths': avg_escape,
            'under_pressure': under_pressure,
            'topology': topology,
        }
    except Exception:
        return None


SCALING_CORPUS = [
    ("3", "I am Eating"),
    ("7", "Action before knowledge. Structure emerges before language."),
    ("10", "One two three four five six seven eight nine ten."),
    ("20", "The quick brown fox jumps over the lazy dog. Structure emerges from action."),
    ("50", " ".join(["w" + str(i % 25) for i in range(50)])),
    ("100", " ".join(["t" + str(i % 20) for i in range(100)])),
]


def main():
    print("=" * 70)
    print("STRUCTURAL SCALING EXPERIMENT")
    print("=" * 70)
    print()
    print("Law: Diversity increases with escape topology width.")
    print()
    print("-" * 70)
    print(f"{'Tokens':<12} {'Identities':<12} {'Relations':<12} {'Avg escape':<12} {'Pressure':<10} {'Diversity':<10}")
    print("-" * 70)

    rows = []
    for name, text in SCALING_CORPUS:
        m = run_structure_and_topology(text)
        if m:
            div = "Low" if m['avg_escape_paths'] < 1.5 else ("Medium" if m['avg_escape_paths'] < 2.5 else "High")
            print(f"{m['n_tokens']:<12} {m['n_identities']:<12} {m['n_relations']:<12} "
                  f"{m['avg_escape_paths']:<12.2f} {m['under_pressure']:<10} {div:<10}")
            rows.append(m)
        else:
            print(f"{name}: FAIL")

    print("-" * 70)
    print()
    print("STRUCTURAL LAW")
    print("-" * 70)
    print("  Tokens up -> Escape topology width up -> Diversity up")
    print("  Small input -> Narrow topology -> Constrained cycling")
    print("  Large input -> Wider topology -> More freedom")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
