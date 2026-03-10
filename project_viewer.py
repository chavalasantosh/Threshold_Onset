#!/usr/bin/env python3
"""
THRESHOLD_ONSET - Project Viewer / Executor

Usage:
    python project_viewer.py              # RUN everything (10-step suite)
    python project_viewer.py --describe    # Print overview (no execution)
    python project_viewer.py --verbose     # Full module report
    python project_viewer.py --out FILE   # Write report to file
    python project_viewer.py --full       # Full source dump
    python project_viewer.py --json       # Output as JSON
"""

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parent

PIPELINE_STEPS = [
    ("Decoder test", "integration/test_decoder.py"),
    ("Validation", "integration/validate_pipeline.py"),
    ("Stress test", "integration/stress_test.py"),
    ("Benchmark", "integration/benchmark.py"),
    ("Baselines", "integration/baselines.py"),
    ("External validation", "integration/external_validation.py"),
    ("Stability mode", "integration/stability_mode.py"),
    ("Stability experiments", "integration/stability_experiments.py"),
    ("Structural scaling", "integration/structural_scaling.py"),
    ("Full pipeline", "integration/run_complete.py"),
]

EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "versions", "1706.03762", "archive"}
EXCLUDE_FILES = {"main.py"}
MAX_DOCSTRING_LEN = 500
MAX_SOURCE_PREVIEW = 3  # lines per definition


def _should_include(path: Path) -> bool:
    if path.name in EXCLUDE_FILES:
        return False
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return False
    return path.suffix == ".py"


def _collect_python_files() -> List[Path]:
    files = []
    for p in ROOT.rglob("*.py"):
        if _should_include(p):
            files.append(p.relative_to(ROOT))
    return sorted(files, key=lambda x: str(x))


def _truncate(text: str, max_len: int) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."


def _extract_docstring(node: ast.AST) -> str:
    doc = ast.get_docstring(node)
    return _truncate(doc or "", MAX_DOCSTRING_LEN)


def _get_signature(node: ast.AST) -> str:
    if isinstance(node, ast.FunctionDef):
        args = [a.arg for a in node.args.args if a.arg != "self"]
        return f"({', '.join(args[:5])}{'...' if len(args) > 5 else ''})"
    return ""


def _parse_file(path: Path) -> Dict[str, Any]:
    full_path = ROOT / path
    try:
        source = full_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": str(e), "path": str(path)}

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"Syntax: {e}", "path": str(path)}

    lines = source.splitlines()
    result: Dict[str, Any] = {
        "path": str(path),
        "lines": len(lines),
        "module_doc": "",
        "imports": [],
        "classes": [],
        "functions": [],
        "constants": [],
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Module) and ast.get_docstring(node):
            result["module_doc"] = _truncate(ast.get_docstring(node), MAX_DOCSTRING_LEN)
            break

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            else:
                mod = node.module or ""
                for alias in node.names:
                    result["imports"].append(f"{mod}.{alias.name}" if mod else alias.name)
        elif isinstance(node, ast.ClassDef):
            methods = [
                {"name": n.name, "doc": _extract_docstring(n)}
                for n in node.body
                if isinstance(n, ast.FunctionDef)
            ]
            result["classes"].append({
                "name": node.name,
                "doc": _extract_docstring(node),
                "methods": methods[:10],
                "method_count": len(methods),
            })
        elif isinstance(node, ast.FunctionDef):
            result["functions"].append({
                "name": node.name,
                "doc": _extract_docstring(node),
                "sig": _get_signature(node),
            })

    result["imports"] = result["imports"][:30]
    result["functions"] = result["functions"][:25]
    return result


def _format_module(data: Dict[str, Any], indent: str = "") -> str:
    lines = []
    path = data.get("path", "?")
    lines.append(f"{indent}## {path}")
    lines.append("")
    if data.get("error"):
        lines.append(f"{indent}  Error: {data['error']}")
        return "\n".join(lines)
    if data.get("module_doc"):
        lines.append(f"{indent}  {data['module_doc']}")
        lines.append("")
    lines.append(f"{indent}  Lines: {data.get('lines', 0)}")
    if data.get("imports"):
        imp = ", ".join(data["imports"][:15])
        if len(data["imports"]) > 15:
            imp += f" (+{len(data['imports'])-15} more)"
        lines.append(f"{indent}  Imports: {imp}")
    if data.get("classes"):
        for c in data["classes"]:
            lines.append(f"{indent}  Class: {c['name']}")
            if c.get("doc"):
                lines.append(f"{indent}    {c['doc'][:200]}")
            lines.append(f"{indent}    Methods: {c.get('method_count', 0)}")
    if data.get("functions"):
        for f in data["functions"]:
            doc = f.get("doc", "")[:100]
            lines.append(f"{indent}  def {f['name']}{f.get('sig','')}: {doc}")
    lines.append("")
    return "\n".join(lines)


