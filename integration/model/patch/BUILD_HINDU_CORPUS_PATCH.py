"""
PATCH for build_hindu_corpus.py
================================

The run logs show two separate problems. This file documents exactly what to
change in build_hindu_corpus.py to fix both.

PROBLEM 1 — Run1: generation running during training (SLOW)
────────────────────────────────────────────────────────────
In the old pipeline config used by run1, generation was NOT disabled.
This caused runs like block 2 to take 50,892 seconds (14 hrs) just on
generation during a training pass. Generation during training is useless —
you're building path_scores, not generating text.

The v4 santek_base_model.py already fixes this with:
  cfg.generation.num_sequences = 0
  cfg.generation.steps = 0

But build_hindu_corpus.py calls the pipeline separately and may not be
setting these flags. Check your _run_pipeline call in build_hindu_corpus.py
and make sure it sets these.

PROBLEM 2 — Run2: corpus state init failed 8,704 times (68.6% of runs)
────────────────────────────────────────────────────────────────────────
The error:
  Invalid control character at: line 149367 column 89 (char 23336583)

This is a corrupted line in your JSONL corpus. The corpus state loads the
full JSONL into memory and json.loads() chokes on the bad character.
Fix: run fix_corpus.py (in this directory) to clean the file.

PROBLEM 3 — run2 outputs=0 (NOT A BUG)
────────────────────────────────────────
This is intentional. Training runs skip generation. This is correct.
After training completes, use:
  python santek_base_model.py generate "your prompt"
to see actual output.
"""

# ─────────────────────────────────────────────────────────────────────────────
# PATCH: In build_hindu_corpus.py, find the function that calls the pipeline
# and add these two lines wherever PipelineConfig is constructed:
# ─────────────────────────────────────────────────────────────────────────────

PATCH_PIPELINE_CONFIG = """
# ADD THESE LINES wherever you build cfg in build_hindu_corpus.py:
cfg.generation.num_sequences = 0   # skip generation during training
cfg.generation.steps = 0           # skip generation during training
cfg.show_tui = False               # no TUI during batch training
"""

# ─────────────────────────────────────────────────────────────────────────────
# PATCH: corpus loading in build_hindu_corpus.py
# ─────────────────────────────────────────────────────────────────────────────

PATCH_CORPUS_LOAD = """
# REPLACE your corpus loading with this robust version that skips bad lines:

import json
from pathlib import Path

def load_corpus_safe(path):
    records = []
    bad = 0
    with open(path, encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                text = obj.get('text', '').strip()
                if text:
                    records.append(obj)
            except json.JSONDecodeError as e:
                bad += 1
                if bad <= 5:
                    print(f"  [WARN] Skipping bad line {i}: {e}")
    if bad:
        print(f"  [WARN] Skipped {bad} malformed lines in corpus")
    return records
"""
