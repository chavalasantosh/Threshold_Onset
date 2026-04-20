#!/usr/bin/env python3
"""
Corpus Scale Test — v3.0  (PURE STDLIB — ZERO THIRD-PARTY)
────────────────────────────────────────────────────────────
Every line of logic in this file was written from scratch.
No numpy. No rich. No matplotlib. No external dependency of any kind.
Python standard library only: json, math, os, sys, time, logging,
concurrent.futures, dataclasses, pathlib, statistics, collections,
datetime, argparse, subprocess, traceback.

Features (all stdlib):
  • Parallel workers via integration.runtime.run_tasks (process backend)
  • Live terminal dashboard — ANSI colours + box-drawing chars (no rich)
  • Deep statistical analysis: linear regression, saturation detection,
    percentile histograms, Pearson correlation, growth-rate acceleration
  • Structured JSON report
  • ASCII charts rendered directly in terminal (no matplotlib)
  • Robust error handling: retries, timeouts, partial-failure recovery
  • Resumable runs via checkpoint state
  • Dataclass-based typed metrics throughout
  • Corpus deduplication + quality scoring
  • Full logging to file alongside terminal output
"""

from __future__ import annotations

import argparse
import collections
import datetime
import json
import logging
import math
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from integration.runtime import ExecutionConfig, JobSpec, RETRY_FAST, choose_workers, run_tasks
from integration.runtime.cli import build_runtime_env

# ── project root ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH        = OUTPUT_DIR / "corpus_scale_test.log"
CHECKPOINT_PATH = OUTPUT_DIR / "corpus_scale_checkpoint.json"
REPORT_PATH     = OUTPUT_DIR / "corpus_scale_report.json"
STATE_PATH      = OUTPUT_DIR / "corpus_state.json"

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8")],
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# ANSI Terminal  (pure stdlib — no rich)
# ─────────────────────────────────────────────────────────────────────────────

