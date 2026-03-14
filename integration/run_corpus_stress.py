#!/usr/bin/env python3
"""
corpus_stress_test/stress_test.py
══════════════════════════════════════════════════════════════════════════════
Enterprise Corpus Stress Test  v3.0
══════════════════════════════════════════════════════════════════════════════

Production-grade successor to the original 20-doc sequential stress test.

Key improvements over v1:
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ Architecture  │ Plugin-based pipeline, dependency-injected components   │
  │ Parallelism   │ ProcessPoolExecutor with adaptive worker scaling         │
  │ Reliability   │ Circuit breaker, exponential backoff, health checks     │
  │ Observability │ Structured JSON logs, Prometheus-style metrics, traces  │
  │ Analysis      │ Regression, saturation detection, anomaly scoring       │
  │ Output        │ Rich TUI dashboard, HTML report, charts, JSON artifact  │
  │ Testing       │ Full unit test suite (pytest-compatible)                │
  │ Config        │ Typed config with env-var overrides, schema validation   │
  └─────────────────────────────────────────────────────────────────────────┘

Usage:
  python stress_test.py                         # default 20 docs
  python stress_test.py --docs 200 --workers 8
  python stress_test.py --docs 500 --resume
  python stress_test.py --docs 20 --dry-run     # validate corpus only
  python stress_test.py --help
"""

from __future__ import annotations

# ── stdlib ────────────────────────────────────────────────────────────────────
import argparse
import dataclasses
import datetime
import json
import logging
import math
import os
import signal
import sys
import threading
import time
import traceback
import uuid
from collections import deque
from concurrent.futures import (
    Future,
    ProcessPoolExecutor,
    as_completed,
)
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Callable,
    Deque,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)
from integration.runtime import choose_workers
from integration.runtime.cli import build_runtime_env

