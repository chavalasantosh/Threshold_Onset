#!/usr/bin/env python3
"""
santek_sle.py  v3
─────────────────────────────────────────────────────────────────────────────
SanTEK Structural Learning Engine  (SanTEK-SLE)
Author: Chavala Santosh
Family: THRESHOLD_ONSET / SanTOK / SanVerse ecosystem

"Given this input, predict this output, measure how wrong I was, update, repeat."

─────────────────────────────────────────────────────────────────────────────
WHAT WAS WRONG (v2) AND WHAT IS FIXED (v3)
─────────────────────────────────────────────────────────────────────────────

  [v2 Bug 5] — Tension reversal after ~epoch 15 in long runs

    Root cause: ASD streak counters accumulate unboundedly across epochs.
    After ~15 epochs the streak multipliers grow so large that reinforcement
    overwhelms the decay (0.05). Scores spike → normalisation compresses
    them badly → tension rises back toward 0.50 and stays there.

    Fix — Streak Cap (max_streak):
    Cap wrong_streak at max_streak (default=3) before computing multiplier.
    Multiplier is at most 1 + max_streak = 4.
    This keeps the ASD push proportionate to decay throughout long runs.
    Still no gradients, no external formula.

  [v2 Bug 6] — Accuracy ceiling at ~39%  (cross-text conflict)

    Root cause: All 10 texts share ONE merged path_scores table.
    Text A may say "symbol 3 → symbol 7 is correct" while text B says
    "symbol 3 → symbol 5 is correct". After the easy (consensus) edges are
    learned, the remaining ~61% are genuine cross-text conflicts. Learning
    one text's prediction un-learns another's. The system is stuck in a
    limit cycle because no single table can satisfy all texts at once.

    Fix — Per-Text Path Score Tables:
    Every text gets its OWN path_scores dict and its OWN streaks dict.
    Prediction and update are text-local — no cross-text interference.
    Global accuracy = aggregate correct/total across all texts.
    Global tension  = mean of all per-step tensions across all texts.
    Each text can converge independently; the global metric improves
    monotonically as individual texts converge.

─────────────────────────────────────────────────────────────────────────────
v1/v2 fixes still active
─────────────────────────────────────────────────────────────────────────────

  Fix 1  Score Decay:      multiply all path_scores by (1 - decay) each epoch.
  Fix 2  Epoch Snapshot:   snapshot scores at epoch start; update live scores.
  Fix 3  ASD asymmetry:    wrong-edge penalised harder than correct is praised.

─────────────────────────────────────────────────────────────────────────────
USAGE
─────────────────────────────────────────────────────────────────────────────
  python santek_sle.py
  python santek_sle.py --corpus "text1" "text2"
  python santek_sle.py --epochs 500 --eta 0.1 --decay 0.05 --max-streak 3
  python santek_sle.py --quiet
─────────────────────────────────────────────────────────────────────────────
"""

import argparse
import hashlib
import importlib.util
import logging
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("santek_sle")

DEFAULT_CORPUS = [
    "Action before knowledge. Function stabilizes before meaning appears.",
    "Structure emerges before language exists.",
    "chinni gunde lo anni asala.",
    "inka yenni dhachi navoo dhanni lona.",
    "oohaa lo illa telave ala telave illa telave.",
    "Hash to residue. Residue to identity. Identity to symbol.",
    "Tokens become residues. Residues form segments. Segments earn identity.",
    "Constraint bounds generation. No self-transition allowed.",
    "Boundary detection clusters the opaque trace.",
    "Repetition earns persistence. Persistence earns identity.",
]


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE LOADER
# ─────────────────────────────────────────────────────────────────────────────
def _load_run_complete():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(repo_root, "integration", "run_complete.py")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Cannot find integration/run_complete.py at {path}\n"
            "Run from the THRESHOLD_ONSET repo root."
        )
    spec = importlib.util.spec_from_file_location("run_complete", path)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules["run_complete"] = mod
    spec.loader.exec_module(mod)
    return mod


