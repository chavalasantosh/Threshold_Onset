#!/usr/bin/env python3
"""
THRESHOLD_ONSET Benchmark

Structured evaluation suite for structure emergence, constraint adherence,
and decoder consistency. Metrics: pipeline success rate, constraint violation
rate, structural consistency (decoder accuracy), self-transition rate.

Uses config benchmark.num_runs when available (use all options from config).
"""

import json
import sys
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def _benchmark_num_runs() -> int:
    """Num runs per sample from config benchmark.num_runs."""
    try:
        with open(project_root / "config" / "default.json", encoding="utf-8") as f:
            n = json.load(f).get("benchmark", {}).get("num_runs")
        if isinstance(n, int) and n >= 1:
            return n
    except Exception:
        pass
    return 3


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

        # Count self-transitions in symbol sequence
        self_transitions = sum(1 for i in range(len(symbols) - 1) if symbols[i] == symbols[i + 1])
        total_transitions = max(1, len(symbols) - 1)
        self_transition_rate = self_transitions / total_transitions

        # Decoder consistency: decoded tokens must be from input vocab
        decoded_tokens = decoded.split()
        vocab = set(tokens)
        consistent = sum(1 for t in decoded_tokens if t in vocab)
        decoder_consistency = consistent / max(1, len(decoded_tokens))

        # Constraint violations: 0 if no self-transitions (invariant holds)
        constraint_violations = self_transitions

        return True, {
            'n_tokens': len(tokens),
            'n_symbols': len(symbol_to_token),
            'n_identities': len(phase2.get('identity_mappings', {})),
            'n_edges': len(phase3.get('persistent_relation_hashes', set())),
            'decoded': decoded,
            'self_transition_rate': self_transition_rate,
            'constraint_violations': constraint_violations,
            'decoder_consistency': decoder_consistency,
            'tokens': tokens,
            'symbol_to_token': symbol_to_token,
        }
    except Exception:
        return False, None


# Benchmark corpus: 50+ diverse inputs
BENCHMARK_CORPUS = [
    ("short_1", "Hi there."),
    ("short_2", "Hello world."),
    ("normal_1", "Action before knowledge. Structure emerges before language."),
    ("normal_2", "Function stabilizes before meaning appears."),
    ("repeated_1", "the the the a a a"),
    ("repeated_2", "word word word"),
    ("single", "word"),
    ("long_1", " ".join(["token"] * 50)),
    ("long_2", " ".join(["item"] * 100)),
    ("punctuation_1", "Hello, world! How are you?"),
    ("punctuation_2", "Yes. No. Maybe."),
    ("mixed_1", "Action before knowledge. Structure emerges. Tokens become actions."),
    ("mixed_2", "Code compiles before execution. Syntax checks before runtime."),
    ("philosophy_1", "Structure emerges from action and repetition."),
    ("philosophy_2", "Knowledge follows action. Kārya before jñāna."),
    ("tech_1", "Tokens become residues. Residues form segments."),
    ("tech_2", "Hash to residue. Segment to identity. Co-occur to relation."),
    ("literary_1", "The moon rises over mountains."),
    ("literary_2", "Stars twinkle in dark sky."),
    ("minimal_1", "a b"),
    ("minimal_2", "one two three"),
    ("medium_1", "One two three four five six seven eight nine ten."),
    ("medium_2", "The quick brown fox jumps over the lazy dog."),
    ("varied_1", "Before after. Start end. Begin finish."),
    ("varied_2", "Left right. Up down. In out."),
    ("dup_1", "same same same"),
    ("dup_2", "repeat repeat repeat repeat"),
    ("caps_1", "Action ACTION action"),
    ("caps_2", "Word WORD word"),
    ("nums_1", "one 1 two 2 three 3"),
    ("nums_2", "first second third"),
    ("struct_1", "A B C D E F G"),
    ("struct_2", "Alpha Beta Gamma Delta"),
    ("lang_mix_1", "Action kārya knowledge jñāna"),
    ("lang_mix_2", "Structure emerges naturally."),
    ("long_sent", "The dominant sequence transduction models are based on recurrent or attention-based neural networks that learn representations from large-scale data."),
    ("stress_100", " ".join(["t" + str(i % 20) for i in range(100)])),
    ("stress_200", " ".join(["t" + str(i % 30) for i in range(200)])),
    ("stress_500", " ".join(["t" + str(i % 50) for i in range(500)])),
]


