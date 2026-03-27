#!/usr/bin/env python3
"""
THRESHOLD_ONSET Baselines

Simple alternatives for comparison on structure emergence metrics:
- Random: uniform random token selection from vocab
- Markov-1: first-order Markov (token -> next token)
- Echo: identity-preserving (echo input tokens)
- Uniform: repeat first token only (minimal structure)
"""

import random
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

import sys

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def tokenize_simple(text: str) -> List[str]:
    return text.split()


def token_to_residue(token: str) -> float:
    h = hashlib.sha256(token.encode()).hexdigest()[:8]
    return float(int(h, 16) % 10000) / 10000.0


# ---------------------------------------------------------------------------
# Baseline 1: Random
# ---------------------------------------------------------------------------
def baseline_random(tokens: List[str], length: int, seed: int = 42) -> List[str]:
    """Generate by uniformly sampling tokens from vocab."""
    rng = random.Random(seed)
    vocab = list(set(tokens))
    if not vocab:
        return []
    return [rng.choice(vocab) for _ in range(length)]


# ---------------------------------------------------------------------------
# Baseline 2: Markov-1
# ---------------------------------------------------------------------------
def baseline_markov1(tokens: List[str], length: int, seed: int = 42) -> List[str]:
    """First-order Markov: P(next|current) from empirical bigram counts."""
    if len(tokens) < 2:
        return (tokens * ((length // len(tokens)) + 1))[:length] if tokens else []
    rng = random.Random(seed)
    counts = defaultdict(lambda: defaultdict(int))
    for i in range(len(tokens) - 1):
        counts[tokens[i]][tokens[i + 1]] += 1
    out = [tokens[0]]
    for _ in range(length - 1):
        cur = out[-1]
        next_tokens = list(counts[cur].keys()) if cur in counts else []
        weights = [counts[cur][t] for t in next_tokens] if next_tokens else []
        if not next_tokens or not weights:
            chosen = rng.choice(tokens)
        else:
            total = sum(weights)
            probs = [w / total for w in weights]
            chosen = rng.choices(next_tokens, weights=probs, k=1)[0]
        out.append(chosen)
    return out[:length]


# ---------------------------------------------------------------------------
# Baseline 3: Echo
# ---------------------------------------------------------------------------
def baseline_echo(tokens: List[str], length: int, _seed: int = 42) -> List[str]:
    """Echo input tokens cyclically. Identity-preserving."""
    if not tokens:
        return []
    out = []
    for i in range(length):
        out.append(tokens[i % len(tokens)])
    return out


# ---------------------------------------------------------------------------
# Baseline 4: Uniform (repeat first token)
# ---------------------------------------------------------------------------
def baseline_uniform(tokens: List[str], length: int, _seed: int = 42) -> List[str]:
    """Repeat first token only. Minimal structure."""
    if not tokens:
        return []
    return [tokens[0]] * length


# ---------------------------------------------------------------------------
# Metrics (comparable to THRESHOLD_ONSET)
# ---------------------------------------------------------------------------
def count_self_transitions(seq: List[str]) -> int:
    """Count consecutive identical tokens (self-transitions)."""
    return sum(1 for i in range(len(seq) - 1) if seq[i] == seq[i + 1])


def decoder_consistency(tokens: List[str], vocab: set) -> float:
    """Fraction of tokens in vocab."""
    if not tokens:
        return 1.0
    return sum(1 for t in tokens if t in vocab) / len(tokens)


def compute_baseline_metrics(
    tokens: List[str],
    generated: List[str],
) -> Dict[str, Any]:
    vocab = set(tokens)
    self_trans = count_self_transitions(generated)
    total_trans = max(1, len(generated) - 1)
    return {
        'self_transition_rate': self_trans / total_trans,
        'constraint_violations': self_trans,
        'decoder_consistency': decoder_consistency(generated, vocab),
        'n_generated': len(generated),
    }


# ---------------------------------------------------------------------------
# Run all baselines on a corpus
# ---------------------------------------------------------------------------
def get_benchmark_corpus() -> List[Tuple[str, str]]:
    """Import and return the 39-sample benchmark corpus for fair comparison."""
    try:
        from integration.benchmark import BENCHMARK_CORPUS
    except ImportError:
        from benchmark import BENCHMARK_CORPUS
    return [(name, text) for name, text in BENCHMARK_CORPUS]


BASELINE_CORPUS = [
    ("short", "Hi there."),
    ("normal", "Action before knowledge. Structure emerges before language."),
    ("repeated", "the the the a a a"),
    ("single", "word"),
    ("long", " ".join(["word"] * 50)),
    ("punctuation", "Hello, world! How are you?"),
    ("mixed", "Action before knowledge. Structure emerges. Tokens become actions."),
    ("philosophy", "Structure emerges from action and repetition."),
    ("tech", "Tokens become residues. Residues form segments."),
    ("medium", "One two three four five six seven eight nine ten."),
]


def run_baselines(
    seed: int = 42,
    gen_length: int = 20,
    corpus: List[Tuple[str, str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Run all baselines; return {baseline_name: {metric: value}}."""
    if corpus is None:
        corpus = BASELINE_CORPUS
    results = {name: [] for name in ['random', 'markov1', 'echo', 'uniform']}

    for _name, text in corpus:
        tokens = tokenize_simple(text)
        if not tokens:
            continue

        for name, fn in [
            ('random', baseline_random),
            ('markov1', baseline_markov1),
            ('echo', baseline_echo),
            ('uniform', baseline_uniform),
        ]:
            gen = fn(tokens, gen_length, seed)
            m = compute_baseline_metrics(tokens, gen)
            results[name].append(m)

    # Aggregate
    agg = {}
    for name, runs in results.items():
        if not runs:
            continue
        n = len(runs)
        agg[name] = {
            'avg_self_transition_rate': sum(r['self_transition_rate'] for r in runs) / n,
            'avg_constraint_violations': sum(r['constraint_violations'] for r in runs) / n,
            'total_constraint_violations': sum(r['constraint_violations'] for r in runs),
            'decoder_consistency': sum(r['decoder_consistency'] for r in runs) / n,
            'n_samples': n,
        }
    return agg


def main():
    use_benchmark = '--benchmark' in sys.argv
    corpus = get_benchmark_corpus() if use_benchmark else BASELINE_CORPUS

    print("=" * 60)
    print("THRESHOLD_ONSET BASELINES")
    print("=" * 60)
    print(f"Corpus: {len(corpus)} samples" + (" (benchmark)" if use_benchmark else ""))
    print("-" * 60)

    agg = run_baselines(seed=42, gen_length=20, corpus=corpus)

    print(f"{'Baseline':<12} {'SelfTrans':>10} {'Violations':>12} {'Consistency':>12}")
    print("-" * 50)
    for name, m in agg.items():
        print(f"{name:<12} {m['avg_self_transition_rate']:>10.2%} "
              f"{m['total_constraint_violations']:>12} {m['decoder_consistency']:>12.2%}")
    print("=" * 60)
    print("THRESHOLD_ONSET achieves 0% self-transition (invariant) vs baselines.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