def _run_pipeline(rc_mod, text: str):
    try:
        result = rc_mod.run(
            text_override=text,
            return_result=True,
            return_model_state=True,
        )
        if result is None or not getattr(result, "model_state", None):
            return None
        return result
    except Exception as exc:
        log.debug("Pipeline failed for %r: %s", text[:40], exc)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# SEGMENT HASH  — must match Phase 2 exactly
# ─────────────────────────────────────────────────────────────────────────────
def _segment_hash(r_a: float, r_b: float) -> str:
    return hashlib.md5(str((r_a, r_b)).encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# SYMBOL SEQUENCE
# ─────────────────────────────────────────────────────────────────────────────
def _get_symbol_sequence(model_state: dict) -> List[int]:
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
        h        = _segment_hash(float(run0[i]), float(run0[i + 1]))
        identity = identity_mappings.get(h)
        if identity is not None:
            sym = identity_to_symbol.get(identity)
            if sym is not None:
                seq.append(int(sym))
    return seq


# ─────────────────────────────────────────────────────────────────────────────
# PER-TEXT PATH SCORES  — build from pipeline output, (int,int)->float only
# ─────────────────────────────────────────────────────────────────────────────
def _build_path_scores(raw_ps: dict) -> Dict[Tuple[int, int], float]:
    ps: Dict[Tuple[int, int], float] = {}
    for edge, score in raw_ps.items():
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            continue
        if not isinstance(score, (int, float)):
            continue
        key = (int(edge[0]), int(edge[1]))
        ps[key] = max(ps.get(key, 0.0), float(score))
    return ps


# ─────────────────────────────────────────────────────────────────────────────
# SCORE DECAY  — prevents unbounded growth, preserves relative ranking
# ─────────────────────────────────────────────────────────────────────────────
def _apply_decay(ps: Dict[Tuple[int, int], float], decay: float) -> None:
    factor = 1.0 - decay
    for k in ps:
        ps[k] *= factor


# ─────────────────────────────────────────────────────────────────────────────
# NORMALISE  — for tension computation only, from snapshot
# ─────────────────────────────────────────────────────────────────────────────
def _normalise(ps: Dict[Tuple[int, int], float]) -> Dict[Tuple[int, int], float]:
    if not ps:
        return {}
    vals = list(ps.values())
    lo, hi = min(vals), max(vals)
    span = hi - lo
    if span == 0.0:
        return {k: 0.5 for k in ps}
    return {k: (v - lo) / span for k, v in ps.items()}


# ─────────────────────────────────────────────────────────────────────────────
# SANTEK TENSION  — from snapshot normalisation
# ─────────────────────────────────────────────────────────────────────────────
def _tension(current: int, actual: int, norm: Dict) -> float:
    return 1.0 - norm.get((current, actual), 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# SANTEK 9-CENTRIC ACCURACY
# ─────────────────────────────────────────────────────────────────────────────
def _digital_root(n: int) -> int:
    if n == 0:
        return 9
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n if n != 0 else 9


def _accuracy_9c(correct: int, total: int) -> Tuple[float, int]:
    if total == 0:
        return 0.0, 9
    raw = correct / total
    return raw, _digital_root(round(raw * 100))


# ─────────────────────────────────────────────────────────────────────────────
# PREDICTION  — from snapshot scores, no self-transition
# ─────────────────────────────────────────────────────────────────────────────
def _predict(current: int, snapshot: Dict[Tuple[int, int], float]) -> Optional[int]:
    best_sym, best_score = None, -1.0
    for (fr, to), score in snapshot.items():
        if fr == current and to != current and score > best_score:
            best_sym, best_score = to, score
    return best_sym


# ─────────────────────────────────────────────────────────────────────────────
# ACCUMULATED STRUCTURAL DELTA  (ASD)  — the learning rule v3
#
#   FIX (Bug 5): streak capped at max_streak before computing multiplier.
#
#   Wrong:
#     streak[(cur, pred)] = min(streak + 1, max_streak)
#     multiplier = 1 + capped_streak
#     correct_edge  += eta * tension * multiplier
#     predicted_edge -= eta * (1.0 - tension) * multiplier   (floor 0)
#
#   Correct:
#     correct_edge  += eta * (1.0 - tension)
#     streak[(cur, pred)] = 0
#
# ─────────────────────────────────────────────────────────────────────────────
def _accumulated_structural_delta(
    live_ps:    Dict[Tuple[int, int], float],
    streaks:    Dict[Tuple[int, int], int],
    current:    int,
    predicted:  Optional[int],
    actual:     int,
    tension:    float,
    eta:        float,
    max_streak: int,
) -> None:
    correct_edge = (current, actual)

    if predicted == actual:
        live_ps[correct_edge] = live_ps.get(correct_edge, 0.0) + eta * (1.0 - tension)
        if predicted is not None:
            streaks[(current, predicted)] = 0
    else:
        if predicted is not None:
            wrong_edge    = (current, predicted)
            raw_streak    = streaks.get(wrong_edge, 0) + 1
            capped_streak = min(raw_streak, max_streak)   # BUG 5 FIX
            streaks[wrong_edge] = capped_streak
            multiplier    = 1 + capped_streak
            live_ps[correct_edge] = (
                live_ps.get(correct_edge, 0.0) + eta * tension * multiplier
            )
            live_ps[wrong_edge] = max(
                0.0,
                live_ps.get(wrong_edge, 0.0) - eta * (1.0 - tension) * multiplier,
            )
        else:
            live_ps[correct_edge] = live_ps.get(correct_edge, 0.0) + eta * tension


# ─────────────────────────────────────────────────────────────────────────────
# RESULT TYPES
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class SanTEKEpochResult:
    epoch:             int
    correct:           int
    total:             int
    raw_accuracy:      float
    accuracy_9centric: int
    mean_tension:      float
    updates:           int
    elapsed_ms:        float


@dataclass
class SanTEKTrainingResult:
    converged:           bool
    converged_at_epoch:  Optional[int]
    total_epochs_run:    int
    best_accuracy:       float = 0.0
    best_9centric:       int   = 1
    epochs:              List[SanTEKEpochResult]       = field(default_factory=list)
    final_path_scores:   Dict[Tuple[int,int], float]  = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# DISPLAY
# ─────────────────────────────────────────────────────────────────────────────
def _bar(v: float, w: int = 20, full: str = "X", empty: str = ".") -> str:
    n = max(0, min(w, round(v * w)))
    return full * n + empty * (w - n)


def _print_epoch(ep: SanTEKEpochResult, total_epochs: int) -> None:
    print(
        f"  Epoch {ep.epoch:>3}/{total_epochs}  "
        f"acc={ep.raw_accuracy:.4f} [{_bar(ep.raw_accuracy)}]  "
        f"9c={ep.accuracy_9centric}  "
        f"tension={ep.mean_tension:.4f} [{_bar(1.0 - ep.mean_tension, full='#', empty='.')}]  "
        f"{ep.correct}/{ep.total}  "
        f"d={ep.updates}  {ep.elapsed_ms:.0f}ms"
    )


def _print_summary(r: SanTEKTrainingResult) -> None:
    print()
    print("=" * 72)
    print("  SanTEK-SLE  v3  TRAINING COMPLETE")
    print("=" * 72)
    print(f"  Epochs run    : {r.total_epochs_run}")
    conv = f"YES at epoch {r.converged_at_epoch}" if r.converged else "NO (limit or plateau)"
    print(f"  Converged     : {conv}")
    print(f"  Best accuracy : {r.best_accuracy:.4f}  ({r.best_accuracy * 100:.1f}%)")
    print(f"  Best 9-centric: {r.best_9centric}  (SanVerse scale 1-9)")
    print(f"  Final edges   : {len(r.final_path_scores)}")
    if r.epochs:
        first, last = r.epochs[0], r.epochs[-1]
        t_delta = last.mean_tension - first.mean_tension
        a_delta = last.raw_accuracy - first.raw_accuracy
        t_dir = "v" if t_delta < 0 else ("^" if t_delta > 0 else "=")
        a_dir = "^" if a_delta > 0 else ("v" if a_delta < 0 else "=")
        print(f"  Tension  {t_dir}    : {first.mean_tension:.4f} -> {last.mean_tension:.4f}"
              f"  (delta={t_delta:+.4f})")
        print(f"  Accuracy {a_dir}    : {first.raw_accuracy:.4f} -> {last.raw_accuracy:.4f}"
              f"  (delta={a_delta:+.4f})")
    print()
    print(f"  {'Ep':>3}  {'Accuracy':>10}  {'9c':>3}  {'Tension':>9}  "
          f"{'Right/Total':>11}  {'Updates':>7}  {'ms':>7}")
    print("  " + "-" * 62)
    for ep in r.epochs:
        mark = " <-- best" if ep.raw_accuracy == r.best_accuracy else ""
        print(f"  {ep.epoch:>3}  {ep.raw_accuracy:>10.4f}  {ep.accuracy_9centric:>3}  "
              f"{ep.mean_tension:>9.4f}  {ep.correct:>5}/{ep.total:<5}  "
              f"{ep.updates:>7}  {ep.elapsed_ms:>7.0f}{mark}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TRAINING LOOP
# ─────────────────────────────────────────────────────────────────────────────
def santek_train(
    corpus: List[str],
    epochs: int = 10,
    eta: float = 0.1,
    decay: float = 0.05,
    max_streak: int = 3,
    tension_threshold: float = 0.10,
    patience: int = 3,
    verbose: bool = True,
) -> SanTEKTrainingResult:

    if verbose:
        print()
        print("=" * 72)
        print("  SanTEK Structural Learning Engine  v3  (SanTEK-SLE)")
        print("  Family: THRESHOLD_ONSET / SanTOK / SanVerse")
        print("  Author: Chavala Santosh")
        print("  Fixes: Score Decay + Epoch Snapshot + ASD + Streak Cap + Per-Text Tables")
        print("=" * 72)
        print(f"  Corpus:{len(corpus)}  Epochs:{epochs}  Eta:{eta}  "
              f"Decay:{decay}  MaxStreak:{max_streak}  "
              f"Converge:tension<{tension_threshold}  Patience:{patience}")
        print()

    log.info("Loading pipeline...")
    try:
        rc = _load_run_complete()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # ── Initialisation ───────────────────────────────────────────────────
    if verbose:
        print("-" * 72)
        print("  INIT — building per-text structural state from corpus")
        print("-" * 72)

    # FIX Bug 6: each text gets its own path_scores and streaks
    text_path_scores: List[Dict[Tuple[int, int], float]] = []
    text_streaks:     List[Dict[Tuple[int, int], int]]   = []
    text_seqs:        List[List[int]]                    = []
    valid_indices:    List[int]                          = []

    for i, text in enumerate(corpus):
        res = _run_pipeline(rc, text)
        if res is None:
            log.warning("corpus[%d] skipped", i)
            text_path_scores.append({})
            text_streaks.append({})
            text_seqs.append([])
            continue
        ms  = res.model_state
        ps  = _build_path_scores(ms.get("path_scores", {}))
        seq = _get_symbol_sequence(ms)
        text_path_scores.append(ps)
        text_streaks.append(defaultdict(int))
        text_seqs.append(seq)
        valid_indices.append(i)
        if verbose:
            n_id = len(ms.get("phase4_metrics", {}).get("identity_to_symbol", {}))
            print(f"  [{i+1:2d}/{len(corpus)}] tokens={len(ms.get('tokens') or []):>3}  "
                  f"identities={n_id:>3}  "
                  f"edges={len(ps):>4}  "
                  f"seq_len={len(seq):>3}")

    if not valid_indices:
        print("[ERROR] No valid pipeline output.", file=sys.stderr)
        sys.exit(1)

    if verbose:
        total_edges = sum(len(text_path_scores[i]) for i in valid_indices)
        print(f"\n  Per-text tables: {len(valid_indices)}/{len(corpus)} texts  "
              f"total edges (sum): {total_edges}\n")

    # ── Training loop ────────────────────────────────────────────────────
    first_valid = valid_indices[0]

    out = SanTEKTrainingResult(
        converged=False, converged_at_epoch=None,
        total_epochs_run=0,
        final_path_scores=text_path_scores[first_valid],
    )
    prev_tension  = float("inf")
    plateau_count = 0

    for epoch in range(1, epochs + 1):
        t0 = time.time()

        correct = total = updates = 0
        all_tensions = []

        for i in valid_indices:
            ps  = text_path_scores[i]
            stk = text_streaks[i]
            seq = text_seqs[i]

            # Decay and snapshot per-text
            _apply_decay(ps, decay)
            snapshot = dict(ps)
            norm     = _normalise(snapshot)

            for step in range(len(seq) - 1):
                cur, actual = seq[step], seq[step + 1]
                if cur == actual:
                    continue

                pred  = _predict(cur, snapshot)
                t_val = _tension(cur, actual, norm)
                all_tensions.append(t_val)

                if pred == actual:
                    correct += 1
                total += 1

                _accumulated_structural_delta(
                    ps, stk, cur, pred, actual, t_val, eta, max_streak
                )
                updates += 1

        elapsed = (time.time() - t0) * 1000
        mean_t  = sum(all_tensions) / len(all_tensions) if all_tensions else 1.0
        raw_acc, acc9 = _accuracy_9c(correct, total)

        ep = SanTEKEpochResult(
            epoch=epoch, correct=correct, total=total,
            raw_accuracy=raw_acc, accuracy_9centric=acc9,
            mean_tension=mean_t, updates=updates, elapsed_ms=elapsed,
        )
        out.epochs.append(ep)
        out.total_epochs_run = epoch
        if raw_acc > out.best_accuracy:
            out.best_accuracy = raw_acc
            out.best_9centric = acc9

        if verbose:
            _print_epoch(ep, epochs)

        if total == 0:
            continue

        # Convergence
        if mean_t < tension_threshold:
            out.converged = True
            out.converged_at_epoch = epoch
            if verbose:
                print(f"\n  CONVERGED  epoch={epoch}  mean_tension={mean_t:.4f} < {tension_threshold}")
            break

        # Plateau
        plateau_count = plateau_count + 1 if abs(mean_t - prev_tension) < 1e-6 else 0
        prev_tension  = mean_t
        if plateau_count >= patience:
            if verbose:
                print(f"\n  PLATEAU  {patience} epochs unchanged  stopping at epoch {epoch}")
            break

    out.final_path_scores = text_path_scores[first_valid]
    if verbose:
        _print_summary(out)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# CLI — interactive when no corpus: ask to use default or enter text
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="SanTEK-SLE v3")
    ap.add_argument("--corpus", nargs="+", default=None, metavar="TEXT",
                    help="Input texts (omit to use default or be prompted)")
    ap.add_argument("--epochs", type=int, default=10, metavar="N")
    ap.add_argument("--eta", type=float, default=0.1, metavar="E")
    ap.add_argument("--decay", type=float, default=0.05, metavar="D",
                    help="Score decay per epoch (default 0.05).")
    ap.add_argument("--max-streak", type=int, default=3, metavar="S",
                    dest="max_streak",
                    help="Max ASD streak before cap (default 3). Prevents tension reversal.")
    ap.add_argument("--tension-threshold", type=float, default=0.10, dest="tt", metavar="T")
    ap.add_argument("--patience", type=int, default=3, metavar="P")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--default", action="store_true", help="Use built-in corpus (no prompt)")
    args = ap.parse_args()

    corpus = args.corpus
    if not corpus and not args.default:
        try:
            from integration.interactive_prompt import prompt_yes_no, prompt_text, is_interactive
            if is_interactive():
                if prompt_yes_no("Use default corpus (10 sample texts)?", default=True):
                    corpus = DEFAULT_CORPUS
                else:
                    print("Enter your text(s). One line per text. Press Enter twice when done.")
                    raw = prompt_text(prompt_line="> ", continuation="... ")
                    if raw and raw.strip():
                        corpus = [line.strip() for line in raw.splitlines() if line.strip()]
        except ImportError:
            pass
    if not corpus:
        corpus = DEFAULT_CORPUS

    santek_train(
        corpus=corpus,
        epochs=args.epochs,
        eta=args.eta,
        decay=args.decay,
        max_streak=args.max_streak,
        tension_threshold=args.tt,
        patience=args.patience,
        verbose=not args.quiet,
    )
    sys.exit(0)