def run_benchmark(verbose: bool = True, num_runs: Optional[int] = None) -> Dict[str, Any]:
    """Run full benchmark across corpus. Return summary metrics. Uses config benchmark.num_runs if num_runs not given."""
    if num_runs is None:
        num_runs = _benchmark_num_runs()
    results = []
    total_time = 0

    for name, text in BENCHMARK_CORPUS:
        t0 = time.perf_counter()
        ok, metrics = run_pipeline(text, num_runs=num_runs)
        elapsed = time.perf_counter() - t0
        total_time += elapsed

        if ok:
            results.append({
                'name': name,
                'success': True,
                'self_transition_rate': metrics['self_transition_rate'],
                'constraint_violations': metrics['constraint_violations'],
                'decoder_consistency': metrics['decoder_consistency'],
                'n_tokens': metrics['n_tokens'],
                'n_symbols': metrics['n_symbols'],
            })
            if verbose:
                print(f"  PASS {name}: {metrics['n_tokens']} tok, {metrics['n_symbols']} sym, "
                      f"viol={metrics['constraint_violations']}, consistency={metrics['decoder_consistency']:.2f}")
        else:
            results.append({'name': name, 'success': False})
            if verbose:
                print(f"  FAIL {name}")

    success_count = sum(1 for r in results if r['success'])
    success_rate = success_count / len(BENCHMARK_CORPUS)

    successful = [r for r in results if r['success']]
    avg_self_transition = sum(r['self_transition_rate'] for r in successful) / max(1, len(successful))
    avg_constraint_violations = sum(r['constraint_violations'] for r in successful) / max(1, len(successful))
    avg_consistency = sum(r['decoder_consistency'] for r in successful) / max(1, len(successful))
    total_violations = sum(r['constraint_violations'] for r in successful)
    zero_violation_count = sum(1 for r in successful if r['constraint_violations'] == 0)

    summary = {
        'n_samples': len(BENCHMARK_CORPUS),
        'success_rate': success_rate,
        'success_count': success_count,
        'avg_self_transition_rate': avg_self_transition,
        'avg_constraint_violations_per_sample': avg_constraint_violations,
        'total_constraint_violations': total_violations,
        'samples_with_zero_violations': zero_violation_count,
        'decoder_consistency': avg_consistency,
        'total_time_seconds': total_time,
    }
    return summary


def main():
    num_runs = _benchmark_num_runs()
    print("=" * 60)
    print("THRESHOLD_ONSET BENCHMARK")
    print("=" * 60)
    print(f"Corpus: {len(BENCHMARK_CORPUS)} samples  num_runs: {num_runs} (from config)")
    print("-" * 60)

    summary = run_benchmark(verbose=True, num_runs=num_runs)

    print("-" * 60)
    print("SUMMARY")
    print("-" * 60)
    print(f"Success rate:        {summary['success_count']}/{summary['n_samples']} = {summary['success_rate']:.1%}")
    print(f"Decoder consistency: {summary['decoder_consistency']:.2%}")
    print(f"Constraint violations (total): {summary['total_constraint_violations']}")
    print(f"Samples with 0 violations: {summary['samples_with_zero_violations']}/{summary['success_count']}")
    print(f"Total time: {summary['total_time_seconds']:.2f}s")
    print("=" * 60)
    return 0 if summary['success_rate'] >= 0.9 else 1


if __name__ == "__main__":
    sys.exit(main())
