# Integration: threshold_onset <-> santok

**कार्य (kārya) happens before ज्ञान (jñāna)**

This directory contains the unified system that integrates threshold_onset with santok.

## Quick Run

From project root:
```bash
python main.py --check "Your text"   # Quick pipeline check (user-facing output)
python main.py --user "Your text"    # Full 10-step suite with your input
```

## Contents

- `run_complete.py` - Full end-to-end pipeline (tokenization, phases 0-4, generation)
- `run_user_result.py` - User-facing output only (used by main.py --check)
- `run_user_input.py` - Quick benchmark-style pipeline
- `benchmark.py` - 39-sample benchmark, run_pipeline()
- `unified_system.py` - Main unified system integration
- `example_unified.py` - Example usage of the unified system

## Overview

The unified system combines:
- **santok**: Text tokenization (action/kārya)
- **threshold_onset**: Structure emergence (knowledge/jñāna)

Text tokens become actions, token patterns become residues, and structure emerges naturally from token sequences.

## Status

This is experimental/integration work. The unified system is under development.
