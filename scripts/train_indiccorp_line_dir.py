#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Train SanTEK base model on Indic-style line corpora: one filesystem file at a time.

Each input file is read as UTF-8 text; every non-empty line becomes one training
text (no --max-texts cap). After training finishes for that file, the model is
written under --output-dir, then the next file is processed.

Typical layout:
  Plain text: data/telugu/indiccorp_telugu_line/part_aa
  HuggingFace shards: data/telugu/indiccorp_telugu_line/data/train-*.parquet (column 'text')

  Default --input-dir prefers .../indiccorp_telugu_line/data if that folder exists.

Usage (from repo root):
  python scripts/train_indiccorp_line_dir.py \\
    --output-dir output/telugu_indiccorp_models \\
    --epochs 18

  # Parquet requires: pip install pyarrow

  # List files and line counts only:
  python scripts/train_indiccorp_line_dir.py --dry-run

SanTEK training stays stdlib-only; Parquet reading uses optional pyarrow.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import traceback
from pathlib import Path
from typing import List, Optional, Tuple

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, OSError, ValueError):
    pass


def _find_repo_with_santek() -> Path:
    """
    Resolve repo root (directory containing santek_base_model.py).
    Search from this script, then from cwd, walking parents.
    """
    script_dir = Path(__file__).resolve().parent
    for base in [script_dir, *script_dir.parents]:
        if (base / "santek_base_model.py").is_file():
            return base
    cwd = Path.cwd().resolve()
    for base in [cwd, *cwd.parents]:
        if (base / "santek_base_model.py").is_file():
            return base
    return script_dir.parent


REPO_ROOT = _find_repo_with_santek()


def _default_indiccorp_input_dir() -> Path:
    """Prefer HF-style `.../indiccorp_telugu_line/data` when present."""
    base = REPO_ROOT / "data" / "telugu" / "indiccorp_telugu_line"
    nested = base / "data"
    if nested.is_dir():
        return nested
    return base


# Basenames (lowercase) to skip when scanning a data dir — not line corpora.
_SKIP_DOC_PLACEHOLDER_NAMES = frozenset(
    {
        "readme",
        "readme.md",
        "readme.txt",
        "readme.rst",
        "license",
        "license.txt",
        ".gitkeep",
        ".gitattributes",
    }
)


def _find_santek_model() -> Optional[Path]:
    p = REPO_ROOT / "santek_base_model.py"
    return p if p.is_file() else None


def _safe_stem(name: str) -> str:
    s = re.sub(r"[^\w\-.]+", "_", name, flags=re.UNICODE).strip("._")
    return s[:180] if s else "file"


def _load_line_corpus(path: Path) -> List[str]:
    if path.suffix.lower() == ".parquet":
        try:
            import pyarrow.parquet as pq  # type: ignore[import-untyped]
        except ImportError as e:
            raise RuntimeError(
                "Reading .parquet shards requires pyarrow. Install: pip install pyarrow"
            ) from e
        table = pq.read_table(path, columns=["text"])
        col = table.column("text")
        texts = col.to_pylist()
        out: List[str] = []
        for t in texts:
            if t is None:
                continue
            s = str(t).strip()
            if s:
                out.append(s)
        return out
    raw = path.read_text(encoding="utf-8", errors="replace")
    return [ln.strip() for ln in raw.splitlines() if ln.strip()]


def _dry_run_line_count(path: Path) -> Tuple[int, str]:
    """
    Return (count, label). Parquet uses file metadata row count (fast; includes empty rows).
    """
    if path.suffix.lower() == ".parquet":
        try:
            import pyarrow.parquet as pq  # type: ignore[import-untyped]
        except ImportError as e:
            raise RuntimeError(
                "Dry-run on .parquet requires pyarrow. Install: pip install pyarrow"
            ) from e
        n = int(pq.ParquetFile(path).metadata.num_rows)
        return n, "rows (parquet metadata)"
    return len(_load_line_corpus(path)), "lines"