class C:
    """ANSI colour codes."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"

    @staticmethod
    def _is_tty() -> bool:
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    @classmethod
    def c(cls, code: str, text: str) -> str:
        if cls._is_tty():
            return f"{code}{text}{cls.RESET}"
        return text

    @classmethod
    def red(cls, t: str)     -> str: return cls.c(cls.RED, t)
    @classmethod
    def green(cls, t: str)   -> str: return cls.c(cls.GREEN, t)
    @classmethod
    def yellow(cls, t: str)  -> str: return cls.c(cls.YELLOW, t)
    @classmethod
    def cyan(cls, t: str)    -> str: return cls.c(cls.CYAN, t)
    @classmethod
    def magenta(cls, t: str) -> str: return cls.c(cls.MAGENTA, t)
    @classmethod
    def bold(cls, t: str)    -> str: return cls.c(cls.BOLD, t)
    @classmethod
    def dim(cls, t: str)     -> str: return cls.c(cls.DIM, t)


def _box_line(width: int = 70) -> str:
    return "─" * width

def _box_top(width: int = 70) -> str:
    return "┌" + "─" * (width - 2) + "┐"

def _box_bot(width: int = 70) -> str:
    return "└" + "─" * (width - 2) + "┘"

def _box_mid(width: int = 70) -> str:
    return "├" + "─" * (width - 2) + "┤"

def _box_row(left: str, right: str, width: int = 70) -> str:
    inner = width - 4
    left_w = inner * 2 // 3
    right_w = inner - left_w
    return "│ " + left[:left_w].ljust(left_w) + " " + right[:right_w].rjust(right_w) + " │"


def _progress_bar(done: int, total: int, width: int = 30) -> str:
    if total == 0:
        frac = 0.0
    else:
        frac = min(1.0, done / total)
    filled = int(width * frac)
    bar = "█" * filled + "░" * (width - filled)
    pct = f"{frac * 100:.1f}%"
    return f"[{bar}] {pct}"


def _sparkline(values: List[float], width: int = 30) -> str:
    """Render a sparkline using unicode block chars — pure stdlib."""
    blocks = " ▁▂▃▄▅▆▇█"
    if not values or len(values) < 2:
        return " " * width
    mn, mx = min(values), max(values)
    span = mx - mn if mx != mn else 1.0
    # sample evenly to fit width
    step = max(1, len(values) // width)
    sampled = [values[i] for i in range(0, len(values), step)][:width]
    return "".join(blocks[int((v - mn) / span * 8)] for v in sampled)


def _ascii_chart(
    xs: List[float], ys: List[float],
    title: str = "", width: int = 60, height: int = 10,
    colour: str = C.CYAN,
) -> str:
    """Render a small ASCII line chart. Pure stdlib."""
    lines: List[str] = []
    if not xs or not ys or len(xs) < 2:
        return f"  {title}: (no data)"

    mn_y, mx_y = min(ys), max(ys)
    span_y = mx_y - mn_y if mx_y != mn_y else 1.0

    # sample xs/ys to fit chart width
    step = max(1, len(xs) // width)
    sampled_y = [ys[i] for i in range(0, len(ys), step)][:width]

    # build grid
    grid = [[" "] * len(sampled_y) for _ in range(height)]
    for col, val in enumerate(sampled_y):
        row = height - 1 - int((val - mn_y) / span_y * (height - 1))
        row = max(0, min(height - 1, row))
        grid[row][col] = "•"

    if title:
        lines.append(C.c(C.BOLD, f"  {title}"))
    y_label_w = 8
    for r, row in enumerate(grid):
        # y-axis label on leftmost and middle rows
        if r == 0:
            lbl = f"{mx_y:>7.1f} "
        elif r == height // 2:
            lbl = f"{(mn_y + mx_y) / 2:>7.1f} "
        elif r == height - 1:
            lbl = f"{mn_y:>7.1f} "
        else:
            lbl = " " * y_label_w
        line_str = "".join(row)
        if C._is_tty():
            line_str = line_str.replace("•", f"{colour}•{C.RESET}")
        lines.append(lbl + "│" + line_str)

    # x-axis
    x_axis = " " * y_label_w + "└" + "─" * len(sampled_y)
    lines.append(x_axis)
    x_min_lbl = f"{xs[0]:.0f}"
    x_max_lbl = f"{xs[-1]:.0f}"
    x_lbls = (" " * (y_label_w + 1) + x_min_lbl
              + " " * (len(sampled_y) - len(x_min_lbl) - len(x_max_lbl))
              + x_max_lbl)
    lines.append(x_lbls)
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Data Structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DocResult:
    doc_index:    int
    text_preview: str
    success:      bool
    duration_ms:  float
    retries:      int = 0
    error:        Optional[str] = None
    n_identities: int = 0
    n_edges:      int = 0
    n_core:       int = 0


@dataclass
class CorpusSnapshot:
    doc_index:    int
    n_identities: int
    n_edges:      int
    n_core:       int
    timestamp:    float = field(default_factory=time.time)


@dataclass
class GrowthStats:
    slope:            float
    intercept:        float
    r_squared:        float
    acceleration:     float
    saturation_index: float


@dataclass
class StabilityHistogram:
    below_half:  int   = 0
    half_to_one: int   = 0
    one_to_two:  int   = 0
    two_to_five: int   = 0
    five_plus:   int   = 0
    p25:         float = 0.0
    p50:         float = 0.0
    p75:         float = 0.0
    p95:         float = 0.0
    mean:        float = 0.0
    std:         float = 0.0

    def classify(self, s: float) -> None:
        if s < 0.5:             self.below_half  += 1
        elif s < 1.0:           self.half_to_one += 1
        elif s < 2.0:           self.one_to_two  += 1
        elif s < 5.0:           self.two_to_five += 1
        else:                   self.five_plus   += 1

    def compute_percentiles(self, values: List[float]) -> None:
        if not values:
            return
        sv = sorted(values)
        n = len(sv)
        self.mean = sum(sv) / n
        self.std  = math.sqrt(sum((x - self.mean) ** 2 for x in sv) / n)
        self.p25  = sv[max(0, int(n * 0.25) - 1)]
        self.p50  = sv[max(0, int(n * 0.50) - 1)]
        self.p75  = sv[max(0, int(n * 0.75) - 1)]
        self.p95  = sv[max(0, int(n * 0.95) - 1)]


@dataclass
class FinalReport:
    run_timestamp:       str
    n_docs_requested:    int
    n_docs_processed:    int
    n_docs_failed:       int
    total_duration_s:    float
    docs_per_second:     float
    worker_count:        int
    final_identities:    int
    final_edges:         int
    final_core:          int
    stability:           StabilityHistogram
    growth_identities:   GrowthStats
    growth_edges:        GrowthStats
    growth_core:         GrowthStats
    snapshots:           List[CorpusSnapshot]
    doc_results:         List[DocResult]
    corpus_quality_score: float
    config:              Dict[str, Any]


# ─────────────────────────────────────────────────────────────────────────────
# Statistics  (pure stdlib — no numpy, no scipy)
# ─────────────────────────────────────────────────────────────────────────────

def _linear_regression(xs: List[float], ys: List[float]) -> Tuple[float, float, float]:
    """Return (slope, intercept, r_squared). Written from scratch."""
    n = len(xs)
    if n < 2:
        return 0.0, 0.0, 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    ss_xx = sum((x - mx) ** 2 for x in xs)
    ss_yy = sum((y - my) ** 2 for y in ys)
    ss_xy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if ss_xx == 0:
        return 0.0, my, 0.0
    slope     = ss_xy / ss_xx
    intercept = my - slope * mx
    r_sq      = (ss_xy ** 2) / (ss_xx * ss_yy) if ss_yy > 0 else 0.0
    return slope, intercept, r_sq


def _percentile(sorted_values: List[float], p: float) -> float:
    """p in [0, 1]. Written from scratch."""
    if not sorted_values:
        return 0.0
    idx = max(0, int(len(sorted_values) * p) - 1)
    return sorted_values[idx]


def _std(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = sum(values) / len(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / len(values))


def compute_growth_stats(doc_indices: List[int], values: List[int]) -> GrowthStats:
    if len(doc_indices) < 4:
        return GrowthStats(0.0, 0.0, 0.0, 0.0, 0.0)
    xs = [float(d) for d in doc_indices]
    ys = [float(v) for v in values]
    slope, intercept, r_sq = _linear_regression(xs, ys)
    mid = len(xs) // 2
    slope_early, _, _ = _linear_regression(xs[:mid], ys[:mid])
    slope_late,  _, _ = _linear_regression(xs[mid:], ys[mid:])
    acceleration = slope_late - slope_early
    max_val = max(ys) if max(ys) > 0 else 1.0
    saturation_index = max(0.0, min(1.0, 1.0 - (slope * len(xs)) / max_val))
    return GrowthStats(
        slope=slope, intercept=intercept, r_squared=r_sq,
        acceleration=acceleration, saturation_index=saturation_index,
    )


def compute_stability_histogram(state_path: Path) -> Tuple[StabilityHistogram, List[float]]:
    hist = StabilityHistogram()
    if not state_path.exists():
        return hist, []
    try:
        with open(state_path, encoding="utf-8") as f:
            data = json.load(f)
        stabilities = list(data.get("identity_stability", {}).values())
        for s in stabilities:
            hist.classify(s)
        hist.compute_percentiles(stabilities)
        return hist, stabilities
    except Exception:
        return hist, []


def score_corpus_quality(texts: List[str]) -> float:
    if not texts:
        return 0.0
    unique_ratio = len({t.strip().lower() for t in texts}) / len(texts)
    lengths      = [len(t.split()) for t in texts]
    mean_len     = sum(lengths) / len(lengths)
    if mean_len == 0:
        len_diversity = 0.0
    else:
        sd = _std([float(l) for l in lengths])
        len_diversity = min(1.0, sd / mean_len)
    return (unique_ratio + len_diversity) / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# Corpus Construction
# ─────────────────────────────────────────────────────────────────────────────

_BUILTIN_CORPUS: List[str] = [
    "Action before knowledge. Structure emerges before language.",
    "Function stabilizes before meaning appears.",
    "The moon rises over silent mountains.",
    "Stars twinkle in the dark sky above.",
    "One two three four five six seven eight nine ten.",
    "The quick brown fox jumps over the lazy dog.",
    "Code compiles before execution. Syntax checks before runtime.",
    "Structure emerges from action and repetition.",
    "Knowledge follows action in every learning system.",
    "Tokens become residues. Residues form segments.",
    "Hash to residue. Segment to identity. Co-occur to relation.",
    "Left right. Up down. In out. Always pairs.",
    "Before after. Start end. Begin finish. Opposites bind.",
    "Structure emerges naturally from constraint.",
    "Memory encodes frequency before meaning.",
    "Semantics is compressed statistics.",
    "Language models compress world-models into weights.",
    "Attention is sparse retrieval over learned keys.",
    "Gradient descent is compressed trial and error.",
    "Entropy falls as patterns crystallize.",
    "A map is not the territory it represents.",
    "The medium shapes the message it carries.",
    "Abstraction sacrifices detail for generality.",
    "Compression finds redundancy and removes it.",
    "Prediction error drives representational learning.",
    "Sparse codes are efficient codes in neural systems.",
    "Topology precedes geometry in development.",
    "Phase transitions mark the emergence of order.",
    "Criticality maximizes information transmission.",
    "Edge-of-chaos dynamics enable adaptable computation.",
    "Self-organized criticality appears in neural avalanches.",
    "Binding requires synchronized oscillations across areas.",
    "Working memory is sustained attractor dynamics.",
    "Episodic memory indexes semantic memory graphs.",
    "Consolidation transfers hippocampal traces to cortex.",
    "Cortical columns implement hierarchical predictions.",
    "Prediction error propagates from low to high layers.",
    "High-level priors suppress low-level prediction errors.",
    "Recurrent connections implement temporal context.",
    "Feedforward sweeps precede recurrent refinement.",
    "Local plasticity rules implement credit assignment.",
    "Neuromodulators gate plasticity and signal novelty.",
    "Dopamine encodes reward-prediction errors precisely.",
    "Serotonin modulates time horizons in planning.",
    "Norepinephrine signals uncertainty and boosts exploration.",
    "Acetylcholine amplifies bottom-up sensory signals.",
    "Sleep replay consolidates and prunes daily learning.",
    "Dreams may simulate adversarial environments for robustness.",
    "Forgetting is adaptive when statistics change over time.",
    "Catastrophic forgetting reflects weight sharing conflicts.",
    "Continual learning requires dynamic architectural support.",
    "Modularity reduces interference between stored memories.",
    "Sparse activation prevents representational overlap.",
    "Inhibitory interneurons sculpt excitatory activity.",
    "Lateral inhibition sharpens representational contrast.",
    "Competition between representations implements selection.",
    "Winner-take-all circuits implement categorical decisions.",
    "Soft attention weights blend multiple representations.",
    "Hard attention selects discrete representational tokens.",
    "Key-value memory enables rapid associative lookup.",
    "Graph neural networks propagate relational structure.",
    "Transformers implement differentiable database retrieval.",
    "Residual connections enable very deep gradient flow.",
    "Layer normalization stabilizes activation statistics.",
    "Dropout regularizes by simulating ensemble averaging.",
    "Weight decay penalizes complexity in learned models.",
    "Early stopping prevents overfitting to training noise.",
    "Cross-validation estimates generalization from held-out data.",
    "Hyperparameter tuning is outer-loop optimization.",
    "Meta-learning learns the learning algorithm itself.",
    "Few-shot learning leverages rich prior representations.",
    "Transfer learning reuses low-level feature detectors.",
    "Fine-tuning adapts frozen representations to new domains.",
    "Tokenization determines the granularity of sequence modeling.",
    "Byte-pair encoding balances vocabulary size and coverage.",
    "Subword tokenization handles morphologically rich languages.",
    "Quantization reduces numerical precision to save memory.",
    "Pruning removes low-magnitude weights to sparsify networks.",
    "Distillation transfers soft targets from teacher to student.",
    "Instruction tuning aligns models to follow natural language directives.",
    "Direct preference optimization avoids explicit reward modeling.",
    "Monte Carlo tree search plans via simulated rollouts.",
    "World models enable planning in latent state space.",
    "Model-based RL uses transition models to improve sample efficiency.",
    "Offline RL learns from fixed datasets without environment interaction.",
    "Goal-conditioned policies generalize across task objectives.",
    "Intrinsic motivation rewards novel or surprising states.",
    "Curiosity-driven exploration follows prediction-error signals.",
    "Information gain guides Bayesian active learning experiments.",
    "Causal inference separates correlation from causal structure.",
    "Counterfactual reasoning asks what would have happened otherwise.",
    "Structural causal models encode causal graphs with mechanisms.",
    "Fair machine learning constrains models to equitable outcomes.",
    "Auditing detects bias by testing model behavior across subgroups.",
    "Red-teaming probes models for harmful or unsafe outputs.",
    "Adversarial examples reveal brittleness of learned classifiers.",
    "Perturbation analysis measures input sensitivity of predictions.",
    "Interpretability reveals internal circuits of neural networks.",
    "Mechanistic interpretability traces computations causally.",
    "Probing classifiers test linear decodability of features.",
    "Sparse autoencoders extract interpretable feature bases.",
    "Grokking reveals delayed generalization after memorization.",
    "Double descent shows test error rise then fall with capacity.",
    "Scaling laws predict loss from compute, data, and parameters.",
    "Emergent capabilities appear discontinuously at scale.",
    "Loss landscape geometry determines optimization difficulty.",
    "chinni gunde lo anni asala.",
    "inka yenni dhachi navoo dhanni lona.",
    "oohaa lo illa telave ala telave illa telave.",
    "Hash to residue. Residue to identity. Identity to symbol.",
    "Constraint bounds generation. No self-transition allowed.",
    "Boundary detection clusters the opaque trace.",
    "Repetition earns persistence. Persistence earns identity.",
]


def load_corpus_from_file(path: Path) -> List[str]:
    """Load list of document texts from a JSON or JSONL corpus file."""
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Corpus file not found: {path}")
    texts: List[str] = []
    if path.suffix.lower() == ".jsonl":
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, str):
                    texts.append(obj)
                elif isinstance(obj, dict) and "text" in obj:
                    texts.append(str(obj["text"]).strip())
                elif isinstance(obj, dict):
                    # fallback: first string value or repr
                    for v in obj.values():
                        if isinstance(v, str) and v.strip():
                            texts.append(v.strip())
                            break
        log.info("Loaded %d docs from JSONL: %s", len(texts), path)
        return texts
    # .json
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                texts.append(item.strip())
            elif isinstance(item, dict) and "text" in item:
                texts.append(str(item["text"]).strip())
            elif isinstance(item, dict):
                for v in item.values():
                    if isinstance(v, str) and v.strip():
                        texts.append(v.strip())
                        break
    elif isinstance(data, dict):
        raw = data.get("texts") or data.get("documents") or data.get("corpus")
        if raw is None:
            raise ValueError(
                f"JSON object must have 'texts', 'documents', or 'corpus' key; got {list(data.keys())[:8]}"
            )
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, str):
                    texts.append(item.strip())
                elif isinstance(item, dict) and "text" in item:
                    texts.append(str(item["text"]).strip())
                else:
                    s = str(item).strip()
                    if s:
                        texts.append(s)
        else:
            raise ValueError(f"Expected list under key; got {type(raw).__name__}")
    else:
        raise ValueError(f"Corpus JSON must be list or object; got {type(data).__name__}")
    texts = [t for t in texts if t]
    log.info("Loaded %d docs from JSON: %s", len(texts), path)
    return texts


def build_corpus(n_docs: int = 200) -> List[str]:
    texts: List[str] = []

    for module_path, attr in [
        ("integration.benchmark",          "BENCHMARK_CORPUS"),
        ("benchmark",                      "BENCHMARK_CORPUS"),
        ("integration.external_validation","EXTERNAL_CORPUS"),
        ("external_validation",            "EXTERNAL_CORPUS"),
    ]:
        try:
            mod    = __import__(module_path, fromlist=[attr])
            corpus = getattr(mod, attr)
            batch  = [text for _name, text in corpus] if isinstance(corpus[0], (list, tuple)) else corpus
            texts.extend(batch)
            log.info("Loaded %d docs from %s", len(batch), module_path)
        except Exception:
            pass

    texts.extend(_BUILTIN_CORPUS)

    # Deduplicate preserving order
    seen: set = set()
    unique: List[str] = []
    for t in texts:
        key = t.strip().lower()
        if key not in seen and t.strip():
            seen.add(key)
            unique.append(t)

    log.info("Unique after dedup: %d", len(unique))

    if len(unique) >= n_docs:
        return unique[:n_docs]

    # Expand via prefix/suffix variation — no external logic
    prefixes = [
        "Notably, ", "In contrast, ", "Furthermore, ", "Critically, ",
        "Importantly, ", "By extension, ", "In practice, ",
        "At a deeper level, ", "Empirically, ", "Theoretically, ",
    ]
    suffixes = [
        " This remains an open question.", " Evidence suggests otherwise.",
        " The data support this view.",    " Further study is warranted.",
        " This has practical implications.", " The theory predicts this outcome.",
        " Recent work challenges this.",   " This is widely accepted.",
    ]
    i = 0
    while len(unique) < n_docs:
        base      = unique[i % len(unique)]
        pfx       = prefixes[i % len(prefixes)]
        sfx       = suffixes[i % len(suffixes)]
        candidate = pfx + base[0].lower() + base[1:].rstrip(".") + sfx
        key       = candidate.strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
        i += 1
        if i > n_docs * 20:
            break

    q = score_corpus_quality(unique[:n_docs])
    log.info("Final corpus: %d docs, quality=%.3f", min(len(unique), n_docs), q)
    return unique[:n_docs]


# ─────────────────────────────────────────────────────────────────────────────
# Document Processing  (worker)
# ─────────────────────────────────────────────────────────────────────────────

def _process_doc_worker(args: Tuple[int, str, Path, int, float]) -> DocResult:
    doc_index, text, root, max_retries, doc_timeout = args
    preview   = text[:60].replace("\n", " ")
    last_error: Optional[str] = None

    for attempt in range(max_retries + 1):
        t0 = time.perf_counter()
        try:
            if str(root) not in sys.path:
                sys.path.insert(0, str(root))

            # Try in-process first
            in_process_ok = False
            try:
                from integration import run_complete  # noqa
                if hasattr(run_complete, "run"):
                    run_complete.run(text)
                elif hasattr(run_complete, "main"):
                    _orig = sys.argv
                    sys.argv = [str(root / "integration" / "run_complete.py"), text]
                    try:
                        run_complete.main()
                    finally:
                        sys.argv = _orig
                else:
                    raise AttributeError
                in_process_ok = True
            except (ImportError, AttributeError):
                pass

            if not in_process_ok:
                child_env = build_runtime_env(workers=1, method_workers=1)
                r = subprocess.run(
                    [sys.executable,
                     str(root / "integration" / "run_complete.py"), text],
                    cwd=str(root), capture_output=True,
                    text=True, timeout=doc_timeout, check=False, env=child_env,
                )
                if r.returncode != 0:
                    raise RuntimeError(f"exit {r.returncode}: {r.stderr[:200]}")

            duration_ms = (time.perf_counter() - t0) * 1000
            return DocResult(doc_index=doc_index, text_preview=preview,
                             success=True, duration_ms=duration_ms, retries=attempt)

        except Exception as exc:
            last_error = str(exc)
            if attempt < max_retries:
                time.sleep(0.1 * (2 ** attempt))

    duration_ms = (time.perf_counter() - t0) * 1000  # type: ignore
    return DocResult(doc_index=doc_index, text_preview=preview,
                     success=False, duration_ms=duration_ms,
                     retries=max_retries, error=last_error)


def _read_state(state_path: Path) -> Tuple[int, int, int]:
    if not state_path.exists():
        return 0, 0, 0
    try:
        with open(state_path, encoding="utf-8") as f:
            data = json.load(f)
        return (
            len(data.get("identity_stability", {})),
            len(data.get("edge_weights", {})),
            len(data.get("core_identities", [])),
        )
    except Exception:
        return 0, 0, 0


# ─────────────────────────────────────────────────────────────────────────────
# Checkpoint
# ─────────────────────────────────────────────────────────────────────────────

def save_checkpoint(processed: List[DocResult],
                    snapshots: List[CorpusSnapshot]) -> None:
    data = {
        "processed": [asdict(r) for r in processed],
        "snapshots":  [asdict(s) for s in snapshots],
    }
    tmp = CHECKPOINT_PATH.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f)
    tmp.replace(CHECKPOINT_PATH)


def load_checkpoint() -> Tuple[List[DocResult], List[CorpusSnapshot]]:
    if not CHECKPOINT_PATH.exists():
        return [], []
    try:
        with open(CHECKPOINT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return (
            [DocResult(**r) for r in data.get("processed", [])],
            [CorpusSnapshot(**s) for s in data.get("snapshots", [])],
        )
    except Exception:
        return [], []


# ─────────────────────────────────────────────────────────────────────────────
# Terminal Dashboard  (pure stdlib — no rich)
# ─────────────────────────────────────────────────────────────────────────────

def _clear_lines(n: int) -> None:
    if sys.stdout.isatty():
        for _ in range(n):
            sys.stdout.write("\033[F\033[2K")
        sys.stdout.flush()


_DASHBOARD_LINES = 0  # track how many lines to clear on refresh


def print_dashboard(
    n_done: int, n_fail: int, n_total: int,
    n_id: int, n_edge: int, n_core: int,
    elapsed: float,
    recent: List[DocResult],
    id_spark: List[float],
    refresh: bool = True,
) -> None:
    global _DASHBOARD_LINES
    W = 72
    lines: List[str] = []

    dps = n_done / elapsed if elapsed > 0 else 0.0
    bar = _progress_bar(n_done, n_total, width=35)
    spark = _sparkline(id_spark, width=30) if id_spark else ""

    lines.append(C.bold("┌" + "─" * (W - 2) + "┐"))
    lines.append(C.bold("│") + C.cyan(
        f"  ◈  CORPUS SCALE TEST v3.0  ◈  "
        f"Workers active  │  Target: {n_total} docs  "
    ).ljust(W - 2) + C.bold("│"))
    lines.append(C.bold("├" + "─" * (W - 2) + "┤"))

    lines.append(
        C.bold("│") +
        f"  Progress : {bar}  {n_done}/{n_total}".ljust(W - 2) +
        C.bold("│")
    )
    lines.append(
        C.bold("│") +
        f"  Elapsed  : {elapsed:>7.1f}s   "
        f"Throughput: {C.green(f'{dps:.2f} doc/s')}   "
        f"Failed: {C.red(str(n_fail)) if n_fail else '0'}".ljust(W - 2) +
        C.bold("│")
    )
    lines.append(C.bold("├" + "─" * (W - 2) + "┤"))
    lines.append(
        C.bold("│") +
        f"  {C.cyan('Identities')}: {n_id:<8}  "
        f"{C.green('Edges')}: {n_edge:<8}  "
        f"{C.magenta('Core')}: {n_core:<6}".ljust(W - 2) +
        C.bold("│")
    )
    if spark:
        lines.append(
            C.bold("│") +
            f"  Id growth : {C.cyan(spark)}".ljust(W - 2) +
            C.bold("│")
        )
    lines.append(C.bold("├" + "─" * (W - 2) + "┤"))
    lines.append(
        C.bold("│") +
        C.bold(f"  {'#':<5} {'St':^4} {'ms':>6}  {'Preview':<48}").ljust(W - 2) +
        C.bold("│")
    )
    for r in list(reversed(recent))[:5]:
        st  = C.green("✓") if r.success else C.red("✗")
        row = f"  {r.doc_index:<5} {st:^4} {r.duration_ms:>6.0f}  {r.text_preview[:46]:<46}"
        lines.append(C.bold("│") + row.ljust(W - 2) + C.bold("│"))
    lines.append(C.bold("└" + "─" * (W - 2) + "┘"))

    if refresh and _DASHBOARD_LINES > 0 and sys.stdout.isatty():
        _clear_lines(_DASHBOARD_LINES)

    for l in lines:
        print(l)
    sys.stdout.flush()
    _DASHBOARD_LINES = len(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Final Summary  (pure stdlib — no rich)
# ─────────────────────────────────────────────────────────────────────────────

def print_final_summary(
    report: FinalReport,
    hist: StabilityHistogram,
    gi: GrowthStats, ge: GrowthStats, gc: GrowthStats,
    snapshots: List[CorpusSnapshot],
) -> None:
    W = 72
    print()
    print(C.bold("╔" + "═" * (W - 2) + "╗"))
    print(C.bold("║") + C.bold(C.cyan(
        "  ═══  FINAL REPORT  ═══  Corpus Scale Test v3.0"
    )).ljust(W - 2) + C.bold("║"))
    print(C.bold("╠" + "═" * (W - 2) + "╣"))

    rows = [
        ("Documents Processed",
         f"{report.n_docs_processed} / {report.n_docs_requested}"),
        ("Documents Failed",
         C.red(str(report.n_docs_failed)) if report.n_docs_failed
         else C.green("0")),
        ("Total Duration",        f"{report.total_duration_s:.2f}s"),
        ("Throughput",            C.green(f"{report.docs_per_second:.2f} doc/s")),
        ("Workers",               str(report.worker_count)),
        ("Corpus Quality Score",  f"{report.corpus_quality_score:.3f}"),
        ("─" * 28,                "─" * 14),
        ("Final Identities",      C.cyan(str(report.final_identities))),
        ("Final Edges",           C.green(str(report.final_edges))),
        ("Final Core",            C.magenta(str(report.final_core))),
        ("─" * 28,                "─" * 14),
        ("Stability p50",         f"{hist.p50:.3f}"),
        ("Stability p95",         f"{hist.p95:.3f}"),
        ("Stability mean ± std",  f"{hist.mean:.3f} ± {hist.std:.3f}"),
        ("─" * 28,                "─" * 14),
        ("Id  slope (R²)",
         f"{gi.slope:.4f}  (R²={gi.r_squared:.3f})"),
        ("Id  saturation index",  f"{gi.saturation_index:.3f}"),
        ("Id  acceleration",      f"{gi.acceleration:+.4f}"),
        ("Edge slope (R²)",
         f"{ge.slope:.4f}  (R²={ge.r_squared:.3f})"),
        ("Core slope (R²)",
         f"{gc.slope:.4f}  (R²={gc.r_squared:.3f})"),
        ("─" * 28,                "─" * 14),
        ("JSON Report",           str(REPORT_PATH)),
        ("Log",                   str(LOG_PATH)),
    ]
    for lbl, val in rows:
        inner = f"  {lbl:<30}  {val}"
        print(C.bold("║") + inner.ljust(W - 2) + C.bold("║"))

    print(C.bold("╠" + "═" * (W - 2) + "╣"))

    # Stability bucket histogram — ASCII bar
    buckets   = ["<0.5 ", "0.5-1", "1-2  ", "2-5  ", "≥5   "]
    counts    = [hist.below_half, hist.half_to_one,
                 hist.one_to_two, hist.two_to_five, hist.five_plus]
    max_count = max(counts) if max(counts) > 0 else 1
    bar_w     = 30
    print(C.bold("║") +
          C.bold("  Stability histogram:").ljust(W - 2) + C.bold("║"))
    for b, cnt in zip(buckets, counts):
        filled = int(cnt / max_count * bar_w)
        bar    = "█" * filled + "░" * (bar_w - filled)
        row    = f"    {b}  {C.cyan(bar)}  {cnt}"
        print(C.bold("║") + row.ljust(W - 2) + C.bold("║"))

    print(C.bold("╠" + "═" * (W - 2) + "╣"))

    # ASCII growth chart
    if snapshots:
        xs  = [float(s.doc_index)    for s in snapshots]
        ids = [float(s.n_identities) for s in snapshots]
        chart = _ascii_chart(xs, ids,
                             title="Identity growth over corpus",
                             width=55, height=8,
                             colour=C.CYAN)
        for ln in chart.split("\n"):
            print(C.bold("║") + ("  " + ln).ljust(W - 2) + C.bold("║"))
        print(C.bold("╠" + "═" * (W - 2) + "╣"))

    # Interpretation
    si = gi.saturation_index
    if si > 0.8:
        msg = C.yellow(f"  ⚠  Identity graph saturated (si={si:.2f}). "
                       "Consider a larger corpus.")
    elif si < 0.3:
        msg = C.green(f"  ✓  Identity graph actively growing (si={si:.2f}).")
    else:
        msg = C.cyan(f"  →  Identity graph growing steadily (si={si:.2f}).")
    print(C.bold("║") + msg.ljust(W - 2) + C.bold("║"))

    if gi.acceleration < -0.01:
        print(C.bold("║") +
              C.cyan("  ↘  Growth decelerating — approaching saturation.").ljust(W - 2) +
              C.bold("║"))
    elif gi.acceleration > 0.01:
        print(C.bold("║") +
              C.green("  ↗  Growth accelerating — corpus revealing new structure.").ljust(W - 2) +
              C.bold("║"))

    print(C.bold("╚" + "═" * (W - 2) + "╝"))
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Main Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

def run_scale(
    n_docs:          int   = 200,
    sample_interval: int   = 10,
    n_workers:       int   = 4,
    max_retries:     int   = 2,
    doc_timeout:     float = 90.0,
    resume:          bool  = False,
    corpus:          Optional[List[str]] = None,
) -> FinalReport:

    t_start = time.time()
    if corpus is not None:
        n_docs = len(corpus)
        log.info("Using provided corpus: %d docs", n_docs)
    else:
        corpus = build_corpus(n_docs)
    quality = score_corpus_quality(corpus)
    log.info("Corpus: %d docs, quality=%.3f", len(corpus), quality)

    if resume:
        existing_results, existing_snapshots = load_checkpoint()
    else:
        existing_results, existing_snapshots = [], []
        for p in (CHECKPOINT_PATH, STATE_PATH):
            if p.exists():
                p.unlink()

    processed_indices = {r.doc_index for r in existing_results}
    all_results: List[DocResult]      = list(existing_results)
    snapshots:   List[CorpusSnapshot] = list(existing_snapshots)

    work_items = [
        (i, corpus[i - 1], ROOT, max_retries, doc_timeout)
        for i in range(1, n_docs + 1)
        if i not in processed_indices
    ]

    recent:   List[DocResult]  = []
    id_spark: List[float]      = []
    n_id = n_edge = n_core = n_fail = 0

    print(C.bold(C.cyan(
        f"\n  ◈  CORPUS SCALE TEST v3.0  "
        f"[{n_docs} docs | {n_workers} workers]  ◈\n"
    )))

    effective_workers = choose_workers(
        submitted=max(1, len(work_items)),
        backend="process",
        max_workers=n_workers,
    )

    jobs = [
        JobSpec(
            job_id=f"doc-{item[0]}",
            fn=_process_doc_worker,
            args=(item,),
            retries=max_retries,
            timeout_s=doc_timeout,
            metadata={"doc_index": item[0], "preview": item[1][:60]},
        )
        for item in work_items
    ]

    def _on_result(_m, jr):
        nonlocal n_id, n_edge, n_core, n_fail
        elapsed = time.time() - t_start
        if jr.ok and jr.value is not None:
            result = jr.value
        else:
            doc_index = int(jr.metadata.get("doc_index", -1))
            preview = str(jr.metadata.get("preview", ""))[:60]
            result = DocResult(
                doc_index=doc_index,
                text_preview=preview,
                success=False,
                duration_ms=jr.duration_ms,
                error=jr.error or "worker failed",
            )

        all_results.append(result)
        recent.append(result)
        if not result.success:
            n_fail += 1
            log.warning("Doc %d failed: %s", result.doc_index, result.error)

        n_done = len(all_results)
        if n_done % sample_interval == 0 or result.doc_index == n_docs:
            n_id, n_edge, n_core = _read_state(STATE_PATH)
            snap = CorpusSnapshot(result.doc_index, n_id, n_edge, n_core)
            snapshots.append(snap)
            result.n_identities = n_id
            result.n_edges = n_edge
            result.n_core = n_core
            id_spark.append(float(n_id))

        print_dashboard(
            n_done=n_done,
            n_fail=n_fail,
            n_total=n_docs,
            n_id=n_id,
            n_edge=n_edge,
            n_core=n_core,
            elapsed=elapsed,
            recent=recent[-8:],
            id_spark=id_spark,
            refresh=True,
        )

        if n_done % 25 == 0:
            save_checkpoint(all_results, snapshots)

    run_tasks(
        jobs,
        config=ExecutionConfig(
            backend="process",
            max_workers=effective_workers,
            queue_bound=max(effective_workers * 2, 1),
            default_timeout_s=doc_timeout,
            retry_policy=RETRY_FAST,
        ),
        progress_callback=_on_result,
    )

    total_elapsed = time.time() - t_start
    n_id, n_edge, n_core = _read_state(STATE_PATH)
    hist, stabilities     = compute_stability_histogram(STATE_PATH)
    snapshots.sort(key=lambda s: s.doc_index)

    snap_xs    = [s.doc_index for s in snapshots]
    growth_id  = compute_growth_stats(snap_xs, [s.n_identities for s in snapshots])
    growth_edge= compute_growth_stats(snap_xs, [s.n_edges       for s in snapshots])
    growth_core= compute_growth_stats(snap_xs, [s.n_core        for s in snapshots])

    report = FinalReport(
        run_timestamp        = datetime.datetime.now(datetime.timezone.utc).isoformat(),
        n_docs_requested     = n_docs,
        n_docs_processed     = len(all_results),
        n_docs_failed        = n_fail,
        total_duration_s     = total_elapsed,
        docs_per_second      = len(all_results) / total_elapsed if total_elapsed > 0 else 0,
        worker_count         = effective_workers,
        final_identities     = n_id,
        final_edges          = n_edge,
        final_core           = n_core,
        stability            = hist,
        growth_identities    = growth_id,
        growth_edges         = growth_edge,
        growth_core          = growth_core,
        snapshots            = snapshots,
        doc_results          = all_results,
        corpus_quality_score = quality,
        config               = {
            "n_docs": n_docs, "n_workers": effective_workers,
            "sample_interval": sample_interval,
            "max_retries": max_retries, "doc_timeout": doc_timeout,
        },
    )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(asdict(report), f, indent=2, default=str)
    log.info("JSON report saved to %s", REPORT_PATH)

    print_final_summary(report, hist, growth_id, growth_edge, growth_core, snapshots)
    save_checkpoint(all_results, snapshots)
    return report


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Corpus Scale Test v3.0 — pure stdlib, parallel, live dashboard"
    )
    parser.add_argument("n_docs",    nargs="?", type=int, default=200)
    parser.add_argument("--workers", "-w", type=int,
                        default=min(8, os.cpu_count() or 4))
    parser.add_argument("--interval","-i", type=int, default=0)
    parser.add_argument("--retries", "-r", type=int, default=2)
    parser.add_argument("--timeout", "-t", type=float, default=90.0)
    parser.add_argument("--resume",        action="store_true")
    parser.add_argument("--corpus",  "-c", type=Path,
                        help="Path to corpus JSON/JSONL file; run scale on this corpus instead of building one")
    args     = parser.parse_args()
    runtime_env = build_runtime_env(workers=args.workers)
    for key in ("SANTEK_TEXT_WORKERS", "STRESS_WORKERS"):
        if key in runtime_env:
            os.environ[key] = runtime_env[key]

    corpus_list: Optional[List[str]] = None
    n_docs = args.n_docs
    if args.corpus is not None:
        corpus_list = load_corpus_from_file(args.corpus)
        n_docs = len(corpus_list)
    interval = args.interval or max(1, n_docs // 20)

    log.info("Start: n=%d workers=%d interval=%d",
             n_docs, args.workers, interval)
    try:
        run_scale(
            n_docs=args.n_docs, sample_interval=interval,
            n_workers=args.workers, max_retries=args.retries,
            doc_timeout=args.timeout, resume=args.resume,
            corpus=corpus_list,
        )
    except KeyboardInterrupt:
        log.warning("Interrupted by user.")
        print(C.yellow("\n  Interrupted — checkpoint saved.\n"))
        return 130
    except Exception:
        log.exception("Unhandled exception")
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    sys.exit(main())