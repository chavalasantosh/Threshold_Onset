#!/usr/bin/env python3
"""
Create the first base model: run pipeline once and save path_scores to output/base_model.json.

Usage:
    python integration/create_base_model.py
    python integration/create_base_model.py "Your seed text here"
    python integration/create_base_model.py --out output/my_base_model.json

The base model can be loaded later with integration.model.base_model.load_base_model().
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Default seed text (short, enough to get path_scores)
DEFAULT_TEXT = "Action before knowledge. Function stabilizes before meaning appears."


def main() -> None:
    argv = sys.argv[1:]
    out_path = Path(ROOT / "output" / "base_model.json")
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 < len(argv):
            out_path = Path(argv[i + 1]).resolve()
            argv = argv[:i] + argv[i + 2 :]
    text = " ".join(argv).strip() if argv else DEFAULT_TEXT

    from integration.run_complete import run, PipelineConfig
    from integration.model.base_model import save_base_model
    from integration.model.config import ModelConfig

    cfg = PipelineConfig.from_project()
    cfg.show_tui = False

    print("Creating first base model...")
    print(f"  Seed text: {text[:60]}{'...' if len(text) > 60 else ''}")
    print(f"  Output:    {out_path}")

    result = run(
        text_override=text,
        cfg=cfg,
        return_result=True,
        return_model_state=True,
    )
    if result is None or result.model_state is None:
        print("ERROR: Pipeline did not return model state.", file=sys.stderr)
        sys.exit(1)

    path_scores = result.model_state.get("path_scores", {})
    if not path_scores:
        print("ERROR: No path_scores in result.", file=sys.stderr)
        sys.exit(1)

    model_cfg = ModelConfig.from_project()
    written = save_base_model(
        path_scores,
        path=out_path,
        learning_rate=model_cfg.learning_rate,
        prediction_method=model_cfg.prediction_method,
        source="create_base_model",
    )
    print(f"Done. Base model saved: {written}")
    print(f"  Path score edges: {len(path_scores)}")


if __name__ == "__main__":
    main()