def _iter_input_files(
    input_dir: Path,
    extensions: Optional[List[str]],
    *,
    include_doc_placeholders: bool,
) -> List[Path]:
    if not input_dir.is_dir():
        return []
    files: List[Path] = []
    for p in sorted(input_dir.iterdir(), key=lambda x: x.name.casefold()):
        if not p.is_file():
            continue
        if p.name.startswith("."):
            continue
        if not include_doc_placeholders and p.name.lower() in _SKIP_DOC_PLACEHOLDER_NAMES:
            continue
        if extensions is None:
            files.append(p)
            continue
        low = p.name.lower()
        if any(low.endswith(ext) for ext in extensions):
            files.append(p)
    return files


def _normalize_extensions(raw: str) -> Optional[List[str]]:
    if not raw.strip():
        return None
    out: List[str] = []
    for e in raw.split(","):
        e = e.strip().lower()
        if not e:
            continue
        out.append(e if e.startswith(".") else f".{e}")
    return out or None


def _unique_model_path(
    output_dir: Path,
    source_name: str,
    used: set[str],
) -> Path:
    """
    Avoid collisions when two different names sanitize to the same stem.
    """
    stem = _safe_stem(source_name)
    base = f"{stem}_santek_base.json"
    if base not in used:
        used.add(base)
        return output_dir / base
    n = 2
    while True:
        candidate = f"{stem}__{n}_santek_base.json"
        if candidate not in used:
            used.add(candidate)
            return output_dir / candidate
        n += 1


