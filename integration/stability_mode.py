#!/usr/bin/env python3
"""
THRESHOLD_ONSET Stability Mode

Identity by recurrence under structural perturbation.
Each run receives a perturbed token sequence (subsampling).
Segment identity is token-grounded: hash((t_i, t_{i+1})).
Persistence = recurrence across perturbed observations.
"""

import sys
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def tokenize_simple(text: str) -> List[str]:
    return text.split()


def subsample_tokens(tokens: List[str], drop_prob: float, seed: int) -> List[str]:
    """Subsample: randomly drop drop_prob fraction of positions, preserve order."""
    rng = random.Random(seed)
    return [t for t in tokens if rng.random() > drop_prob]


def token_pair_hash(t_i: str, t_j: str) -> str:
    """Canonical segment identity: hash of token pair."""
    h = hashlib.md5(f"({t_i},{t_j})".encode()).hexdigest()
    return h


def run_stability_mode(
    text: str,
    num_runs: int = 3,
    drop_prob: float = 0.1,
    theta: int = 2,
    seed: int = 42,
    output_mode: str = "pair",
) -> Dict:
    """
    Run stability mode: perturbed runs, token-level persistence.

    output_mode: "pair" -> identity maps to (t_i, t_j) both tokens
                "pivot" -> identity maps to t_i only (first token)
                "both" -> return both mappings

    Returns:
        - persistent_segments: set of token pairs that persist
        - persistence_counts: dict token_pair -> count
        - identity_to_token: dict identity_hash -> token (pivot) or (t_i, t_j) per output_mode
        - identity_to_tokens: dict identity_hash -> [t_i, t_j] (always, for pair fidelity)
        - n_runs, n_persistent
    """
    tokens = tokenize_simple(text)
    if len(tokens) < 2:
        return {'persistent_segments': set(), 'persistence_counts': {}, 'n_runs': num_runs}

    # Count recurrence of each token pair across runs
    pair_counts = defaultdict(int)

    for k in range(num_runs):
        run_seed = seed + k * 1000
        perturbed = subsample_tokens(tokens, drop_prob, run_seed)
        seen_this_run = set()

        for i in range(len(perturbed) - 1):
            pair = (perturbed[i], perturbed[i + 1])
            pair_id = token_pair_hash(pair[0], pair[1])
            if pair_id not in seen_this_run:
                pair_counts[pair_id] += 1
                seen_this_run.add(pair_id)

    # Persistent = recurrence >= theta
    persistent = {
        pair_id for pair_id, count in pair_counts.items()
        if count >= theta
    }

    # Build identity -> token (first token of pair)
    # We need to recover the token pair from persistence; we store (t_i, t_j) per pair_id
    pair_id_to_tokens = {}
    for k in range(num_runs):
        run_seed = seed + k * 1000
        perturbed = subsample_tokens(tokens, drop_prob, run_seed)
        for i in range(len(perturbed) - 1):
            pair = (perturbed[i], perturbed[i + 1])
            pair_id = token_pair_hash(pair[0], pair[1])
            if pair_id in persistent and pair_id not in pair_id_to_tokens:
                pair_id_to_tokens[pair_id] = pair

    identity_to_tokens = {pid: [p[0], p[1]] for pid, p in pair_id_to_tokens.items()}
    if output_mode == "pair":
        identity_to_token = {pid: tuple(p) for pid, p in identity_to_tokens.items()}
    else:
        identity_to_token = {pid: p[0] for pid, p in pair_id_to_tokens.items()}

    return {
        'persistent_segments': persistent,
        'persistence_counts': dict(pair_counts),
        'identity_to_token': identity_to_token,
        'identity_to_tokens': identity_to_tokens,
        'n_runs': num_runs,
        'n_persistent': len(persistent),
        'drop_prob': drop_prob,
        'theta': theta,
    }


def main():
    text = "Action before knowledge. Structure emerges before language. Tokens become actions."
    print("=" * 60)
    print("THRESHOLD_ONSET STABILITY MODE")
    print("=" * 60)
    print(f"Input: {text[:50]}...")
    print(f"drop_prob=0.1, K=3, theta=2")
    print("-" * 60)

    result = run_stability_mode(text, num_runs=3, drop_prob=0.1, theta=2, seed=42, output_mode="pair")

    print(f"Runs: {result['n_runs']}")
    print(f"Persistent token pairs: {result['n_persistent']}")
    print(f"Identity -> tokens (pair, sample): {list(result['identity_to_tokens'].items())[:5]}")
    print("-" * 60)
    print("Stability mode: identity by recurrence under perturbation.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
