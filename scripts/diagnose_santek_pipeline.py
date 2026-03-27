#!/usr/bin/env python3
"""
Diagnostic script: run pipeline for ONE text with return_model_state=True.
Use to verify pipeline returns model_state before debugging full corpus run.
"""
import os
import sys

# Ensure we're in repo root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

# Minimal env for fast run
os.environ.setdefault("SANTEK_TRAIN_FAST", "1")
os.environ.setdefault("PHASE1_SKIP_DISTANCES", "1")
os.environ.setdefault("PHASE3_SKIP_PATH_LENGTHS", "1")
os.environ.setdefault("THRESHOLD_ONSET_NUM_RUNS", "3")  # Must be >=2 for Phase 2 persistence

def main():
    from integration.run_complete import run, PipelineConfig

    text = "Action before knowledge. Function stabilizes before meaning appears."
    cfg = PipelineConfig.from_project()
    cfg.show_tui = True
    cfg.tokenization_method = "word"
    cfg.generation.num_sequences = 0
    cfg.generation.steps = 0

    print("Running pipeline with return_model_state=True...")
    result = run(
        text_override=text,
        cfg=cfg,
        return_result=True,
        return_model_state=True,
    )

    if result is None:
        print("[FAIL] run() returned None")
        return 1

    ms = getattr(result, "model_state", None)
    if ms is None:
        print("[FAIL] result.model_state is None")
        print(f"  result type: {type(result)}")
        print(f"  result keys: {getattr(result, '__dataclass_fields__', dir(result))}")
        return 1

    print("[OK] model_state present")
    print(f"  phase2_metrics keys: {list(ms.get('phase2_metrics', {}).keys())}")
    print(f"  path_scores count: {len(ms.get('path_scores', {}))}")
    print(f"  tokens count: {len(ms.get('tokens', []))}")
    print(f"  residue_sequences count: {len(ms.get('residue_sequences', []))}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