def _tree_to_str(files: List[Path]) -> List[str]:
    lines = []
    for f in files:
        lines.append(f"  {f}")
    return lines


def _generate_full_report() -> str:
    """Report with full source code of every file."""
    files = _collect_python_files()
    sections = []
    sections.append("=" * 80)
    sections.append("THRESHOLD_ONSET - FULL PROJECT SOURCE (main.py excluded)")
    sections.append("=" * 80)
    sections.append("")
    for f in files:
        full_path = ROOT / f
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            source = f"# Error reading: {e}"
        sections.append("")
        sections.append("#" * 80)
        sections.append(f"# FILE: {f}")
        sections.append("#" * 80)
        sections.append("")
        sections.append(source)
        sections.append("")
    return "\n".join(sections)


def _run_all() -> int:
    """Execute all 10 pipeline steps. Returns exit code."""
    sep = "=" * 70
    print(f"\n{sep}\nTHRESHOLD_ONSET — RUNNING ALL\n{sep}\n")
    results = []
    for name, script in PIPELINE_STEPS:
        print(f"\n{sep}\nRUNNING: {name}\n{sep}")
        cmd = [sys.executable, str(ROOT / script)]
        result = subprocess.run(cmd, cwd=str(ROOT), capture_output=False, check=False)
        ok = result.returncode == 0
        results.append((name, ok))
        print(f"\n[{name}] {'PASS' if ok else 'FAIL'} (exit {result.returncode})")
    print(f"\n{sep}\nSUMMARY\n{sep}")
    for name, ok in results:
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")
    passed = sum(1 for _, ok in results if ok)
    print(f"\nTotal: {passed}/{len(results)} passed\n{sep}")
    return 0 if passed == len(results) else 1


def _generate_simple_report() -> str:
    """Human-readable overview. No module dump."""
    sections = []
    sections.append("=" * 70)
    sections.append("THRESHOLD_ONSET — Project Overview")
    sections.append("=" * 70)
    sections.append("")
    sections.append("WHAT THIS PROJECT DOES")
    sections.append("-" * 40)
    sections.append("Structure emerges from action and repetition, before symbols or meaning.")
    sections.append("Text -> tokens -> residues -> identities -> relations -> symbols -> text.")
    sections.append("No embeddings. No neural nets. Pure structure.")
    sections.append("")
    sections.append("HOW TO RUN")
    sections.append("-" * 40)
    sections.append("  python main.py                    # Full 10-step suite")
    sections.append("  python main.py --check \"text\"     # Quick pipeline check")
    sections.append("  python main.py --user \"text\"      # Full suite with your text")
    sections.append("  python integration/run_complete.py # Direct pipeline")
    sections.append("")
    sections.append("PIPELINE (text -> structure -> text)")
    sections.append("-" * 40)
    sections.append("  1. run_complete.py / run_user_result.py  — Full pipeline")
    sections.append("  2. phase0–4 (threshold_onset)               — Structure emergence")
    sections.append("  3. phase5–9 (semantic)                     — Meaning, roles, fluency")
    sections.append("  4. generate.py, scoring.py, surface.py    — Generation, scoring, output")
    sections.append("")
    sections.append("PHASES")
    sections.append("-" * 40)
    sections.append("  phase0  Action, trace, repetition")
    sections.append("  phase1  Boundaries, clusters")
    sections.append("  phase2  Identity detection, persistence")
    sections.append("  phase3  Relations, graph")
    sections.append("  phase4  Symbol aliasing")
    sections.append("  phase5–9  Consequence, meaning, roles, constraints, fluency")
    sections.append("")
    sections.append("KEY SCRIPTS")
    sections.append("-" * 40)
    sections.append("  run_all.py, main.py              — Orchestrators")
    sections.append("  integration/benchmark.py         — 39-sample benchmark")
    sections.append("  integration/baselines.py         — Random, Markov, Echo, Uniform")
    sections.append("  integration/external_validation.py — 136 external samples")
    sections.append("")
    sections.append("For full module details: python project_viewer.py --verbose")
    sections.append("To run everything: python project_viewer.py (default)")
    sections.append("=" * 70)
    return "\n".join(sections)


