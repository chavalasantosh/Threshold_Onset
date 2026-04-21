#!/usr/bin/env python3
# pylint: disable=too-many-lines,redefined-outer-name
"""
run_complete.py  ·  Complete End-to-End Unified Pipeline  ·  v2.0
══════════════════════════════════════════════════════════════════════════════

threshold_onset <-> santok

कार्य (kārya) happens before ज्ञान (jñāna)
Action before knowledge.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHITECTURE  (v2.0 improvements over v1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌─────────────────────────────────────────────────────────────────────┐
  │ Layer             │ v1                    │ v2                      │
  ├───────────────────┼───────────────────────┼─────────────────────────┤
  │ Types             │ bare dicts            │ dataclasses + TypedDict │
  │ Config            │ buried in main()      │ PipelineConfig + schema │
  │ Phases            │ loose function calls  │ PhaseRunner protocol    │
  │ TokenAction       │ sha256 per call       │ LRU-cached residues     │
  │ Imports           │ silent except-pass    │ ImportResult registry   │
  │ Parallelism       │ serial only           │ async phase groups      │
  │ Topology          │ protected method hack │ TopologyAnalyzer class  │
  │ Clustering        │ hardcoded thresholds  │ config-driven + typed   │
  │ Generation        │ loose print loop      │ GenerationPipeline      │
  │ Logging           │ print() everywhere    │ structured + rich TUI   │
  │ Profiling         │ none                  │ PhaseTimer + flamegraph │
  │ Error handling    │ broad except-pass     │ typed PhaseError chain  │
  │ Return type       │ dict or None          │ PipelineResult          │
  │ API               │ main() only           │ run() + async_run()     │
  │ Corpus            │ buried in main()      │ CorpusManager class     │
  │ Testing           │ none                  │ injectable phases       │
  └─────────────────────────────────────────────────────────────────────┘

Usage:
  python run_complete.py "your text here"
  python run_complete.py /path/to/file.txt
  python run_complete.py --config custom.json "text"
  python run_complete.py --profile "text"          # emit timing flamegraph
  python run_complete.py --no-tui "text"           # plain output
  python run_complete.py --async "text"            # async execution

Implementation notes (intentional stubs / optional behaviour):
  · PhaseRunner: protocol only (run/validate_output are ...); real logic in
    DefaultPhaseRunners and phase0–4 modules. validate_output is for tests.
  · _NullLearner: intentional no-op when PreferenceLearner is unavailable.
  · Fluency generator: optional; when available, its output is included in
    generated_outputs (first when present).
  · Env overrides (PIPELINE_*): invalid values are logged and the default kept.
  · build_surface_mapping: three strategies (structural decoder → integration
    surface → hash fallback); first success wins.
  · Tokenization: multi-strategy with stdlib split as last fallback.
"""

from __future__ import annotations

# ── stdlib ────────────────────────────────────────────────────────────────────
import asyncio
import argparse
import dataclasses
import functools
import hashlib
import logging
import math
import os
import random
import sys
import textwrap
import time
import traceback
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    FrozenSet,
    Iterator,
    List,
    Optional,
    Protocol,
    Sequence,
    Set,
    Tuple,
    runtime_checkable,
)
try:
    from integration.runtime.cli import build_runtime_env
except Exception:  # pragma: no cover - optional runtime layer
    def build_runtime_env(
        workers: Optional[int] = None,
        method_workers: Optional[int] = None,
        profile: bool = False,
    ) -> Dict[str, str]:
        """Fallback when integration.runtime is unavailable."""
        _ = workers, method_workers, profile
        return {}

# ── optional third-party ──────────────────────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# ── project root ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Structured Logging
# ══════════════════════════════════════════════════════════════════════════════

_CONSOLE = Console(stderr=True) if HAS_RICH else None

def _get_logger(name: str) -> logging.Logger:
    """Return project logger, falling back cleanly if logging_config missing."""
    try:
        from threshold_onset.core.logging_config import get_logger  # type: ignore
        return get_logger(name)  # type: ignore[return-value]
    except Exception:  # pylint: disable=broad-exception-caught
        logger = logging.getLogger(name)
        if not logger.handlers:
            h = logging.StreamHandler(sys.stderr)
            h.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
            logger.addHandler(h)
        return logger

log = _get_logger("integration.run_complete")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Exceptions
# ══════════════════════════════════════════════════════════════════════════════