# ── optional third-party (graceful degradation) ───────────────────────────────
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        MofNCompleteColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
        TimeRemainingColumn,
    )
    from rich.table import Table
    from rich.text import Text
    from rich import box
    from rich.syntax import Syntax

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.patches import FancyArrowPatch

    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ── project root ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Configuration
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class StressTestConfig:
    """
    Fully typed, env-override-capable configuration.
    All fields read from CLI → env → default in that priority order.
    """

    # Core
    n_docs: int = 20
    worker_count: int = field(default_factory=lambda: min(8, os.cpu_count() or 4))
    sample_interval: int = 0  # 0 = auto (n_docs // 10)
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    dry_run: bool = False
    resume: bool = False

    # Pipeline
    doc_timeout_s: float = 60.0
    max_retries: int = 2
    retry_base_delay_s: float = 0.1
    pipeline_script: Path = field(
        default_factory=lambda: ROOT / "integration" / "run_complete.py"
    )
    corpus_state_path: Path = field(
        default_factory=lambda: ROOT / "output" / "corpus_state.json"
    )

    # Circuit breaker
    cb_failure_threshold: int = 5   # consecutive failures before open
    cb_recovery_timeout_s: float = 10.0

    # Output
    output_dir: Path = field(default_factory=lambda: OUTPUT_DIR)
    report_html: bool = True
    report_charts: bool = True
    report_json: bool = True
    log_level: str = "INFO"

    def effective_sample_interval(self) -> int:
        return self.sample_interval or max(1, self.n_docs // 10)

    @classmethod
    def from_env(cls) -> "StressTestConfig":
        """Override defaults from environment variables."""
        cfg = cls()
        mapping = {
            "STRESS_N_DOCS": ("n_docs", int),
            "STRESS_WORKERS": ("worker_count", int),
            "STRESS_TIMEOUT": ("doc_timeout_s", float),
            "STRESS_RETRIES": ("max_retries", int),
            "STRESS_LOG_LEVEL": ("log_level", str),
        }
        for env_key, (attr, cast) in mapping.items():
            val = os.environ.get(env_key)
            if val is not None:
                try:
                    setattr(cfg, attr, cast(val))
                except (ValueError, TypeError):
                    pass
        return cfg

    def validate(self) -> List[str]:
        """Return list of validation errors (empty = valid)."""
        errors = []
        if self.n_docs < 1:
            errors.append("n_docs must be >= 1")
        if self.worker_count < 1:
            errors.append("worker_count must be >= 1")
        if self.doc_timeout_s <= 0:
            errors.append("doc_timeout_s must be > 0")
        if self.max_retries < 0:
            errors.append("max_retries must be >= 0")
        if not self.pipeline_script.exists() and not self.dry_run:
            errors.append(
                f"pipeline_script not found: {self.pipeline_script}"
            )
        return errors

    def normalize_workers(self) -> None:
        """Normalize worker count using shared runtime policy."""
        self.worker_count = choose_workers(
            submitted=max(1, self.n_docs),
            backend="process",
            max_workers=self.worker_count,
        )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Corpus
# ══════════════════════════════════════════════════════════════════════════════

# Original 20-doc benchmark — preserved exactly for reproducibility
CANONICAL_SAMPLES: List[Tuple[str, str]] = [
    ("greeting_short",    "Hi there."),
    ("greeting_world",    "Hello world."),
    ("action_knowledge",  "Action before knowledge. Structure emerges before language."),
    ("function_meaning",  "Function stabilizes before meaning appears."),
    ("noise_articles",    "the the the a a a"),
    ("noise_repeat",      "word word word"),
    ("action_tokens",     "Action before knowledge. Structure emerges. Tokens become actions."),
    ("code_compile",      "Code compiles before execution. Syntax checks before runtime."),
    ("structure_repeat",  "Structure emerges from action and repetition."),
    ("knowledge_action",  "Knowledge follows action."),
    ("token_residue",     "Tokens become residues. Residues form segments."),
    ("hash_identity",     "Hash to residue. Segment to identity. Co-occur to relation."),
    ("moon_rise",         "The moon rises over mountains."),
    ("stars_twinkle",     "Stars twinkle in dark sky."),
    ("count_ten",         "One two three four five six seven eight nine ten."),
    ("quick_brown",       "The quick brown fox jumps over the lazy dog."),
    ("before_after",      "Before after. Start end. Begin finish."),
    ("left_right",        "Left right. Up down. In out."),
    ("noise_same",        "same same same"),
    ("structure_natural", "Structure emerges naturally."),
]

# Extended corpus for larger runs
EXTENDED_SAMPLES: List[Tuple[str, str]] = [
    ("compress_stat",     "Semantics is compressed statistics."),
    ("attn_sparse",       "Attention is sparse retrieval over learned keys."),
    ("grad_descent",      "Gradient descent is compressed trial and error."),
    ("entropy_fall",      "Entropy falls as patterns crystallize."),
    ("map_territory",     "A map is not the territory it represents."),
    ("medium_message",    "The medium shapes the message it carries."),
    ("abstract_detail",   "Abstraction sacrifices detail for generality."),
    ("compress_redund",   "Compression finds redundancy and removes it."),
    ("pred_error",        "Prediction error drives representational learning."),
    ("sparse_code",       "Sparse codes are efficient codes in neural systems."),
    ("topology_geom",     "Topology precedes geometry in development."),
    ("phase_trans",       "Phase transitions mark the emergence of order."),
    ("criticality",       "Criticality maximizes information transmission."),
    ("edge_chaos",        "Edge-of-chaos dynamics enable adaptable computation."),
    ("wm_attractor",      "Working memory is sustained attractor dynamics."),
    ("consolidation",     "Consolidation transfers hippocampal traces to cortex."),
    ("cortical_pred",     "Cortical columns implement hierarchical predictions."),
    ("recurrent_ctx",     "Recurrent connections implement temporal context."),
    ("local_plastic",     "Local plasticity rules implement credit assignment."),
    ("dopamine_rpe",      "Dopamine encodes reward-prediction errors precisely."),
    ("sleep_replay",      "Sleep replay consolidates and prunes daily learning."),
    ("forget_adapt",      "Forgetting is adaptive when statistics change over time."),
    ("modular_mem",       "Modularity reduces interference between stored memories."),
    ("inhib_intern",      "Inhibitory interneurons sculpt excitatory activity."),
    ("lateral_inhib",     "Lateral inhibition sharpens representational contrast."),
    ("soft_attn",         "Soft attention weights blend multiple representations."),
    ("kv_memory",         "Key-value memory enables rapid associative lookup."),
    ("residual_grad",     "Residual connections enable very deep gradient flow."),
    ("layer_norm",        "Layer normalization stabilizes activation statistics."),
    ("dropout_reg",       "Dropout regularizes by simulating ensemble averaging."),
    ("scaling_law",       "Scaling laws predict loss from compute, data, and parameters."),
    ("emergent_cap",      "Emergent capabilities appear discontinuously at scale."),
    ("loss_landscape",    "Loss landscape geometry determines optimization difficulty."),
    ("superposition",     "Superposition allows more features than neurons through interference."),
    ("circuit_analysis",  "Circuit analysis traces information flow through model layers."),
    ("induction_head",    "Induction heads implement in-context copying and completion."),
    ("grokking",          "Grokking reveals delayed generalization after memorization."),
    ("causal_inf",        "Causal inference separates correlation from causal structure."),
    ("counterfact",       "Counterfactual reasoning asks what would have happened otherwise."),
    ("fair_ml",           "Fair machine learning constrains models to equitable outcomes."),
]


@dataclass
class CorpusEntry:
    """A single document in the test corpus."""
    name: str
    text: str
    source: str = "builtin"
    word_count: int = field(init=False)
    char_count: int = field(init=False)
    repetition_ratio: float = field(init=False)  # 1.0 = all unique words

    def __post_init__(self) -> None:
        words = self.text.split()
        self.word_count = len(words)
        self.char_count = len(self.text)
        if words:
            self.repetition_ratio = len(set(w.lower() for w in words)) / len(words)
        else:
            self.repetition_ratio = 0.0

    @property
    def is_noise(self) -> bool:
        return self.repetition_ratio < 0.5 and self.word_count <= 6

    @property
    def complexity(self) -> str:
        if self.word_count <= 3:
            return "minimal"
        if self.word_count <= 8:
            return "short"
        if self.word_count <= 15:
            return "medium"
        return "long"


def build_corpus(n_docs: int, cfg: StressTestConfig) -> List[CorpusEntry]:
    """
    Build a deduplicated, quality-scored corpus.
    Loads canonical + extended + external project corpora.
    Expands with intelligent semantic variations to reach n_docs.
    """
    raw: List[Tuple[str, str, str]] = []  # (name, text, source)

    # 1. Canonical 20
    raw.extend((n, t, "canonical") for n, t in CANONICAL_SAMPLES)

    # 2. Extended built-in
    raw.extend((n, t, "extended") for n, t in EXTENDED_SAMPLES)

    # 3. Project benchmark (if available)
    for mod_path, attr in [
        ("integration.benchmark", "BENCHMARK_CORPUS"),
        ("benchmark", "BENCHMARK_CORPUS"),
    ]:
        try:
            import importlib
            mod = importlib.import_module(mod_path)
            corpus = getattr(mod, attr, None)
            if corpus:
                raw.extend((n, t, f"project:{mod_path}") for n, t in corpus)
                break
        except (ImportError, AttributeError):
            pass

    # 4. Project external validation
    for mod_path, attr in [
        ("integration.external_validation", "EXTERNAL_CORPUS"),
        ("external_validation", "EXTERNAL_CORPUS"),
    ]:
        try:
            import importlib
            mod = importlib.import_module(mod_path)
            corpus = getattr(mod, attr, None)
            if corpus:
                raw.extend((f"ext_{i}", t, f"project:{mod_path}") for i, t in enumerate(corpus))
                break
        except (ImportError, AttributeError):
            pass

    # Deduplicate preserving order
    seen: set = set()
    unique: List[Tuple[str, str, str]] = []
    for name, text, source in raw:
        key = text.strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append((name, text, source))

    # Expand with semantic variations if needed
    if len(unique) < n_docs:
        templates = [
            ("Notably, {0}", "variation"),
            ("In contrast, {0}", "variation"),
            ("Furthermore, {0}", "variation"),
            ("Empirically, {0}", "variation"),
            ("By extension, {0}", "variation"),
            ("{0} This has implications.", "augmented"),
            ("{0} Evidence supports this.", "augmented"),
            ("{0} The data agree.", "augmented"),
        ]
        i = 0
        while len(unique) < n_docs:
            base_name, base_text, base_src = unique[i % len(unique)]
            tmpl, kind = templates[i % len(templates)]
            adj = base_text[0].lower() + base_text[1:] if base_text else base_text
            candidate = tmpl.format(adj)
            key = candidate.strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append((f"{base_name}_{kind}_{i}", candidate, kind))
            i += 1
            if i > n_docs * 50:
                break

    entries = [
        CorpusEntry(name=n, text=t, source=s)
        for n, t, s in unique[:n_docs]
    ]
    return entries


def corpus_quality_score(entries: List[CorpusEntry]) -> Dict[str, float]:
    """Multi-dimensional corpus quality metrics."""
    if not entries:
        return {}
    n = len(entries)
    texts = [e.text.strip().lower() for e in entries]
    uniqueness = len(set(texts)) / n
    wc = [e.word_count for e in entries]
    mean_wc = sum(wc) / n
    std_wc = math.sqrt(sum((w - mean_wc) ** 2 for w in wc) / n) if n > 1 else 0
    length_diversity = min(1.0, std_wc / mean_wc) if mean_wc > 0 else 0
    noise_ratio = sum(1 for e in entries if e.is_noise) / n
    mean_rep = sum(e.repetition_ratio for e in entries) / n
    overall = (uniqueness * 0.4 + length_diversity * 0.3 +
               (1 - noise_ratio) * 0.2 + mean_rep * 0.1)
    return {
        "overall": overall,
        "uniqueness": uniqueness,
        "length_diversity": length_diversity,
        "noise_ratio": noise_ratio,
        "mean_repetition_ratio": mean_rep,
        "mean_word_count": mean_wc,
    }


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Data Structures & Enums
# ══════════════════════════════════════════════════════════════════════════════


class DocStatus(Enum):
    SUCCESS = auto()
    FAILED = auto()
    TIMEOUT = auto()
    SKIPPED = auto()


class CircuitState(Enum):
    CLOSED = auto()   # normal operation
    OPEN = auto()     # failing fast
    HALF_OPEN = auto()  # testing recovery


@dataclass
class DocResult:
    """Immutable result record for one document execution."""
    run_id: str
    doc_index: int
    doc_name: str
    text_preview: str
    status: DocStatus
    duration_ms: float
    retries: int = 0
    error: Optional[str] = None
    error_type: Optional[str] = None
    # Corpus state snapshot at time of read (may be 0 if not sampled)
    n_identities: int = 0
    n_edges: int = 0
    n_core: int = 0
    corpus_line: Optional[str] = None  # raw corpus output line
    timestamp: float = field(default_factory=time.time)
    worker_pid: Optional[int] = None

    @property
    def succeeded(self) -> bool:
        return self.status == DocStatus.SUCCESS

    @property
    def failed(self) -> bool:
        return self.status in (DocStatus.FAILED, DocStatus.TIMEOUT)


@dataclass
class CorpusSnapshot:
    """Point-in-time corpus state measurement."""
    doc_index: int
    n_identities: int
    n_edges: int
    n_core: int
    timestamp: float = field(default_factory=time.time)

    # Derived rates (filled in post-hoc)
    identity_growth_rate: float = 0.0  # per doc since last snapshot
    edge_growth_rate: float = 0.0


@dataclass
class LinearFit:
    slope: float
    intercept: float
    r_squared: float
    n_points: int


@dataclass
class GrowthAnalysis:
    """Complete statistical growth analysis for one metric."""
    metric: str
    fit_full: LinearFit
    fit_first_half: LinearFit
    fit_second_half: LinearFit
    acceleration: float          # slope_second - slope_first
    saturation_index: float      # 0 = growing, 1 = saturated
    is_saturating: bool
    plateau_at_doc: Optional[int]  # estimated plateau document


@dataclass
class AnomalyEvent:
    """Detected anomaly in processing or growth."""
    doc_index: int
    kind: str       # "slow_doc", "growth_spike", "growth_stall", "failure_burst"
    severity: float  # 0–1
    detail: str


@dataclass
class StabilityStats:
    """Distribution statistics for identity stability scores."""
    # Histogram buckets
    below_half: int = 0
    half_to_one: int = 0
    one_to_two: int = 0
    two_to_five: int = 0
    five_plus: int = 0
    # Percentiles
    p10: float = 0.0
    p25: float = 0.0
    p50: float = 0.0
    p75: float = 0.0
    p90: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    mean: float = 0.0
    std: float = 0.0
    min_val: float = 0.0
    max_val: float = 0.0
    n_total: int = 0

    @classmethod
    def from_values(cls, values: List[float]) -> "StabilityStats":
        s = cls()
        if not values:
            return s
        s.n_total = len(values)
        for v in values:
            if v < 0.5:
                s.below_half += 1
            elif v < 1.0:
                s.half_to_one += 1
            elif v < 2.0:
                s.one_to_two += 1
            elif v < 5.0:
                s.two_to_five += 1
            else:
                s.five_plus += 1
        sv = sorted(values)
        n = len(sv)
        s.mean = sum(sv) / n
        s.std = math.sqrt(sum((x - s.mean) ** 2 for x in sv) / n)
        s.min_val = sv[0]
        s.max_val = sv[-1]

        def pct(p: float) -> float:
            return sv[max(0, int(n * p) - 1)]

        s.p10 = pct(0.10)
        s.p25 = pct(0.25)
        s.p50 = pct(0.50)
        s.p75 = pct(0.75)
        s.p90 = pct(0.90)
        s.p95 = pct(0.95)
        s.p99 = pct(0.99)
        return s


@dataclass
class RunMetrics:
    """Aggregated run-level performance metrics."""
    total_docs: int
    succeeded: int
    failed: int
    timed_out: int
    total_duration_s: float
    docs_per_second: float
    mean_doc_ms: float
    p50_doc_ms: float
    p95_doc_ms: float
    p99_doc_ms: float
    max_doc_ms: float
    total_retries: int
    circuit_trips: int


@dataclass
class FinalReport:
    """Complete structured report — JSON-serializable."""
    schema_version: str = "3.0.0"
    run_id: str = ""
    run_timestamp: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    corpus_quality: Dict[str, float] = field(default_factory=dict)
    metrics: Optional[RunMetrics] = None
    stability: Optional[StabilityStats] = None
    growth_identities: Optional[GrowthAnalysis] = None
    growth_edges: Optional[GrowthAnalysis] = None
    growth_core: Optional[GrowthAnalysis] = None
    snapshots: List[CorpusSnapshot] = field(default_factory=list)
    anomalies: List[AnomalyEvent] = field(default_factory=list)
    doc_results: List[DocResult] = field(default_factory=list)
    output_files: Dict[str, str] = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Circuit Breaker
# ══════════════════════════════════════════════════════════════════════════════


class CircuitBreaker:
    """
    Standard circuit breaker pattern to halt processing on sustained failure.
    States: CLOSED → OPEN → HALF_OPEN → CLOSED
    """

    def __init__(self, failure_threshold: int, recovery_timeout_s: float) -> None:
        self._threshold = failure_threshold
        self._recovery_timeout = recovery_timeout_s
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._opened_at: Optional[float] = None
        self._trip_count = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                if time.time() - (self._opened_at or 0) >= self._recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
            return self._state

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    @property
    def trip_count(self) -> int:
        return self._trip_count

    def record_success(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            self._state = CircuitState.CLOSED

    def record_failure(self) -> bool:
        """Record failure. Returns True if circuit just tripped."""
        with self._lock:
            self._consecutive_failures += 1
            if (
                self._state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)
                and self._consecutive_failures >= self._threshold
            ):
                self._state = CircuitState.OPEN
                self._opened_at = time.time()
                self._trip_count += 1
                return True
            return False


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Statistics Engine
# ══════════════════════════════════════════════════════════════════════════════


def _linear_fit(xs: Sequence[float], ys: Sequence[float]) -> LinearFit:
    """Ordinary least-squares linear regression."""
    n = len(xs)
    if n < 2:
        return LinearFit(0.0, float(ys[0]) if ys else 0.0, 0.0, n)
    mx = sum(xs) / n
    my = sum(ys) / n
    ss_xx = sum((x - mx) ** 2 for x in xs)
    ss_yy = sum((y - my) ** 2 for y in ys)
    ss_xy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if ss_xx == 0:
        return LinearFit(0.0, my, 0.0, n)
    slope = ss_xy / ss_xx
    intercept = my - slope * mx
    r_sq = (ss_xy ** 2) / (ss_xx * ss_yy) if ss_yy > 0 else 0.0
    return LinearFit(slope=slope, intercept=intercept, r_squared=r_sq, n_points=n)


def analyze_growth(
    doc_indices: List[int],
    values: List[int],
    metric: str,
) -> GrowthAnalysis:
    """Full growth analysis with saturation and plateau detection."""
    xs = [float(d) for d in doc_indices]
    ys = [float(v) for v in values]
    n = len(xs)

    fit_full = _linear_fit(xs, ys)
    mid = max(1, n // 2)
    fit_first = _linear_fit(xs[:mid], ys[:mid])
    fit_second = _linear_fit(xs[mid:], ys[mid:]) if n - mid >= 2 else fit_full

    acceleration = fit_second.slope - fit_first.slope
    max_val = max(ys) if ys else 1.0
    # Saturation: compare actual growth rate in second half relative to first half
    first_half_range = ys[mid - 1] - ys[0] if mid > 0 else 1.0
    second_half_range = ys[-1] - ys[mid] if len(ys) > mid else 0.0
    # If second half grows much less than first half → saturating
    if first_half_range <= 0:
        saturation_index = 0.0 if second_half_range <= 0 else 0.0
    else:
        growth_ratio = second_half_range / first_half_range
        # growth_ratio=1 → same rate (not saturating), 0 → fully flat (saturated)
        saturation_index = max(0.0, min(1.0, 1.0 - growth_ratio))
    is_saturating = saturation_index > 0.7

    # Estimate plateau document (where slope → 0)
    plateau_at_doc: Optional[int] = None
    if fit_second.slope > 0.001:
        # Project forward: how many more docs until slope would reach current max
        remaining = (max_val - (fit_second.slope * xs[-1] + fit_second.intercept))
        if remaining > 0:
            plateau_at_doc = int(xs[-1] + remaining / fit_second.slope)

    return GrowthAnalysis(
        metric=metric,
        fit_full=fit_full,
        fit_first_half=fit_first,
        fit_second_half=fit_second,
        acceleration=acceleration,
        saturation_index=saturation_index,
        is_saturating=is_saturating,
        plateau_at_doc=plateau_at_doc,
    )


def detect_anomalies(
    results: List[DocResult],
    snapshots: List[CorpusSnapshot],
) -> List[AnomalyEvent]:
    """
    Detect anomalies:
     - Unusually slow documents (> 3σ above mean)
     - Sudden growth spikes or stalls
     - Burst failures
    """
    anomalies: List[AnomalyEvent] = []

    # Slow docs
    durations = [r.duration_ms for r in results if r.succeeded]
    if len(durations) >= 4:
        mean_d = sum(durations) / len(durations)
        std_d = math.sqrt(sum((d - mean_d) ** 2 for d in durations) / len(durations))
        for r in results:
            if r.succeeded and r.duration_ms > mean_d + 3 * std_d:
                severity = min(1.0, (r.duration_ms - mean_d) / (3 * std_d + 1e-9))
                anomalies.append(AnomalyEvent(
                    doc_index=r.doc_index,
                    kind="slow_doc",
                    severity=severity,
                    detail=f"{r.duration_ms:.0f}ms vs mean={mean_d:.0f}ms",
                ))

    # Growth spikes / stalls
    if len(snapshots) >= 3:
        deltas = [
            snapshots[i].n_identities - snapshots[i - 1].n_identities
            for i in range(1, len(snapshots))
        ]
        mean_delta = sum(deltas) / len(deltas)
        std_delta = math.sqrt(sum((d - mean_delta) ** 2 for d in deltas) / len(deltas))
        for i, delta in enumerate(deltas):
            snap = snapshots[i + 1]
            if std_delta > 0:
                z = abs(delta - mean_delta) / std_delta
                if z > 2.5:
                    kind = "growth_spike" if delta > mean_delta else "growth_stall"
                    anomalies.append(AnomalyEvent(
                        doc_index=snap.doc_index,
                        kind=kind,
                        severity=min(1.0, z / 5.0),
                        detail=f"Δidentities={delta:+d} (z={z:.1f})",
                    ))

    # Failure bursts (5 consecutive failures)
    streak = 0
    streak_start = 0
    for r in results:
        if r.failed:
            if streak == 0:
                streak_start = r.doc_index
            streak += 1
        else:
            streak = 0
        if streak >= 5:
            anomalies.append(AnomalyEvent(
                doc_index=streak_start,
                kind="failure_burst",
                severity=min(1.0, streak / 10.0),
                detail=f"{streak} consecutive failures starting at doc {streak_start}",
            ))
            streak = 0  # reset to avoid duplicate

    return anomalies


def compute_run_metrics(results: List[DocResult], elapsed_s: float) -> RunMetrics:
    durations = sorted(r.duration_ms for r in results)
    n = len(durations)
    succeeded = sum(1 for r in results if r.succeeded)
    failed = sum(1 for r in results if r.status == DocStatus.FAILED)
    timed_out = sum(1 for r in results if r.status == DocStatus.TIMEOUT)
    total_retries = sum(r.retries for r in results)

    def pct(p: float) -> float:
        if not durations:
            return 0.0
        return durations[min(n - 1, int(n * p))]

    return RunMetrics(
        total_docs=n,
        succeeded=succeeded,
        failed=failed,
        timed_out=timed_out,
        total_duration_s=elapsed_s,
        docs_per_second=n / elapsed_s if elapsed_s > 0 else 0.0,
        mean_doc_ms=sum(durations) / n if n else 0.0,
        p50_doc_ms=pct(0.50),
        p95_doc_ms=pct(0.95),
        p99_doc_ms=pct(0.99),
        max_doc_ms=durations[-1] if durations else 0.0,
        total_retries=total_retries,
        circuit_trips=0,  # filled in by orchestrator
    )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Pipeline Worker
# ══════════════════════════════════════════════════════════════════════════════


def _invoke_pipeline(
    text: str,
    script_path: Path,
    root: Path,
    timeout_s: float,
) -> Tuple[bool, str, str]:
    """
    Invoke the pipeline for a single document.
    Returns (success, stdout, stderr).
    Attempts in-process call first; falls back to subprocess.
    """
    # In-process fast path
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("run_complete", script_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            if hasattr(mod, "run"):
                mod.run(text)
                return True, "", ""
            elif hasattr(mod, "main"):
                orig_argv = sys.argv[:]
                sys.argv = [str(script_path), text]
                try:
                    mod.main()
                    return True, "", ""
                finally:
                    sys.argv = orig_argv
    except Exception:
        pass  # fall through to subprocess

    # Subprocess fallback
    import subprocess
    try:
        child_env = build_runtime_env(workers=1, method_workers=1)
        proc = subprocess.run(
            [sys.executable, str(script_path), text],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
            env=child_env,
        )
        return proc.returncode == 0, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return False, "", "TIMEOUT"
    except Exception as exc:
        return False, "", str(exc)


def _worker_task(
    args: Tuple[str, int, str, str, Path, Path, float, int, float],
) -> DocResult:
    """
    Worker entry point (runs in subprocess).
    Full retry logic with exponential backoff.
    """
    (run_id, doc_index, doc_name, text,
     script_path, root, timeout_s, max_retries, base_delay) = args

    preview = text[:60].replace("\n", " ")
    pid = os.getpid()
    retries = 0
    last_error: Optional[str] = None
    last_error_type: Optional[str] = None

    for attempt in range(max_retries + 1):
        t0 = time.perf_counter()
        try:
            success, stdout, stderr = _invoke_pipeline(
                text, script_path, root, timeout_s
            )
            duration_ms = (time.perf_counter() - t0) * 1000

            if success:
                # Extract corpus line if present
                corpus_line = None
                for line in stdout.splitlines():
                    if "Corpus state updated" in line or "corpus" in line.lower():
                        corpus_line = line.strip()
                        break
                return DocResult(
                    run_id=run_id,
                    doc_index=doc_index,
                    doc_name=doc_name,
                    text_preview=preview,
                    status=DocStatus.SUCCESS,
                    duration_ms=duration_ms,
                    retries=retries,
                    corpus_line=corpus_line,
                    worker_pid=pid,
                )
            else:
                is_timeout = "TIMEOUT" in stderr
                last_error = stderr[:300] if stderr else "non-zero exit"
                last_error_type = "timeout" if is_timeout else "pipeline_error"
                if is_timeout:
                    duration_ms = timeout_s * 1000
                    # Don't retry timeouts
                    return DocResult(
                        run_id=run_id,
                        doc_index=doc_index,
                        doc_name=doc_name,
                        text_preview=preview,
                        status=DocStatus.TIMEOUT,
                        duration_ms=duration_ms,
                        retries=retries,
                        error=last_error,
                        error_type=last_error_type,
                        worker_pid=pid,
                    )
                retries += 1

        except Exception as exc:
            duration_ms = (time.perf_counter() - t0) * 1000
            last_error = str(exc)
            last_error_type = type(exc).__name__
            retries += 1

        if attempt < max_retries:
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)

    return DocResult(
        run_id=run_id,
        doc_index=doc_index,
        doc_name=doc_name,
        text_preview=preview,
        status=DocStatus.FAILED,
        duration_ms=0.0,
        retries=retries,
        error=last_error,
        error_type=last_error_type,
        worker_pid=pid,
    )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — State Reader
# ══════════════════════════════════════════════════════════════════════════════


def read_corpus_state(state_path: Path) -> Tuple[int, int, int]:
    """Safely read (n_identities, n_edges, n_core) from JSON state."""
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
    except (json.JSONDecodeError, OSError):
        return 0, 0, 0


def read_stability_values(state_path: Path) -> List[float]:
    if not state_path.exists():
        return []
    try:
        with open(state_path, encoding="utf-8") as f:
            data = json.load(f)
        return list(data.get("identity_stability", {}).values())
    except (json.JSONDecodeError, OSError):
        return []


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — Checkpoint / Resume
# ══════════════════════════════════════════════════════════════════════════════

CHECKPOINT_PATH = OUTPUT_DIR / "stress_test_checkpoint.json"


def _result_to_dict(r: DocResult) -> Dict[str, Any]:
    """Serialize DocResult to JSON-safe dict."""
    d = asdict(r)
    d["status"] = r.status.name  # serialize Enum as string
    return d


def save_checkpoint(
    run_id: str,
    results: List[DocResult],
    snapshots: List[CorpusSnapshot],
) -> None:
    """Atomic checkpoint save (write-then-rename)."""
    data = {
        "run_id": run_id,
        "saved_at": time.time(),
        "results": [_result_to_dict(r) for r in results],
        "snapshots": [asdict(s) for s in snapshots],
    }
    tmp = CHECKPOINT_PATH.with_suffix(".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f)
        tmp.replace(CHECKPOINT_PATH)
    except OSError:
        pass


def load_checkpoint(run_id: str) -> Tuple[List[DocResult], List[CorpusSnapshot]]:
    if not CHECKPOINT_PATH.exists():
        return [], []
    try:
        with open(CHECKPOINT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("run_id") != run_id and run_id:
            return [], []  # different run
        results = []
        for r in data.get("results", []):
            r["status"] = DocStatus[r["status"].split(".")[-1]]
            results.append(DocResult(**r))
        snapshots = [CorpusSnapshot(**s) for s in data.get("snapshots", [])]
        return results, snapshots
    except Exception:
        return [], []


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — Charts
# ══════════════════════════════════════════════════════════════════════════════

CHART_PATH = OUTPUT_DIR / "stress_test_charts.png"


def save_charts(
    snapshots: List[CorpusSnapshot],
    results: List[DocResult],
    stability: StabilityStats,
    stability_values: List[float],
    gi: GrowthAnalysis,
    ge: GrowthAnalysis,
    gc: GrowthAnalysis,
) -> None:
    if not HAS_MPL or not snapshots:
        return

    # ── Palette & style ───────────────────────────────────────────────────────
    BG = "#0a0e1a"
    PANEL = "#0f1420"
    GRID = "#1e2535"
    BLUE = "#4f9eff"
    GREEN = "#39d98a"
    AMBER = "#ffb547"
    RED = "#ff5c5c"
    PURPLE = "#b975ff"
    WHITE = "#e8eaf6"
    DIM = "#6b7280"

    fig = plt.figure(figsize=(20, 14), facecolor=BG)
    fig.suptitle(
        "Corpus Stress Test  ·  Analysis Report",
        color=WHITE, fontsize=18, fontweight="bold",
        fontfamily="monospace", y=0.975,
    )

    gs = gridspec.GridSpec(
        3, 3, figure=fig, hspace=0.52, wspace=0.38,
        left=0.06, right=0.97, top=0.94, bottom=0.06,
    )

    def styled(ax, title: str) -> None:
        ax.set_facecolor(PANEL)
        ax.set_title(title, color=WHITE, fontsize=10, fontweight="bold",
                     fontfamily="monospace", pad=8)
        ax.tick_params(colors=DIM, labelsize=8)
        ax.xaxis.label.set_color(DIM)
        ax.yaxis.label.set_color(DIM)
        for sp in ax.spines.values():
            sp.set_edgecolor(GRID)
        ax.grid(color=GRID, linewidth=0.6, alpha=0.8, zorder=0)

    xs = [s.doc_index for s in snapshots]
    ids_ys = [s.n_identities for s in snapshots]
    edge_ys = [s.n_edges for s in snapshots]
    core_ys = [s.n_core for s in snapshots]

    # ── 1. Growth curves + trend lines ───────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.plot(xs, ids_ys, color=BLUE, lw=2.2, label="Identities", zorder=3)
    ax1.plot(xs, edge_ys, color=GREEN, lw=2.2, label="Edges", zorder=3)
    ax1.plot(xs, core_ys, color=RED, lw=2.2, label="Core", zorder=3)
    for ys, col in [(ids_ys, BLUE), (edge_ys, GREEN), (core_ys, RED)]:
        if len(xs) >= 2:
            fit = _linear_fit([float(x) for x in xs], [float(y) for y in ys])
            trend = [fit.slope * x + fit.intercept for x in xs]
            ax1.plot(xs, trend, color=col, lw=1, ls="--", alpha=0.35, zorder=2)
    ax1.fill_between(xs, ids_ys, alpha=0.06, color=BLUE)
    ax1.legend(facecolor=PANEL, labelcolor=WHITE, edgecolor=GRID, fontsize=8)
    ax1.set_xlabel("Documents")
    ax1.set_ylabel("Count")
    styled(ax1, "Graph Growth  (dashed = linear trend)")

    # ── 2. Saturation gauge ───────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 2])
    si = gi.saturation_index
    theta = [i / 100 * math.pi for i in range(101)]
    ax2.plot(
        [math.cos(t) for t in theta],
        [math.sin(t) for t in theta],
        color=GRID, lw=6,
    )
    filled_theta = theta[: int(si * 100) + 1]
    fill_color = RED if si > 0.7 else (AMBER if si > 0.4 else GREEN)
    ax2.plot(
        [math.cos(t) for t in filled_theta],
        [math.sin(t) for t in filled_theta],
        color=fill_color, lw=6,
    )
    ax2.text(0, -0.1, f"{si:.1%}", ha="center", va="center",
             color=fill_color, fontsize=22, fontweight="bold",
             fontfamily="monospace")
    ax2.text(0, -0.45, "Saturation Index", ha="center", va="center",
             color=DIM, fontsize=8, fontfamily="monospace")
    label = "SATURATED" if si > 0.7 else ("SLOWING" if si > 0.4 else "GROWING")
    ax2.text(0, 0.3, label, ha="center", va="center",
             color=fill_color, fontsize=9, fontweight="bold",
             fontfamily="monospace")
    ax2.set_xlim(-1.3, 1.3)
    ax2.set_ylim(-0.7, 1.2)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_facecolor(PANEL)
    ax2.set_title("Saturation Index", color=WHITE, fontsize=10,
                  fontweight="bold", fontfamily="monospace", pad=8)
    for sp in ax2.spines.values():
        sp.set_edgecolor(GRID)

    # ── 3. Per-doc latency ────────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    good = [(r.doc_index, r.duration_ms) for r in results if r.succeeded]
    bad = [(r.doc_index, r.duration_ms or 5000) for r in results if r.failed]
    if good:
        gx, gy = zip(*good)
        ax3.scatter(gx, gy, color=BLUE, s=18, alpha=0.7, zorder=3, label="Success")
        # Moving average
        win = max(1, len(gy) // 8)
        ma = [sum(list(gy)[max(0, i - win):i + 1]) / min(win, i + 1)
              for i in range(len(gy))]
        ax3.plot(list(gx), ma, color=WHITE, lw=1.5, alpha=0.8, zorder=4, label="MA")
    if bad:
        bx, by = zip(*bad)
        ax3.scatter(bx, by, color=RED, s=28, marker="x", zorder=5, label="Failed")
    ax3.legend(facecolor=PANEL, labelcolor=WHITE, edgecolor=GRID, fontsize=7)
    ax3.set_xlabel("Document")
    ax3.set_ylabel("ms")
    styled(ax3, "Latency per Document")

    # ── 4. Stability histogram ────────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    bins = ["<0.5", "0.5–1", "1–2", "2–5", "≥5"]
    counts = [
        stability.below_half, stability.half_to_one, stability.one_to_two,
        stability.two_to_five, stability.five_plus,
    ]
    bar_colors = [RED, AMBER, GREEN, BLUE, PURPLE]
    bars = ax4.bar(bins, counts, color=bar_colors, edgecolor=PANEL, lw=1.2, zorder=3)
    for bar, cnt in zip(bars, counts):
        if cnt:
            ax4.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                str(cnt), ha="center", va="bottom",
                color=WHITE, fontsize=8, fontfamily="monospace",
            )
    ax4.set_xlabel("Stability score")
    ax4.set_ylabel("Identities")
    styled(ax4, "Stability Histogram")

    # ── 5. Stability CDF ──────────────────────────────────────────────────────
    ax5 = fig.add_subplot(gs[1, 2])
    if stability_values:
        sv = sorted(stability_values)
        cdf_y = [i / len(sv) for i in range(1, len(sv) + 1)]
        ax5.plot(sv, cdf_y, color=PURPLE, lw=2, zorder=3)
        ax5.fill_between(sv, cdf_y, alpha=0.08, color=PURPLE)
        for pval, label, col in [
            (stability.p50, "p50", AMBER),
            (stability.p95, "p95", RED),
        ]:
            ax5.axvline(pval, color=col, lw=1, ls="--", alpha=0.8, zorder=4)
            ax5.text(pval + 0.02, 0.05, label, color=col, fontsize=7,
                     fontfamily="monospace")
    ax5.set_xlabel("Stability score")
    ax5.set_ylabel("CDF")
    styled(ax5, "Stability CDF")

    # ── 6. Growth rate (derivative) ───────────────────────────────────────────
    ax6 = fig.add_subplot(gs[2, 0])
    if len(ids_ys) >= 4:
        step = max(1, len(ids_ys) // 20)
        d_xs = xs[step:]
        d_ys = [(ids_ys[i] - ids_ys[i - step]) / step
                for i in range(step, len(ids_ys))]
        accel_color = [GREEN if d >= 0 else RED for d in d_ys]
        ax6.bar(d_xs, d_ys, color=accel_color, alpha=0.7, zorder=3, width=0.8)
        ax6.axhline(0, color=GRID, lw=1, zorder=2)
    ax6.set_xlabel("Document")
    ax6.set_ylabel("Δid / doc")
    styled(ax6, "Identity Growth Rate")

    # ── 7. Success/fail timeline ──────────────────────────────────────────────
    ax7 = fig.add_subplot(gs[2, 1])
    win = max(1, len(results) // 20)
    window_fail_rates = []
    window_xs = []
    for i in range(0, len(results), max(1, win)):
        chunk = results[i:i + win]
        fail_rate = sum(1 for r in chunk if r.failed) / len(chunk)
        window_fail_rates.append(fail_rate * 100)
        window_xs.append(chunk[len(chunk) // 2].doc_index)
    ax7.fill_between(window_xs, window_fail_rates, color=RED, alpha=0.4, zorder=2)
    ax7.plot(window_xs, window_fail_rates, color=RED, lw=1.5, zorder=3)
    ax7.set_ylim(0, 105)
    ax7.set_xlabel("Document")
    ax7.set_ylabel("Failure %")
    styled(ax7, "Rolling Failure Rate")

    # ── 8. Regression fit quality ─────────────────────────────────────────────
    ax8 = fig.add_subplot(gs[2, 2])
    metrics_labels = ["Identities", "Edges", "Core"]
    metrics_r2 = [
        gi.fit_full.r_squared,
        ge.fit_full.r_squared,
        gc.fit_full.r_squared,
    ]
    metrics_slopes = [
        gi.fit_full.slope,
        ge.fit_full.slope,
        gc.fit_full.slope,
    ]
    bar_w = 0.35
    idxs = [0, 1, 2]
    b1 = ax8.bar([x - bar_w / 2 for x in idxs], metrics_r2,
                 width=bar_w, color=BLUE, alpha=0.8, label="R²", zorder=3)
    ax8_r = ax8.twinx()
    ax8_r.bar([x + bar_w / 2 for x in idxs], metrics_slopes,
              width=bar_w, color=GREEN, alpha=0.8, label="Slope", zorder=3)
    ax8_r.tick_params(colors=DIM, labelsize=7)
    ax8_r.set_ylabel("Slope", color=DIM, fontsize=8)
    ax8.set_xticks(idxs)
    ax8.set_xticklabels(metrics_labels, fontsize=8)
    ax8.set_ylabel("R²", color=DIM, fontsize=8)
    ax8.set_ylim(0, 1.1)
    ax8.legend(loc="upper left", facecolor=PANEL, labelcolor=WHITE,
               edgecolor=GRID, fontsize=7)
    ax8_r.legend(loc="upper right", facecolor=PANEL, labelcolor=WHITE,
                 edgecolor=GRID, fontsize=7)
    ax8.set_facecolor(PANEL)
    ax8.set_title("Regression Quality", color=WHITE, fontsize=10,
                  fontweight="bold", fontfamily="monospace", pad=8)
    ax8.tick_params(colors=DIM, labelsize=8)
    for sp in ax8.spines.values():
        sp.set_edgecolor(GRID)
    ax8.grid(color=GRID, linewidth=0.6, alpha=0.8, zorder=0)

    plt.savefig(CHART_PATH, dpi=160, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — HTML Report
# ══════════════════════════════════════════════════════════════════════════════

HTML_REPORT_PATH = OUTPUT_DIR / "stress_test_report.html"


def save_html_report(report: FinalReport, chart_path: Path) -> None:
    """Generate a self-contained HTML report with embedded chart."""
    import base64

    chart_b64 = ""
    if chart_path.exists():
        with open(chart_path, "rb") as f:
            chart_b64 = base64.b64encode(f.read()).decode()

    m = report.metrics
    g = report.growth_identities
    s = report.stability
    cq = report.corpus_quality

    def fmt(v: Any, decimals: int = 2) -> str:
        if isinstance(v, float):
            return f"{v:.{decimals}f}"
        return str(v)

    def row(label: str, value: str, accent: str = "#4f9eff") -> str:
        return (
            f'<tr><td style="color:#6b7280;padding:6px 12px">{label}</td>'
            f'<td style="color:{accent};font-weight:600;padding:6px 12px;'
            f'font-family:monospace">{value}</td></tr>'
        )

    anomaly_rows = ""
    for a in report.anomalies:
        sev_col = "#ff5c5c" if a.severity > 0.6 else ("#ffb547" if a.severity > 0.3 else "#39d98a")
        anomaly_rows += (
            f'<tr><td style="color:#6b7280;padding:4px 12px">{a.doc_index}</td>'
            f'<td style="color:{sev_col};padding:4px 12px;font-family:monospace">{a.kind}</td>'
            f'<td style="color:#e8eaf6;padding:4px 12px">{a.detail}</td></tr>'
        )

    fail_rows = ""
    for r in report.doc_results:
        if r.failed:
            fail_rows += (
                f'<tr><td style="color:#6b7280;padding:4px 12px">{r.doc_index}</td>'
                f'<td style="color:#ff5c5c;padding:4px 12px;font-family:monospace">'
                f'{r.status.name}</td>'
                f'<td style="color:#e8eaf6;padding:4px 12px">{r.error or ""}</td></tr>'
            )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Corpus Stress Test Report · {report.run_id}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;700;800&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #080c18; color: #e8eaf6; font-family: 'Syne', sans-serif;
           min-height: 100vh; padding: 40px 24px; }}
  .wrap {{ max-width: 1200px; margin: 0 auto; }}
  header {{ border-bottom: 1px solid #1e2535; padding-bottom: 24px; margin-bottom: 40px; }}
  h1 {{ font-size: 2.4rem; font-weight: 800; letter-spacing: -0.02em;
        background: linear-gradient(135deg, #4f9eff 0%, #b975ff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  .sub {{ color: #6b7280; font-family: 'JetBrains Mono', monospace;
          font-size: 0.8rem; margin-top: 6px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 20px; margin-bottom: 32px; }}
  .card {{ background: #0f1420; border: 1px solid #1e2535; border-radius: 12px;
            padding: 20px; }}
  .card h2 {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em;
               color: #6b7280; margin-bottom: 12px; }}
  .kpi {{ font-size: 2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }}
  .kpi.blue {{ color: #4f9eff; }} .kpi.green {{ color: #39d98a; }}
  .kpi.red {{ color: #ff5c5c; }} .kpi.amber {{ color: #ffb547; }}
  .kpi.purple {{ color: #b975ff; }}
  table {{ width: 100%; border-collapse: collapse; }}
  table th {{ text-align: left; color: #6b7280; font-size: 0.75rem;
               text-transform: uppercase; letter-spacing: 0.08em;
               padding: 8px 12px; border-bottom: 1px solid #1e2535; }}
  section {{ background: #0f1420; border: 1px solid #1e2535; border-radius: 12px;
              padding: 24px; margin-bottom: 24px; }}
  section h2 {{ font-size: 1rem; font-weight: 700; color: #e8eaf6;
                 margin-bottom: 16px; letter-spacing: 0.02em; }}
  .chart-wrap {{ text-align: center; }}
  .chart-wrap img {{ max-width: 100%; border-radius: 8px;
                      border: 1px solid #1e2535; }}
  .badge {{ display:inline-block; padding: 2px 8px; border-radius: 4px;
             font-size: 0.7rem; font-family: 'JetBrains Mono', monospace;
             font-weight: 600; }}
  .badge-ok {{ background: #0d2b1a; color: #39d98a; }}
  .badge-warn {{ background: #2b1e08; color: #ffb547; }}
  .badge-err {{ background: #2b0d0d; color: #ff5c5c; }}
  footer {{ color: #374151; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;
             margin-top: 40px; text-align: center; }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>Corpus Stress Test</h1>
  <div class="sub">Run ID: {report.run_id} &nbsp;·&nbsp; {report.run_timestamp}
       &nbsp;·&nbsp; v{report.schema_version}</div>
</header>

<!-- KPI grid -->
<div class="grid">
  <div class="card"><h2>Documents Processed</h2>
    <div class="kpi blue">{m.total_docs if m else 0}</div></div>
  <div class="card"><h2>Success Rate</h2>
    <div class="kpi {'green' if m and m.failed == 0 else 'amber'}">
      {fmt((m.succeeded / m.total_docs * 100) if m and m.total_docs else 0, 1)}%</div></div>
  <div class="card"><h2>Throughput</h2>
    <div class="kpi green">{fmt(m.docs_per_second if m else 0)} doc/s</div></div>
  <div class="card"><h2>Final Identities</h2>
    <div class="kpi purple">{report.snapshots[-1].n_identities if report.snapshots else 0}</div></div>
  <div class="card"><h2>Final Edges</h2>
    <div class="kpi blue">{report.snapshots[-1].n_edges if report.snapshots else 0}</div></div>
  <div class="card"><h2>Stability p50</h2>
    <div class="kpi amber">{fmt(s.p50 if s else 0)}</div></div>
</div>

<!-- Chart -->
{"" if not chart_b64 else f'''
<section>
  <h2>Analysis Charts</h2>
  <div class="chart-wrap">
    <img src="data:image/png;base64,{chart_b64}" alt="Analysis Charts">
  </div>
</section>
'''}

<!-- Performance stats -->
<section>
  <h2>Performance Metrics</h2>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    {row("Succeeded", str(m.succeeded if m else 0), "#39d98a")}
    {row("Failed", str(m.failed if m else 0), "#ff5c5c" if (m and m.failed) else "#39d98a")}
    {row("Timed Out", str(m.timed_out if m else 0))}
    {row("Total Duration", fmt(m.total_duration_s if m else 0) + "s")}
    {row("Mean Latency", fmt(m.mean_doc_ms if m else 0) + "ms")}
    {row("p95 Latency", fmt(m.p95_doc_ms if m else 0) + "ms")}
    {row("p99 Latency", fmt(m.p99_doc_ms if m else 0) + "ms")}
    {row("Max Latency", fmt(m.max_doc_ms if m else 0) + "ms")}
    {row("Total Retries", str(m.total_retries if m else 0))}
    {row("Circuit Trips", str(m.circuit_trips if m else 0))}
  </table>
</section>

<!-- Growth analysis -->
<section>
  <h2>Growth Analysis (Identities)</h2>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    {row("Full slope", fmt(g.fit_full.slope if g else 0, 4)) if g else ""}
    {row("Full R²", fmt(g.fit_full.r_squared if g else 0, 4)) if g else ""}
    {row("Acceleration", fmt(g.acceleration if g else 0, 4)) if g else ""}
    {row("Saturation Index", fmt(g.saturation_index if g else 0, 3)) if g else ""}
    {row("Is Saturating?", str(g.is_saturating if g else False)) if g else ""}
    {row("Plateau Est.", str(g.plateau_at_doc if g and g.plateau_at_doc else "N/A")) if g else ""}
  </table>
</section>

<!-- Stability stats -->
<section>
  <h2>Stability Distribution</h2>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    {row("Total identities", str(s.n_total if s else 0))}
    {row("Mean ± Std", f"{fmt(s.mean if s else 0)} ± {fmt(s.std if s else 0)}") if s else ""}
    {row("p50 / p95 / p99", f"{fmt(s.p50 if s else 0)} / {fmt(s.p95 if s else 0)} / {fmt(s.p99 if s else 0)}") if s else ""}
    {row("Min / Max", f"{fmt(s.min_val if s else 0)} / {fmt(s.max_val if s else 0)}") if s else ""}
  </table>
</section>

<!-- Corpus quality -->
<section>
  <h2>Corpus Quality</h2>
  <table>
    <tr><th>Metric</th><th>Value</th></tr>
    {"".join(row(k.replace("_", " ").title(), fmt(v, 3)) for k, v in cq.items())}
  </table>
</section>

<!-- Anomalies -->
{"" if not report.anomalies else f"""
<section>
  <h2>Anomalies Detected ({len(report.anomalies)})</h2>
  <table>
    <tr><th>Doc</th><th>Kind</th><th>Detail</th></tr>
    {anomaly_rows}
  </table>
</section>
"""}

<!-- Failures -->
{"" if not any(r.failed for r in report.doc_results) else f"""
<section>
  <h2>Failed Documents</h2>
  <table>
    <tr><th>Doc</th><th>Status</th><th>Error</th></tr>
    {fail_rows}
  </table>
</section>
"""}

<footer>Generated by Corpus Stress Test v{report.schema_version} · {report.run_timestamp}</footer>
</div>
</body>
</html>"""

    with open(HTML_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(html)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 11 — Logging
# ══════════════════════════════════════════════════════════════════════════════

LOG_PATH = OUTPUT_DIR / "stress_test.log"
JSON_LOG_PATH = OUTPUT_DIR / "stress_test_events.jsonl"

_json_log_lock = threading.Lock()


def setup_logging(level_str: str) -> None:
    level = getattr(logging, level_str.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)-8s] %(message)s",
        handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8")],
    )


def log_event(event: str, **kwargs: Any) -> None:
    """Write a structured JSONL event log entry."""
    record = {"t": time.time(), "event": event, **kwargs}
    with _json_log_lock:
        with open(JSON_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")


log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 12 — Rich TUI Dashboard
# ══════════════════════════════════════════════════════════════════════════════

if HAS_RICH:
    _console = Console()
else:
    _console = None  # type: ignore[assignment]


def _make_kpi_table(
    n_done: int, n_fail: int, n_total: int,
    n_id: int, n_edge: int, n_core: int,
    elapsed: float, cb_state: CircuitState,
) -> Table:
    t = Table(box=box.SIMPLE, show_header=False, pad_edge=False, expand=True)
    t.add_column("K", style="dim")
    t.add_column("V", justify="right")
    dps = n_done / elapsed if elapsed > 0 else 0
    pct = f"{n_done / n_total * 100:.1f}%" if n_total else "—"
    cb_col = "green" if cb_state == CircuitState.CLOSED else (
        "red" if cb_state == CircuitState.OPEN else "yellow")
    t.add_row("Progress", f"[bold]{n_done}[/bold] / {n_total}  ({pct})")
    t.add_row("Failed", f"[red]{n_fail}[/red]" if n_fail else "[green]0[/green]")
    t.add_row("Elapsed", f"{elapsed:.1f}s")
    t.add_row("Throughput", f"[green]{dps:.2f}[/green] doc/s")
    t.add_row("", "")
    t.add_row("Identities", f"[cyan]{n_id}[/cyan]")
    t.add_row("Edges", f"[green]{n_edge}[/green]")
    t.add_row("Core", f"[magenta]{n_core}[/magenta]")
    t.add_row("", "")
    t.add_row("Circuit", f"[{cb_col}]{cb_state.name}[/{cb_col}]")
    return t


def _make_recent_table(recent: List[DocResult]) -> Table:
    t = Table(box=box.MINIMAL, show_header=True,
              header_style="dim", pad_edge=False, expand=True)
    t.add_column("#", width=5)
    t.add_column("Name", width=18, no_wrap=True)
    t.add_column("St", width=3)
    t.add_column("ms", width=7, justify="right")
    t.add_column("Corpus line", no_wrap=True)
    for r in list(recent)[-10:]:
        st = "[green]✓[/green]" if r.succeeded else "[red]✗[/red]"
        ms = f"{r.duration_ms:.0f}" if r.duration_ms < 9999 else "TO"
        cl = r.corpus_line or r.text_preview[:35]
        t.add_row(str(r.doc_index), r.doc_name[:18], st, ms, cl)
    return t


def _make_anomaly_panel(anomalies: List[AnomalyEvent]) -> str:
    if not anomalies:
        return "[dim]No anomalies detected[/dim]"
    lines = []
    for a in anomalies[-5:]:
        col = "red" if a.severity > 0.6 else ("yellow" if a.severity > 0.3 else "green")
        lines.append(f"[{col}]doc {a.doc_index}[/{col}] {a.kind}: {a.detail}")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 13 — Orchestrator
# ══════════════════════════════════════════════════════════════════════════════


def run(cfg: StressTestConfig) -> FinalReport:
    """
    Main orchestration:
     1. Validate config
     2. Build corpus
     3. Dispatch parallel workers
     4. Live dashboard update
     5. Collect results, snapshots
     6. Statistical analysis
     7. Anomaly detection
     8. Produce all outputs
    """
    setup_logging(cfg.log_level)
    log.info("Starting run %s  n=%d workers=%d", cfg.run_id, cfg.n_docs, cfg.worker_count)
    log_event("run_start", run_id=cfg.run_id, n_docs=cfg.n_docs, workers=cfg.worker_count)

    # Config validation
    errors = cfg.validate()
    if errors:
        for e in errors:
            print(f"[CONFIG ERROR] {e}", file=sys.stderr)
        if not cfg.dry_run:
            sys.exit(2)

    # Corpus
    corpus = build_corpus(cfg.n_docs, cfg)
    cq = corpus_quality_score(corpus)
    log.info("Corpus built: %d docs, quality=%.3f", len(corpus), cq.get("overall", 0))

    if cfg.dry_run:
        print(f"[DRY RUN] Corpus: {len(corpus)} docs, quality={cq.get('overall', 0):.3f}")
        for e in corpus:
            print(f"  [{e.source}] {e.name}: {e.text[:60]}")
        return FinalReport(run_id=cfg.run_id, corpus_quality=cq)

    # Clean state for fresh run
    if not cfg.resume and cfg.corpus_state_path.exists():
        cfg.corpus_state_path.unlink()

    # Resume
    existing_results: List[DocResult] = []
    existing_snapshots: List[CorpusSnapshot] = []
    if cfg.resume:
        existing_results, existing_snapshots = load_checkpoint(cfg.run_id)
        log.info("Resumed: %d results, %d snapshots", len(existing_results), len(existing_snapshots))

    done_indices = {r.doc_index for r in existing_results}
    all_results: List[DocResult] = list(existing_results)
    snapshots: List[CorpusSnapshot] = list(existing_snapshots)
    recent: Deque[DocResult] = deque(maxlen=20)
    anomalies: List[AnomalyEvent] = []
    circuit = CircuitBreaker(cfg.cb_failure_threshold, cfg.cb_recovery_timeout_s)

    work_items = [
        (
            cfg.run_id, i, corpus[i - 1].name, corpus[i - 1].text,
            cfg.pipeline_script, ROOT,
            cfg.doc_timeout_s, cfg.max_retries, cfg.retry_base_delay_s,
        )
        for i in range(1, cfg.n_docs + 1)
        if i not in done_indices
    ]

    n_id = n_edge = n_core = 0
    interval = cfg.effective_sample_interval()
    t_start = time.time()
    shutdown_event = threading.Event()

    # Graceful shutdown on Ctrl-C
    def _handle_sigint(sig: int, frame: Any) -> None:
        shutdown_event.set()
    signal.signal(signal.SIGINT, _handle_sigint)

    # ── Rich TUI run ──────────────────────────────────────────────────────────
    if HAS_RICH and _console:
        progress = Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[bold cyan]Processing[/bold cyan]"),
            BarColumn(bar_width=None),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            TextColumn("{task.fields[rate]}", style="bold green"),
            console=_console,
            expand=True,
        )
        task_id = progress.add_task("docs", total=len(work_items), rate="")

        layout = Layout()
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body"),
            Layout(name="footer", size=5),
        )
        layout["body"].split_row(
            Layout(name="kpi", ratio=1),
            Layout(name="recent", ratio=3),
        )
        layout["body"].split_row(
            Layout(name="kpi", ratio=1),
            Layout(name="right"),
        )
        layout["right"].split_column(
            Layout(name="recent", ratio=2),
            Layout(name="anomalies", ratio=1),
        )

        def refresh(elapsed: float) -> None:
            layout["header"].update(Panel(
                Text(
                    f"  ◈  CORPUS STRESS TEST  v3.0  ◈  "
                    f"Run: {cfg.run_id}  │  Workers: {cfg.worker_count}  │  "
                    f"T_atomic=2.0  │  "
                    f"Q={cq.get('overall', 0):.2f}",
                    style="bold white",
                ),
                style="on #0d1529",
            ))
            layout["kpi"].update(Panel(
                _make_kpi_table(
                    len(all_results), sum(1 for r in all_results if r.failed),
                    cfg.n_docs, n_id, n_edge, n_core, elapsed, circuit.state,
                ),
                title="[bold]Metrics[/bold]", border_style="blue",
            ))
            layout["recent"].update(Panel(
                _make_recent_table(list(recent)),
                title="[bold]Recent Documents[/bold]", border_style="magenta",
            ))
            layout["anomalies"].update(Panel(
                _make_anomaly_panel(anomalies),
                title="[bold]Anomalies[/bold]", border_style="yellow",
            ))
            layout["footer"].update(Panel(progress, border_style="cyan"))

        with Live(layout, console=_console, refresh_per_second=8, screen=False):
            with ProcessPoolExecutor(max_workers=cfg.worker_count) as pool:
                futures: Dict[Future, tuple] = {
                    pool.submit(_worker_task, item): item
                    for item in work_items
                }
                for future in as_completed(futures):
                    if shutdown_event.is_set():
                        log.warning("Shutdown requested, cancelling remaining futures")
                        for f in futures:
                            f.cancel()
                        break

                    elapsed = time.time() - t_start
                    try:
                        result: DocResult = future.result(timeout=cfg.doc_timeout_s + 5)
                    except Exception as exc:
                        item = futures[future]
                        result = DocResult(
                            run_id=cfg.run_id,
                            doc_index=item[1],
                            doc_name=item[2],
                            text_preview=item[3][:60],
                            status=DocStatus.FAILED,
                            duration_ms=0,
                            error=str(exc),
                            error_type=type(exc).__name__,
                        )

                    all_results.append(result)
                    recent.append(result)
                    log_event(
                        "doc_done",
                        doc=result.doc_index,
                        status=result.status.name,
                        ms=result.duration_ms,
                    )

                    if result.failed:
                        tripped = circuit.record_failure()
                        if tripped:
                            log.error("Circuit breaker OPEN at doc %d", result.doc_index)
                            log_event("circuit_open", doc=result.doc_index)
                    else:
                        circuit.record_success()

                    # Sample corpus state
                    if len(all_results) % interval == 0 or result.doc_index == cfg.n_docs:
                        n_id, n_edge, n_core = read_corpus_state(cfg.corpus_state_path)
                        snap = CorpusSnapshot(result.doc_index, n_id, n_edge, n_core)
                        if len(snapshots) > 0:
                            prev = snapshots[-1]
                            doc_delta = snap.doc_index - prev.doc_index
                            if doc_delta > 0:
                                snap.identity_growth_rate = (snap.n_identities - prev.n_identities) / doc_delta
                                snap.edge_growth_rate = (snap.n_edges - prev.n_edges) / doc_delta
                        snapshots.append(snap)

                        # Check anomalies incrementally
                        new_anomalies = detect_anomalies(all_results, snapshots)
                        anomalies = new_anomalies

                    dps = len(all_results) / elapsed if elapsed > 0 else 0
                    progress.update(task_id, advance=1, rate=f"{dps:.2f} doc/s")
                    refresh(elapsed)

                    if len(all_results) % 10 == 0:
                        save_checkpoint(cfg.run_id, all_results, snapshots)

    else:
        # Plain fallback
        print("=" * 70)
        print(f"CORPUS STRESS TEST v3.0  ·  Run: {cfg.run_id}")
        print(f"  Docs: {cfg.n_docs}  Workers: {cfg.worker_count}")
        print("=" * 70)
        with ProcessPoolExecutor(max_workers=cfg.worker_count) as pool:
            futures_plain = {pool.submit(_worker_task, item): item for item in work_items}
            for future in as_completed(futures_plain):
                if shutdown_event.is_set():
                    break
                elapsed = time.time() - t_start
                try:
                    result = future.result(timeout=cfg.doc_timeout_s + 5)
                except Exception as exc:
                    item = futures_plain[future]
                    result = DocResult(
                        run_id=cfg.run_id, doc_index=item[1], doc_name=item[2],
                        text_preview=item[3][:60], status=DocStatus.FAILED,
                        duration_ms=0, error=str(exc),
                    )
                all_results.append(result)
                if result.failed:
                    circuit.record_failure()
                else:
                    circuit.record_success()
                if len(all_results) % interval == 0:
                    n_id, n_edge, n_core = read_corpus_state(cfg.corpus_state_path)
                    snapshots.append(CorpusSnapshot(result.doc_index, n_id, n_edge, n_core))
                    dps = len(all_results) / elapsed if elapsed > 0 else 0
                    status_sym = "✓" if result.succeeded else "✗"
                    print(f"  {status_sym} Doc {result.doc_index:4d} | "
                          f"{n_id:4d} id | {n_edge:4d} edges | {n_core:2d} core | "
                          f"{dps:.2f} doc/s")

    total_elapsed = time.time() - t_start

    # ── Final state reads ─────────────────────────────────────────────────────
    n_id, n_edge, n_core = read_corpus_state(cfg.corpus_state_path)
    stability_values = read_stability_values(cfg.corpus_state_path)
    stability = StabilityStats.from_values(stability_values)

    snapshots.sort(key=lambda s: s.doc_index)
    snap_xs = [s.doc_index for s in snapshots]

    gi = analyze_growth(snap_xs, [s.n_identities for s in snapshots], "identities")
    ge = analyze_growth(snap_xs, [s.n_edges for s in snapshots], "edges")
    gc = analyze_growth(snap_xs, [s.n_core for s in snapshots], "core")

    metrics = compute_run_metrics(all_results, total_elapsed)
    metrics.circuit_trips = circuit.trip_count

    anomalies = detect_anomalies(all_results, snapshots)

    # ── Build report ──────────────────────────────────────────────────────────
    report = FinalReport(
        run_id=cfg.run_id,
        run_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        config=dataclasses.asdict(cfg),
        corpus_quality=cq,
        metrics=metrics,
        stability=stability,
        growth_identities=gi,
        growth_edges=ge,
        growth_core=gc,
        snapshots=snapshots,
        anomalies=anomalies,
        doc_results=all_results,
    )

    # ── Save outputs ──────────────────────────────────────────────────────────
    if cfg.report_charts:
        save_charts(snapshots, all_results, stability, stability_values, gi, ge, gc)
        report.output_files["charts"] = str(CHART_PATH)

    if cfg.report_html:
        save_html_report(report, CHART_PATH)
        report.output_files["html"] = str(HTML_REPORT_PATH)

    if cfg.report_json:
        json_out = OUTPUT_DIR / f"stress_test_{cfg.run_id}.json"
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(dataclasses.asdict(report), f, indent=2, default=str)
        report.output_files["json"] = str(json_out)

    report.output_files["log"] = str(LOG_PATH)
    report.output_files["events"] = str(JSON_LOG_PATH)

    save_checkpoint(cfg.run_id, all_results, snapshots)
    log_event("run_complete", run_id=cfg.run_id, elapsed=total_elapsed,
              succeeded=metrics.succeeded, failed=metrics.failed)

    # ── Terminal final summary ────────────────────────────────────────────────
    _print_summary(report, gi, stability)

    return report


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 14 — Final Summary Printer
# ══════════════════════════════════════════════════════════════════════════════


def _print_summary(
    report: FinalReport,
    gi: Optional[GrowthAnalysis],
    s: Optional[StabilityStats],
) -> None:
    m = report.metrics
    if not HAS_RICH or not _console:
        print("=" * 70)
        print("FINAL SUMMARY")
        if m:
            print(f"  Docs: {m.total_docs}  Succeeded: {m.succeeded}  Failed: {m.failed}")
            print(f"  Duration: {m.total_duration_s:.2f}s  Throughput: {m.docs_per_second:.2f} doc/s")
        if gi:
            print(f"  Identity slope={gi.fit_full.slope:.4f}  R²={gi.fit_full.r_squared:.3f}")
            print(f"  Saturation={gi.saturation_index:.3f}  Accel={gi.acceleration:+.4f}")
        if s:
            print(f"  Stability p50={s.p50:.3f}  p95={s.p95:.3f}")
        for k, v in report.output_files.items():
            print(f"  {k}: {v}")
        print("=" * 70)
        return

    tbl = Table(
        box=box.ROUNDED,
        title=f"[bold white]◈  FINAL REPORT  ·  Run {report.run_id}  ◈[/bold white]",
        title_style="bold white",
        header_style="bold cyan",
        show_header=True,
        expand=False,
    )
    tbl.add_column("Category", style="dim white", width=30)
    tbl.add_column("Value", style="bold white", justify="right", width=28)

    if m:
        tbl.add_row("Documents processed", f"{m.total_docs}")
        tbl.add_row("Succeeded",
                    f"[green]{m.succeeded}[/green]" if m.failed == 0
                    else f"[yellow]{m.succeeded}[/yellow]")
        tbl.add_row("Failed",
                    f"[red]{m.failed}[/red]" if m.failed else "[green]0[/green]")
        tbl.add_row("Timed out", str(m.timed_out))
        tbl.add_row("Total duration", f"{m.total_duration_s:.2f}s")
        tbl.add_row("Throughput", f"[green]{m.docs_per_second:.2f}[/green] doc/s")
        tbl.add_row("Latency p50/p95/p99",
                    f"{m.p50_doc_ms:.0f} / {m.p95_doc_ms:.0f} / {m.p99_doc_ms:.0f} ms")
        tbl.add_row("Total retries", str(m.total_retries))
        tbl.add_row("Circuit trips",
                    f"[red]{m.circuit_trips}[/red]" if m.circuit_trips else "[green]0[/green]")

    tbl.add_row("─" * 27, "─" * 25)

    if report.snapshots:
        last = report.snapshots[-1]
        tbl.add_row("Final identities", f"[cyan]{last.n_identities}[/cyan]")
        tbl.add_row("Final edges", f"[green]{last.n_edges}[/green]")
        tbl.add_row("Final core", f"[magenta]{last.n_core}[/magenta]")

    if gi:
        tbl.add_row("─" * 27, "─" * 25)
        tbl.add_row("Identity slope (R²)",
                    f"{gi.fit_full.slope:.4f}  (R²={gi.fit_full.r_squared:.3f})")
        tbl.add_row("Saturation index",
                    f"[red]{gi.saturation_index:.3f}[/red]" if gi.is_saturating
                    else f"[green]{gi.saturation_index:.3f}[/green]")
        accel_col = "green" if gi.acceleration >= 0 else "yellow"
        tbl.add_row("Growth acceleration", f"[{accel_col}]{gi.acceleration:+.4f}[/{accel_col}]")
        if gi.plateau_at_doc:
            tbl.add_row("Est. plateau at doc", str(gi.plateau_at_doc))

    if s and s.n_total:
        tbl.add_row("─" * 27, "─" * 25)
        tbl.add_row("Stability n", str(s.n_total))
        tbl.add_row("Stability mean ± std", f"{s.mean:.3f} ± {s.std:.3f}")
        tbl.add_row("Stability p50 / p95", f"{s.p50:.3f} / {s.p95:.3f}")

    if report.anomalies:
        tbl.add_row("─" * 27, "─" * 25)
        tbl.add_row("Anomalies detected", f"[yellow]{len(report.anomalies)}[/yellow]")

    if report.output_files:
        tbl.add_row("─" * 27, "─" * 25)
        for k, v in report.output_files.items():
            tbl.add_row(k.title(), f"[dim]{Path(v).name}[/dim]")

    _console.print()
    _console.print(tbl)
    _console.print()

    # Interpretive insights
    if gi:
        si = gi.saturation_index
        if si > 0.8:
            _console.print(
                "[yellow]⚠  Identity graph is saturating "
                f"(SI={si:.2f}). Corpus diversity may be insufficient.[/yellow]"
            )
        elif si < 0.3:
            _console.print(
                f"[green]✓  Identity graph growing freely (SI={si:.2f}). "
                "Corpus is revealing new structure.[/green]"
            )
        if gi.acceleration < -0.05:
            _console.print("[cyan]↘  Growth decelerating — approaching saturation.[/cyan]")
        elif gi.acceleration > 0.05:
            _console.print("[green]↗  Growth accelerating — corpus expanding coverage.[/green]")
    if m and m.failed > m.total_docs * 0.1:
        _console.print(
            f"[red]⚠  High failure rate ({m.failed/m.total_docs*100:.0f}%). "
            "Check pipeline health.[/red]"
        )
    _console.print()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 15 — Entry Point
# ══════════════════════════════════════════════════════════════════════════════


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="stress_test",
        description="Enterprise Corpus Stress Test v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stress_test.py                        # default 20 docs
  python stress_test.py --docs 200 --workers 8
  python stress_test.py --docs 500 --resume
  python stress_test.py --docs 20 --dry-run
  STRESS_N_DOCS=100 python stress_test.py      # env-var override
        """,
    )
    parser.add_argument("--docs", "-n", type=int, default=20,
                        help="Number of documents (default: 20)")
    parser.add_argument("--workers", "-w", type=int,
                        default=min(8, os.cpu_count() or 4),
                        help="Parallel worker count (default: auto)")
    parser.add_argument("--interval", "-i", type=int, default=0,
                        help="Snapshot interval (default: n_docs//10)")
    parser.add_argument("--timeout", "-t", type=float, default=60.0,
                        help="Per-doc timeout in seconds (default: 60)")
    parser.add_argument("--retries", "-r", type=int, default=2,
                        help="Max retries per doc (default: 2)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from last checkpoint")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate corpus only, do not run pipeline")
    parser.add_argument("--run-id", type=str, default="",
                        help="Custom run ID (default: random hex)")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help="Log verbosity (default: INFO)")
    parser.add_argument("--no-charts", action="store_true")
    parser.add_argument("--no-html", action="store_true")

    args = parser.parse_args()
    runtime_env = build_runtime_env(workers=args.workers)
    for key in ("SANTEK_TEXT_WORKERS", "STRESS_WORKERS"):
        if key in runtime_env:
            os.environ[key] = runtime_env[key]

    cfg = StressTestConfig.from_env()
    cfg.n_docs = args.docs
    cfg.worker_count = args.workers
    cfg.sample_interval = args.interval
    cfg.doc_timeout_s = args.timeout
    cfg.max_retries = args.retries
    cfg.resume = args.resume
    cfg.dry_run = args.dry_run
    cfg.log_level = args.log_level
    cfg.normalize_workers()
    if args.run_id:
        cfg.run_id = args.run_id
    if args.no_charts:
        cfg.report_charts = False
    if args.no_html:
        cfg.report_html = False

    try:
        run(cfg)
    except KeyboardInterrupt:
        print("\n[Interrupted — checkpoint saved]", file=sys.stderr)
        return 130
    except Exception:
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    sys.exit(main())
