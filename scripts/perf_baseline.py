#!/usr/bin/env python3
"""Baseline benchmark runner with comparable metrics output."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from threshold_onset.line_codec import encode as encode_compact

LOG_DIR = ROOT / "logs" / "perf"
LATEST_REPORT = LOG_DIR / "baseline_latest.txt"
LATEST_MD = LOG_DIR / "baseline_latest.md"


@dataclass
class CommandMetrics:
    name: str
    command: List[str]
    exit_code: int
    elapsed_ms: float
    stdout_path: str
    stderr_path: str
    final_result_count: int = 0
    status_ok_count: int = 0
    traceback_count: int = 0
    total_time_ms_values: List[float] = field(default_factory=list)
    notes: Dict[str, str] = field(default_factory=dict)


@dataclass
class BaselineReport:
    generated_at: str
    profile: str
    machine: Dict[str, str]
    env: Dict[str, str]
    commands: List[CommandMetrics]
    total_elapsed_ms: float


def _safe_env_value(name: str) -> str:
    return os.environ.get(name, "")


def _run_command(
    name: str,
    command: List[str],
    timeout_s: Optional[int],
) -> CommandMetrics:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    cmd_key = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    stdout_path = LOG_DIR / f"{stamp}_{cmd_key}.stdout.log"
    stderr_path = LOG_DIR / f"{stamp}_{cmd_key}.stderr.log"

    t0 = time.time()
    timed_out = False
    with open(stdout_path, "w", encoding="utf-8", errors="replace") as out_f, open(
        stderr_path, "w", encoding="utf-8", errors="replace"
    ) as err_f:
        try:
            proc = subprocess.run(
                command,
                cwd=str(ROOT),
                stdout=out_f,
                stderr=err_f,
                text=True,
                timeout=timeout_s,
                check=False,
            )
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            exit_code = 124
            err_f.write(f"\nCommand timed out after {timeout_s}s\n")
    elapsed_ms = (time.time() - t0) * 1000.0

    stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace")
    stderr_text = stderr_path.read_text(encoding="utf-8", errors="replace")
    combined_text = f"{stdout_text}\n{stderr_text}"
    final_result_count = len(re.findall(r"FINAL RESULT", stdout_text))
    status_ok_count = len(re.findall(r"Status:\s+OK", stdout_text))
    traceback_count = len(re.findall(r"Traceback \(most recent call last\):", combined_text))
    total_time_ms_values = [float(x) for x in re.findall(r"Total time:\s+([0-9]+(?:\.[0-9]+)?)ms", stdout_text)]

    return CommandMetrics(
        name=name,
        command=command,
        exit_code=exit_code,
        elapsed_ms=elapsed_ms,
        stdout_path=str(stdout_path),
        stderr_path=str(stderr_path),
        final_result_count=final_result_count,
        status_ok_count=status_ok_count,
        traceback_count=traceback_count,
        total_time_ms_values=total_time_ms_values,
        notes={"timed_out": str(timed_out).lower()} if timed_out else {},
    )


def _preset_commands(profile: str) -> List[tuple[str, List[str], Optional[int]]]:
    py = sys.executable
    if profile == "quick":
        return [
            (
                "pipeline_check",
                [py, "integration/run_user_result.py", "Action before knowledge."],
                180,
            ),
            (
                "small_train_smoke",
                [
                    py,
                    "build_hindu_corpus.py",
                    "--skip-download",
                    "--epochs",
                    "1",
                    "--max-texts",
                    "3",
                ],
                900,
            ),
        ]
    return [
        (
            "hindu_corpus_train",
            [
                py,
                "build_hindu_corpus.py",
                "--skip-download",
                "--epochs",
                "10",
                "--max-texts",
                "100",
            ],
            None,
        ),
        (  # keep this bounded to avoid runaway benchmarks
            "integration_scale",
            [py, "integration/run_corpus_scale.py", "100", "--workers", "4"],
            3600,
        ),
    ]


def _write_markdown(report: BaselineReport) -> None:
    lines: List[str] = []
    lines.append(f"# Baseline Report ({report.profile})")
    lines.append("")
    lines.append(f"- Generated: `{report.generated_at}`")
    lines.append(f"- Total elapsed: `{report.total_elapsed_ms:.1f} ms`")
    lines.append(
        f"- Python: `{report.machine.get('python_version','')}` | CPU count: `{report.machine.get('cpu_count','')}`"
    )
    lines.append("")
    lines.append("| Command | Exit | Elapsed (ms) | FINAL RESULT | Status OK | Tracebacks |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for c in report.commands:
        lines.append(
            f"| `{c.name}` | `{c.exit_code}` | `{c.elapsed_ms:.1f}` | `{c.final_result_count}` | `{c.status_ok_count}` | `{c.traceback_count}` |"
        )
    LATEST_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run baseline perf benchmark suite.")
    parser.add_argument(
        "--profile",
        choices=["quick", "full"],
        default="quick",
        help="quick (fast smoke) or full (heavy baseline)",
    )
    args = parser.parse_args()

    commands = _preset_commands(args.profile)
    results: List[CommandMetrics] = []
    t0 = time.time()
    for name, cmd, timeout_s in commands:
        print(f"[baseline] running {name}: {' '.join(cmd)}")
        results.append(_run_command(name=name, command=cmd, timeout_s=timeout_s))

    report = BaselineReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        profile=args.profile,
        machine={
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "cpu_count": str(os.cpu_count() or 0),
        },
        env={
            "SANTEK_TEXT_WORKERS": _safe_env_value("SANTEK_TEXT_WORKERS"),
            "SANTEK_METHOD_WORKERS": _safe_env_value("SANTEK_METHOD_WORKERS"),
        },
        commands=results,
        total_elapsed_ms=(time.time() - t0) * 1000.0,
    )

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LATEST_REPORT.write_text(encode_compact(asdict(report), sort_keys=True), encoding="utf-8")
    _write_markdown(report)
    print(f"[baseline] saved {LATEST_REPORT}")
    print(f"[baseline] saved {LATEST_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
