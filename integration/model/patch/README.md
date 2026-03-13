# SanTEK Fix — What Went Wrong & Exactly What To Do

## What actually happened

### Run 1 (2,500 epochs)
- Generation was NOT disabled during training
- Every text ran through text generation during the training loop
- Block 2 alone took **14 hours** generating text that was thrown away
- This is why run1 took so long and only processed 6 texts

### Run 2 (25,000 epochs, 12,702 texts)
- Generation correctly disabled (outputs=0 is NOT a bug — it's correct for training)
- **BUT**: corpus JSON file has a corrupted character at char 23,336,583
- This caused 8,704 out of 12,693 runs (68.6%) to fall back to training
  without the shared corpus state
- The model was essentially trained on isolated texts for most of the run
- The shared identity/edge graph that makes SanTEK work was not built properly

### Run 2 outputs=0
- This is correct. Training does not generate text.
- After training you run: `python santek_base_model.py generate "your prompt"`

---

## Fix in 3 steps

### Step 1: Fix the corpus (ONE TIME, takes ~1 min)
```bash
python fix_corpus.py --input data/hindu_corpus_real.jsonl
```
This creates `data/hindu_corpus_clean.jsonl` with the bad character removed.
Verify it worked:
```bash
python fix_corpus.py --input data/hindu_corpus_clean.jsonl --verify-only
```
Expected: `✓ ALL CLEAN — no JSON errors found`

### Step 2: Run training (Run 3)
```bash
python run3_clean.py
```
This will:
- Use the clean corpus automatically
- Skip generation during training (fast)
- Use all 9 tokenization methods (v4)
- Early stop when tension < 0.10 or plateaus
- Save model to `output/santek_base_model_v4.json`

Epochs are set to 500 with early stopping — it will stop much earlier when
the model converges. You do NOT need 25,000 epochs. The early stopping with
patience=5 will handle it.

### Step 3: Generate text
```bash
python santek_base_model.py generate "Om Namah Shivaya" --model output/santek_base_model_v4.json
python santek_base_model.py chat --model output/santek_base_model_v4.json
python santek_base_model.py eval --model output/santek_base_model_v4.json
```

---

## Files in this fix package

| File | What it does |
|------|-------------|
| `fix_corpus.py` | Scans and repairs the corrupted JSONL corpus |
| `run3_clean.py` | Run 3 launcher with all fixes baked in |
| `BUILD_HINDU_CORPUS_PATCH.py` | Documents patches needed in build_hindu_corpus.py |

---

## Why the 2 days were not completely wasted

- Run 1 proved the pipeline works end-to-end
- Run 2 identified the exact corpus corruption location (char 23,336,583)
- v4 santek_base_model.py is architecturally correct (9 methods, additive merge, ASD v4)
- The fix is one corrupted character in one file

---

## One thing to check in build_hindu_corpus.py

Find wherever you call PipelineConfig and make sure these lines are there:
```python
cfg.generation.num_sequences = 0   # skip generation during training
cfg.generation.steps = 0           # skip generation during training
cfg.show_tui = False
```
If they are missing, training will be extremely slow (like run1).
