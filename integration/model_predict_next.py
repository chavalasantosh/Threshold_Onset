#!/usr/bin/env python3
"""
CLI for predict-next-identity model.

Thin wrapper: runs pipeline with return_model_state=True, then calls
integration.model.evaluate or evaluate_with_learning. No business logic here.
Contract: docs/MODEL_CONTRACT.md. API: integration.model.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    args = list(sys.argv[1:])
    learn = "--learn" in args
    if learn:
        args.remove("--learn")
    eta: float = 0.1
    if "--eta" in args:
        idx = args.index("--eta")
        if idx + 1 < len(args):
            try:
                eta = float(args[idx + 1])
            except ValueError:
                pass
            args.pop(idx)
            args.pop(idx)
    text = " ".join(args).strip() if args else ""
    if not text:
        text = (
            "Action before knowledge. "
            "Function stabilizes before meaning appears. "
            "Structure emerges before language exists."
        ).strip()

    from integration.model import evaluate, evaluate_with_learning, ModelConfig
    from integration.run_complete import run, PipelineConfig

    pipeline_cfg = PipelineConfig.from_project()
    pipeline_cfg.show_tui = False
    result = run(
        text_override=text,
        cfg=pipeline_cfg,
        return_result=True,
        return_model_state=True,
    )
    if not result or not result.model_state:
        print("Error: Pipeline failed or did not return model state.", file=sys.stderr)
        sys.exit(1)

    model_cfg = ModelConfig.from_project()
    model_cfg.learning_rate = eta
    if learn:
        r = evaluate_with_learning(result.model_state, model_cfg)
    else:
        r = evaluate(result.model_state, model_cfg)

    if r.error:
        print("Error:", r.error, file=sys.stderr)
        sys.exit(1)

    print("Model: predict next identity")
    print("Text length:", len(text), "chars,", len(text.split()), "tokens (whitespace)")
    print("Learning:", "on (eta={})".format(eta) if learn else "off")
    print("Next-identity prediction accuracy:", f"{r.accuracy:.4f}")
    print("Predictions: {} correct / {} total".format(r.correct_predictions, r.total_predictions))
    sys.exit(0)


if __name__ == "__main__":
    main()
