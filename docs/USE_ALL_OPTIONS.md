# Use All Options — No Settling for One

This project supports **multiple options** in many dimensions. The rule: **use the full set from config, not a single default.**

When config (or a canonical list) defines several choices, the pipeline and scripts **run for each** and report all, so we get the "full meal" instead of "only water."

---

## Dimensions (config → behaviour)

| Dimension | Config key(s) | Single-choice fallback | "Use all" behaviour |
|----------|----------------|------------------------|---------------------|
| **Tokenization** | `pipeline.tokenization_methods` | `tokenization_method: "word"` | Pipeline and run_full_clean_log run for each of the 9 methods (whitespace, word, character, grammar, subword, subword_bpe, subword_syllable, subword_frequency, byte). |
| **Prediction** | `model.prediction_methods` | `prediction_method: "highest_score"` | Generation (and predict-next) run for each of highest_score, weighted_random when list is set. |
| **Continuation** | `pipeline.continuation_texts` | `continuation_text: "..."` | Continuation observation runs for each string in the list when set. |
| **Benchmark sizes** | `benchmark.sizes` | (hardcoded list in stress_test) | Stress test and benchmark use all sizes from config when available. |
| **Benchmark runs** | `benchmark.num_runs` | (hardcoded 3) | Benchmark uses this count for runs per sample. |
| **Generation methods** | Aligned with `model.prediction_methods` | `GenerationConfig.method` | When prediction_methods is set, generation produces outputs for each method. |

---

## Config shape (optional lists)

In `config/default.json` you can use **plural list keys** to enable "use all":

- `pipeline.tokenization_methods` — list of tokenization methods (already used).
- `pipeline.continuation_texts` — optional list of continuation strings; if present, continuation observation runs for each.
- `model.prediction_methods` — optional list of prediction methods (e.g. `["highest_score", "weighted_random"]`); if present, generation and predict-next use all.
- `benchmark.sizes` — list of token counts for stress/scale runs; scripts use all.
- `benchmark.num_runs` — number of runs per benchmark sample.

When a list is set, code **iterates over every element**. When only the singular key is set (or missing), behaviour stays backward-compatible with a single choice.

---

## Scripts that honour "use all"

- **integration/run_complete.py** — tokenization_methods, continuation_texts, prediction_methods (generation).
- **scripts/run_full_clean_log.py** — all tokenization methods; can be extended for prediction methods and continuation texts.
- **integration/stress_test.py** — benchmark.sizes, benchmark.num_runs from config when available.
- **integration/benchmark.py** — benchmark.num_runs and corpus/sizes from config when wired.

---

## Adding a new dimension

1. Add the **list key** to config (e.g. `foo_options: [a, b, c]`) and keep a singular default for backward compat.
2. In the relevant pipeline or script: **if list is set, loop over it**; else use the single value.
3. Update this doc and any run_full_clean_log / CLI logic so the full set is exercised and logged.
