#!/usr/bin/env python3
"""
Stress test: scale and timing.

Run on varied corpus sizes, measure time and memory.
Uses config benchmark.sizes and benchmark.num_runs when available (use all, not one).
"""

import json
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def _load_benchmark_config():
    """Load benchmark.sizes and benchmark.num_runs from config. Use all sizes."""
    try:
        config_path = project_root / "config" / "default.json"
        with open(config_path, encoding="utf-8") as f:
            data = json.load(f)
        bench = data.get("benchmark", {})
        sizes = bench.get("sizes")
        num_runs = bench.get("num_runs", 3)
        if isinstance(sizes, list) and len(sizes) > 0:
            return sizes, num_runs
    except Exception:
        pass
    return [100, 500, 1000, 2000, 5000], 3


def tokenize_simple(text):
    return text.split()


def token_to_residue(token):
    import hashlib
    h = hashlib.sha256(token.encode()).hexdigest()[:8]
    return float(int(h, 16) % 10000) / 10000.0


def run_one(size_tokens, num_runs=3):
    """Run pipeline for given token count. Return (seconds, success)."""
    tokens = ["token" + str(i % 100) for i in range(size_tokens)]
    text = " ".join(tokens)

    from threshold_onset.phase1.phase1 import phase1
    from threshold_onset.phase2.phase2 import phase2_multi_run
    from threshold_onset.phase3.phase3 import phase3_multi_run
    from threshold_onset.phase4.phase4 import phase4
    from threshold_onset.semantic.phase9.symbol_decoder import (
        build_structural_decoder,
        decode_symbol_sequence,
    )

    t0 = time.perf_counter()
    residue_sequences = []
    phase1_list = []
    for _ in range(num_runs):
        residues = [token_to_residue(t) for t in tokens] * 2
        residue_sequences.append(residues)
        phase1_list.append(phase1(residues))

    phase2 = phase2_multi_run(residue_sequences, phase1_list)
    phase3 = phase3_multi_run(residue_sequences, phase1_list, phase2)
    phase4_metrics = phase4(phase2, phase3)
    symbol_to_token = build_structural_decoder(
        tokens, residue_sequences, phase2, phase4_metrics
    )
    symbols = list(phase4_metrics.get('identity_to_symbol', {}).values())[:50]
    _ = decode_symbol_sequence(symbols, symbol_to_token)
    t1 = time.perf_counter()
    return t1 - t0, bool(symbol_to_token)


def main():
    sizes, num_runs = _load_benchmark_config()
    print("Size\tTime(s)\tSuccess")
    print("-" * 30)
    print(f"(config: {len(sizes)} sizes, num_runs={num_runs})")
    for n in sizes:
        elapsed, ok = run_one(n, num_runs=num_runs)
        print(f"{n}\t{elapsed:.3f}\t{ok}")
    print("-" * 30)
    print("Done")


if __name__ == "__main__":
    main()
