#!/usr/bin/env python3
"""
integration/structural_prediction_loop.py
─────────────────────────────────────────────────────────────────────────────
Structural Prediction Loop
Author: Chavala Santosh
Family: THRESHOLD_ONSET / SanTOK / SanVerse ecosystem

Principle: "Given this input, predict this output, measure how wrong I was,
            update, repeat."

─────────────────────────────────────────────────────────────────────────────
WHAT WAS WRONG (v1) AND WHAT IS FIXED (v2)
─────────────────────────────────────────────────────────────────────────────

  PROBLEM OBSERVED IN LOG:
    Epoch 1: acc=0.7143  (improved)
    Epoch 2: acc=0.8571  (improved)
    Epochs 3-10: acc=0.8571  STUCK — no change for 8 epochs

  ROOT CAUSE — Deadlock:
    The 2 remaining wrong predictions are structural deadlocks.
    Example: sequence has  ...A → C...  and  ...A → D...
    Both are valid continuations from A.
    But path_scores[(A, B)] started highest (from pipeline), so we always
    predict B. We subtract eta from (A,B) and add eta to (A,C).
    If the gap |score(A,B) - score(A,C)| > eta, one update is not enough.
    With eta=0.1 and gaps that can be 10-100x eta, it takes many epochs
    to cross the threshold.

  FIX — Accumulated Path Reinforcement (APR):
    Wrong prediction applies eta × (1 + wrong_streak) not just eta.
    wrong_streak = how many consecutive times THIS edge was predicted wrong.
    More wrong = stronger correction. Deadlocks break in 2-3 epochs.
    This is still our own rule — no gradient, no external formula.
    Correct prediction resets the streak for that edge.

─────────────────────────────────────────────────────────────────────────────
USAGE
─────────────────────────────────────────────────────────────────────────────
  python integration/structural_prediction_loop.py "Your text here"
  python integration/structural_prediction_loop.py --epochs 20 --eta 0.05 "text"
  python integration/structural_prediction_loop.py --quiet "Short text"
  python integration/structural_prediction_loop.py   # uses default text

─────────────────────────────────────────────────────────────────────────────
DEPENDENCIES: stdlib only + this project's integration/run_complete.py
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import copy
import hashlib
import importlib.util
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

DEFAULT_TEXT = "Action before knowledge. Function stabilizes before meaning appears."


# ─────────────────────────────────────────────────────────────────────────────
# SEGMENT HASH  — must match Phase 2 identity.py exactly
# ─────────────────────────────────────────────────────────────────────────────
def _segment_hash(r_a: float, r_b: float) -> str:
    return hashlib.md5(str((r_a, r_b)).encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# SYMBOL SEQUENCE
# ─────────────────────────────────────────────────────────────────────────────
def _symbol_sequence(model_state: dict) -> List[int]:
    p2 = model_state.get("phase2_metrics", {})
    p4 = model_state.get("phase4_metrics", {})
    identity_mappings  = p2.get("identity_mappings", {})
    identity_to_symbol = p4.get("identity_to_symbol", {})
    residue_sequences  = model_state.get("residue_sequences", [])

    if not identity_mappings or not identity_to_symbol or not residue_sequences:
        return []

    run0 = residue_sequences[0]
    if len(run0) < 2:
        return []

    seq = []
    for i in range(len(run0) - 1):
        h = _segment_hash(float(run0[i]), float(run0[i + 1]))
        identity = identity_mappings.get(h)
        if identity is not None:
            sym = identity_to_symbol.get(identity)
            if sym is not None:
                seq.append(int(sym))
    return seq


# ─────────────────────────────────────────────────────────────────────────────
# PATH SCORES  — copy only, (int,int)->float
# ─────────────────────────────────────────────────────────────────────────────
def _extract_path_scores(raw_ps: dict) -> Dict[Tuple[int, int], float]:
    clean: Dict[Tuple[int, int], float] = {}
    for edge, score in raw_ps.items():
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            continue
        if not isinstance(score, (int, float)):
            continue
        clean[(int(edge[0]), int(edge[1]))] = float(score)
    return clean


# ─────────────────────────────────────────────────────────────────────────────
# PREDICTION  — argmax, no self-transition
# ─────────────────────────────────────────────────────────────────────────────
def _predict_next(
    current: int,
    path_scores: Dict[Tuple[int, int], float],
) -> Optional[int]:
    best_sym, best_score = None, -1.0
    for (fr, to), score in path_scores.items():
        if fr == current and to != current and score > best_score:
            best_sym, best_score = to, score
    return best_sym


# ─────────────────────────────────────────────────────────────────────────────
# STRUCTURAL PREDICTION ERROR  (SPE)
# ─────────────────────────────────────────────────────────────────────────────
def _spe(wrong: int, total: int) -> float:
    return wrong / total if total > 0 else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# ACCUMULATED PATH REINFORCEMENT  (APR)  — the update rule v2
#
#   Correct:  scores[(current, actual_next)] += eta
#             streak[(current, predicted)]    = 0  (reset)
#
#   Wrong:    streak[(current, predicted)]   += 1
#             multiplier = 1 + streak[(current, predicted)]
#             scores[(current, predicted)]   -= eta × multiplier
#             scores[(current, actual_next)] += eta × multiplier
#
#   Floor: scores never go below 0.
#   Rationale: the more times we're wrong on the same edge, the stronger
#   the correction. Deadlocks (where one bad edge dominates) break quickly.
#   Still no gradients, no external formula — entirely our own rule.
# ─────────────────────────────────────────────────────────────────────────────
def _accumulated_path_reinforcement(
    scores: Dict[Tuple[int, int], float],
    streaks: Dict[Tuple[int, int], int],
    current: int,
    predicted: Optional[int],
    actual_next: int,
    eta: float,
) -> None:
    correct_edge = (current, actual_next)

    if predicted == actual_next:
        # Correct — reinforce the edge that happened, reset streak
        scores[correct_edge] = scores.get(correct_edge, 0.0) + eta
        if predicted is not None:
            streaks[(current, predicted)] = 0
    else:
        # Wrong — accumulate streak, scale correction by streak
        if predicted is not None:
            wrong_edge = (current, predicted)
            streaks[wrong_edge] = streaks.get(wrong_edge, 0) + 1
            multiplier = 1 + streaks[wrong_edge]
            scores[wrong_edge] = max(0.0, scores.get(wrong_edge, 0.0) - eta * multiplier)
            scores[correct_edge] = scores.get(correct_edge, 0.0) + eta * multiplier
        else:
            # No prediction possible — just reinforce correct
            scores[correct_edge] = scores.get(correct_edge, 0.0) + eta


# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────────────────────────
def run_structural_prediction_loop(
    text: str,
    epochs: int = 10,
    eta: float = 0.1,
    verbose: bool = True,
) -> None:

    if verbose:
        print()
        print("=" * 60)
        print("  Structural Prediction Loop  v2")
        print("  Family: THRESHOLD_ONSET / SanTOK / SanVerse")
        print("  Author: Chavala Santosh")
        print("  Update rule: Accumulated Path Reinforcement (APR)")
        print("=" * 60)
        print(f"  Text   : {text[:60]}{'...' if len(text) > 60 else ''}")
        print(f"  Epochs : {epochs}  |  Eta: {eta}")
        print()

    # ── Load pipeline ────────────────────────────────────────────────────
    here      = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)
    rc_path   = os.path.join(repo_root, "integration", "run_complete.py")

    if not os.path.exists(rc_path):
        print(f"[ERROR] Cannot find {rc_path}", file=sys.stderr)
        sys.exit(1)

    spec   = importlib.util.spec_from_file_location("run_complete", rc_path)
    rc_mod = importlib.util.module_from_spec(spec)
    sys.modules["run_complete"] = rc_mod
    spec.loader.exec_module(rc_mod)

    # ── Run pipeline once ────────────────────────────────────────────────
    if verbose:
        print("  [INIT] Running pipeline...")

    try:
        result = rc_mod.run(
            text_override=text,
            return_result=True,
            return_model_state=True,
        )
    except Exception as e:
        print(f"[ERROR] Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)

    if result is None or not getattr(result, "model_state", None):
        print("[ERROR] Pipeline returned no model_state.", file=sys.stderr)
        sys.exit(1)

    ms = result.model_state

    # ── Extract structural state (COPY — never mutate pipeline output) ───
    seq         = _symbol_sequence(ms)
    path_scores = _extract_path_scores(ms.get("path_scores", {}))

    # streak table: tracks consecutive wrong predictions per edge
    streaks: Dict[Tuple[int, int], int] = defaultdict(int)

    if not seq:
        print("[ERROR] Symbol sequence empty — text too short.", file=sys.stderr)
        sys.exit(1)
    if not path_scores:
        print("[ERROR] Path scores empty.", file=sys.stderr)
        sys.exit(1)

    if verbose:
        n_id = len(ms.get("phase4_metrics", {}).get("identity_to_symbol", {}))
        print(f"  [OK] tokens={len(ms.get('tokens') or [])}  "
              f"identities={n_id}  "
              f"path_edges={len(path_scores)}  "
              f"seq_len={len(seq)}")
        print()

    # ── Epoch loop ───────────────────────────────────────────────────────
    if verbose:
        print(f"  {'Epoch':>5}  {'SPE':>8}  {'Accuracy':>10}  {'Wrong/Total':>12}  {'ms':>7}")
        print("  " + "-" * 52)

    prev_spe = float("inf")
    plateau  = 0

    for epoch in range(1, epochs + 1):
        t0    = time.time()
        wrong = total = 0

        for step in range(len(seq) - 1):
            current     = seq[step]
            actual_next = seq[step + 1]

            if current == actual_next:   # no self-transition (A_ii = 0)
                continue

            predicted = _predict_next(current, path_scores)
            is_wrong  = (predicted != actual_next)
            if is_wrong:
                wrong += 1
            total += 1

            _accumulated_path_reinforcement(
                path_scores, streaks, current, predicted, actual_next, eta
            )

        spe      = _spe(wrong, total)
        accuracy = 1.0 - spe
        elapsed  = (time.time() - t0) * 1000

        if verbose:
            bar_w  = 16
            filled = round(accuracy * bar_w)
            bar    = "X" * filled + "." * (bar_w - filled)
            print(f"  {epoch:>5}  {spe:>8.4f}  {accuracy:>8.4f} [{bar}]  "
                  f"{wrong:>4}/{total:<6}  {elapsed:>7.0f}ms")

        # Plateau detection: if SPE unchanged for 3 epochs, stop
        if abs(spe - prev_spe) < 1e-9:
            plateau += 1
        else:
            plateau = 0
        prev_spe = spe

        if spe == 0.0:
            if verbose:
                print(f"\n  PERFECT  SPE=0 at epoch {epoch}  All predictions correct.")
            break

        if plateau >= 3:
            if verbose:
                print(f"\n  PLATEAU  SPE unchanged for 3 epochs."
                      f"  Remaining {wrong} wrong predictions are structurally ambiguous.")
            break

    if verbose:
        print()
        print(f"  DONE  |  Final path edges: {len(path_scores)}"
              f"  |  Final SPE: {spe:.4f}  acc: {accuracy:.4f}")
        print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI — interactive when no text given (end user can type/paste)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Structural Prediction Loop v2 — THRESHOLD_ONSET family"
    )
    ap.add_argument("text", nargs="?", default=None, help="Input text (omit to be prompted)")
    ap.add_argument("--epochs", type=int, default=10, metavar="N")
    ap.add_argument("--eta", type=float, default=0.1, metavar="E")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--default", action="store_true", help="Use built-in default text (no prompt)")
    args = ap.parse_args()

    text = args.text
    if text is None or (isinstance(text, str) and not text.strip()):
        try:
            from integration.interactive_prompt import prompt_text, is_interactive
            if not args.default and is_interactive():
                print("Enter your text (press Enter twice when done):")
                text = prompt_text(prompt_line="> ", continuation="... ")
        except ImportError:
            pass
        if not text or not str(text).strip():
            text = DEFAULT_TEXT
    text = (text or DEFAULT_TEXT).strip()

    run_structural_prediction_loop(
        text=text, epochs=args.epochs, eta=args.eta, verbose=not args.quiet
    )
    sys.exit(0)
