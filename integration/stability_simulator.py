#!/usr/bin/env python3
"""
THRESHOLD_ONSET Stability Simulator — Phase 0

Validates governing physics before CorpusState implementation.
Simulates S_O evolution on synthetic corpus.

Laws (from docs/STABILITY_LAW.md):
- Reinforcement: if present, S_O += r (new: S_O = r)
- Decay: if absent, S_O *= (1 - d); core uses d_core = d * 0.1
- Atomicization: if S_O > T_atomic, mark core
- Prune: remove S_O < theta_prune

Gate: stable identities converge, noise decays, memory does not explode.

Usage:
    python integration/stability_simulator.py           # 200 docs (default)
    python integration/stability_simulator.py --stress  # 5k, 20k, 50k docs
"""

import argparse
import random
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def generate_synthetic_corpus(
    n_docs: int,
    n_stable: int,
    n_noise_per_doc: int,
    stable_recurrence_prob: float = 0.8,
    seed: int = 42,
) -> List[Set[str]]:
    """
    Generate synthetic corpus.
    - stable IDs: recur in ~stable_recurrence_prob of docs
    - noise IDs: unique per doc, appear once
    """
    rng = random.Random(seed)
    corpus: List[Set[str]] = []
    doc_id = 0

    for _ in range(n_docs):
        doc: Set[str] = set()

        # Stable: recur with probability stable_recurrence_prob
        for i in range(n_stable):
            oid = f"stable_{i}"
            if rng.random() < stable_recurrence_prob:
                doc.add(oid)

        # Noise: unique per doc
        for _ in range(n_noise_per_doc):
            doc.add(f"noise_{doc_id}_{rng.randint(0, 9999)}")

        corpus.append(doc)
        doc_id += 1

    return corpus


def run_simulator(
    corpus: List[Set[str]],
    r: float = 1.0,
    d: float = 0.1,
    T_atomic: float = 10.0,
    theta_prune: float = 0.01,
    prune_every: int = 10,
    use_atomicization: bool = True,
    sample_interval: int = 1,
) -> Dict[str, Any]:
    """
    Run stability evolution. Returns metrics.
    sample_interval: record history every N docs (1 = all; 500 for long runs).
    """
    S: Dict[str, float] = {}
    core: Set[str] = set()
    history: List[Dict[str, Any]] = []

    for doc_idx, doc in enumerate(corpus):
        # 1. Reinforce present
        for oid in doc:
            if oid not in S:
                S[oid] = r
            else:
                S[oid] += r

        # 2. Decay absent
        for oid in list(S.keys()):
            if oid not in doc:
                decay_rate = (d * 0.1) if (use_atomicization and oid in core) else d
                S[oid] *= 1.0 - decay_rate

        # 3. Atomicize
        if use_atomicization:
            for oid, s in list(S.items()):
                if s > T_atomic:
                    core.add(oid)

        # 4. Prune
        if (doc_idx + 1) % prune_every == 0:
            to_remove = [oid for oid, s in S.items() if s < theta_prune]
            for oid in to_remove:
                del S[oid]
                core.discard(oid)

        # Record (sampled)
        if (doc_idx + 1) % sample_interval == 0 or doc_idx == len(corpus) - 1:
            stable_ids = [o for o in S if o.startswith("stable_")]
            noise_ids = [o for o in S if o.startswith("noise_")]
            history.append({
                "doc": doc_idx + 1,
                "n_objects": len(S),
                "n_stable": len(stable_ids),
                "n_noise": len(noise_ids),
                "n_core": len(core),
                "avg_S_stable": sum(S.get(o, 0) for o in stable_ids) / max(1, len(stable_ids)),
                "avg_S_noise": sum(S.get(o, 0) for o in noise_ids) / max(1, len(noise_ids)),
            })

    # Final metrics
    stable_ids = [o for o in S if o.startswith("stable_")]
    noise_ids = [o for o in S if o.startswith("noise_")]

    # Growth slope: objects per doc over second half vs first half
    growth_slope = None
    if len(history) >= 2:
        mid = len(history) // 2
        early = history[mid]
        late = history[-1]
        doc_span = max(1, late["doc"] - early["doc"])
        growth_slope = (late["n_objects"] - early["n_objects"]) / doc_span

    return {
        "n_docs": len(corpus),
        "final_n_objects": len(S),
        "final_n_stable": len(stable_ids),
        "final_n_noise": len(noise_ids),
        "final_n_core": len(core),
        "avg_S_stable_final": sum(S.get(o, 0) for o in stable_ids) / max(1, len(stable_ids)),
        "avg_S_noise_final": sum(S.get(o, 0) for o in noise_ids) / max(1, len(noise_ids)),
        "growth_slope": growth_slope,
        "history": history,
        "gate": {
            "stable_converged": len(stable_ids) > 0 and len(stable_ids) <= 50,
            "noise_decayed": len(noise_ids) < len(corpus) * 2,
            "memory_bounded": len(S) < len(corpus) * 5,
        },
    }


