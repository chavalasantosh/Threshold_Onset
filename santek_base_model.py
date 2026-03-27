#!/usr/bin/env python3
"""
santek_base_model.py
═══════════════════════════════════════════════════════════════════════════════
SanTEK Base Model  —  v1.0
Author : Chavala Santosh
Family : THRESHOLD_ONSET / SanTOK / SanVerse / Sanformers ecosystem

"Structure first. Generation second. No borrowed ideas."

───────────────────────────────────────────────────────────────────────────────
WHAT THIS IS
───────────────────────────────────────────────────────────────────────────────
This is the first generative base model in the THRESHOLD_ONSET family.

It builds directly on what is already proven:

  Phase 0-4   — structural pipeline (token → residue → identity → symbol)
  SanTEK-SLE  — learning engine (99.15% accuracy, no third-party code)
  APR         — Accumulated Path Reinforcement (deadlock-breaking update rule)
  ASD         — Accumulated Structural Delta (streak-capped learning)

What is NEW in this file (the "base model" part):

  TRAIN  — run SanTEK-SLE on a corpus, save full model to JSON
  VOCAB  — build symbol→token table during training (so we can decode later)
  GEN    — given a prompt, run it through the pipeline, then extend the
           symbol sequence using learned path_scores, then decode back to text
  CHAT   — interactive loop: you type, it responds, continuously

Zero third-party imports. Zero external formulas. Pure stdlib throughout.

───────────────────────────────────────────────────────────────────────────────
ARCHITECTURE
───────────────────────────────────────────────────────────────────────────────

  YOUR TEXT IN
       │
       ▼
  Phase 0-4 pipeline ──► symbol sequence  [3, 7, 1, 5, 2 ...]
       │                  + vocab table   {3: "Action", 7: "before", ...}
       │                  + path_scores   {(3,7): 0.91, (7,1): 0.88, ...}
       │
       ▼  (SanTEK-SLE training over corpus)
  Learned path_scores  ──► saved to base_model.json
       │
       ▼  (generation)
  Prompt → pipeline → symbols → extend via path_scores → decode → TEXT OUT

───────────────────────────────────────────────────────────────────────────────
GENERATION ALGORITHM  — "Structural Greedy Beam"  (invented here)
───────────────────────────────────────────────────────────────────────────────

  1. Run prompt through Phase 0-4 pipeline → get symbol sequence S
  2. Take last symbol of S as the starting point
  3. Repeat N times:
       candidates = all (last_sym, next_sym) in path_scores where
                    next_sym ≠ last_sym   (no self-transition; A_ii = 0)
       if no candidates: stop
       score each candidate: path_scores[(last, next)]
       apply recency penalty: -0.3 per occurrence of next in recent window
       pick highest scoring next_sym  →  append to sequence
  4. Convert symbol sequence → tokens via vocab table
  5. Join tokens → output text

No attention. No weights matrix. No gradients. No embeddings.
The learned structure IS the model.

───────────────────────────────────────────────────────────────────────────────
USAGE
───────────────────────────────────────────────────────────────────────────────

  # Train on corpus from config (config/default.json → santek_base_model.training_corpus_file or .training_corpus)
  python santek_base_model.py train

  # Train on custom texts
  python santek_base_model.py train --corpus "text one" "text two" --epochs 200

  # Generate from a prompt using saved model
  python santek_base_model.py generate "Action before knowledge"

  # Generate with custom length
  python santek_base_model.py generate "Structure emerges" --length 30

  # Chat mode (interactive)
  python santek_base_model.py chat

  # All defaults, no flags — enters chat
  python santek_base_model.py

───────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import List

# Canonical model surface
from integration.model import (
    SantekModel,
    eval_held_out,
    load_santek_model,
    save_santek_model,
    santek_generate,
    santek_train,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

VERSION = "1.0"

DEFAULT_MODEL_PATH = Path("output") / "santek_base_model.json"


def _download_corpus_url(url: str, cache_path: Path) -> str:
    """Download URL to cache_path; return raw text. Stdlib only."""
    req = urllib.request.Request(url, headers={"User-Agent": "THRESHOLD_ONSET/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(raw, encoding="utf-8")
    return raw


def _load_corpus_from_config(repo_root: Path) -> List[str]:
    """Load training corpus from config: .training_corpus_urls (list) or .training_corpus_url (single), .training_corpus_file, or .training_corpus. No hardcoded text."""
    path = repo_root / "config" / "default.json"
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    block = data.get("santek_base_model") or {}
    split_mode = (block.get("training_corpus_split") or "paragraphs").strip().lower()

    # 1) Multiple public URLs: download each (cached by URL hash), combine, then split
    urls = block.get("training_corpus_urls")
    if isinstance(urls, list) and urls:
        cache_dir = repo_root / "data" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        all_raw: List[str] = []
        for u in urls:
            if not isinstance(u, str) or not u.strip():
                continue
            u = u.strip()
            h = hashlib.sha256(u.encode("utf-8")).hexdigest()[:16]
            cache_path = cache_dir / f"corpus_{h}.txt"
            if not cache_path.exists():
                try:
                    _download_corpus_url(u, cache_path)
                except Exception as e:
                    print(f"  [warn] Could not download {u[:50]}...: {e}", file=sys.stderr)
                    continue
            all_raw.append(cache_path.read_text(encoding="utf-8", errors="replace"))
        if all_raw:
            raw = "\n\n".join(all_raw)
            if split_mode == "lines":
                docs = [s.strip() for s in raw.splitlines() if s.strip()]
            else:
                docs = [s.strip() for s in raw.split("\n\n") if s.strip()]
            if docs:
                return docs
    # 2) Single public URL
    url = block.get("training_corpus_url")
    if url and isinstance(url, str):
        cache_path = repo_root / "data" / "cache" / "downloaded_corpus.txt"
        if not cache_path.exists():
            try:
                _download_corpus_url(url.strip(), cache_path)
            except Exception as e:
                print(f"  [warn] Could not download corpus URL: {e}", file=sys.stderr)
                return []
        raw = cache_path.read_text(encoding="utf-8", errors="replace")
        if split_mode == "lines":
            docs = [s.strip() for s in raw.splitlines() if s.strip()]
        else:
            docs = [s.strip() for s in raw.split("\n\n") if s.strip()]
        if docs:
            return docs
    # 2) Local file: one document per line
    file_path = block.get("training_corpus_file")
    if file_path:
        full = repo_root / file_path
        if full.exists():
            lines = full.read_text(encoding="utf-8", errors="replace").strip().splitlines()
            out = [s.strip() for s in lines if s.strip()]
            if out:
                return out
    # 3) List in config
    arr = block.get("training_corpus")
    if isinstance(arr, list):
        return [str(s).strip() for s in arr if str(s).strip()]
    return []


def _load_corpus_jsonl_splits(repo_root: Path):
    """
    If config has santek_base_model.corpus_jsonl (path to JSONL), load and split.
    Returns (train_texts, val_texts, test_texts, manifest) or None if not configured.
    """
    path = repo_root / "config" / "default.json"
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None
    block = data.get("santek_base_model") or {}
    jpath = block.get("corpus_jsonl") or ""
    if not jpath or not isinstance(jpath, str):
        return None
    full = repo_root / jpath.strip()
    if not full.exists():
        return None
    from integration.model.dataset import load_and_split, texts_from_records
    train_rec, val_rec, test_rec, manifest = load_and_split(full)
    return (
        texts_from_records(train_rec),
        texts_from_records(val_rec),
        texts_from_records(test_rec),
        manifest,
    )


def _load_val_corpus(repo_root: Path) -> List[str]:
    """Load validation corpus from config: santek_base_model.training_corpus_file_val (one doc per line). Used for held-out eval only."""
    path = repo_root / "config" / "default.json"
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    block = data.get("santek_base_model") or {}
    file_path = block.get("training_corpus_file_val") or ""
    if not file_path or not isinstance(file_path, str):
        return []
    full = repo_root / file_path.strip()
    if not full.exists():
        return []
    lines = full.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    return [s.strip() for s in lines if s.strip()]


def _default_prompt_from_config(repo_root: Path) -> str:
    """Default prompt for generate when none given. From config santek_base_model.default_prompt."""
    path = repo_root / "config" / "default.json"
    if not path.exists():
        return "Action before knowledge."
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return "Action before knowledge."
    block = data.get("santek_base_model") or {}
    return str(block.get("default_prompt", "Action before knowledge.")).strip() or "Action before knowledge."


# ─────────────────────────────────────────────────────────────────────────────
# REPO ROOT  — for passing to canonical API
# ─────────────────────────────────────────────────────────────────────────────

def _find_repo_root() -> Path:
    """Walk up from this file until we find integration/run_complete.py."""
    here = Path(os.path.abspath(__file__)).parent
    for candidate in [here, here.parent, here.parent.parent]:
        if (candidate / "integration" / "run_complete.py").exists():
            return candidate
    raise FileNotFoundError(
        "Cannot locate THRESHOLD_ONSET repo root. "
        "Place santek_base_model.py in the repo root or a subfolder."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TRAIN  — canonical: integration.model.santek_base.train + save
# ─────────────────────────────────────────────────────────────────────────────

def cmd_train(
    corpus: List[str],
    epochs: int = 100,
    eta: float = 0.10,
    decay: float = 0.05,
    max_streak: int = 3,
    tension_threshold: float = 0.10,
    patience: int = 5,
    model_path: Path = DEFAULT_MODEL_PATH,
    verbose: bool = True,
    split_manifest=None,
) -> None:
    """Train on corpus only (canonical: integration.model.santek_base)."""
    _print_banner()
    print("  MODE: TRAIN  (train split only — no val/test used for training)")
    print(f"  Corpus: {len(corpus)} texts  |  Epochs: {epochs}  |  Eta: {eta}")
    print(f"  Decay: {decay}  |  MaxStreak: {max_streak}  |  Patience: {patience}")
    print(f"  Output: {model_path}")
    print()

    repo_root = _find_repo_root()
    training_config = {
        "epochs": epochs,
        "eta": eta,
        "decay": decay,
        "max_streak": max_streak,
        "tension_threshold": tension_threshold,
        "patience": patience,
    }
    try:
        # Compatibility across API variants.
        train_params = inspect.signature(santek_train).parameters
        trainer_writes_model_file = "model_path" in train_params
        train_kwargs = {
            "corpus": corpus,
            "epochs": epochs,
            "eta": eta,
            "decay": decay,
            "max_streak": max_streak,
            "tension_threshold": tension_threshold,
            "patience": patience,
        }
        if "repo_root" in train_params:
            train_kwargs["repo_root"] = repo_root
        # Single file: santek_train checkpoints post-init, every epoch, and final atomic save.
        if "model_path" in train_params:
            train_kwargs["model_path"] = Path(model_path)
        if "training_config" in train_params:
            train_kwargs["training_config"] = dict(training_config)
        if "split_manifest" in train_params:
            train_kwargs["split_manifest"] = split_manifest
        train_out = santek_train(**train_kwargs)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # Compatibility: training may return either a SantekModel or a
    # SanTEKTrainingResult-like object. Normalize to SantekModel.
    if hasattr(train_out, "path_scores") and hasattr(train_out, "vocab"):
        model = train_out
        meta = dict(getattr(model, "meta", {}) or {})
    else:
        meta = {
            "converged": getattr(train_out, "converged", False),
            "converged_at_epoch": getattr(train_out, "converged_at_epoch", None),
            "epochs_run": getattr(train_out, "total_epochs_run", epochs),
            "best_accuracy": float(getattr(train_out, "best_accuracy", 0.0) or 0.0),
            "best_9centric": int(getattr(train_out, "best_9centric", 1) or 1),
            "best_tension": float(getattr(train_out, "best_tension", 1.0) or 1.0),
            "edge_count": len(getattr(train_out, "final_path_scores", {}) or {}),
            "vocab_size": len(getattr(train_out, "global_vocab", {}) or {}),
        }
        model = SantekModel(
            path_scores=dict(getattr(train_out, "final_path_scores", {}) or {}),
            vocab=dict(getattr(train_out, "global_vocab", {}) or {}),
            meta=meta,
        )

    meta.setdefault("author", "Chavala Santosh")
    meta.setdefault("family", "THRESHOLD_ONSET / SanTOK / SanVerse / Sanformers")
    model = SantekModel(path_scores=model.path_scores, vocab=model.vocab, meta=meta)

    saved_path = Path(model_path).resolve()
    if not trainer_writes_model_file:
        saved_path = save_santek_model(
            model,
            model_path,
            training_config=training_config,
            split_manifest=split_manifest,
        ).resolve()
    if verbose:
        print(f"  Best accuracy : {model.meta.get('best_accuracy', 0):.4f}")
        bt = model.meta.get("best_tension")
        if bt is not None:
            print(f"  Best tension  : {float(bt):.4f}  (lowest mean epoch tension)")
        if trainer_writes_model_file:
            print(f"  Model file    : {saved_path}  (checkpoints + final save from trainer)")
        else:
            print(f"  Model saved → {saved_path}")
        print(f"  Edges: {len(model.path_scores)}  Vocab: {len(model.vocab)} symbols")
        print()


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE  — canonical; refuses disconnected prompts
# ─────────────────────────────────────────────────────────────────────────────

def cmd_generate(
    prompt: str,
    length: int = 20,
    model_path: Path = DEFAULT_MODEL_PATH,
    verbose: bool = True,
) -> str:
    """Generate from prompt; refuses if prompt is disconnected from learned graph."""
    try:
        model = load_santek_model(model_path)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    repo_root = _find_repo_root()
    text_out, refused = santek_generate(
        prompt, model, repo_root, length=length, refuse_if_disconnected=True
    )

    if verbose:
        _print_banner()
        print("  MODE: GENERATE")
        print(f"  Model : {model_path}  ({len(model.path_scores)} edges, vocab={len(model.vocab)})")
        print(f"  Prompt: {prompt[:70]}{'...' if len(prompt) > 70 else ''}")
        print(f"  Length: {length} symbols")
        print()
        print("─" * 72)
        if refused:
            print("  REFUSED (disconnected or unparseable prompt)")
            print(f"  {text_out}")
        else:
            print("  GENERATED TEXT")
            print(f"  {text_out}")
        print()

    return text_out


# ─────────────────────────────────────────────────────────────────────────────
# CHAT  — canonical; refuses disconnected prompts
# ─────────────────────────────────────────────────────────────────────────────

def cmd_chat(
    model_path: Path = DEFAULT_MODEL_PATH,
    length: int = 20,
) -> None:
    """Interactive chat; refuses when prompt is disconnected from learned graph."""
    _print_banner()
    print("  MODE: CHAT")
    print(f"  Model: {model_path}")
    print(f"  Type your text and press Enter. Type 'exit' or 'quit' to stop.")
    print()

    try:
        model = load_santek_model(model_path)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        print("  Run first: python santek_base_model.py train", file=sys.stderr)
        sys.exit(1)

    print(f"  Model loaded  edges={len(model.path_scores)}  vocab={len(model.vocab)}")
    print()

    repo_root = _find_repo_root()

    while True:
        try:
            user_input = input("  You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  [exit]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("  [exit]")
            break

        text_out, refused = santek_generate(
            user_input, model, repo_root, length=length, refuse_if_disconnected=True
        )
        if refused:
            print(f"  Model> {text_out}")
        elif text_out:
            print(f"  Model> {text_out}")
        else:
            print("  [model] (no decodable output)")
        print()


# ─────────────────────────────────────────────────────────────────────────────
# EVAL  — held-out accuracy + frequency baseline
# ─────────────────────────────────────────────────────────────────────────────

def cmd_eval(
    model_path: Path = DEFAULT_MODEL_PATH,
    verbose: bool = True,
) -> None:
    """Report held-out accuracy and frequency baseline (canonical: eval_held_out)."""
    _print_banner()
    print("  MODE: EVAL  (held-out validation + frequency baseline)")
    print(f"  Model: {model_path}")
    print()

    repo_root = _find_repo_root()
    splits = _load_corpus_jsonl_splits(repo_root)
    if splits is not None:
        train_docs, val_docs, _test_docs, _manifest = splits
    else:
        train_docs = _load_corpus_from_config(repo_root)
        val_docs = _load_val_corpus(repo_root)

    if not train_docs:
        print("[ERROR] No training corpus. Set santek_base_model.corpus_jsonl or .training_corpus_file / .training_corpus_url.", file=sys.stderr)
        sys.exit(1)
    if not val_docs:
        print("[ERROR] No validation corpus. Set santek_base_model.corpus_jsonl (deterministic split) or .training_corpus_file_val.", file=sys.stderr)
        sys.exit(1)

    eval_params = inspect.signature(eval_held_out).parameters
    if "repo_root" in eval_params:
        result = eval_held_out(model_path, repo_root, train_docs, val_docs)
    else:
        result = eval_held_out(model_path, train_docs, val_docs)

    if result.error:
        print(f"  Error: {result.error}", file=sys.stderr)
        sys.exit(1)

    print("─" * 72)
    print("  HELD-OUT EVAL")
    print("─" * 72)
    print(f"  Total predictions : {result.total_predictions}")
    print(f"  Model   accuracy   : {result.model_accuracy:.4f}  ({result.model_correct} correct)")
    print(f"  Baseline accuracy : {result.baseline_accuracy:.4f}  ({result.baseline_correct} correct)")
    print()
    if result.baseline_accuracy > 0:
        delta = result.model_accuracy - result.baseline_accuracy
        print(f"  Model vs baseline : {delta:+.4f}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# INFO — show model stats
# ─────────────────────────────────────────────────────────────────────────────

def cmd_info(model_path: Path = DEFAULT_MODEL_PATH) -> None:
    _print_banner()
    try:
        model = load_santek_model(model_path)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    meta = model.meta
    print("  MODEL INFO")
    print("─" * 72)
    print(f"  Path         : {model_path}")
    print(f"  Version      : {meta.get('version', '?')}")
    print(f"  Created      : {meta.get('created_at', '?')}")
    print(f"  Author       : {meta.get('author', '?')}")
    print(f"  Family       : {meta.get('family', '?')}")
    print(f"  Corpus size  : {meta.get('corpus_size', '?')} texts")
    print(f"  Valid texts  : {meta.get('valid_texts', '?')}")
    print(f"  Epochs run   : {meta.get('epochs_run', '?')}")
    print(f"  Best accuracy: {meta.get('best_accuracy', '?')}")
    print(f"  Best tension : {meta.get('best_tension', '?')}")
    print(f"  Edge count   : {len(model.path_scores)}")
    print(f"  Vocab size   : {len(model.vocab)}")
    print()
    if model.vocab:
        sample = list(model.vocab.items())[:10]
        print("  Vocab sample (symbol → token):")
        for sym, tok in sample:
            print(f"    {sym:>6} → {tok!r}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _print_banner() -> None:
    print()
    print("=" * 72)
    print("  SanTEK Base Model  v" + VERSION)
    print("  Author : Chavala Santosh")
    print("  Family : THRESHOLD_ONSET / SanTOK / SanVerse / Sanformers")
    print("  Stdlib : zero third-party imports")
    print("=" * 72)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="SanTEK Base Model v1 — THRESHOLD_ONSET family",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  train      Learn from train corpus only, save model to JSON
  generate   Generate text from a prompt (refuses disconnected prompts)
  chat       Interactive chat loop
  eval       Held-out accuracy + frequency baseline (requires val corpus in config)
  info       Show saved model statistics

Examples:
  python santek_base_model.py train
  python santek_base_model.py train --epochs 500 --corpus "text 1" "text 2"
  python santek_base_model.py generate "Action before knowledge"
  python santek_base_model.py eval
  python santek_base_model.py chat
  python santek_base_model.py info
        """,
    )
    ap.add_argument("mode", nargs="?", default="chat",
                    choices=["train", "generate", "gen", "chat", "eval", "info"],
                    help="Mode (default: chat)")

    # Train args
    ap.add_argument("--corpus", nargs="+", default=None, metavar="TEXT",
                    help="Texts for training (default: from config santek_base_model.training_corpus_file or .training_corpus)")
    ap.add_argument("--epochs",  type=int,   default=100,  metavar="N")
    ap.add_argument("--eta",     type=float, default=0.10, metavar="E",
                    help="Learning rate (default 0.10)")
    ap.add_argument("--decay",   type=float, default=0.05, metavar="D",
                    help="Score decay per epoch (default 0.05)")
    ap.add_argument("--max-streak", type=int, default=3, dest="max_streak", metavar="S",
                    help="ASD streak cap (default 3)")
    ap.add_argument("--tension-threshold", type=float, default=0.10, dest="tt",
                    metavar="T", help="Convergence tension threshold (default 0.10)")
    ap.add_argument("--patience", type=int, default=5, metavar="P",
                    help="Plateau patience epochs (default 5)")

    # Generate args
    ap.add_argument("prompt", nargs="?", default=None,
                    help="Prompt text for generate mode")
    ap.add_argument("--length", type=int, default=20, metavar="L",
                    help="Generation length in symbols (default 20)")

    # Shared
    ap.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH, metavar="PATH",
                    help=f"Model file path (default: {DEFAULT_MODEL_PATH})")
    ap.add_argument("--quiet", action="store_true", help="Suppress verbose output")

    args = ap.parse_args()
    mode = args.mode if args.mode else "chat"
    if mode == "gen":
        mode = "generate"

    if mode == "train":
        repo_root = _find_repo_root()
        corpus = args.corpus
        split_manifest = None
        if not corpus:
            splits = _load_corpus_jsonl_splits(repo_root)
            if splits is not None:
                train_texts, _val, _test, split_manifest = splits
                corpus = train_texts
            if not corpus:
                corpus = _load_corpus_from_config(repo_root)
        if not corpus:
            print("[ERROR] No training corpus.", file=sys.stderr)
            print("  Set santek_base_model.corpus_jsonl (JSONL with id, text, lang[, domain]), or", file=sys.stderr)
            print("  santek_base_model.training_corpus_file / .training_corpus_url, or use --corpus 'doc1' 'doc2' ...", file=sys.stderr)
            print("  See data/README.md.", file=sys.stderr)
            sys.exit(1)
        cmd_train(
            corpus=corpus,
            epochs=args.epochs,
            eta=args.eta,
            decay=args.decay,
            max_streak=args.max_streak,
            tension_threshold=args.tt,
            patience=args.patience,
            model_path=args.model,
            verbose=not args.quiet,
            split_manifest=split_manifest,
        )

    elif mode == "generate":
        prompt = args.prompt
        if not prompt:
            # Interactive fallback
            try:
                prompt = input("Enter prompt: ").strip()
            except (EOFError, KeyboardInterrupt):
                prompt = ""
        if not prompt:
            prompt = _default_prompt_from_config(_find_repo_root())
        cmd_generate(
            prompt=prompt,
            length=args.length,
            model_path=args.model,
            verbose=not args.quiet,
        )

    elif mode == "chat":
        cmd_chat(model_path=args.model, length=args.length)

    elif mode == "eval":
        cmd_eval(model_path=args.model, verbose=not args.quiet)

    elif mode == "info":
        cmd_info(model_path=args.model)


if __name__ == "__main__":
    main()
