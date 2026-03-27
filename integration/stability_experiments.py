#!/usr/bin/env python3
"""
THRESHOLD_ONSET Stability Experiments

Parameter sweeps: drop_prob, K, theta.
Distribution over recurrence counts.
Stability curves for publication.

Phase transition analysis:
- Fixed-denominator normalization (fraction = persistent / total_unique_pairs)
- Theoretical P(X >= theta) for X ~ Binomial(K, (1-p)^2)
- Mean-field boundary p* = 1 - sqrt(theta/K)

Usage:
    python integration/stability_experiments.py           # Full sweep + phase table
    python integration/stability_experiments.py --csv     # CSV for plotting
    python integration/stability_experiments.py --plot   # Generate plot (if matplotlib)
    python integration/stability_experiments.py --workers 8
"""

import math
import sys
import random
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from integration.runtime import ExecutionConfig, JobSpec, RETRY_NONE, choose_workers, run_tasks

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def binomial_survival_prob(K: int, q: float, theta: int) -> float:
    """
    P(X >= theta) for X ~ Binomial(K, q).
    Theoretical probability that a pair persists under threshold theta.
    """
    if theta > K or theta <= 0:
        return 0.0 if theta > K else 1.0
    total = 0.0
    for k in range(theta, K + 1):
        total += math.comb(K, k) * (q ** k) * ((1 - q) ** (K - k))
    return total


def mean_field_boundary(theta: int, K: int) -> float:
    """p* = 1 - sqrt(theta/K). Mean-field collapse boundary."""
    if K <= 0 or theta > K:
        return 1.0
    return 1.0 - math.sqrt(theta / K)


def tokenize_simple(text: str) -> List[str]:
    return text.split()


def subsample_tokens(tokens: List[str], drop_prob: float, seed: int) -> List[str]:
    rng = random.Random(seed)
    return [t for t in tokens if rng.random() > drop_prob]


def token_pair_hash(t_i: str, t_j: str) -> str:
    return hashlib.md5(f"({t_i},{t_j})".encode()).hexdigest()


def _evaluate_combo_worker(
    payload: Tuple[float, int, List[str], List[int], int, int, List[str]]
) -> List[Dict]:
    """Worker for one (drop_prob, K) parameter combo."""
    drop_prob, K, tokens, theta_values, seed, total_pairs_uniques, original_pair_ids_list = payload
    if K < 2:
        return []
    original_pair_ids = set(original_pair_ids_list)
    pair_counts = defaultdict(int)
    for k in range(K):
        run_seed = seed + k * 1000
        perturbed = subsample_tokens(tokens, drop_prob, run_seed)
        seen = set()
        for i in range(len(perturbed) - 1):
            pair_id = token_pair_hash(perturbed[i], perturbed[i + 1])
            if pair_id not in seen:
                pair_counts[pair_id] += 1
                seen.add(pair_id)

    count_dist = defaultdict(int)
    for _pid, c in pair_counts.items():
        count_dist[c] += 1

    rows: List[Dict] = []
    for theta in theta_values:
        if theta > K:
            continue
        n_persistent = sum(
            1 for pid, c in pair_counts.items()
            if c >= theta and pid in original_pair_ids
        )
        frac_persistent = n_persistent / max(1, total_pairs_uniques)
        pct_observed = 100.0 * n_persistent / max(1, len(pair_counts))
        q = (1 - drop_prob) ** 2
        theory_p_survival = binomial_survival_prob(K, q, theta)
        p_star = mean_field_boundary(theta, K)
        rows.append({
            'drop_prob': drop_prob,
            'K': K,
            'theta': theta,
            'n_persistent': n_persistent,
            'total_pairs': len(pair_counts),
            'total_unique_pairs': total_pairs_uniques,
            'frac_persistent': frac_persistent,
            'pct_persistent': pct_observed,
            'theory_p_survival': theory_p_survival,
            'p_star': p_star,
            'count_dist': dict(count_dist),
        })
    return rows


def run_stability_sweep(
    text: str,
    drop_probs: List[float],
    K_values: List[int],
    theta_values: List[int],
    seed: int = 42,
) -> Dict:
    """Run stability mode across parameter grid. Return full metrics."""
    tokens = tokenize_simple(text)
    if len(tokens) < 2:
        return {}

    original_pair_ids = set(
        token_pair_hash(tokens[i], tokens[i + 1])
        for i in range(len(tokens) - 1)
    )
    total_pairs_uniques = len(original_pair_ids)

    combos = [(drop_prob, K) for drop_prob in drop_probs for K in K_values if K >= 2]
    requested_workers = int(os.environ.get("STABILITY_WORKERS", "0") or "0")
    max_workers = choose_workers(
        submitted=len(combos),
        backend="process",
        max_workers=(requested_workers if requested_workers > 0 else None),
    )

    jobs = [
        JobSpec(
            job_id=f"combo-{idx}",
            fn=_evaluate_combo_worker,
            args=((combo[0], combo[1], tokens, theta_values, seed, total_pairs_uniques, list(original_pair_ids)),),
            retries=0,
        )
        for idx, combo in enumerate(combos)
    ]
    results: List[Dict] = []
    job_results, _metrics = run_tasks(
        jobs,
        config=ExecutionConfig(
            backend="process",
            max_workers=max_workers,
            queue_bound=max_workers * 2,
            retry_policy=RETRY_NONE,
        ),
    )
    for jr in job_results:
        if jr.ok and jr.value:
            results.extend(jr.value)

    results.sort(key=lambda r: (r["drop_prob"], r["K"], r["theta"]))

    return {
        'results': results,
        'n_tokens': len(tokens),
        'total_unique_pairs': total_pairs_uniques,
    }


