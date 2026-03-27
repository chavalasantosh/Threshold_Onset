# SanTEK Base Model — Observations from a Full Run

Notes from running `santek_base_model.py train`, `generate`, and `chat`. Things to observe carefully.

---

## 1. Corpus state JSON error (every pipeline run)

```
Corpus state init failed (disabling): Extra data: line 2213 column 2 (char 322421)
```

- **Meaning:** `output/corpus_state.json` is invalid for the loader — e.g. multiple JSON objects concatenated, or trailing content after the first object.
- **Effect:** Corpus persistence is disabled for that run; pipeline still runs.
- **Fix:** Delete or fix `output/corpus_state.json` (e.g. ensure it’s a single valid JSON object), or reset and let the pipeline rewrite it.

---

## 2. Train: convergence and model size

- **10/10 texts valid**, total 414 edges (sum across texts); after merge, **72 edges**, **9 vocab symbols** (first-seen wins per symbol).
- **Converged** at epoch 55 (tension 0.0995 &lt; 0.1). Best accuracy **99.15%** at epoch 27.
- **Observation:** The saved model is small (72 edges, 9 symbols). Good for the default corpus; prompts that use different words/symbols will not have edges in this graph.

---

## 3. Generate: out-of-corpus prompts

- Prompt: *"I'm so lonely, {lonely} and i wish i could find a lover who could kiss me and im crying in my room."*
- Pipeline produced **45 symbols**; vocab grew to **23** (prompt tokens merged).
- **Generated text** mixed corpus phrases (“meaning”, “telave”, “before”, “knowledge”, “action”, “stabilizes”, “hash”) with prompt words (“wish”, “lover”, “crying”, “room”).
- **Why:** Path scores only have **72 edges** over **9** training symbols. The prompt introduces many new symbols; the *continuation* is still driven by the small graph, so the tail of the generation collapses into the same high-scoring paths (e.g. “action before action knowledge stabilizes…”).

**Takeaway:** With a small training graph, out-of-corpus prompts get prompt-specific decoding at the start, then repetitive, corpus-style continuations.

---

## 4. Chat: short prompts and fallback

- **“hi”** → 1 token, 1 identity, **0 path_scores** (no edges from that symbol).
- **“who are you ?”** → 3 tokens, 3 identities, 6 path_scores (tiny local graph).
- **“end”** → same as “hi”: 1 token, 0 edges.

When the prompt yields **no outgoing edges** in the saved model, the code uses the **fallback start**: `best_edge = max(ps, key=...)` — i.e. start from the highest-scoring edge in the 72-edge model. So:

- **Model reply** is always the same trajectory: *“stabilizes action before action before action knowledge stabilizes…”*
- The user’s words (“hi”, “who are you”, “end”) don’t appear in the reply because their symbols are not in the training graph; generation is purely from the training path_scores.

**Takeaway:** Single-token or OOV prompts don’t connect to the training graph; chat falls back to the same canned path. To get varied, prompt-sensitive replies, the model needs either (a) a larger/more diverse training corpus, or (b) logic that uses prompt symbols and extends the graph at inference time.

---

## 5. Repetition in generation

- Phrase **“action before action before action knowledge stabilizes”** repeats.
- Structural Greedy Beam + recency penalty (window 6, penalty 0.3) still allow this because the *graph* has strong cycles (e.g. action → before → action). Recency only penalizes repeating the *same symbol* in the window; it doesn’t break cycles of two or three symbols.
- **Possible improvements:** Stronger recency over longer windows, n-gram or cycle penalties, or sampling instead of strict argmax.

---

## 6. Pipeline verbosity (fixed in code)

- Previously, every `_run_pipeline` call (train init, generate, each chat turn) ran the full pipeline with **TUI on**, so the console was flooded with step-by-step output.
- **Change:** `_run_pipeline` now builds a config with `show_tui=False` by default so train/generate/chat stay quiet unless you explicitly enable TUI.

---

## 7. Deprecation (fixed in code)

- `datetime.utcnow()` is deprecated; replaced with `datetime.now(timezone.utc)` in `save_model()`.

---

## 8. Summary table

| Observation              | Where it shows up              | Severity / action                          |
|--------------------------|--------------------------------|--------------------------------------------|
| corpus_state.json invalid| Every pipeline run             | Fix or reset file; optional for SanTEK BM  |
| Small graph (72 edges)   | generate/chat with OOV prompts | Expected for default corpus; train bigger  |
| Same reply for “hi”/“end”| Chat with 1 token              | Fallback start; need richer model or logic |
| Repetitive cycles       | Generated text                 | Tune recency / add cycle or n-gram penalty |
| TUI flood                | train/generate/chat            | Fixed: show_tui=False in _run_pipeline     |
| datetime.utcnow          | save_model                     | Fixed: use timezone.utc                    |

---

*Generated from a single full run (train → generate → chat). Re-run and compare after changing corpus, model size, or generation parameters.*