def _generate_report() -> str:
    files = _collect_python_files()
    parsed = [_parse_file(f) for f in files]

    sections = []

    # Header
    sections.append("=" * 80)
    sections.append("THRESHOLD_ONSET - COMPREHENSIVE PROJECT VIEW")
    sections.append("=" * 80)
    sections.append("")
    sections.append("Excludes: main.py")
    sections.append(f"Total Python files: {len(files)}")
    sections.append("")

    # File list
    sections.append("=" * 80)
    sections.append("PROJECT STRUCTURE (all .py files, main.py excluded)")
    sections.append("=" * 80)
    sections.extend(_tree_to_str(files))
    sections.append("")

    # Pipeline flow
    sections.append("=" * 80)
    sections.append("PIPELINE FLOW (text -> structure -> text)")
    sections.append("=" * 80)
    sections.append("  1. integration/run_complete.py     - Full end-to-end pipeline")
    sections.append("  2. integration/run_user_result.py - User-facing output only")
    sections.append("  3. integration/benchmark.py      - Metrics, run_pipeline()")
    sections.append("  4. threshold_onset/phase0-4       - Structure emergence")
    sections.append("  5. threshold_onset/semantic/phase9 - Symbol decoder, fluency")
    sections.append("  6. integration/generate.py        - Constraint-aware generation")
    sections.append("  7. integration/scoring.py       - Path scoring, input-order boost")
    sections.append("  8. integration/surface.py       - Symbol->token mapping")
    sections.append("")

    # Module index
    sections.append("=" * 80)
    sections.append("MODULE INDEX (by directory)")
    sections.append("=" * 80)

    by_dir: Dict[str, List[Dict]] = {}
    for p in parsed:
        if "error" in p:
            continue
        dirname = str(Path(p["path"]).parent)
        if dirname == ".":
            dirname = "(root)"
        if dirname not in by_dir:
            by_dir[dirname] = []
        by_dir[dirname].append(p)

    for dirname in sorted(by_dir.keys(), key=lambda x: (x.count("/"), x)):
        sections.append("")
        sections.append(f"--- {dirname} ---")
        for p in by_dir[dirname]:
            sections.append(_format_module(p, "  "))

    # Key entry points
    sections.append("=" * 80)
    sections.append("KEY ENTRY POINTS")
    sections.append("=" * 80)
    sections.append("  run_all.py                    - Orchestrator (legacy)")
    sections.append("  integration/run_complete.py    - Full pipeline, step-by-step")
    sections.append("  integration/run_user_result.py - Clean output for users")
    sections.append("  integration/run_user_input.py  - Quick pipeline (benchmark)")
    sections.append("  integration/benchmark.py       - 39-sample benchmark")
    sections.append("  integration/baselines.py       - Random, Markov, Echo, Uniform")
    sections.append("  integration/external_validation.py - 136 external samples")
    sections.append("  integration/validate_pipeline.py  - 7 input-type validation")
    sections.append("  integration/stress_test.py    - Scale 100-5000 tokens")
    sections.append("  integration/structural_scaling.py - Topology law experiment")
    sections.append("")

    # Phase descriptions
    sections.append("=" * 80)
    sections.append("THRESHOLD_ONSET PHASES (structure emergence)")
    sections.append("=" * 80)
    sections.append("  phase0 - Action, trace, repetition (no identity)")
    sections.append("  phase1 - Clustering, boundaries, patterns")
    sections.append("  phase2 - Identity detection, persistence")
    sections.append("  phase3 - Relations, graph, edges")
    sections.append("  phase4 - Symbol aliasing, identity->symbol")
    sections.append("  semantic/phase5-9 - Consequence, rollout, meaning, roles, decoder")
    sections.append("")

    # Integration module roles
    sections.append("=" * 80)
    sections.append("INTEGRATION MODULE ROLES")
    sections.append("=" * 80)
    sections.append("  generate.py     - Constraint-aware symbol sequence generation")
    sections.append("  scoring.py      - Path scoring, input-order boost, pressure")
    sections.append("  surface.py      - Symbol->token mapping, sentence boundaries")
    sections.append("  escape_topology.py - Measure escape paths, pressure")
    sections.append("  continuation_observer.py - Refusal tracking, adjacency")
    sections.append("  preference_learner.py - Learned bias on edges")
    sections.append("  unified_system.py - process_text_through_phases, TokenAction")
    sections.append("")

    return "\n".join(sections)


def main() -> int:
    out_file = None
    as_json = False
    full_source = False
    verbose = False
    describe = False
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] == "--out" and i + 1 < len(argv):
            out_file = argv[i + 1]
            i += 2
        elif argv[i] == "--json":
            as_json = True
            i += 1
        elif argv[i] == "--full":
            full_source = True
            i += 1
        elif argv[i] in ("--verbose", "--simple"):
            verbose = True
            i += 1
        elif argv[i] == "--describe":
            describe = True
            i += 1
        else:
            i += 1

    # Default: run everything
    if not (describe or verbose or full_source or as_json or out_file):
        return _run_all()

    files = _collect_python_files()
    parsed = [_parse_file(f) for f in files]

    if verbose:
        output = _generate_report()
    elif full_source:
        output = _generate_full_report()
        if not out_file:
            out_file = "PROJECT_FULL_SOURCE.txt"
    elif as_json:
        data = {
            "project": "THRESHOLD_ONSET",
            "excludes": ["main.py"],
            "file_count": len(files),
            "files": [str(f) for f in files],
            "modules": parsed,
        }
        output = json.dumps(data, indent=2)
    else:
        output = _generate_simple_report()

    if out_file:
        Path(out_file).write_text(output, encoding="utf-8")
        print(f"Written to {out_file}")
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