def _load_cmd_train():
    santek_path = _find_santek_model()
    if santek_path is None:
        print(
            "Cannot find santek_base_model.py (searched from script dir and cwd parents).",
            file=sys.stderr,
        )
        sys.exit(1)
    spec = importlib.util.spec_from_file_location(
        "santek_base_model_indiccorp", str(santek_path)
    )
    if spec is None or spec.loader is None:
        print("Failed to load module spec for santek_base_model.py", file=sys.stderr)
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Train SanTEK on each line file in a directory; save after each file."
    )
    ap.add_argument(
        "--input-dir",
        type=Path,
        default=_default_indiccorp_input_dir(),
        help=(
            "Directory of corpus files: UTF-8 text and/or HuggingFace .parquet (column text). "
            "Default: data/telugu/indiccorp_telugu_line/data if present, else .../indiccorp_telugu_line"
        ),
    )
    ap.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "output" / "telugu_indiccorp_models",
        help="Where to write one JSON model per input file",
    )
    ap.add_argument(
        "--extensions",
        type=str,
        default="",
        help="Comma-separated suffixes to include, e.g. '.txt,.dat' (default: all regular files)",
    )
    ap.add_argument(
        "--include-readme",
        action="store_true",
        help="Include README / LICENSE / .gitkeep-style files as corpus (default: skip them)",
    )
    ap.add_argument("--epochs", type=int, default=18)
    ap.add_argument("--eta", type=float, default=0.10)
    ap.add_argument("--decay", type=float, default=0.05)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print files and line counts; do not train",
    )
    ap.add_argument(
        "--continue-on-error",
        action="store_true",
        help="If one file fails, log and continue with the next (default: stop on first error)",
    )
    args = ap.parse_args()

    input_dir = args.input_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    exts = _normalize_extensions(args.extensions)

    if input_dir.exists() and not input_dir.is_dir():
        print(f"Not a directory: {input_dir}", file=sys.stderr)
        sys.exit(2)

    files = _iter_input_files(
        input_dir, exts, include_doc_placeholders=args.include_readme
    )
    if not files:
        print(f"No input files under: {input_dir}", file=sys.stderr)
        if not input_dir.is_dir():
            print("  (path does not exist or is not a directory)", file=sys.stderr)
        elif exts is not None:
            print(
                f"  (no files matching extensions: {', '.join(exts)})",
                file=sys.stderr,
            )
        elif not args.include_readme and input_dir.is_dir():
            skipped: List[str] = []
            for p in sorted(input_dir.iterdir(), key=lambda x: x.name.casefold()):
                if not p.is_file() or p.name.startswith("."):
                    continue
                if p.name.lower() in _SKIP_DOC_PLACEHOLDER_NAMES:
                    skipped.append(p.name)
            if skipped:
                print(
                    f"  (skipped documentation placeholders: {', '.join(sorted(set(skipped)))}; "
                    "use --include-readme to train on them, or add shard files)",
                    file=sys.stderr,
                )
        print(
            "Create the folder and place IndicCorp line shards there, or pass --input-dir.",
            file=sys.stderr,
        )
        sys.exit(2)

    print("=" * 64)
    print("  SanTEK — per-file line training (no max-texts cap per file)")
    print("=" * 64)
    print(f"  Input dir   : {input_dir}")
    print(f"  Output dir  : {output_dir}")
    print(f"  Files       : {len(files)}")
    print(f"  Epochs/file : {args.epochs}")
    print()

    output_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        total_lines = 0
        for p in files:
            try:
                n, label = _dry_run_line_count(p)
            except (OSError, RuntimeError) as e:
                print(f"  {p.name}: ERROR {e}", file=sys.stderr)
                continue
            total_lines += n
            print(f"  {p.name}: {n:,} {label}")
        print(f"  Total (all files): {total_lines:,}")
        return

    try:
        module = _load_cmd_train()
    except Exception:
        traceback.print_exc()
        sys.exit(1)

    used_names: set[str] = set()
    failed: List[str] = []

    for idx, path in enumerate(files, start=1):
        try:
            corpus = _load_line_corpus(path)
        except (OSError, RuntimeError) as e:
            msg = f"[{idx}/{len(files)}] READ ERROR {path.name}: {e}"
            print(msg, file=sys.stderr)
            failed.append(path.name)
            if not args.continue_on_error:
                sys.exit(1)
            continue
        except Exception as e:
            if isinstance(e, (KeyboardInterrupt, SystemExit)):
                raise
            msg = f"[{idx}/{len(files)}] READ ERROR {path.name}: {e}"
            print(msg, file=sys.stderr)
            traceback.print_exc()
            failed.append(path.name)
            if not args.continue_on_error:
                sys.exit(1)
            continue

        if not corpus:
            print(f"  [{idx}/{len(files)}] SKIP empty: {path.name}")
            continue

        model_path = _unique_model_path(output_dir, path.name, used_names)

        print()
        print("-" * 64)
        print(f"  [{idx}/{len(files)}] FILE: {path.name}")
        print(f"  Lines (texts): {len(corpus):,}")
        print(f"  -> Model: {model_path}")
        print("-" * 64)

        try:
            module.cmd_train(
                corpus=corpus,
                epochs=args.epochs,
                eta=args.eta,
                decay=args.decay,
                max_streak=3,
                tension_threshold=0.10,
                patience=5,
                model_path=model_path,
                verbose=True,
            )
        except KeyboardInterrupt:
            print(
                f"\nInterrupted during file {idx}/{len(files)}: {path.name}",
                file=sys.stderr,
            )
            sys.exit(130)
        except SystemExit as e:
            if e.code not in (0, None):
                failed.append(path.name)
                if args.continue_on_error:
                    print(f"  cmd_train exited with code {e.code}: {path.name}", file=sys.stderr)
                    continue
            raise
        except Exception:
            failed.append(path.name)
            traceback.print_exc()
            if not args.continue_on_error:
                sys.exit(1)
            continue

        print(f"  OK saved: {model_path}")

    print()
    print("=" * 64)
    if failed:
        print(f"  Finished with {len(failed)} failure(s): {failed}")
    else:
        print("  All files processed.")
    print("=" * 64)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
