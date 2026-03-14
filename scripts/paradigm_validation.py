#!/usr/bin/env python3
"""Paradigm validation gate for THRESHOLD_ONSET."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import statistics
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

from integration.run_complete import PipelineConfig, run
from integration.baselines import run_baselines


ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs" / "paradigm"
LATEST_JSON = LOG_DIR / "paradigm_validation_latest.json"
LATEST_MD = LOG_DIR / "paradigm_validation_latest.md"


QUICK_PROMPTS = [
    "Action before knowledge.",
    "Structure emerges before language.",
    "Tokens become residues and identities.",
    "Constraint bounds generation without self transition.",
]

FULL_PROMPTS = [
    "Action before knowledge.",
    "Structure emerges before language.",
    "Tokens become residues and identities.",
    "Constraint bounds generation without self transition.",
    "Short factual request: list two colors.",
    "Explain one practical implication of strict transition constraints.",
    "Generate one concise sentence without repeated adjacent words.",
    "Mixed domain: code compiles before execution, tests before deployment.",
]


@dataclass
class RunRecord:
    prompt_idx: int
    repeat_idx: int
    success: bool
    token_count: int
    identity_count: int
    relation_count: int
    refusal_count: int
    latency_ms: float
    signature: str
    output_preview: str
    self_transition_count: int = 0
    self_transition_rate: float = 0.0
    decoder_consistency: float = 0.0
    failure_code: str = ""
    error: str = ""


@dataclass
class ValidationReport:
    generated_at: str
    profile: str
    repeats: int
    prompt_count: int
    success_rate: float
    structural_valid_rate: float
    determinism_rate: float
    latency_p50_ms: float
    latency_p95_ms: float
    total_elapsed_ms: float
    model_baseline_metrics: Dict[str, float] = field(default_factory=dict)
    baseline_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    baseline_wins: int = 0
    failure_code_counts: Dict[str, int] = field(default_factory=dict)
    failures: List[str] = field(default_factory=list)
    records: List[RunRecord] = field(default_factory=list)


def _signature_for_result(result) -> str:
    primary = result.generated_outputs[0] if result.generated_outputs else ""
    payload = {
        "success": bool(result.succeeded),
        "token_count": int(result.token_count),
        "identity_count": int(result.identity_count),
        "relation_count": int(result.relation_count),
        "refusal_count": int(result.refusal_count),
        "primary_output": primary.strip(),
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _run_once(prompt: str):
    cfg = PipelineConfig.from_project()
    cfg.show_tui = False
    cfg.deterministic_mode = True

    t0 = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        result = run(
            text_override=prompt,
            cfg=cfg,
            learner=None,
            return_result=True,
            return_model_state=False,
        )
    latency_ms = (time.perf_counter() - t0) * 1000.0
    return result, latency_ms


def _count_self_transitions(tokens: List[str]) -> int:
    return sum(1 for idx in range(len(tokens) - 1) if tokens[idx] == tokens[idx + 1])


def _decoder_consistency(tokens: List[str], vocab: set) -> float:
    if not tokens:
        return 1.0
    return sum(1 for tok in tokens if tok in vocab) / len(tokens)


def _compute_output_metrics(prompt: str, output: str) -> Tuple[int, float, float]:
    output_tokens = output.split()
    prompt_vocab = set(prompt.lower().split())
    self_count = _count_self_transitions(output_tokens)
    total_trans = max(1, len(output_tokens) - 1)
    self_rate = self_count / total_trans
    consistency = _decoder_consistency([tok.lower() for tok in output_tokens], prompt_vocab)
    return self_count, self_rate, consistency


def _compute_model_baseline_metrics(records: List[RunRecord]) -> Dict[str, float]:
    valid = [r for r in records if r.success]
    if not valid:
        return {
            "avg_self_transition_rate": 1.0,
            "avg_constraint_violations": 0.0,
            "total_constraint_violations": 0.0,
            "decoder_consistency": 0.0,
            "n_samples": 0.0,
        }

    return {
        "avg_self_transition_rate": sum(r.self_transition_rate for r in valid) / len(valid),
        "avg_constraint_violations": sum(float(r.self_transition_count) for r in valid) / len(valid),
        "total_constraint_violations": float(sum(r.self_transition_count for r in valid)),
        "decoder_consistency": sum(r.decoder_consistency for r in valid) / len(valid),
        "n_samples": float(len(valid)),
    }


def _run_internal_baselines(
    prompts: List[str],
    repeats: int,
    gen_length: int,
) -> Dict[str, Dict[str, float]]:
    corpus: List[Tuple[str, str]] = []
    for idx, prompt in enumerate(prompts):
        for rep in range(repeats):
            corpus.append((f"p{idx}_r{rep}", prompt))
    return run_baselines(seed=42, gen_length=max(1, gen_length), corpus=corpus)


def _count_baseline_wins(
    model_metrics: Dict[str, float],
    baseline_metrics: Dict[str, Dict[str, float]],
) -> int:
    model_self = model_metrics.get("avg_self_transition_rate", 1.0)
    model_violations = model_metrics.get("avg_constraint_violations", float("inf"))
    wins = 0
    for metrics in baseline_metrics.values():
        base_self = metrics.get("avg_self_transition_rate", 1.0)
        base_violations = metrics.get("avg_constraint_violations", float("inf"))
        # Win if invariant quality is better or strictly better at equal self-transition.
        if model_self < base_self or (model_self == base_self and model_violations < base_violations):
            wins += 1
    return wins


def _classify_failure(result, error_text: str = "") -> str:
    """Stable failure taxonomy for validation runs."""
    if result is None:
        return "pipeline_no_result"
    if getattr(result, "succeeded", False):
        return ""
    text = error_text.lower()
    if "phase 2 gate failed" in text or "phase 3 gate failed" in text or "phase 4 gate failed" in text:
        return "phase_gate_failure"
    if "token" in text and "no tokens" in text:
        return "tokenization_failure"
    if "scoring" in text or "contract" in text:
        return "scoring_contract"
    if "timeout" in text or "timed out" in text:
        return "runtime_timeout"
    return "runtime_error"


def _compute_determinism(records: List[RunRecord], repeats: int) -> float:
    by_prompt: Dict[int, List[str]] = {}
    for rec in records:
        by_prompt.setdefault(rec.prompt_idx, []).append(rec.signature)

    stable = 0
    total = 0
    for _prompt_idx, signatures in by_prompt.items():
        if len(signatures) < repeats:
            continue
        total += 1
        if len(set(signatures)) == 1:
            stable += 1
    if total == 0:
        return 0.0
    return stable / total


def _write_markdown(report: ValidationReport) -> None:
    lines: List[str] = []
    lines.append("# THRESHOLD_ONSET Paradigm Validation")
    lines.append("")
    lines.append(f"- Generated: `{report.generated_at}`")
    lines.append(f"- Profile: `{report.profile}`")
    lines.append(f"- Prompts: `{report.prompt_count}`")
    lines.append(f"- Repeats: `{report.repeats}`")
    lines.append(f"- Success rate: `{report.success_rate:.2%}`")
    lines.append(f"- Structural valid rate: `{report.structural_valid_rate:.2%}`")
    lines.append(f"- Determinism rate: `{report.determinism_rate:.2%}`")
    lines.append(f"- Latency p50: `{report.latency_p50_ms:.1f} ms`")
    lines.append(f"- Latency p95: `{report.latency_p95_ms:.1f} ms`")
    if report.model_baseline_metrics:
        lines.append(f"- Baseline wins: `{report.baseline_wins}`")
    lines.append("")
    if report.model_baseline_metrics:
        lines.append("## Baseline Comparisons (Internal)")
        lines.append("")
        lines.append("| System | Avg self-transition | Avg violations | Decoder consistency | Samples |")
        lines.append("|---|---:|---:|---:|---:|")
        mm = report.model_baseline_metrics
        lines.append(
            f"| threshold_onset | {mm.get('avg_self_transition_rate', 0.0):.2%} | "
            f"{mm.get('avg_constraint_violations', 0.0):.2f} | "
            f"{mm.get('decoder_consistency', 0.0):.2%} | "
            f"{int(mm.get('n_samples', 0.0))} |"
        )
        for name, metrics in sorted(report.baseline_metrics.items()):
            lines.append(
                f"| {name} | {metrics.get('avg_self_transition_rate', 0.0):.2%} | "
                f"{metrics.get('avg_constraint_violations', 0.0):.2f} | "
                f"{metrics.get('decoder_consistency', 0.0):.2%} | "
                f"{int(metrics.get('n_samples', 0.0))} |"
            )
        lines.append("")
    if report.failure_code_counts:
        lines.append("## Failure Code Counts")
        for code, count in sorted(report.failure_code_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"- `{code}`: {count}")
        lines.append("")
    if report.failures:
        lines.append("## Gate Failures")
        for fail in report.failures:
            lines.append(f"- {fail}")
        lines.append("")
    lines.append("## Samples")
    lines.append("| prompt_idx | repeat | success | failure_code | tokens | ids | relations | refusals | latency_ms |")
    lines.append("|---:|---:|---:|---|---:|---:|---:|---:|---:|")
    for rec in report.records[:25]:
        lines.append(
            f"| {rec.prompt_idx} | {rec.repeat_idx} | {int(rec.success)} | `{rec.failure_code}` | "
            f"{rec.token_count} | {rec.identity_count} | {rec.relation_count} | "
            f"{rec.refusal_count} | {rec.latency_ms:.1f} |"
        )
    LATEST_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Paradigm validation gate for THRESHOLD_ONSET.")
    parser.add_argument("--profile", choices=["quick", "full"], default="quick")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--min-success-rate", type=float, default=0.90)
    parser.add_argument("--min-structural-rate", type=float, default=0.90)
    parser.add_argument("--min-determinism-rate", type=float, default=0.80)
    parser.add_argument("--max-p95-ms", type=float, default=0.0, help="0 disables latency gate")
    parser.add_argument("--baseline-gen-length", type=int, default=20)
    parser.add_argument("--skip-baselines", action="store_true")
    parser.add_argument("--min-baseline-wins", type=int, default=0,
                        help="Require threshold_onset to beat this many internal baselines")
    args = parser.parse_args()

    prompts = QUICK_PROMPTS if args.profile == "quick" else FULL_PROMPTS
    repeats = max(1, args.repeats)

    records: List[RunRecord] = []
    t_start = time.perf_counter()

    for p_idx, prompt in enumerate(prompts):
        for r_idx in range(repeats):
            try:
                result, latency_ms = _run_once(prompt)
                if result is None:
                    records.append(
                        RunRecord(
                            prompt_idx=p_idx,
                            repeat_idx=r_idx,
                            success=False,
                            token_count=0,
                            identity_count=0,
                            relation_count=0,
                            refusal_count=0,
                            latency_ms=latency_ms,
                            signature="none",
                            output_preview="",
                            failure_code="pipeline_no_result",
                            error="pipeline returned None",
                        )
                    )
                    continue

                sig = _signature_for_result(result)
                primary = result.generated_outputs[0] if result.generated_outputs else ""
                self_count, self_rate, consistency = _compute_output_metrics(prompt, primary)
                records.append(
                    RunRecord(
                        prompt_idx=p_idx,
                        repeat_idx=r_idx,
                        success=bool(result.succeeded),
                        token_count=int(result.token_count),
                        identity_count=int(result.identity_count),
                        relation_count=int(result.relation_count),
                        refusal_count=int(result.refusal_count),
                        latency_ms=latency_ms,
                        signature=sig,
                        output_preview=primary[:120],
                        self_transition_count=self_count,
                        self_transition_rate=self_rate,
                        decoder_consistency=consistency,
                        failure_code=_classify_failure(result),
                    )
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                records.append(
                    RunRecord(
                        prompt_idx=p_idx,
                        repeat_idx=r_idx,
                        success=False,
                        token_count=0,
                        identity_count=0,
                        relation_count=0,
                        refusal_count=0,
                        latency_ms=0.0,
                        signature="error",
                        output_preview="",
                        failure_code=_classify_failure(None, str(exc)),
                        error=str(exc),
                    )
                )

    total_elapsed_ms = (time.perf_counter() - t_start) * 1000.0
    total = max(1, len(records))
    successes = sum(1 for r in records if r.success)
    structural = sum(1 for r in records if r.identity_count > 0 and r.relation_count >= 0)
    latencies = [r.latency_ms for r in records if r.latency_ms > 0]
    latency_p50 = statistics.median(latencies) if latencies else 0.0
    if latencies:
        sorted_lats = sorted(latencies)
        i95 = int(round(0.95 * (len(sorted_lats) - 1)))
        latency_p95 = sorted_lats[i95]
    else:
        latency_p95 = 0.0

    success_rate = successes / total
    structural_rate = structural / total
    determinism_rate = _compute_determinism(records, repeats)
    failure_code_counts: Dict[str, int] = {}
    for rec in records:
        if rec.failure_code:
            failure_code_counts[rec.failure_code] = failure_code_counts.get(rec.failure_code, 0) + 1

    model_baseline_metrics = _compute_model_baseline_metrics(records)
    baseline_metrics: Dict[str, Dict[str, float]] = {}
    baseline_wins = 0
    if not args.skip_baselines:
        baseline_metrics = _run_internal_baselines(prompts, repeats, args.baseline_gen_length)
        baseline_wins = _count_baseline_wins(model_baseline_metrics, baseline_metrics)

    failures: List[str] = []
    if success_rate < args.min_success_rate:
        failures.append(f"success_rate {success_rate:.2%} < {args.min_success_rate:.2%}")
    if structural_rate < args.min_structural_rate:
        failures.append(f"structural_valid_rate {structural_rate:.2%} < {args.min_structural_rate:.2%}")
    if determinism_rate < args.min_determinism_rate:
        failures.append(f"determinism_rate {determinism_rate:.2%} < {args.min_determinism_rate:.2%}")
    if args.max_p95_ms > 0 and latency_p95 > args.max_p95_ms:
        failures.append(f"latency_p95_ms {latency_p95:.1f} > {args.max_p95_ms:.1f}")
    if args.min_baseline_wins > 0 and baseline_wins < args.min_baseline_wins:
        failures.append(f"baseline_wins {baseline_wins} < {args.min_baseline_wins}")

    report = ValidationReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        profile=args.profile,
        repeats=repeats,
        prompt_count=len(prompts),
        success_rate=success_rate,
        structural_valid_rate=structural_rate,
        determinism_rate=determinism_rate,
        latency_p50_ms=latency_p50,
        latency_p95_ms=latency_p95,
        total_elapsed_ms=total_elapsed_ms,
        model_baseline_metrics=model_baseline_metrics,
        baseline_metrics=baseline_metrics,
        baseline_wins=baseline_wins,
        failure_code_counts=failure_code_counts,
        failures=failures,
        records=records,
    )

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_JSON.write_text(json.dumps(asdict(report), indent=2, ensure_ascii=False), encoding="utf-8")
    _write_markdown(report)

    print(f"[paradigm-validation] report: {LATEST_JSON}")
    print(f"[paradigm-validation] success={success_rate:.2%} structural={structural_rate:.2%} "
          f"determinism={determinism_rate:.2%} p95={latency_p95:.1f}ms")
    if baseline_metrics:
        print(f"[paradigm-validation] baseline_wins={baseline_wins} "
              f"model_self_transition={model_baseline_metrics['avg_self_transition_rate']:.2%}")
    if failures:
        print("[paradigm-validation] FAILED")
        for fail in failures:
            print(f"  - {fail}")
        return 1
    print("[paradigm-validation] PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