def _run_plot(sweep: Dict, out_path: str = "stability_phase_plot.png") -> bool:
    """Generate overlay plot if matplotlib available."""
    try:
        import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel
    except ImportError:
        return False
    # Focus on one config for clarity: K=3, theta=2
    rows = [r for r in sweep['results'] if r['K'] == 3 and r['theta'] == 2]
    if not rows:
        rows = [r for r in sweep['results'] if r['K'] == 3][:10]  # fallback
    rows = sorted(rows, key=lambda x: x['drop_prob'])
    p_vals = [r['drop_prob'] for r in rows]
    emp_frac = [r['frac_persistent'] for r in rows]
    theory = [r['theory_p_survival'] for r in rows]
    p_star = rows[0]['p_star'] if rows else 0
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(p_vals, emp_frac, 'o-', label='Empirical (frac persistent)')
    ax.plot(p_vals, theory, 's--', alpha=0.8, label='Theory P(X≥θ)')
    ax.axvline(p_star, color='gray', linestyle=':', alpha=0.7, label=f'p* = {p_star:.2f}')
    ax.set_xlabel('Drop probability p')
    ax.set_ylabel('Fraction persistent (fixed denominator)')
    ax.set_title('Identity Phase Transition (K=3, θ=2)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-0.02, max(p_vals) + 0.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Plot saved: {out_path}")
    return True


def main():
    argv = sys.argv[1:]
    do_csv = '--csv' in argv
    do_plot = '--plot' in argv
    if '--workers' in argv:
        idx = argv.index('--workers')
        if idx + 1 < len(argv):
            try:
                workers = max(1, int(argv[idx + 1]))
                os.environ["STABILITY_WORKERS"] = str(workers)
            except ValueError:
                pass

    text = "Action before knowledge. Structure emerges before language. Tokens become actions. Patterns become residues."
    print("=" * 70)
    print("THRESHOLD_ONSET STABILITY EXPERIMENTS")
    print("=" * 70)
    print(f"Input: {len(text.split())} tokens, {len(set(text.split()))} unique")
    print("-" * 70)

    drop_probs = [0.0, 0.05, 0.1, 0.15, 0.2]
    K_values = [3, 5, 7]
    theta_values = [2, 3]

    sweep = run_stability_sweep(text, drop_probs, K_values, theta_values, seed=42)
    total_unique = sweep['total_unique_pairs']

    # Table 1: Parameter sweep with fixed-denominator and theoretical
    print("\nTable 1: Parameter sweep (drop_prob, K, theta)")
    print("  frac = fraction of original unique pairs that persist (fixed denominator)")
    print("  theory = P(X >= theta) for X ~ Binomial(K, (1-p)^2)")
    print("-" * 90)
    print(f"{'drop_prob':>10} {'K':>4} {'theta':>6} {'persistent':>10} {'frac':>8} {'theory':>8} {'p*':>6}")
    print("-" * 90)
    for r in sweep['results']:
        print(f"{r['drop_prob']:>10.2f} {r['K']:>4} {r['theta']:>6} "
              f"{r['n_persistent']:>10} {r['frac_persistent']:>7.2%} {r['theory_p_survival']:>7.2%} {r['p_star']:>6.2f}")

    # Distribution over recurrence (sample for drop_prob=0.1, K=3)
    sample = [r for r in sweep['results'] if r['drop_prob'] == 0.1 and r['K'] == 3 and r['theta'] == 2]
    if sample:
        r0 = sample[0]
        print("\n" + "-" * 70)
        print("Table 2: Recurrence count distribution (drop_prob=0.1, K=3)")
        print("-" * 70)
        for c in sorted(r0['count_dist'].keys(), reverse=True):
            print(f"  Appeared in {c}/{r0['K']} runs: {r0['count_dist'][c]} pairs")

    print("\n" + "=" * 70)
    print("Phase boundary: p* = 1 - sqrt(theta/K). Above p*, identities collapse.")
    print("=" * 70)

    if do_csv:
        csv_path = Path(project_root) / "stability_phase_data.csv"
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write("drop_prob,K,theta,n_persistent,frac_persistent,theory_p_survival,p_star\n")
            for r in sweep['results']:
                f.write(f"{r['drop_prob']},{r['K']},{r['theta']},{r['n_persistent']},"
                        f"{r['frac_persistent']:.6f},{r['theory_p_survival']:.6f},{r['p_star']:.4f}\n")
        print(f"\nCSV saved: {csv_path}")

    if do_plot:
        if not _run_plot(sweep):
            print("\n(Install matplotlib for --plot: pip install matplotlib)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