def run_stress_simulation() -> Dict[str, Any]:
    """
    Run long-horizon simulation at 5k, 20k, 50k docs.
    Returns growth curves and slopes for physics validation.
    """
    scales = [5_000, 20_000, 50_000]
    results = []

    for n_docs in scales:
        corpus = generate_synthetic_corpus(
            n_docs=n_docs,
            n_stable=20,
            n_noise_per_doc=5,
            stable_recurrence_prob=0.7,
            seed=42,
        )
        sample = max(1, n_docs // 100)  # ~100 samples per run
        result = run_simulator(
            corpus,
            r=1.0,
            d=0.1,
            T_atomic=10.0,
            theta_prune=0.01,
            prune_every=10,
            use_atomicization=True,
            sample_interval=sample,
        )
        result["scale"] = n_docs
        results.append(result)

    return {"scales": scales, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser(description="Stability simulator")
    parser.add_argument("--stress", action="store_true", help="Run 5k, 20k, 50k docs")
    args = parser.parse_args()

    if args.stress:
        return _run_stress(args)
    return _run_default()


def _run_default() -> int:
    """Default 200-doc run."""
    print("=" * 60)
    print("THRESHOLD_ONSET STABILITY SIMULATOR")
    print("=" * 60)

    corpus = generate_synthetic_corpus(
        n_docs=200,
        n_stable=20,
        n_noise_per_doc=5,
        stable_recurrence_prob=0.7,
        seed=42,
    )

    print(f"Corpus: {len(corpus)} docs, ~{len(corpus[0])} objects per doc")
    print("-" * 60)

    result = run_simulator(
        corpus,
        r=1.0,
        d=0.1,
        T_atomic=10.0,
        theta_prune=0.01,
        prune_every=10,
        use_atomicization=True,
    )

    print("RESULTS")
    print("-" * 60)
    print(f"Final objects: {result['final_n_objects']}")
    print(f"  Stable: {result['final_n_stable']} (avg S = {result['avg_S_stable_final']:.2f})")
    print(f"  Noise:  {result['final_n_noise']} (avg S = {result['avg_S_noise_final']:.4f})")
    print(f"  Core:   {result['final_n_core']}")
    if result.get("growth_slope") is not None:
        print(f"  Growth slope (2nd half): {result['growth_slope']:.4f} objects/doc")
    print("-" * 60)
    print("GATE")
    print("-" * 60)
    g = result["gate"]
    print(f"  Stable converged: {g['stable_converged']}")
    print(f"  Noise decayed:    {g['noise_decayed']}")
    print(f"  Memory bounded:  {g['memory_bounded']}")
    passed = all(g.values())
    print(f"  PASS: {passed}")
    print("=" * 60)

    return 0 if passed else 1


def _run_stress(args) -> int:  # pylint: disable=unused-argument
    """Long-horizon stress: 5k, 20k, 50k docs."""
    print("=" * 70)
    print("THRESHOLD_ONSET STABILITY SIMULATOR — LONG-HORIZON STRESS")
    print("=" * 70)
    print("Scales: 5,000 | 20,000 | 50,000 docs")
    print("Metrics: object count, stable count, noise tail, growth slope")
    print("-" * 70)

    stress = run_stress_simulation()
    all_passed = True

    for r in stress["results"]:
        n = r["scale"]
        print(f"\n  {n:,} docs:")
        print(f"    Final objects: {r['final_n_objects']} (stable: {r['final_n_stable']}, noise: {r['final_n_noise']})")
        print(f"    Avg S stable: {r['avg_S_stable_final']:.1f}  |  noise: {r['avg_S_noise_final']:.4f}")
        slope = r.get("growth_slope")
        if slope is not None:
            print(f"    Growth slope (2nd half): {slope:.4f} objects/doc")
            if slope > 0.5:
                print("    WARNING: slope > 0.5 - consider increasing decay/prune")
        passed = all(r["gate"].values())
        if not passed:
            all_passed = False
        print(f"    Gate: {'PASS' if passed else 'FAIL'}")

    print("\n" + "-" * 70)
    print("INTERPRETATION")
    print("-" * 70)
    slopes = [x.get("growth_slope") for x in stress["results"] if x.get("growth_slope") is not None]
    if slopes:
        if len(slopes) >= 2 and slopes[-1] < slopes[0]:
            print("  Slope flattens with scale -> physics holds (sublinear trend)")
        elif max(slopes) < 0.1:
            print("  Slope < 0.1 -> memory growth effectively flat")
        elif max(slopes) > 0.5:
            print("  Slope > 0.5 -> consider increasing decay_rate or theta_prune")
        else:
            print("  Slope moderate -> monitor at 100k+ docs")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
