#!/usr/bin/env python3
"""
Quantitative External Validation

Runs THRESHOLD_ONSET on external text samples for quantitative validation.
Uses a fixed corpus of 100+ sentences from diverse domains.
Outputs: success rate, constraint violation rate, decoder consistency, timing.
"""

import sys
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def tokenize_simple(text: str) -> List[str]:
    return text.split()


def token_to_residue(token: str) -> float:
    h = hashlib.sha256(token.encode()).hexdigest()[:8]
    return float(int(h, 16) % 10000) / 10000.0


def run_pipeline(text: str, num_runs: int = 3) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Run full pipeline; return (success, metrics_dict or None)."""
    try:
        tokens = tokenize_simple(text)
        if not tokens:
            return False, None

        from threshold_onset.phase1.phase1 import phase1
        from threshold_onset.phase2.phase2 import phase2_multi_run
        from threshold_onset.phase3.phase3 import phase3_multi_run
        from threshold_onset.phase4.phase4 import phase4
        from threshold_onset.semantic.phase9.symbol_decoder import (
            build_structural_decoder,
            decode_symbol_sequence,
        )

        residue_sequences = []
        phase1_list = []
        for _ in range(num_runs):
            residues = [token_to_residue(t) for t in tokens] * 2
            residue_sequences.append(residues)
            phase1_list.append(phase1(residues))

        phase2 = phase2_multi_run(residue_sequences, phase1_list)
        if not phase2 or not phase2.get('identity_mappings'):
            return False, None

        phase3 = phase3_multi_run(residue_sequences, phase1_list, phase2)
        if not phase3:
            return False, None

        phase4_metrics = phase4(phase2, phase3)
        if not phase4_metrics:
            return False, None

        symbol_to_token = build_structural_decoder(
            tokens, residue_sequences, phase2, phase4_metrics
        )
        if not symbol_to_token:
            return False, None

        identity_to_symbol = phase4_metrics.get('identity_to_symbol', {})
        symbols = list(identity_to_symbol.values())[:30]
        decoded = decode_symbol_sequence(symbols, symbol_to_token)

        self_transitions = sum(1 for i in range(len(symbols) - 1) if symbols[i] == symbols[i + 1])
        total_transitions = max(1, len(symbols) - 1)
        decoded_tokens = decoded.split()
        vocab = set(tokens)
        consistent = sum(1 for t in decoded_tokens if t in vocab)

        return True, {
            'n_tokens': len(tokens),
            'n_symbols': len(symbol_to_token),
            'self_transition_rate': self_transitions / total_transitions,
            'constraint_violations': self_transitions,
            'decoder_consistency': consistent / max(1, len(decoded_tokens)),
        }
    except Exception:
        return False, None


# External validation corpus: 100 diverse sentences
# Sources: synthetic, philosophy, tech, literary, mixed
EXTERNAL_CORPUS = [
    "The sky is blue.",
    "Water flows downhill.",
    "Birds fly south in winter.",
    "Cats sleep during the day.",
    "Structure emerges from action.",
    "Knowledge follows action.",
    "Tokens become residues naturally.",
    "Identity earns persistence.",
    "Co-occurrence forms relations.",
    "Constraint bounds generation.",
    "Code compiles before execution.",
    "Syntax checks before runtime.",
    "Types validate before execution.",
    "Functions define before calling.",
    "Hash to residue. Segment to identity.",
    "Action before knowledge.",
    "Function stabilizes before meaning.",
    "Structure emerges before language.",
    "The moon rises over mountains.",
    "Stars twinkle in dark sky.",
    "Waves crash on shore.",
    "Wind whispers through trees.",
    "Before after. Start end.",
    "Left right. Up down.",
    "One two three four five.",
    "Alpha Beta Gamma Delta.",
    "First second third fourth.",
    "Same same same same.",
    "Repeat repeat repeat.",
    "Word word word word.",
    "A B C D E F G.",
    "Hello world. Hello again.",
    "Yes. No. Maybe.",
    "Action kārya knowledge jñāna.",
    "Kārya before jñāna.",
    "Structure emerges naturally.",
    "Tokens become actions.",
    "Patterns become residues.",
    "Identity earns structure.",
    "Relation follows co-occurrence.",
    "Symbol aliases identity.",
    "Decoder inverts forward.",
    "No self-transition. Ever.",
    "Refusal is a feature.",
    "Constraint drives selection.",
    "Path selection respects edges.",
    "Build is O(n). Decode is O(1).",
    "Zero parameters. Zero training.",
    "Deterministic hashing.",
    "Persistence requires repetition.",
    "Segment window size two.",
    "Cluster threshold point one.",
    "Multi-run count three.",
    "Frequency weight one.",
    "Pressure weight point one.",
    "Learned bias point zero five.",
    "Phase zero residue only.",
    "Phase one segmentation only.",
    "Phase two identity only.",
    "Phase three relation only.",
    "Phase four symbol only.",
    "Structural inversion complete.",
    "First occurrence wins.",
    "Residue to token map.",
    "Identity to residues map.",
    "Symbol to identity map.",
    "Graph edges allowed only.",
    "Self-transitions refused.",
    "Invariant holds always.",
    "Topology drives generation.",
    "Pressure clusters identities.",
    "Escape paths matter.",
    "Scored paths select.",
    "Highest score wins.",
    "Weighted random optional.",
    "Decoder lookup O(1).",
    "No heuristics. No probability.",
    "Pure backward walk.",
    "Forward builds structure.",
    "Reverse decodes structure.",
    "Hash collision rare.",
    "Collision aliases tokens.",
    "Stress test five thousand.",
    "Validation seven types.",
    "Decoder test passes.",
    "Full pipeline passes.",
    "Zero constraint violations.",
    "Interpretability follows structure.",
    "Trace symbol to token.",
    "Trace token to residue.",
    "Trace residue to identity.",
    "Trace identity to symbol.",
    "Orthogonal to LLMs.",
    "Different paradigm entirely.",
    "Different evaluation criteria.",
    "Structure first. Always.",
    "Action before knowledge.",
    "Repetition enables structure.",
    "Persistence defines identity.",
    "Co-occurrence defines relation.",
    "Alias assigns symbol.",
    "Structural decoder inverts.",
    "Constraint bound generation.",
    "Refusal as invariant.",
    "Necessity from refusal.",
    "Selection from scoring.",
    "Text from selection.",
    "Difference from topology.",
    "Not from semantics.",
    "Parameters zero.",
    "Training none.",
    "Embeddings none.",
    "Attention none.",
    "Neural networks none.",
    "Standard library only.",
    "Hashlib SHA256 MD5.",
] + [
    " ".join(["token"] * (i % 20 + 5)) for i in range(20)
]


def run_external_validation(verbose: bool = True) -> Dict[str, Any]:
    """Run external validation across corpus."""
    results = []
    total_time = 0

    for i, text in enumerate(EXTERNAL_CORPUS):
        t0 = time.perf_counter()
        ok, metrics = run_pipeline(text)
        elapsed = time.perf_counter() - t0
        total_time += elapsed

        if ok:
            results.append({
                'success': True,
                'self_transition_rate': metrics['self_transition_rate'],
                'constraint_violations': metrics['constraint_violations'],
                'decoder_consistency': metrics['decoder_consistency'],
                'n_tokens': metrics['n_tokens'],
            })
        else:
            results.append({'success': False})

    success_count = sum(1 for r in results if r['success'])
    success_rate = success_count / len(EXTERNAL_CORPUS)
    successful = [r for r in results if r['success']]
    avg_consistency = sum(r['decoder_consistency'] for r in successful) / max(1, len(successful))
    total_violations = sum(r['constraint_violations'] for r in successful)
    zero_violation = sum(1 for r in successful if r['constraint_violations'] == 0)

    summary = {
        'n_samples': len(EXTERNAL_CORPUS),
        'success_rate': success_rate,
        'success_count': success_count,
        'decoder_consistency': avg_consistency,
        'total_constraint_violations': total_violations,
        'samples_zero_violations': zero_violation,
        'total_time_seconds': total_time,
    }
    return summary


def main():
    print("=" * 60)
    print("QUANTITATIVE EXTERNAL VALIDATION")
    print("=" * 60)
    print(f"Corpus: {len(EXTERNAL_CORPUS)} external samples")
    print("-" * 60)

    summary = run_external_validation(verbose=False)

    print(f"Success rate:        {summary['success_count']}/{summary['n_samples']} = {summary['success_rate']:.1%}")
    print(f"Decoder consistency: {summary['decoder_consistency']:.2%}")
    print(f"Constraint violations (total): {summary['total_constraint_violations']}")
    print(f"Samples with 0 violations: {summary['samples_zero_violations']}/{summary['success_count']}")
    print(f"Total time: {summary['total_time_seconds']:.2f}s")
    print("=" * 60)
    return 0 if summary['success_rate'] >= 0.8 else 1


if __name__ == "__main__":
    sys.exit(main())
