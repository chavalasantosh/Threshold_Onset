# Structural Prediction Loop — Own Algorithm

**Script:** `integration/structural_prediction_loop.py`  
**Principle:** "Given this input, predict this output, measure how wrong I was, update, repeat."  
**No third-party:** Only stdlib and this project's pipeline (`run_complete`). All representation, metric, and update rule are our own.

---

## 1. Loop (high level)

1. **Input** → run pipeline once → get **structural state** (symbols from recurrence, path scores from phase scoring).
2. **Predict** next symbol at each position (our rule below).
3. **Measure** how wrong we were → **Structural Prediction Error (SPE)**.
4. **Update** path scores using **Path Reinforcement** (our rule below).
5. **Repeat** for the next epoch (same sequence, updated scores).

---

## 2. Representation (ours)

- **Symbol sequence:** Built from pipeline `model_state`: `residue_sequences` + Phase 2 `identity_mappings` (segment hash → identity) + Phase 4 `identity_to_symbol` (identity → symbol). Segment = two consecutive residues; hash = MD5 of `str(segment)` (same family as Phase 2). No external tokenizers or embeddings.
- **Path scores:** Dict `(current_symbol, next_symbol) → float` from the pipeline’s own scoring. We only read and update a **copy**; we never mutate pipeline output.

---

## 3. Prediction rule (ours)

- **Input:** Current symbol `s`, path scores `S`.
- **Output:** Next symbol with **maximum** `S[(s, next)]` over all `(s, next)` in `S`. Ties broken by first key in iteration order (deterministic).
- No softmax, no sampling from an external library — just “best score from current.”

---

## 4. Wrongness measure (ours)

- **Structural Prediction Error (SPE):** For every position in every symbol sequence: compare **predicted** next vs **actual** next.  
  `SPE = total_wrong / total_predictions` in [0, 1].  
  So `accuracy = 1 - SPE`.
- We do not use cross-entropy, MSE, or any external loss. One scalar: fraction of positions wrong.

---

## 5. Update rule (ours): Path Reinforcement

- **Correct prediction:** `path_scores[(current, actual_next)] += eta`.
- **Wrong prediction:**  
  `path_scores[(current, predicted)] -= eta`  
  `path_scores[(current, actual_next)] += eta`
- `eta` = step size (from project `config/default.json` `model.learning_rate` or default 0.1). No gradients, no optimizers — only reinforce the path that happened and penalize the path we wrongly predicted.

---

## 6. Repeat

- Same text → same symbol sequences every epoch. Only path scores change. Each epoch: measure SPE → print → apply Path Reinforcement → next epoch.
- So we see SPE (and accuracy) over epochs; no separate “test” phase in the script (can be extended later with held-out segments if desired).

---

## 7. Usage

```bash
python integration/structural_prediction_loop.py "Your text here"
python integration/structural_prediction_loop.py --epochs 20 --eta 0.05 "Your text"
python integration/structural_prediction_loop.py --quiet "Short text"
```

Default input if no text: a short English sentence (pipeline default).

---

## 8. Dependencies

- **Standard library only:** `copy`, `hashlib`, `json`, `sys`, `pathlib`, `argparse`.
- **Project only:** `integration.run_complete.run(..., return_model_state=True)` to get structural state. No numpy, torch, sklearn, or any other third-party code or formulas.