class PipelineError(Exception):
    """Base class for all pipeline errors."""
    def __init__(self, message: str, phase: Optional[str] = None,
                 cause: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.phase = phase
        self.cause = cause

    def __str__(self) -> str:
        base = super().__str__()
        parts = [base]
        if self.phase:
            parts.append(f"  Phase: {self.phase}")
        if self.cause:
            parts.append(f"  Caused by: {type(self.cause).__name__}: {self.cause}")
        return "\n".join(parts)


class PhaseGateError(PipelineError):
    """Raised when a phase returns None/empty (gate failure)."""


class ConfigurationError(PipelineError):
    """Raised on invalid configuration."""


class TokenizationError(PipelineError):
    """Raised when all tokenization strategies fail."""


class ImportRegistryError(PipelineError):
    """Raised when a required import is unavailable."""


class EmptyInputError(PipelineError):
    """Raised when no input text or file path was provided."""


class FileInputError(PipelineError):
    """Raised when a file path was given but the file is empty or unreadable."""


class ScoringContractError(PipelineError):
    """Raised when path_scores (or similar) violates the expected contract (e.g. non-float value)."""


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Import Registry (replaces scattered try/except import blocks)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class ImportResult:
    """Records the outcome of an import attempt."""
    name: str
    available: bool
    module: Optional[Any] = None
    error: Optional[str] = None
    strategy: str = "unknown"  # which import path succeeded


class ImportRegistry:
    """
    Centralised import manager.
    Records all import outcomes for diagnostic reporting.
    Provides a single source of truth for what's available.
    """
    _results: ClassVar[Dict[str, ImportResult]] = {}

    @classmethod
    def attempt(
        cls,
        name: str,
        strategies: List[Tuple[str, str]],  # [(module_path, attr_or_empty), ...]
        required: bool = False,
    ) -> Optional[Any]:
        """
        Try each strategy in order, return first success.
        strategies: list of (module_path, attribute) — attribute="" means import module itself.
        """
        errors: List[str] = []
        for module_path, attr in strategies:
            try:
                import importlib
                mod = importlib.import_module(module_path)
                imported = getattr(mod, attr) if attr else mod
                cls._results[name] = ImportResult(
                    name=name, available=True,
                    module=imported, strategy=f"{module_path}.{attr}" if attr else module_path,
                )
                log.debug("Import OK: %s via %s", name, module_path)
                return imported
            except (ImportError, AttributeError, ModuleNotFoundError) as exc:
                errors.append(f"{module_path}: {exc}")

        cls._results[name] = ImportResult(
            name=name, available=False,
            error="; ".join(errors), strategy="all_failed",
        )
        msg = f"Import failed for '{name}': {'; '.join(errors)}"
        if required:
            raise ImportRegistryError(msg)
        log.debug("Import unavailable: %s", name)
        return None

    @classmethod
    def get(cls, name: str) -> Optional[Any]:
        entry = cls._results.get(name)
        return entry.module if entry and entry.available else None

    @classmethod
    def is_available(cls, name: str) -> bool:
        entry = cls._results.get(name)
        return bool(entry and entry.available)

    @classmethod
    def diagnostic_report(cls) -> str:
        lines = ["Import Registry:"]
        for name, r in sorted(cls._results.items()):
            status = "✓" if r.available else "✗"
            detail = r.strategy if r.available else r.error
            lines.append(f"  {status} {name:40s} {detail}")
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Configuration
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class CorpusConfig:
    enabled: bool = False
    state_path: str = "output/corpus_state.json"
    reinforcement: float = 1.0
    decay_rate: float = 0.1
    T_atomic: float = 10.0
    theta_prune: float = 0.01
    prune_interval_docs: int = 10
    max_identities: int = 100_000
    max_edges: int = 500_000

    def validate(self) -> List[str]:
        errors = []
        if self.reinforcement <= 0:
            errors.append("corpus.reinforcement must be > 0")
        if not 0 < self.decay_rate < 1:
            errors.append("corpus.decay_rate must be in (0, 1)")
        if self.T_atomic <= 0:
            errors.append("corpus.T_atomic must be > 0")
        if self.max_identities < 1:
            errors.append("corpus.max_identities must be >= 1")
        return errors


@dataclass
class ClusteringConfig:
    """Thresholds for topology clustering — no more magic numbers."""
    high_pressure_min_attempts: int = 1     # attempts > this → high pressure
    medium_pressure_min_near_refusals: int = 5  # near_refusals > this → medium
    high_freedom_min_paths: int = 3         # escape_paths >= this → high freedom
    medium_freedom_paths: int = 2           # exactly this → medium
    concentrated_threshold: float = 1.0    # concentration == 1.0 → concentrated
    distributed_threshold: float = 0.5     # concentration < this → distributed


@dataclass
class GenerationConfig:
    method: str = "weighted_random"
    temperature: float = 0.7
    steps: int = 20
    num_sequences: int = 3
    fluency_length: int = 25
    fluency_seed: int = 42
    insert_sentence_breaks: bool = True
    max_preview_words: int = 15


@dataclass
class PipelineConfig:
    """
    Fully typed, validated configuration.
    Loaded from config/default.json + env overrides.
    """
    tokenization_method: str = "word"
    tokenization_methods: Optional[List[str]] = None  # When set, run pipeline for each (all 9).
    num_runs: int = 3
    continuation_text: str = "Tokens become actions. Patterns become residues."
    continuation_texts: Optional[List[str]] = None  # When set, run continuation observation for each.
    max_file_bytes: int = 50 * 1024 * 1024
    file_input_mode: str = "auto"
    learner_alpha: float = 0.05
    learner_bound: float = 1.0
    topology_max_steps: int = 200
    continuation_max_steps: int = 100
    emit_flamegraph: bool = False
    show_tui: bool = True
    async_mode: bool = False
    deterministic_mode: bool = False
    deterministic_seed: int = 42
    corpus: CorpusConfig = field(default_factory=CorpusConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    # When True and return_model_state=True, attach phase10_metrics (JSON dict) to model_state.
    include_phase10_metrics: bool = False
    # If True, Phase 10 counts only transitions licensed by Phase 3 undirected edges.
    phase10_cross_check_phase3: bool = False

    VALID_TOKENIZATION_METHODS: ClassVar[FrozenSet[str]] = frozenset({
        "whitespace", "space", "word", "character", "char",
        "grammar", "subword", "subword_bpe", "subword_syllable",
        "subword_frequency", "byte",
    })

    @staticmethod
    def _normalize_method(m: str) -> str:
        """Map config aliases (space, char) to canonical names."""
        if m == "space":
            return "whitespace"
        if m == "char":
            return "character"
        return m

    def validate(self) -> List[str]:
        errors: List[str] = []
        if self.tokenization_methods:
            for m in self.tokenization_methods:
                canonical = self._normalize_method(m)
                if canonical not in self.VALID_TOKENIZATION_METHODS:
                    errors.append(
                        f"tokenization_methods entry '{m}' not in {sorted(self.VALID_TOKENIZATION_METHODS)}"
                    )
                    break
        elif self.tokenization_method not in self.VALID_TOKENIZATION_METHODS:
            errors.append(
                f"tokenization_method '{self.tokenization_method}' not in "
                f"{sorted(self.VALID_TOKENIZATION_METHODS)}"
            )
        if self.num_runs < 1:
            errors.append("num_runs must be >= 1")
        if not 0 < self.learner_alpha < 1:
            errors.append("learner_alpha must be in (0, 1)")
        if self.topology_max_steps < 1:
            errors.append("topology_max_steps must be >= 1")
        if self.deterministic_seed < 0:
            errors.append("deterministic_seed must be >= 0")
        errors.extend(self.corpus.validate())
        return errors

    @classmethod
    def from_project(cls, config_override: Optional[Path] = None) -> "PipelineConfig":
        """Load from project config, env overrides, CLI flags."""
        cfg = cls()

        # Load from config file
        raw: Dict[str, Any] = {}
        try:
            from threshold_onset.config import load_config, get_config  # type: ignore
            if config_override:
                load_config(config_override)
            raw = get_config()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            log.debug("Config load failed (using defaults): %s", exc)

        # Merge pipeline section
        pipeline = raw.get("pipeline", {})
        for attr in ("tokenization_method", "tokenization_methods", "num_runs", "continuation_text",
                     "continuation_texts", "max_file_bytes", "file_input_mode",
                     "include_phase10_metrics", "phase10_cross_check_phase3"):
            if attr in pipeline:
                setattr(cfg, attr, pipeline[attr])

        # Merge corpus section
        corpus_raw = raw.get("corpus", {})
        for attr in dataclasses.fields(CorpusConfig):
            if attr.name in corpus_raw:
                setattr(cfg.corpus, attr.name, corpus_raw[attr.name])

        # Env overrides
        env_map = {
            "PIPELINE_TOKENIZATION_METHOD": ("tokenization_method", str),
            "PIPELINE_NUM_RUNS": ("num_runs", int),
            "PIPELINE_ASYNC": ("async_mode", lambda v: v.lower() in ("1", "true", "yes")),
            "PIPELINE_NO_TUI": ("show_tui", lambda v: v.lower() not in ("1", "true", "yes")),
            "PIPELINE_PROFILE": ("emit_flamegraph", lambda v: v.lower() in ("1", "true", "yes")),
            "PIPELINE_DETERMINISTIC": ("deterministic_mode", lambda v: v.lower() in ("1", "true", "yes")),
            "PIPELINE_DETERMINISTIC_SEED": ("deterministic_seed", int),
            "PIPELINE_PHASE10_METRICS": ("include_phase10_metrics", lambda v: v.lower() in ("1", "true", "yes")),
            "PIPELINE_PHASE10_CROSS_CHECK_PHASE3": (
                "phase10_cross_check_phase3",
                lambda v: v.lower() in ("1", "true", "yes"),
            ),
        }
        for env_key, (attr, cast) in env_map.items():
            val = os.environ.get(env_key)
            if val:
                try:
                    setattr(cfg, attr, cast(val))
                except (ValueError, TypeError) as e:
                    log.warning(
                        "Env override %s=%r ignored (invalid for %s): %s",
                        env_key, val, attr, e,
                    )

        return cfg

    def as_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Result Types
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class PhaseTimings:
    """Per-phase wall-clock timing."""
    phase0_ms: float = 0.0
    phase1_ms: float = 0.0
    phase2_ms: float = 0.0
    phase3_ms: float = 0.0
    phase4_ms: float = 0.0
    tokenization_ms: float = 0.0
    topology_ms: float = 0.0
    clustering_ms: float = 0.0
    scoring_ms: float = 0.0
    generation_ms: float = 0.0
    total_ms: float = 0.0

    def slowest(self, top_n: int = 3) -> List[Tuple[str, float]]:
        items = [
            (k.replace("_ms", ""), v)
            for k, v in dataclasses.asdict(self).items()
            if k != "total_ms"
        ]
        return sorted(items, key=lambda x: x[1], reverse=True)[:top_n]

    def as_flamegraph_lines(self, _run_id: str) -> List[str]:
        """Produce Brendan Gregg collapsed stack format for flamegraph.pl."""
        lines = []
        for k, v in dataclasses.asdict(self).items():
            if k != "total_ms":
                phase = k.replace("_ms", "")
                lines.append(f"pipeline;{phase} {int(v * 1000)}")
        return lines


@dataclass
class TopologyData:
    """Typed replacement for the untyped topology dict."""
    symbol: str
    appearances: int = 0
    self_transition_attempts: int = 0
    near_refusal_events: int = 0
    escape_paths: Counter = field(default_factory=Counter)
    distinct_escape_paths: int = 0
    escape_concentration: float = 0.0

    def compute_concentration(self) -> None:
        total = sum(self.escape_paths.values())
        if total == 0:
            self.escape_concentration = 0.0
            return
        probabilities = [c / total for c in self.escape_paths.values()]
        entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
        max_entropy = math.log2(len(self.escape_paths)) if len(self.escape_paths) > 1 else 0.0
        self.escape_concentration = (
            1.0 - entropy / max_entropy if max_entropy > 0 else 1.0
        )
        self.distinct_escape_paths = len(self.escape_paths)


@dataclass
class ClusterMember:
    symbol: str
    attempts: int
    near_refusals: int
    escape_paths: int
    concentration: float
    escape_targets: List[str]


@dataclass
class RefusalEvent:
    step_index: int
    current_symbol: str
    attempted_next_symbol: str
    reason: str
    relation_exists: bool

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class CorpusMetrics:
    identities_count: int = 0
    edges_count: int = 0
    doc_count: int = 0
    updated: bool = False


@dataclass
class PipelineResult:
    """
    Fully typed return value from run().
    Replaces the ad-hoc dict returned by v1.
    """
    run_id: str
    input_text: str
    input_type: str                   # "text" | "binary" | "file"
    tokens: List[str]
    generated_outputs: List[str]
    token_count: int
    identity_count: int
    relation_count: int
    refusal_count: int
    all_self_refusals: bool
    topology: Dict[str, TopologyData]
    clusters: Dict[str, List[ClusterMember]]
    scored_path_count: int
    symbol_mapping_count: int
    corpus: CorpusMetrics
    timings: PhaseTimings
    config: PipelineConfig
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    # Optional state for predict-next evaluation (set when run(..., return_model_state=True))
    model_state: Optional[Dict[str, Any]] = None

    @property
    def succeeded(self) -> bool:
        return len(self.errors) == 0 # and len(self.generated_outputs) > 0

    def summary(self) -> str:
        lines = [
            f"Run ID:           {self.run_id}",
            f"Status:           {'OK' if self.succeeded else 'FAILED'}",
            f"Tokens:           {self.token_count}",
            f"Identities:       {self.identity_count}",
            f"Relations:        {self.relation_count}",
            f"Refusals:         {self.refusal_count}",
            f"Topology nodes:   {len(self.topology)}",
            f"Clusters:         {len(self.clusters)}",
            f"Scored paths:     {self.scored_path_count}",
            f"Outputs:          {len(self.generated_outputs)}",
            f"Total time:       {self.timings.total_ms:.1f}ms",
            "Slowest phases:   " + ", ".join(
                f"{p}={ms:.0f}ms" for p, ms in self.timings.slowest(3)
            ),
        ]
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Phase Timer (profiling)
# ══════════════════════════════════════════════════════════════════════════════

class PhaseTimer:
    """Context manager for timing pipeline phases."""

    def __init__(self, name: str, timings: PhaseTimings) -> None:
        self._name = name
        self._timings = timings
        self._t0: float = 0.0

    def __enter__(self) -> "PhaseTimer":
        self._t0 = time.perf_counter()
        return self

    def __exit__(self, *_: Any) -> None:
        elapsed_ms = (time.perf_counter() - self._t0) * 1000.0
        attr = f"{self._name}_ms"
        if hasattr(self._timings, attr):
            setattr(self._timings, attr, elapsed_ms)
        log.debug("Phase %s: %.2fms", self._name, elapsed_ms)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — Token Action (with LRU cache)
# ══════════════════════════════════════════════════════════════════════════════

@functools.lru_cache(maxsize=8192)
def _token_to_residue(token: str) -> float:
    """
    Convert token string to residue float.
    LRU-cached: sha256 computed once per unique token, not on every call.
    Pure function — safe to cache.
    """
    token_bytes = token.encode("utf-8")
    hash_int = int(hashlib.sha256(token_bytes).hexdigest()[:8], 16)
    return float(hash_int % 10000) / 10000.0


class TokenAction:
    """
    Converts text tokens into Phase 0 actions.

    Improvements over v1:
      - Uses LRU-cached _token_to_residue (no redundant sha256 computation)
      - Wrap-around is explicit and logged, not silent
      - Provides __len__ and __iter__ for introspection
      - reset() method for explicit state management
    """

    def __init__(self, tokens: Sequence[str]) -> None:
        self._tokens: Tuple[str, ...] = tuple(tokens)
        self._index: int = 0
        self._wrap_count: int = 0

    def __call__(self) -> float:
        if not self._tokens:
            return 0.0
        if self._index >= len(self._tokens):
            self._index = 0
            self._wrap_count += 1
            log.debug("TokenAction wrapped (count=%d)", self._wrap_count)
        token = self._tokens[self._index]
        self._index += 1
        return _token_to_residue(token)

    def __len__(self) -> int:
        return len(self._tokens)

    def __iter__(self) -> Iterator[float]:
        for token in self._tokens:
            yield _token_to_residue(token)

    def reset(self) -> None:
        self._index = 0

    @property
    def position(self) -> int:
        return self._index

    @property
    def wrap_count(self) -> int:
        return self._wrap_count

    def residue_map(self) -> Dict[str, float]:
        """Return deterministic {token: residue} mapping for all tokens."""
        return {t: _token_to_residue(t) for t in self._tokens}


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — Tokenization (multi-strategy with ImportRegistry)
# ══════════════════════════════════════════════════════════════════════════════

# Eagerly register available tokenizers (once, at module load)
def _register_tokenizers() -> None:
    ImportRegistry.attempt(
        "santok.core_functions",
        [
            ("santok", "tokenize_space"),
            ("santok.core", "tokenize_space"),
        ],
    )
    ImportRegistry.attempt(
        "santok.tokenize_text",
        [("santok", "tokenize_text")],
    )
    ImportRegistry.attempt(
        "santok_complete",
        [("santok_complete.core.core_tokenizer", "tokenize_text")],
    )


_register_tokenizers()


def _token_strings_nonempty(strings: List[str]) -> bool:
    """True if at least one extracted token string is non-empty."""
    return any(bool(s) for s in strings)


def tokenize_text(text: str, method: str = "word") -> List[str]:
    """
    Tokenize text using best available strategy, with full fallback chain.
    Raises TokenizationError only if all strategies fail AND text is non-empty.
    """
    if not text:
        return []

    errors: List[str] = []

    # Strategy 1: santok direct function imports
    try:
        import santok  # type: ignore
        fns = {
            "space": getattr(santok, "tokenize_space", None),
            "whitespace": getattr(santok, "tokenize_space", None),
            "word": getattr(santok, "tokenize_word", None),
            "character": getattr(santok, "tokenize_char", None),
            "char": getattr(santok, "tokenize_char", None),
            "grammar": getattr(santok, "tokenize_grammar", None),
            "subword": getattr(santok, "tokenize_subword", None),
            "subword_bpe": getattr(santok, "tokenize_subword", None),
            "subword_syllable": getattr(santok, "tokenize_subword", None),
            "subword_frequency": getattr(santok, "tokenize_subword", None),
            "byte": getattr(santok, "tokenize_bytes", None),
        }
        fn = fns.get(method)
        if fn is not None:
            if method in ("subword", "subword_bpe", "subword_syllable", "subword_frequency"):
                strategy_map = {
                    "subword": "fixed",
                    "subword_bpe": "bpe",
                    "subword_syllable": "syllable",
                    "subword_frequency": "frequency",
                }
                strat = strategy_map[method]
                tokens = []
                for chunk_len in range(10):
                    tokens.extend(fn(text, chunk_len=chunk_len, strategy=strat))
            else:
                tokens = fn(text)
            out = _extract_token_strings(tokens)
            if _token_strings_nonempty(out):
                return out
    except Exception as exc:  # pylint: disable=broad-exception-caught
        errors.append(f"santok direct: {exc}")

    # Strategy 2: santok.tokenize_text unified API
    try:
        from santok import tokenize_text as _santok_tt  # type: ignore
        tok_result = _santok_tt(text, tokenization_method=method)
        tokens = tok_result.get("tokens", []) if isinstance(tok_result, dict) else tok_result
        out = _extract_token_strings(tokens)
        if _token_strings_nonempty(out):
            return out
    except Exception as exc:  # pylint: disable=broad-exception-caught
        errors.append(f"santok.tokenize_text: {exc}")

    # Strategy 3: santok_complete in-tree
    try:
        from santok_complete.core.core_tokenizer import tokenize_text as _sc_tt  # type: ignore
        method_mapped = {"whitespace": "space", "character": "char"}.get(method, method)
        tokens = _sc_tt(text, tokenizer_type=method_mapped)
        out = _extract_token_strings(tokens)
        if _token_strings_nonempty(out):
            return out
    except Exception as exc:  # pylint: disable=broad-exception-caught
        errors.append(f"santok_complete: {exc}")

    # Strategy 4: stdlib fallback (whitespace split — always available)
    log.warning(
        "All tokenizers unavailable (%s), using stdlib split. Errors: %s",
        method, "; ".join(errors)
    )
    return text.split()


def _extract_token_strings(tokens: List[Any]) -> List[str]:
    """Normalise token list: extract string from dict/object/str."""
    out = []
    for token in tokens:
        if isinstance(token, str):
            out.append(token)
        elif isinstance(token, dict):
            out.append(token.get("text", str(token)))
        else:
            out.append(str(token))
    return out


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — Phase Runner Protocol
# ══════════════════════════════════════════════════════════════════════════════

@runtime_checkable
class PhaseRunner(Protocol):
    """
    Protocol defining the interface every phase must satisfy.
    Enables dependency injection and testing with mock phases.
    The method bodies are intentionally omitted (Protocol contract only);
    DefaultPhaseRunners and phase0–4 modules provide the real implementations.
    """
    name: str

    def run(self, *args: Any, **kwargs: Any) -> Any:
        ...  # Implemented by phase0–4 (or mocks in tests)

    def validate_output(self, output: Any) -> bool:
        ...  # Optional; used by tests to gate phase output


@dataclass
class PhaseRunnerBase:
    """Mixin providing common phase machinery."""
    name: str

    def gate_check(self, output: Any, _field_name: str = "") -> None:
        """Raise PhaseGateError if output fails basic validity."""
        if output is None:
            raise PhaseGateError(f"Phase {self.name} returned None", phase=self.name)
        if isinstance(output, dict) and not output:
            raise PhaseGateError(
                f"Phase {self.name} returned empty dict", phase=self.name
            )


class DefaultPhaseRunners:
    """
    Wraps the real threshold_onset phase functions behind the PhaseRunner protocol.
    Lazily imported to avoid circular dependency at module load time.
    """

    @staticmethod
    def phase0() -> Callable:
        from threshold_onset.phase0.phase0 import phase0  # type: ignore
        return phase0

    @staticmethod
    def phase1() -> Callable:
        from threshold_onset.phase1.phase1 import phase1  # type: ignore
        return phase1

    @staticmethod
    def phase2() -> Callable:
        from threshold_onset.phase2.phase2 import phase2_multi_run  # type: ignore
        return phase2_multi_run

    @staticmethod
    def phase3() -> Callable:
        from threshold_onset.phase3.phase3 import phase3_multi_run  # type: ignore
        return phase3_multi_run

    @staticmethod
    def phase4() -> Callable:
        from threshold_onset.phase4.phase4 import phase4  # type: ignore
        return phase4


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — Continuation Observer (refactored)
# ══════════════════════════════════════════════════════════════════════════════

class ContinuationObserver:
    """
    Observes continuation after Phase 4 and records refusals.

    v2 improvements:
      - Uses typed RefusalEvent instead of dict
      - Residue→identity mapping extracted as a public method
      - Adjacency building uses frozenset edge keys (order-invariant)
      - All internal methods are public (no more _private access from outside)
    """

    def __init__(
        self,
        phase4_output: Dict[str, Any],
        phase3_metrics: Dict[str, Any],
        phase2_metrics: Dict[str, Any],
    ) -> None:
        self._identity_to_symbol: Dict[str, str] = phase4_output.get("identity_to_symbol", {})
        self._symbol_to_identity: Dict[str, str] = phase4_output.get("symbol_to_identity", {})
        self._graph_nodes: Set[str] = phase3_metrics.get("graph_nodes", set())
        self._graph_edges: Set[Any] = phase3_metrics.get("graph_edges", set())
        self._identity_mappings: Dict[str, str] = phase2_metrics.get("identity_mappings", {})
        self._persistent_hashes: List[str] = phase2_metrics.get("persistent_segment_hashes", [])
        self._adjacency: Dict[str, Set[str]] = self._build_adjacency()
        self._identity_list: List[str] = self._build_identity_list()
        self.refusals: List[RefusalEvent] = []

    def _build_adjacency(self) -> Dict[str, Set[str]]:
        adj: Dict[str, Set[str]] = {node: set() for node in self._graph_nodes}
        for edge in self._graph_edges:
            if len(edge) == 2:
                h1, h2 = edge
                adj.setdefault(h1, set()).add(h2)
                adj.setdefault(h2, set()).add(h1)
        return adj

    def _build_identity_list(self) -> List[str]:
        identity_hashes: Set[str] = set()
        for seg_hash in self._persistent_hashes:
            mapped = self._identity_mappings.get(seg_hash)
            if mapped:
                identity_hashes.add(mapped)
        identity_hashes.update(self._identity_mappings.values())
        return sorted(identity_hashes)

    def residue_to_identity(self, residue: float) -> Optional[str]:
        if not self._identity_list:
            return None
        idx = int(abs(residue * 10000)) % len(self._identity_list)
        return self._identity_list[idx]

    def identity_to_symbol(self, identity_hash: str) -> Optional[str]:
        return self._identity_to_symbol.get(identity_hash)

    def transition_allowed(self, from_hash: str, to_hash: str) -> bool:
        return to_hash in self._adjacency.get(from_hash, set())

    def observe_continuation(
        self, continuation_tokens: Sequence[str], max_steps: int = 100
    ) -> List[RefusalEvent]:
        self.refusals = []
        action = TokenAction(list(continuation_tokens))
        current_id: Optional[str] = None
        current_sym: Optional[str] = None

        for step in range(min(max_steps, len(continuation_tokens))):
            residue = action()
            next_id = self.residue_to_identity(residue)
            if next_id is None:
                continue
            next_sym = self.identity_to_symbol(next_id)
            if next_sym is None:
                continue

            if current_id is not None:
                if not self.transition_allowed(current_id, next_id):
                    self.refusals.append(RefusalEvent(
                        step_index=step,
                        current_symbol=current_sym,  # type: ignore[arg-type]
                        attempted_next_symbol=next_sym,
                        reason="no_persistent_relation",
                        relation_exists=next_id in self._adjacency.get(current_id, set()),
                    ))
                    continue

            current_id = next_id
            current_sym = next_sym

        return self.refusals


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 11 — Topology Analyzer (replaces free function)
# ══════════════════════════════════════════════════════════════════════════════

class TopologyAnalyzer:
    """
    Measures escape topology per identity/symbol.

    v2 improvements:
      - Uses typed TopologyData instead of nested string-keyed dict
      - Fully encapsulated — no protected method access from outside
      - Configurable max_steps
      - Returns Dict[str, TopologyData] instead of Dict[str, dict]
    """

    def __init__(self, observer: ContinuationObserver, max_steps: int = 200) -> None:
        self._observer = observer
        self._max_steps = max_steps

    def measure(self, continuation_tokens: Sequence[str]) -> Dict[str, TopologyData]:
        tokens_list = list(continuation_tokens)
        action = TokenAction(tokens_list)

        topology: Dict[str, TopologyData] = {}
        current_id: Optional[str] = None
        current_sym: Optional[str] = None

        for _ in range(min(self._max_steps, len(tokens_list) * 3)):
            residue = action()
            next_id = self._observer.residue_to_identity(residue)
            if next_id is None:
                continue
            next_sym = self._observer.identity_to_symbol(next_id)
            if next_sym is None:
                continue

            if next_sym not in topology:
                topology[next_sym] = TopologyData(symbol=next_sym)
            topology[next_sym].appearances += 1

            if current_sym is not None:
                topology[current_sym].near_refusal_events += 1
                if current_sym == next_sym:
                    topology[current_sym].self_transition_attempts += 1
                else:
                    topology[current_sym].escape_paths[next_sym] += 1

            if current_id != next_id:
                current_id = next_id
                current_sym = next_sym

        # Compute derived metrics
        for td in topology.values():
            td.compute_concentration()

        return topology


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 12 — Topology Clustering (config-driven)
# ══════════════════════════════════════════════════════════════════════════════

class TopologyClusterer:
    """
    Clusters identities by escape topology.

    v2 improvements:
      - Thresholds from ClusteringConfig (no magic numbers)
      - Returns typed ClusterMember list
      - Cluster keys are stable enums, not fragile f-strings
    """

    def __init__(self, cfg: ClusteringConfig) -> None:
        self._cfg = cfg

    def _pressure(self, td: TopologyData) -> str:
        if td.self_transition_attempts > self._cfg.high_pressure_min_attempts - 1:
            return "high"
        if td.near_refusal_events > self._cfg.medium_pressure_min_near_refusals:
            return "medium"
        return "low"

    def _freedom(self, td: TopologyData) -> str:
        if td.distinct_escape_paths >= self._cfg.high_freedom_min_paths:
            return "high"
        if td.distinct_escape_paths == self._cfg.medium_freedom_paths:
            return "medium"
        return "low"

    def _concentration_type(self, td: TopologyData) -> str:
        if td.escape_concentration >= self._cfg.concentrated_threshold:
            return "concentrated"
        if td.escape_concentration < self._cfg.distributed_threshold:
            return "distributed"
        return "mixed"

    def cluster(
        self, topology: Dict[str, TopologyData]
    ) -> Dict[str, List[ClusterMember]]:
        clusters: Dict[str, List[ClusterMember]] = defaultdict(list)
        for symbol, td in topology.items():
            key = (
                f"{self._pressure(td)}_pressure_"
                f"{self._freedom(td)}_freedom_"
                f"{self._concentration_type(td)}"
            )
            clusters[key].append(ClusterMember(
                symbol=symbol,
                attempts=td.self_transition_attempts,
                near_refusals=td.near_refusal_events,
                escape_paths=td.distinct_escape_paths,
                concentration=td.escape_concentration,
                escape_targets=list(td.escape_paths.keys()),
            ))
        return dict(clusters)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 13 — Path Scoring (thin typed wrapper)
# ══════════════════════════════════════════════════════════════════════════════

def _load_scoring() -> Tuple[Callable, Callable]:
    """Load scoring functions with clear error on failure."""
    try:
        from integration.scoring import score_allowed_paths, rank_paths_from_symbol  # type: ignore
        return score_allowed_paths, rank_paths_from_symbol
    except ImportError as exc:
        raise ImportRegistryError(
            "integration.scoring not found — required for path scoring",
            cause=exc,
        ) from exc


def choose_next_path(
    from_symbol: str,
    path_scores: Dict[Any, float],
    method: str = "highest_score",
    *,
    rank_fn: Callable,
) -> Optional[str]:
    """
    Choose next path from a symbol based on scoring.

    v2: rank_fn is injected (testable), method validated.
    """
    ranked = rank_fn(from_symbol, path_scores)
    if not ranked:
        return None

    if method == "highest_score":
        return ranked[0][0]

    if method == "weighted_random":
        symbols = [s for s, _ in ranked]
        scores = [max(0.0, sc) for _, sc in ranked]
        total = sum(scores)
        if total == 0:
            return random.choice(symbols)
        return random.choices(symbols, weights=[s / total for s in scores], k=1)[0]

    # Default
    return ranked[0][0]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 14 — Surface Mapping
# ══════════════════════════════════════════════════════════════════════════════

def build_surface_mapping(
    tokens: List[str],
    residue_sequences: List[List[float]],
    phase2_metrics: Dict[str, Any],
    phase4_metrics: Dict[str, Any],
    token_to_residue_map: Dict[str, float],
) -> Dict[str, str]:
    """
    Build symbol → token mapping with cascading fallbacks.
    v2: explicit fallback chain, typed, logged.
    """
    # Strategy 1: structural decoder (preferred)
    try:
        from threshold_onset.semantic.phase9.symbol_decoder import (  # type: ignore
            build_structural_decoder,
        )
        mapping_result = build_structural_decoder(
            tokens, residue_sequences, phase2_metrics, phase4_metrics
        )
        if mapping_result:
            log.debug(
                "Surface mapping: structural decoder (%d mappings)",
                len(mapping_result),
            )
            return mapping_result
    except Exception as exc:  # pylint: disable=broad-exception-caught
        log.debug("Structural decoder failed: %s", exc)

    # Strategy 2: integration.surface fallback
    try:
        from integration.surface import build_symbol_to_token_mapping  # type: ignore
        mapping_result = build_symbol_to_token_mapping(
            tokens, phase4_metrics, phase2_metrics,
            residue_sequences, token_to_residue_map,
        )
        if mapping_result:
            log.debug(
                "Surface mapping: integration.surface (%d mappings)",
                len(mapping_result),
            )
            return mapping_result
    except Exception as exc:  # pylint: disable=broad-exception-caught
        log.debug("integration.surface failed: %s", exc)

    # Strategy 3: direct residue → token via deterministic hash
    log.warning("Surface mapping: falling back to direct hash mapping")
    fallback_map: Dict[str, str] = {}
    identity_to_symbol = phase4_metrics.get("identity_to_symbol", {})
    identity_mappings = phase2_metrics.get("identity_mappings", {})
    reverse_map: Dict[str, str] = {v: k for k, v in identity_mappings.items()}
    for identity_hash, symbol in identity_to_symbol.items():
        seg_hash = reverse_map.get(identity_hash)
        if seg_hash:
            token_idx = int(seg_hash[:4], 16) % len(tokens) if tokens else 0
            fallback_map[symbol] = tokens[token_idx]
    return fallback_map


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 15 — Corpus Manager
# ══════════════════════════════════════════════════════════════════════════════

class CorpusManager:
    """
    Encapsulates all corpus state logic previously buried in main().

    v2: single responsibility, typed metrics, clean save/load.
    """

    def __init__(self, cfg: CorpusConfig, project_root: Path) -> None:
        self._cfg = cfg
        self._root = project_root
        self._state: Optional[Any] = None
        self._enabled = cfg.enabled

    @property
    def enabled(self) -> bool:
        return self._enabled

    def initialize(self) -> bool:
        """Load or create corpus state. Returns True if successful."""
        if not self._enabled:
            return False
        try:
            from threshold_onset.corpus_state import CorpusState  # type: ignore
            state_path = self._resolve_path(self._cfg.state_path)
            if state_path.exists():
                self._state = CorpusState.load(state_path, **dataclasses.asdict(self._cfg))
                log.info("Loaded corpus state from %s", state_path)
            else:
                self._state = CorpusState(
                    reinforcement=self._cfg.reinforcement,
                    decay_rate=self._cfg.decay_rate,
                    T_atomic=self._cfg.T_atomic,
                    theta_prune=self._cfg.theta_prune,
                    prune_interval_docs=self._cfg.prune_interval_docs,
                    max_identities=self._cfg.max_identities,
                    max_edges=self._cfg.max_edges,
                )
            return True
        except Exception as exc:  # pylint: disable=broad-exception-caught
            log.warning("Corpus state init failed (disabling): %s", exc)
            self._enabled = False
            return False

    def update_and_save(
        self,
        identity_hashes: Set[str],
        edge_pairs: Set[Any],
    ) -> CorpusMetrics:
        """Update state with new document's identities and edges, then persist."""
        if not self._enabled or self._state is None:
            return CorpusMetrics()
        try:
            self._state.update(identity_hashes, edge_pairs)
            state_path = self._resolve_path(self._cfg.state_path)
            self._state.save(state_path)
            m = self._state.metrics()
            return CorpusMetrics(
                identities_count=m.get("corpus_identities_count", 0),
                edges_count=m.get("corpus_edges_count", 0),
                doc_count=m.get("corpus_doc_count", 0),
                updated=True,
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            log.error("Corpus save failed: %s", exc)
            return CorpusMetrics()

    def _resolve_path(self, path_str: str) -> Path:
        p = Path(path_str)
        return p if p.is_absolute() else self._root / p


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 16 — Generation Pipeline
# ══════════════════════════════════════════════════════════════════════════════

class GenerationPipeline:
    """
    Encapsulates text generation logic previously scattered in main().

    v2: injectable learner, typed config, clear output contract.
    """

    def __init__(self, cfg: GenerationConfig) -> None:
        self._cfg = cfg

    def generate(  # pylint: disable=unused-argument
        self,
        tokens: List[str],
        residue_sequences: List[List[float]],
        phase2_metrics: Dict[str, Any],
        phase3_metrics: Dict[str, Any],
        phase4_metrics: Dict[str, Any],
        topology: Dict[str, TopologyData],
        path_scores: Dict[Any, float],
        symbol_to_token: Dict[str, str],
        learner: Any,
        score_fn: Callable,
        rank_fn: Callable,
    ) -> List[str]:
        """
        Generate text sequences. Returns list of text strings.

        Fluency generator (if available) is run first and prepended to outputs.
        Symbol-walk generation uses path_scores and learner; topology/score_fn/
        rank_fn are accepted for API consistency (scoring is done in run()).
        """
        from integration.generate import generate_sequence  # type: ignore
        from integration.surface import symbols_to_text  # type: ignore

        outputs: List[str] = []

        # Fluency generator path (Phase 5-9): when available, prepend to outputs
        try:
            from integration.fluency_text_generator import generate_text_via_fluency  # type: ignore
            fluency_text = generate_text_via_fluency(
                tokens, residue_sequences, phase2_metrics,
                phase3_metrics, phase4_metrics,
                length=self._cfg.fluency_length,
                seed=self._cfg.fluency_seed,
            )
            if fluency_text and fluency_text.strip():
                outputs.append(fluency_text.strip())
                log.debug("FluencyGenerator: %s", fluency_text[:60])
        except Exception as exc:  # pylint: disable=broad-exception-caught
            log.debug("FluencyGenerator skipped: %s", exc)

        # Determine start symbols: prefer token matching first input word
        all_symbols = list(phase4_metrics.get("identity_to_symbol", {}).values())
        first_token = tokens[0] if tokens else None
        first_symbol = next(
            (s for s, t in symbol_to_token.items() if t == first_token), None
        )
        candidates = (
            ([first_symbol] if first_symbol else [])
            + [s for s in all_symbols[:4] if s != first_symbol][:2]
        )
        start_symbols = candidates[: self._cfg.num_sequences]

        for start_symbol in start_symbols:
            try:
                symbol_sequence = generate_sequence(
                    start_symbol=start_symbol,
                    steps=self._cfg.steps,
                    phase4_output=phase4_metrics,
                    phase3_metrics=phase3_metrics,
                    phase2_metrics=phase2_metrics,
                    path_scores=path_scores,
                    method=self._cfg.method,
                    temperature=self._cfg.temperature,
                    learner=learner,
                )
                text_out = symbols_to_text(
                    symbol_sequence,
                    symbol_to_token,
                    insert_sentence_breaks=self._cfg.insert_sentence_breaks,
                )
                outputs.append(text_out)
                # Guard: only step learner if it has a step() method
                if hasattr(learner, "step") and callable(learner.step):
                    learner.step()
            except Exception as exc:  # pylint: disable=broad-exception-caught
                log.warning("Generation failed for symbol %s: %s", start_symbol, exc)

        return outputs


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 17 — Input Handler
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class InputResult:
    text: str
    input_type: str  # "text" | "binary" | "file"
    from_file: bool
    source_path: Optional[Path] = None


def _prompt_interactive_input() -> str:
    """
    Prompt the user for text in an interactive terminal.
    Uses shared integration.interactive_prompt when available.
    """
    try:
        from integration.interactive_prompt import prompt_text
        return prompt_text(
            "Enter your text (or path to a file).",
            prompt_line="> ",
            continuation="... ",
        )
    except ImportError:
        _safe_print("\nEnter your text (or path to a file). Press Enter twice when done.\n")
        lines = []
        try:
            while True:
                line = input("> " if not lines else "... ")
                if line == "" and lines:
                    break
                if line != "":
                    lines.append(line)
        except EOFError:
            pass
        return "\n".join(lines).strip() if lines else ""


def resolve_input(
    raw_input: str,
    cfg: PipelineConfig,
    project_root: Path,
) -> InputResult:
    """
    Resolve raw input string to actual text content.
    Handles: plain text, file paths (all types via universal_input).
    """
    if not raw_input:
        raise EmptyInputError("Empty input — provide text or a file path")

    try:
        from threshold_onset.universal_input import (  # type: ignore
            is_file_path,
            file_to_input_string,
        )
        if is_file_path(raw_input, project_root):
            path = Path(raw_input)
            path = (project_root / path).resolve() if not path.is_absolute() else path
            text, input_type = file_to_input_string(
                path,
                mode=cfg.file_input_mode,
                max_bytes=cfg.max_file_bytes,
            )
            if not text:
                raise FileInputError(f"File empty or unreadable: {path}", cause=None)
            log.info("Loaded file %s (type=%s)", path, input_type)
            return InputResult(text=text, input_type=input_type, from_file=True, source_path=path)
    except (ImportError, FileNotFoundError, ValueError) as exc:
        log.debug("File resolution skipped: %s", exc)

    return InputResult(text=raw_input, input_type="text", from_file=False)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 18 — Rich TUI Renderer
# ══════════════════════════════════════════════════════════════════════════════

class TUIRenderer:
    """
    Renders pipeline progress and results using Rich (or plain text fallback).
    v2: decoupled from pipeline logic entirely.
    """

    def __init__(self, show_tui: bool = True) -> None:
        self._enabled = show_tui and HAS_RICH
        self._console = _CONSOLE if self._enabled else None

    def header(self) -> None:
        if self._enabled and self._console:
            self._console.print(Panel(
                Text("COMPLETE UNIFIED PIPELINE  ·  v2.0\n"
                     "threshold_onset ↔ santok\n"
                     "कार्य (kārya) happens before ज्ञान (jñāna)",
                     justify="center", style="bold white"),
                style="on #0d1529", expand=False,
            ))
        else:
            _safe_print("\n" + "=" * 70)
            _safe_print("COMPLETE UNIFIED PIPELINE  v2.0")
            _safe_print("threshold_onset <-> santok")
            _safe_print("Action before knowledge")
            _safe_print("=" * 70)

    def phase_start(self, name: str, detail: str = "") -> None:
        if self._enabled and self._console:
            self._console.print(f"[bold cyan]▶ {name}[/bold cyan]"
                                + (f"  [dim]{detail}[/dim]" if detail else ""))
        else:
            _safe_print(f"\n{'=' * 70}\n{name}" + (f"\n{detail}" if detail else ""))

    def phase_ok(self, name: str, metrics: Dict[str, Any]) -> None:
        parts = "  ".join(f"[green]{k}[/green]=[bold]{v}[/bold]" for k, v in metrics.items())
        if self._enabled and self._console:
            self._console.print(f"  [green]✓[/green] {name}  {parts}")
        else:
            plain = "  ".join(f"{k}={v}" for k, v in metrics.items())
            _safe_print(f"  [OK] {name}  {plain}")

    def phase_warn(self, msg: str) -> None:
        if self._enabled and self._console:
            self._console.print(f"  [yellow]⚠  {msg}[/yellow]")
        else:
            _safe_print(f"  [WARN] {msg}")

    def phase_fail(self, name: str, error: str) -> None:
        if self._enabled and self._console:
            self._console.print(f"  [red]✗ {name}: {error}[/red]")
        else:
            _safe_print(f"  [FAIL] {name}: {error}")

    def section(self, title: str) -> None:
        if self._enabled and self._console:
            self._console.rule(f"[bold]{title}[/bold]")
        else:
            _safe_print(f"\n{'─' * 70}\n{title}\n{'─' * 70}")

    def result_table(self, pipeline_result: "PipelineResult") -> None:
        """Render the final summary table."""
        if self._enabled and self._console:
            tbl = Table(
                box=box.ROUNDED,
                title="[bold white]◈  PIPELINE RESULT  ◈[/bold white]",
                title_style="bold white",
                show_header=True,
                header_style="bold cyan",
            )
            tbl.add_column("Metric", style="dim white", width=28)
            tbl.add_column("Value", style="bold white", justify="right")

            rows = [
                ("Run ID", pipeline_result.run_id),
                (
                    "Status",
                    "[green]OK[/green]" if pipeline_result.succeeded else "[red]FAILED[/red]",
                ),
                ("Tokens", str(pipeline_result.token_count)),
                ("Identities", str(pipeline_result.identity_count)),
                ("Relations", str(pipeline_result.relation_count)),
                ("Refusals", str(pipeline_result.refusal_count)),
                ("Topology nodes", str(len(pipeline_result.topology))),
                ("Clusters", str(len(pipeline_result.clusters))),
                ("Scored paths", str(pipeline_result.scored_path_count)),
                ("Outputs", str(len(pipeline_result.generated_outputs))),
                ("Total time", f"{pipeline_result.timings.total_ms:.1f}ms"),
            ]
            for slowest_phase, ms in pipeline_result.timings.slowest(3):
                rows.append((f"  ↳ {slowest_phase}", f"{ms:.0f}ms"))

            for k, v in rows:
                tbl.add_row(k, v)

            self._console.print()
            self._console.print(tbl)
        else:
            _safe_print("\n" + "=" * 70 + "\nFINAL RESULT")
            _safe_print(pipeline_result.summary())
            _safe_print("=" * 70)

    def end_user_result(self, pipeline_result: "PipelineResult", max_width: int = 70) -> None:
        """Print the end-user facing output."""
        _safe_print()
        _safe_print("=" * (max_width + 4))
        _safe_print("  END USER RESULT")
        _safe_print("=" * (max_width + 4))
        _safe_print()
        _safe_print("  INPUT:")
        _safe_print("  " + "-" * max_width)
        for line in textwrap.wrap(pipeline_result.input_text.strip(), max_width):
            _safe_print("  " + line)
        _safe_print()
        _safe_print("  STRUCTURAL WALK (your words, no consecutive repeats):")
        _safe_print("  " + "-" * max_width)
        if pipeline_result.generated_outputs:
            primary = _format_output(pipeline_result.generated_outputs[0])
            for block in primary.split("\n"):
                for line in textwrap.wrap(block, max_width):
                    _safe_print("  " + line)
            if len(pipeline_result.generated_outputs) > 1:
                _safe_print()
                _safe_print("  Variations:")
                for i, out in enumerate(pipeline_result.generated_outputs[1:3], 2):
                    _safe_print(f"    {i}. {_format_output(out)}")
        else:
            _safe_print("    (no output)")
        _safe_print()
        _safe_print("=" * (max_width + 4))


def _format_output(text: str, max_words: Optional[int] = None) -> str:
    """Capitalise, truncate to max_words if given, add terminal punctuation."""
    words = text.split()
    if max_words and len(words) > max_words:
        text = " ".join(words[:max_words]) + "..."
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text and not text.endswith((".", "!", "?", "...")):
        text = text.rstrip() + "."
    return text


def _safe_print(msg: str = "") -> None:
    """Print with ASCII fallback for environments that can't handle Unicode."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 19 — Core Pipeline Executor
# ══════════════════════════════════════════════════════════════════════════════

def _run_structure_emergence(
    tokens: List[str],
    cfg: PipelineConfig,
    timings: PhaseTimings,
    tui: TUIRenderer,
) -> Tuple[
    List[List[float]],       # residue_sequences
    List[Dict[str, Any]],    # phase1_metrics_list
    Dict[str, Any],          # phase2_metrics
    Dict[str, Any],          # phase3_metrics
    Dict[str, Any],          # phase4_metrics
    Dict[str, float],        # token_to_residue_map
    List[List[float]],       # phase0_residues_by_run (for surface mapping)
]:
    """
    Runs Phases 0-4 in multi-run mode.
    Extracted from main() into its own function for clarity and testability.
    """
    # Lazy import phase functions
    phase0_fn = DefaultPhaseRunners.phase0()
    phase1_fn = DefaultPhaseRunners.phase1()
    phase2_fn = DefaultPhaseRunners.phase2()
    phase3_fn = DefaultPhaseRunners.phase3()
    phase4_fn = DefaultPhaseRunners.phase4()

    residue_sequences: List[List[float]] = []
    phase1_metrics_list: List[Dict[str, Any]] = []
    phase0_residues_by_run: List[List[float]] = []
    token_to_residue_map: Dict[str, float] = {}

    tui.section("STEP 2: STRUCTURE EMERGENCE (Phases 0-4)")

    if cfg.num_runs < 2:
        log.warning(
            "num_runs=%d — Phase 2 persistence requires >=2 runs. "
            "Set THRESHOLD_ONSET_NUM_RUNS=3 (or PIPELINE_NUM_RUNS=3) to avoid 'all methods failed'.",
            cfg.num_runs,
        )

    for run_num in range(cfg.num_runs):
        action = TokenAction(tokens)
        steps = len(tokens) * 2

        # Build token→residue map on first run (deterministic hash, run-independent)
        if run_num == 0:
            token_to_residue_map = action.residue_map()

        # Phase 0
        with PhaseTimer("phase0", timings):
            residues: List[float] = []
            for residue, _count, _step_count in phase0_fn([action], steps=steps):
                residues.append(residue)

        residue_sequences.append(residues)
        phase0_residues_by_run.append(residues)

        # Phase 1
        with PhaseTimer("phase1", timings):
            phase1_metrics = phase1_fn(residues)
        phase1_metrics_list.append(phase1_metrics)

        tui.phase_ok(
            f"Run {run_num + 1}/{cfg.num_runs}",
            {
                "residues": len(residues),
                "unique": len(set(residues)),
                "clusters": phase1_metrics["cluster_count"],
                "reps": phase1_metrics["repetition_count"],
            },
        )

    # Phase 2
    tui.phase_start("Phase 2: Identity detection")
    with PhaseTimer("phase2", timings):
        phase2_metrics = phase2_fn(residue_sequences, phase1_metrics_list)

    if not phase2_metrics:
        raise PhaseGateError("Phase 2 gate failed — no identity mappings", phase="phase2")

    tui.phase_ok("Phase 2", {
        "persistent_segments": len(phase2_metrics["persistent_segment_hashes"]),
        "identity_mappings": len(phase2_metrics["identity_mappings"]),
    })

    # Phase 3
    tui.phase_start("Phase 3: Relation detection")
    with PhaseTimer("phase3", timings):
        phase3_metrics = phase3_fn(residue_sequences, phase1_metrics_list, phase2_metrics)

    if not phase3_metrics:
        raise PhaseGateError("Phase 3 gate failed — no relations", phase="phase3")

    tui.phase_ok("Phase 3", {
        "nodes": phase3_metrics["node_count"],
        "edges": phase3_metrics["edge_count"],
        "persistent_relations": len(phase3_metrics["persistent_relation_hashes"]),
    })

    # Phase 4
    tui.phase_start("Phase 4: Symbol aliasing")
    with PhaseTimer("phase4", timings):
        phase4_metrics = phase4_fn(phase2_metrics, phase3_metrics)

    if not phase4_metrics:
        raise PhaseGateError("Phase 4 gate failed — no symbols", phase="phase4")

    tui.phase_ok("Phase 4", {
        "identity_aliases": phase4_metrics["identity_alias_count"],
        "relation_aliases": phase4_metrics["relation_alias_count"],
    })

    return (
        residue_sequences, phase1_metrics_list,
        phase2_metrics, phase3_metrics, phase4_metrics,
        token_to_residue_map, phase0_residues_by_run,
    )


def _apply_deterministic_mode(cfg: PipelineConfig) -> None:
    """
    Enforce deterministic-friendly runtime behavior.
    Keeps San-family logic intact while removing random generation paths.
    """
    if not cfg.deterministic_mode:
        return

    random.seed(int(cfg.deterministic_seed))
    cfg.generation.method = "highest_score"
    cfg.generation.temperature = 0.0
    cfg.generation.fluency_seed = int(cfg.deterministic_seed)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 20 — Public API: run() and async_run()
# ══════════════════════════════════════════════════════════════════════════════

def run(
    text_override: Optional[str] = None,
    cfg: Optional[PipelineConfig] = None,
    learner: Optional[Any] = None,
    *,
    return_result: bool = True,
    return_model_state: bool = False,
) -> Optional[PipelineResult]:
    """
    Synchronous pipeline entry point.

    Args:
        text_override: Text to process (overrides argv/stdin).
        cfg: PipelineConfig (loaded from project if None).
        learner: Optional PreferenceLearner (created if None).
        return_result: If False, prints end-user result and returns None.
        return_model_state: If True, result.model_state is set (phase2/3/4, path_scores, tokens, residue_sequences) for predict-next evaluation. If cfg.include_phase10_metrics is True, model_state also contains phase10_metrics (directed continuation snapshot).

    Returns:
        PipelineResult on success, None if return_result=False.
    """
    run_id = uuid.uuid4().hex[:8]
    t_total_start = time.perf_counter()

    if cfg is None:
        cfg = PipelineConfig.from_project()

    _apply_deterministic_mode(cfg)

    # Validate config
    errors = cfg.validate()
    if errors:
        raise ConfigurationError(
            "Configuration invalid:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    timings = PhaseTimings()
    tui = TUIRenderer(show_tui=cfg.show_tui)
    tui.header()

    # ── Resolve input ─────────────────────────────────────────────────────────
    if text_override is None:
        if getattr(cfg, "_use_default_input", False):
            raw_input = (
                "Action before knowledge.\n"
                "Function stabilizes before meaning appears.\n"
                "Structure emerges before language exists."
            )
        elif not sys.stdin.isatty():
            raw_input = sys.stdin.read().strip()
        elif len(sys.argv) > 1 and not getattr(cfg, "_cli_parsed", False):
            # Backward-compat for direct run() calls that did not parse CLI first.
            raw_input = " ".join(sys.argv[1:]).strip()
        else:
            raw_input = _prompt_interactive_input()
            if not raw_input or not raw_input.strip():
                raw_input = (
                    "Action before knowledge.\n"
                    "Function stabilizes before meaning appears.\n"
                    "Structure emerges before language exists."
                )
                if cfg.show_tui and HAS_RICH:
                    tui.phase_ok("Input", {"note": "empty input — using default text"})
    else:
        raw_input = text_override.strip()

    input_result = resolve_input(raw_input, cfg, PROJECT_ROOT)
    text = input_result.text

    tui.section("INPUT")
    preview = text[:200] + ("..." if len(text) > 200 else "")
    tui.phase_ok("Input resolved", {
        "type": input_result.input_type,
        "chars": len(text),
        "preview": preview[:50],
    })

    # ── Tokenisation ──────────────────────────────────────────────────────────
    tui.section("STEP 1: TOKENIZATION")
    with PhaseTimer("tokenization", timings):
        if input_result.input_type == "binary":
            tokens = text.split()
        else:
            tokens = tokenize_text(text, cfg.tokenization_method)

    if not tokens:
        raise TokenizationError(f"No tokens produced from input ({cfg.tokenization_method})")

    tui.phase_ok("Tokenization", {
        "method": cfg.tokenization_method,
        "tokens": len(tokens),
        "unique": len(set(tokens)),
        "sample": str(tokens[:5]),
    })

    # ── Structure Emergence (Phases 0-4) ──────────────────────────────────────
    (residue_sequences, _phase1_metrics_list,
     phase2_metrics, phase3_metrics, phase4_metrics,
     token_to_residue_map, _phase0_residues_by_run) = _run_structure_emergence(
        tokens, cfg, timings, tui
    )

    # ── Corpus ────────────────────────────────────────────────────────────────
    corpus_mgr = CorpusManager(cfg.corpus, PROJECT_ROOT)
    corpus_metrics = CorpusMetrics()
    if corpus_mgr.initialize():
        identity_hashes = set(phase2_metrics.get("identity_mappings", {}).values())
        edge_pairs = phase3_metrics.get("graph_edges", set())
        corpus_metrics = corpus_mgr.update_and_save(identity_hashes, edge_pairs)
        if corpus_metrics.updated:
            tui.phase_ok("Corpus state", {
                "identities": corpus_metrics.identities_count,
                "edges": corpus_metrics.edges_count,
                "docs": corpus_metrics.doc_count,
            })

    # ── Continuation Observation ──────────────────────────────────────────────
    tui.section("STEP 3: CONTINUATION OBSERVATION")
    texts_to_observe = (
        cfg.continuation_texts
        if getattr(cfg, "continuation_texts", None)
        else [cfg.continuation_text]
    )
    continuation_tokens = tokenize_text(texts_to_observe[0], cfg.tokenization_method)
    observer = ContinuationObserver(phase4_metrics, phase3_metrics, phase2_metrics)
    all_refusals: List[Any] = []
    for idx, cont_text in enumerate(texts_to_observe):
        ct_tokens = tokenize_text(cont_text, cfg.tokenization_method)
        refusals = observer.observe_continuation(ct_tokens, cfg.continuation_max_steps)
        all_refusals.extend(refusals)
        all_self = all(r.current_symbol == r.attempted_next_symbol for r in refusals)
        tui.phase_ok(
            f"Continuation {idx + 1}/{len(texts_to_observe)}" if len(texts_to_observe) > 1 else "Continuation",
            {
                "preview": cont_text[:50] + ("..." if len(cont_text) > 50 else ""),
                "tokens": len(ct_tokens),
                "refusals": len(refusals),
                "all_self": all_self,
            },
        )
    refusals = all_refusals
    all_self = all(r.current_symbol == r.attempted_next_symbol for r in refusals)
    continuation_tokens = tokenize_text(texts_to_observe[0], cfg.tokenization_method)

    # ── Topology ──────────────────────────────────────────────────────────────
    tui.section("STEP 4: ESCAPE TOPOLOGY")
    with PhaseTimer("topology", timings):
        analyzer = TopologyAnalyzer(observer, max_steps=cfg.topology_max_steps)
        topology = analyzer.measure(continuation_tokens)

    under_pressure = sum(1 for td in topology.values() if td.self_transition_attempts > 0)
    avg_escape = (
        sum(td.distinct_escape_paths for td in topology.values()) / len(topology)
        if topology else 0.0
    )
    tui.phase_ok("Topology", {
        "nodes": len(topology),
        "under_pressure": under_pressure,
        "avg_escape_paths": f"{avg_escape:.2f}",
    })

    # ── Clustering ────────────────────────────────────────────────────────────
    tui.section("STEP 5: TOPOLOGY CLUSTERING")
    with PhaseTimer("clustering", timings):
        clusterer = TopologyClusterer(cfg.clustering)
        clusters = clusterer.cluster(topology)

    tui.phase_ok("Clustering", {"clusters": len(clusters)})

    # ── Path Scoring ──────────────────────────────────────────────────────────
    tui.section("STEP 6: PATH SCORING")
    score_fn, rank_fn = _load_scoring()

    if learner is None:
        try:
            from integration.preference_learner import PreferenceLearner  # type: ignore
            learner = PreferenceLearner(alpha=cfg.learner_alpha, bound=cfg.learner_bound)
        except ImportError:
            learner = _NullLearner()

    with PhaseTimer("scoring", timings):
        path_scores = score_fn(
            phase4_metrics, phase3_metrics, phase2_metrics,
            topology, [tokens], learner=learner,
            symbol_to_token=None,  # filled after surface mapping
        )

    # Contract enforcement: all tuple-keyed values must be float
    for k, v in list(path_scores.items()):
        if isinstance(k, tuple) and len(k) == 2 and not isinstance(v, float):
            raise ScoringContractError(
                f"path_scores[{k!r}]: expected float, got {type(v).__name__}",
                phase="scoring",
            )

    actual_path_scores = {
        k: v for k, v in path_scores.items()
        if isinstance(k, tuple) and len(k) == 2
    }
    # CONTRACT: all values must be scalar floats (no dicts) before ranking/generation
    for k, v in actual_path_scores.items():
        assert isinstance(v, float), (
            f"path_scores contract violation at {k!r}: expected float, got {type(v).__name__}"
        )
    tui.phase_ok("Scoring", {"paths": len(actual_path_scores)})

    # ── Surface Mapping ───────────────────────────────────────────────────────
    tui.section("STEP 7: SURFACE MAPPING")
    symbol_to_token = build_surface_mapping(
        tokens, residue_sequences, phase2_metrics,
        phase4_metrics, token_to_residue_map,
    )
    tui.phase_ok("Surface", {"mappings": len(symbol_to_token)})

    # ── Re-score with surface info ────────────────────────────────────────────
    try:
        path_scores = score_fn(
            phase4_metrics, phase3_metrics, phase2_metrics,
            topology, [tokens], learner=learner,
            symbol_to_token=symbol_to_token,
        )
        actual_path_scores = {
            k: v for k, v in path_scores.items()
            if isinstance(k, tuple) and len(k) == 2
        }
        for k, v in actual_path_scores.items():
            assert isinstance(v, float), (
                f"path_scores contract violation at {k!r}: expected float, got {type(v).__name__}"
            )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        log.warning("Re-score with surface failed, using initial scores: %s", exc)

    # ── Text Generation ───────────────────────────────────────────────────────
    tui.section("STEP 8: TEXT GENERATION")
    if cfg.generation.num_sequences == 0 or cfg.generation.steps == 0:
        generated_outputs = []
    else:
        raw_cfg = {}
        try:
            from threshold_onset.config import get_config  # type: ignore
            raw_cfg = get_config()
        except Exception:  # pylint: disable=broad-except
            pass
        prediction_methods: List[str] = (
            raw_cfg.get("model", {}).get("prediction_methods")
            or [cfg.generation.method]
        )
        if cfg.deterministic_mode:
            prediction_methods = [cfg.generation.method]
        if not isinstance(prediction_methods, list):
            prediction_methods = [cfg.generation.method]
        generated_outputs = []
        with PhaseTimer("generation", timings):
            for pred_method in prediction_methods:
                if len(prediction_methods) > 1:
                    tui.phase_ok(f"Generation method: {pred_method}", {})
                gen_cfg = dataclasses.replace(cfg.generation, method=pred_method)
                gen_pipeline_m = GenerationPipeline(gen_cfg)
                outs = gen_pipeline_m.generate(
                    tokens=tokens,
                    residue_sequences=residue_sequences,
                    phase2_metrics=phase2_metrics,
                    phase3_metrics=phase3_metrics,
                    phase4_metrics=phase4_metrics,
                    topology=topology,
                    path_scores=actual_path_scores,
                    symbol_to_token=symbol_to_token,
                    learner=learner,
                    score_fn=score_fn,
                    rank_fn=rank_fn,
                )
                generated_outputs.extend(outs)

    for i, out in enumerate(generated_outputs, 1):
        tui.phase_ok(f"Output {i}", {"text": out[:60]})

    # ── Finalise ──────────────────────────────────────────────────────────────
    timings.total_ms = (time.perf_counter() - t_total_start) * 1000.0

    result = PipelineResult(
        run_id=run_id,
        input_text=text,
        input_type=input_result.input_type,
        tokens=tokens,
        generated_outputs=generated_outputs,
        token_count=len(tokens),
        identity_count=phase4_metrics.get("identity_alias_count", 0),
        relation_count=phase4_metrics.get("relation_alias_count", 0),
        refusal_count=len(refusals),
        all_self_refusals=all_self,
        topology=topology,
        clusters=clusters,
        scored_path_count=len(actual_path_scores),
        symbol_mapping_count=len(symbol_to_token),
        corpus=corpus_metrics,
        timings=timings,
        config=cfg,
    )
    if return_model_state:
        result.model_state = {
            "phase2_metrics": phase2_metrics,
            "phase3_metrics": phase3_metrics,
            "phase4_metrics": phase4_metrics,
            "path_scores": actual_path_scores,
            "tokens": tokens,
            "residue_sequences": residue_sequences,
            "symbol_to_token": symbol_to_token,  # escape physics needs this
        }
        if cfg.include_phase10_metrics:
            from threshold_onset.phase10 import run_phase10_from_model_state

            p10 = run_phase10_from_model_state(
                result.model_state,
                cross_check_phase3=cfg.phase10_cross_check_phase3,
            )
            result.model_state["phase10_metrics"] = p10.to_jsonable()

    tui.result_table(result)

    # Flamegraph output
    if cfg.emit_flamegraph:
        fg_path = PROJECT_ROOT / "output" / f"flamegraph_{run_id}.collapsed"
        fg_path.parent.mkdir(parents=True, exist_ok=True)
        fg_path.write_text("\n".join(timings.as_flamegraph_lines(run_id)))
        log.info("Flamegraph: %s", fg_path)

    # Diagnostic import report
    log.debug("%s", ImportRegistry.diagnostic_report())

    if return_result:
        return result

    tui.end_user_result(result)
    return None


async def async_run(
    text_override: Optional[str] = None,
    cfg: Optional[PipelineConfig] = None,
    learner: Optional[Any] = None,
    *,
    return_result: bool = True,
    return_model_state: bool = False,
) -> Optional[PipelineResult]:
    """
    Async wrapper for run().
    Allows pipeline to be awaited in async contexts.

    Mirrors synchronous ``run()`` flags: ``return_result``, ``return_model_state``
    (e.g. for ``model_state`` / optional ``phase10_metrics`` when configured).
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        functools.partial(
            run,
            text_override=text_override,
            cfg=cfg,
            learner=learner,
            return_result=return_result,
            return_model_state=return_model_state,
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 21 — Null Learner (fallback when PreferenceLearner unavailable)
# ══════════════════════════════════════════════════════════════════════════════

class _NullLearner:
    """
    Intentional no-op learner when PreferenceLearner is unavailable.
    step() and get_stats() are no-ops; other attributes return a no-op callable.
    """

    def step(self) -> None:
        pass  # intentional no-op

    def get_stats(self) -> Dict[str, Any]:
        return {"total_edges": 0, "avg_bias": 0.0}

    def __getattr__(self, name: str) -> Any:
        return lambda *a, **kw: None


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 22 — CLI Entry Point
# ══════════════════════════════════════════════════════════════════════════════

def _parse_cli() -> Tuple[Optional[str], PipelineConfig]:
    """Parse CLI arguments into (text_override, PipelineConfig)."""
    parser = argparse.ArgumentParser(
        prog="run_complete",
        description="Complete End-to-End Unified Pipeline  v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
        Examples:
          python run_complete.py                    # interactive: prompts for text
          python run_complete.py "Action before knowledge."
          python run_complete.py /path/to/corpus.txt
          python run_complete.py --default          # use built-in text, no prompt
          python run_complete.py --method subword --runs 5 "text here"
          python run_complete.py --profile --no-tui "text"
          PIPELINE_ASYNC=1 python run_complete.py "text"
          python run_complete.py --phase10-metrics --default   # model_state includes phase10_metrics when used with API returning state
        """),
    )
    parser.add_argument("--default", action="store_true",
                        help="Use built-in default text instead of prompting when no text given")
    parser.add_argument("--config", type=Path, help="Config file override")
    parser.add_argument("--method", "-m", help="Tokenization method")
    parser.add_argument("--runs", "-r", type=int, help="Number of multi-runs")
    parser.add_argument("--profile", action="store_true", help="Emit flamegraph")
    parser.add_argument("--no-tui", action="store_true", help="Disable Rich TUI")
    parser.add_argument("--async", dest="async_mode", action="store_true",
                        help="Run in async mode")
    parser.add_argument("--deterministic", action="store_true",
                        help="Enable deterministic mode (disables random generation paths)")
    parser.add_argument("--seed", type=int,
                        help="Deterministic seed (used when deterministic mode is enabled)")
    parser.add_argument("--workers", type=int,
                        help="Set SANTEK_TEXT_WORKERS for downstream execution")
    parser.add_argument("--method-workers", type=int,
                        help="Set SANTEK_METHOD_WORKERS for downstream execution")
    parser.add_argument("--log-level", default="WARNING",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--phase10-metrics", action="store_true",
                        help="Attach phase10_metrics to model_state when pipeline returns state (API/scripts; default off)")
    parser.add_argument("--phase10-cross-check-phase3", action="store_true",
                        help="With --phase10-metrics, count only transitions allowed by Phase 3 undirected edges")
    parser.add_argument("text", nargs="*", help="Input text (or file path). Omit for interactive prompt.")

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    cfg = PipelineConfig.from_project(args.config)
    if args.method:
        cfg.tokenization_method = args.method
        cfg.tokenization_methods = None  # single-method run
    if args.runs:
        cfg.num_runs = args.runs
    if args.profile:
        cfg.emit_flamegraph = True
    if args.no_tui:
        cfg.show_tui = False
    if args.async_mode:
        cfg.async_mode = True
    if args.deterministic:
        cfg.deterministic_mode = True
    if args.seed is not None:
        cfg.deterministic_seed = args.seed
    if args.default:
        setattr(cfg, "_use_default_input", True)
    if args.phase10_metrics:
        cfg.include_phase10_metrics = True
    if args.phase10_cross_check_phase3:
        cfg.phase10_cross_check_phase3 = True
    setattr(cfg, "_cli_parsed", True)
    runtime_env = build_runtime_env(
        workers=args.workers,
        method_workers=args.method_workers,
        profile=args.profile,
    )
    for key in ("SANTEK_TEXT_WORKERS", "STRESS_WORKERS", "SANTEK_METHOD_WORKERS", "PIPELINE_PROFILE"):
        if key in runtime_env:
            os.environ[key] = runtime_env[key]

    text_override = " ".join(args.text).strip() if args.text else None
    return text_override, cfg


def main(
    learner: Optional[Any] = None,
    return_result: bool = False,
    text_override: Optional[str] = None,
) -> Optional[PipelineResult]:
    """
    Backwards-compatible entry point.
    Preserves v1 signature: main(learner, return_result, text_override).
    """
    def _pipeline_error_code(exc: PipelineError) -> str:
        if isinstance(exc, ConfigurationError):
            return "configuration_error"
        if isinstance(exc, TokenizationError):
            return "tokenization_error"
        if isinstance(exc, ImportRegistryError):
            return "import_registry_error"
        if isinstance(exc, EmptyInputError):
            return "empty_input_error"
        if isinstance(exc, FileInputError):
            return "file_input_error"
        if isinstance(exc, ScoringContractError):
            return "scoring_contract_error"
        if isinstance(exc, PhaseGateError):
            return "phase_gate_error"
        return "pipeline_error"

    try:
        cfg = PipelineConfig.from_project()
        result = run(
            text_override=text_override,
            cfg=cfg,
            learner=learner,
            return_result=True,
        )
        if return_result:
            # Backwards-compat: v1 returned a plain dict
            if result:
                return {  # type: ignore[return-value]
                    "input_text": result.input_text,
                    "generated_outputs": result.generated_outputs,
                    "token_count": result.token_count,
                    "identity_count": result.identity_count,
                    "tokens": result.tokens,
                }
            return None

        # Print end-user result
        if result:
            tui = TUIRenderer(show_tui=cfg.show_tui)
            tui.end_user_result(result)
        return None

    except PipelineError as exc:
        code = _pipeline_error_code(exc)
        log.error("Pipeline error: %s", exc)
        _safe_print(f"\nPipeline error [{code}]: {exc}")
        return None
    except Exception as exc:  # pylint: disable=broad-exception-caught
        log.exception("Unhandled exception")
        _safe_print(f"\nUnhandled error [runtime_error]: {exc}")
        traceback.print_exc()
        return None


_DEFAULT_INPUT_TEXT = (
    "Action before knowledge.\n"
    "Function stabilizes before meaning appears.\n"
    "Structure emerges before language exists."
)

if __name__ == "__main__":
    text_override_cli, cfg_cli = _parse_cli()

    # Resolve --default flag into a concrete string NOW, before any run() call.
    # This is critical: dataclasses.replace() used in the multi-method loop creates
    # a fresh config object and drops any dynamic setattr flags (_use_default_input,
    # _cli_parsed). By resolving the text here, run() always receives a real string
    # and never falls back to reading sys.argv as input.
    if text_override_cli is None and getattr(cfg_cli, "_use_default_input", False):
        text_override_cli = _DEFAULT_INPUT_TEXT

    # Interactive prompt once when no text given (so user can type/paste instead of CLI)
    if text_override_cli is None and sys.stdin.isatty():
        text_override_cli = _prompt_interactive_input().strip() or _DEFAULT_INPUT_TEXT

    if cfg_cli.async_mode:
        asyncio.run(async_run(text_override=text_override_cli, cfg=cfg_cli))
    else:
        try:
            if getattr(cfg_cli, "tokenization_methods", None):
                # Run pipeline for each of the 9 (or N) tokenization methods
                methods = cfg_cli.tokenization_methods
                for idx, method in enumerate(methods, 1):
                    canonical = cfg_cli._normalize_method(method)
                    _safe_print(f"\n{'=' * 70}\nTokenization method {idx}/{len(methods)}: {canonical}\n{'=' * 70}\n")
                    run(
                        text_override=text_override_cli,
                        cfg=dataclasses.replace(
                            cfg_cli,
                            tokenization_method=canonical,
                            tokenization_methods=None,
                        ),
                        return_result=False,
                    )
            else:
                result = run(
                    text_override=text_override_cli,
                    cfg=cfg_cli,
                    return_result=False,
                )
        except PipelineError as e:
            _safe_print(f"\nPipeline error:\n{e}")
            sys.exit(1)
        except KeyboardInterrupt:
            _safe_print("\nInterrupted.")
            sys.exit(130)
