#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
train_hindu_base_model.py — Launcher for build_hindu_corpus.py

Same pipeline, same flags. Use this name if you prefer it.

  python train_hindu_base_model.py --download-only
  python train_hindu_base_model.py --skip-download --epochs 2500
"""
import subprocess
import sys
from pathlib import Path

def main():
    root = Path(__file__).parent.resolve()
    script = root / "build_hindu_corpus.py"
    if not script.exists():
        print("build_hindu_corpus.py not found next to this script.", file=sys.stderr)
        sys.exit(1)
    cmd = [sys.executable, str(script)] + sys.argv[1:]
    sys.exit(subprocess.run(cmd, cwd=root).returncode)

if __name__ == "__main__":
    main()
