# Gap to Model: Roadmap

This document captures the gap between the current **research architecture** and a **trained model** with a clear objective, learning loop, evaluation, and interface. It is a checklist for turning THRESHOLD_ONSET + SanTOK + Phases 5–9 into a legitimate, comparable model.

---

## What to do first (one path, in order)   

**Do not split effort.** Do not build the next layer (necessity/self-observation from `NEXT_LAYER_DESIGN.md`) until you have a **model** that has an objective and improves. More architecture on top of “structure discovery” does not fix the gap.

**Do this, in this order:**

1. **Pick one objective** (e.g. “predict next identity” given prefix). Write it in one sentence. Define one number that measures success (e.g. accuracy or log-score). Do nothing else until this is done.
2. **Add one learning rule** — something that changes a small set of parameters (e.g. transition counts or scores) when the model is right vs wrong. One loop: predict → compare to truth → update. No new phases, no new layers.
3. **Expose one interface** — e.g. `predict_next_identity(prefix)` or `generate(prompt, length)` that hides the pipeline and returns a single result. One command or one function call for “run the model.”
4. **One task, one baseline** — evaluate that objective on a fixed dataset (e.g. 10k tokens); run the same task with a trivial baseline (e.g. bigram or Markov). Report the same metric for both. Now you can say “this is better/worse/different.”

After 1–4 you have a **model**. Then (and only then) consider Layer 10 (necessity/self-observation) as an optional add-on that reads from that model.

**You vs Qwen:** Qwen 0.6B = 600M parameters, next-token prediction. You = structure (identities, relations, constraints), few or no neural weights. Different axis. “Having a model” for you = one task + one interface + one metric + one update rule. Not “match 0.6B parameters.”

---

## Current State

**What the system is today:** A pipeline that discovers structure (tokenization → residue → identity → relation → symbol → consequence → meaning → roles → constraints → fluency). It observes and enforces structure; it does not yet **improve from a single, measurable objective**.

**What we have that is rare and valuable:**
- Structural representation of sequences (identities, relations, symbols)
- Deterministic constraint enforcement
- Refusal mechanism
- Identity graph
- Consequence field concept

**Goal (realistic):** Prove the architecture works at **small scale** — not to beat 100B+ LLMs.

---

## 1. Clear Model Objective

| Need | Current | Target |
|------|--------|--------|
| Single task the system optimizes | Structure discovery (descriptive) | One of: **predict next identity** or **maximize structural stability** (or another well-defined objective) |

**Action items:**
- [ ] Choose and document the **primary objective** (e.g. next-identity prediction, or stability under perturbation).
- [ ] Define **success metric** for that objective (e.g. accuracy, log-probability, or stability score).
- [ ] Ensure the pipeline has a **single head** that can be scored and improved (e.g. transition / identity predictor).

---

## 2. Real Learning Loop

| Need | Current | Target |
|------|--------|--------|
| Adaptation | Mostly observation; little parameter update | Explicit **update rule** driven by prediction error or reward |

**Action items:**
- [ ] Define **parameters** that can change (e.g. transition scores, identity weights, or constraint weights).
- [ ] Define **learning rule**: e.g. `score += reward`, `score -= penalty`, or a simple gradient-free update from prediction error.
- [ ] Implement one **minimal loop**: input → prediction → error/reward → update parameters → repeat.
- [ ] Avoid requiring neural nets if desired; tabular or count-based updates are sufficient for a first version.

---

## 3. External Evaluation (Tasks)

| Need | Current | Target |
|------|--------|--------|
| Evaluation | Internal metrics (entropy, cluster stability, constraint rigidity) | **Tasks** that outsiders recognize (e.g. next-token/identity prediction, stability under perturbation, or a small benchmark) |

**Action items:**
- [ ] Pick 1–2 **external tasks** (e.g. next-identity prediction on held-out text, or stability score on perturbed inputs).
- [ ] Define **train/val/test** or fixed evaluation sets.
- [ ] Report **task metrics** (accuracy, loss, or task-specific score) in addition to internal metrics.

---

## 4. Clean Model Interface

| Need | Current | Target |
|------|--------|--------|
| Usage | Multi-step pipeline (SanTOK → Phase 0 → … → Phase 9) | **Simple API** for “run as a model” |

**Action items:**
- [ ] Expose at least one of: `model.predict(text)` or `model.generate(prompt)` (or equivalent: e.g. `predict_next_identity(prefix)`).
- [ ] Document **minimal usage** (install, one command, one code snippet).
- [ ] Keep pipeline details internal; the interface should hide phases and options for the default case.

---

## 5. Scale Experiments

| Need | Current | Target |
|------|--------|--------|
| Data scale | Small text samples | **Larger data** to observe scaling and stability |

**Action items:**
- [ ] Run on **100k tokens** (then 1M if feasible).
- [ ] Record **learning curves** or stability vs. corpus size.
- [ ] Document **scaling behavior** (e.g. identity count, relation count, runtime, memory).

---

## 6. Comparative Baseline

| Need | Current | Target |
|------|--------|--------|
| Comparison | No direct comparison to simple models | **Baselines** on the same task and data |

**Action items:**
- [ ] Compare against at least one of: **n-gram**, **Markov chain**, or **simple transformer** on the **same objective** (e.g. next-token or next-identity prediction).
- [ ] Report **same metrics** for baseline(s) and THRESHOLD_ONSET so the approach can be judged as better, worse, or different.

---

## 7. Formal Theory Documentation

| Need | Current | Target |
|------|--------|--------|
| Theory | Ideas (structure → constraint → refusal → necessity) | **Formal terms**: state space, transition function, constraint operator, learning rule |

**Action items:**
- [ ] Write a short **formal specification**: state space, transition function, constraint operator, and (once chosen) learning rule.
- [ ] Use it as the single reference for “what the model is” so the project is scientific rather than only philosophical.

---

## Summary: Four Additions That Make It a Model

1. **Clear objective** — e.g. predict next identity (or maximize structural stability).
2. **Learning rule** — update transition (or other) scores based on success/failure.
3. **Larger-scale training** — run over 100k+ tokens (then more if possible).
4. **Benchmark evaluation** — same task, same metrics, compare against simple models (n-gram, Markov, etc.).

---

## Scope Reminder

**Do not** aim to beat large LLMs (Claude, Qwen, etc.).  
**Do** aim to prove the architecture works at small scale with a clear objective, a real learning loop, and comparable evaluation. That is already a strong result.

---

## First runnable step (done)

- **Contract:** `docs/MODEL_CONTRACT.md` — inputs, outputs, invariants, no magic.
- **API module:** `integration.model` — `evaluate(state, config)`, `evaluate_with_learning(state, config)`, `ModelConfig.from_project()`. See `integration/model/README.md`.
- **CLI:** `python integration/model_predict_next.py "your text"` or `--learn` / `--eta 0.1`. Thin wrapper over the API.
- **Config:** `config/default.json` under `"model"`: `learning_rate`, `prediction_method`.
- **Tests:** `tests/test_model_api.py` — contract, evaluate/evaluate_with_learning, learning copy-only.
- **What to do next:** Run on larger data (e.g. 100k tokens), then add a simple baseline (e.g. bigram) and report both accuracies.
