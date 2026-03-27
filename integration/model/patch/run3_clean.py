"""
run3_clean.py — Run 3 launcher with all fixes applied.

Fixes applied vs run1 and run2:
  1. Corpus cleaned first (fix_corpus.py must be run once before this)
  2. Generation disabled during training (already correct in v4)
  3. Corpus loaded with error-tolerant parser (skips bad lines instead of disabling)
  4. Uses v4 santek_base_model.py (all 9 tokenization methods, additive merge)
  5. Epochs set to a sensible value with early stopping

Usage:
  # Step 1: Fix corpus ONCE
  python fix_corpus.py --input data/hindu_corpus_real.jsonl

  # Step 2: Run training
  python run3_clean.py

  # Step 3: Generate
  python santek_base_model.py generate "Om Namah Shivaya"
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path


def load_corpus_safe(path: Path):
    """Load JSONL corpus, skip malformed lines instead of crashing."""
    records = []
    bad = 0
    with open(path, encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                text = str(obj.get('text', '')).strip()
                if text:
                    records.append(text)
            except json.JSONDecodeError as e:
                bad += 1
                if bad <= 5:
                    print(f"  [WARN] Skipping bad line {i}: {e}")
    if bad:
        print(f"  [WARN] Total skipped: {bad} malformed lines")
    return records


def main():
    # ── Config ────────────────────────────────────────────────────────────────
    CORPUS_PATH = Path("data/hindu_corpus_real.jsonl")
    CORPUS_CLEAN_PATH = Path("data/hindu_corpus_clean.jsonl")   # produced by fix_corpus.py
    MODEL_PATH = Path("output/santek_base_model_v4.json")

    EPOCHS = 500          # Reduced from 25000 — early stopping will kick in well before
    ETA = 0.10
    DECAY = 0.05
    MAX_STREAK = 3
    PATIENCE = 5
    TENSION_THRESHOLD = 0.10

    print()
    print("=" * 70)
    print("  SanTEK Run 3  —  Clean corpus, v4 model, proper training")
    print("=" * 70)

    # ── Corpus ────────────────────────────────────────────────────────────────
    # Prefer clean corpus if it exists
    corpus_to_use = CORPUS_CLEAN_PATH if CORPUS_CLEAN_PATH.exists() else CORPUS_PATH

    if not corpus_to_use.exists():
        print(f"\n  [ERROR] Corpus not found: {corpus_to_use}")
        print(f"  Run: python fix_corpus.py --input {CORPUS_PATH}")
        sys.exit(1)

    if corpus_to_use == CORPUS_PATH:
        print(f"\n  [WARN] Using original corpus (not cleaned). Run fix_corpus.py first.")
        print(f"  Continuing with error-tolerant loader...")

    print(f"\n  Loading corpus: {corpus_to_use}")
    t0 = time.time()
    texts = load_corpus_safe(corpus_to_use)
    print(f"  Loaded {len(texts):,} texts in {time.time()-t0:.1f}s")

    if not texts:
        print("  [ERROR] No texts loaded. Check corpus path.")
        sys.exit(1)

    # ── Import and train ──────────────────────────────────────────────────────
    try:
        from santek_base_model import santek_train
    except ImportError:
        print("  [ERROR] Cannot import santek_base_model. Run from THRESHOLD_ONSET root.")
        sys.exit(1)

    print(f"\n  Training with {len(texts):,} texts")
    print(f"  Epochs: {EPOCHS} (early stop at tension < {TENSION_THRESHOLD} or plateau {PATIENCE})")
    print(f"  Model output: {MODEL_PATH}")
    print()

    result = santek_train(
        corpus=texts,
        epochs=EPOCHS,
        eta=ETA,
        decay=DECAY,
        max_streak=MAX_STREAK,
        tension_threshold=TENSION_THRESHOLD,
        patience=PATIENCE,
        verbose=True,
        model_path=MODEL_PATH,
    )

    print(f"\n  ✓ Training complete")
    print(f"  Best accuracy : {result.best_accuracy:.4f}  ({result.best_accuracy*100:.1f}%)")
    print(f"  Best 9-centric: {result.best_9centric}")
    print(f"  Epochs run    : {result.total_epochs_run}")
    print(f"  Converged     : {result.converged}")
    print(f"  Model saved   : {MODEL_PATH}")
    print()
    print(f"  Next: python santek_base_model.py generate 'your prompt' --model {MODEL_PATH}")


if __name__ == '__main__':
    main()
