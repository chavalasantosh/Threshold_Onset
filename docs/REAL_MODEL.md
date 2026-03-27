# Getting a real model

You get a **real model** when training finishes and writes `output/santek_base_model.json`. You can then run `generate` and `chat` against that file.

## Fastest way to a real model

From the repo root:

```powershell
python "docs/Hindu spiritual corpus.py" --minimal
```

- **Corpus:** first 10 Hindu spiritual texts (Vedas, Upanishads, Gita, etc.)
- **Epochs:** 15  
- **Time:** about 20–40 minutes (depends on machine; pipeline is ~2–3 min per text)
- **Output:** `output/santek_base_model.json` (path_scores + vocab)

When it finishes you have a real model. Then:

```powershell
python santek_base_model.py generate "Tat tvam asi"
python santek_base_model.py chat
```

## Better model (more data, more epochs)

```powershell
python "docs/Hindu spiritual corpus.py" --quick
```

- 40 texts, 40 epochs  
- Roughly 1–2 hours  
- Same output path: `output/santek_base_model.json`

## Full Hindu corpus

```powershell
python "docs/Hindu spiritual corpus.py" --epochs 80
```

- All 156 texts, 80 epochs  
- Several hours  
- Best quality for this corpus

## If a run is already in progress

Training may have been started in the background (e.g. `--quick` or `--epochs 80`). When it completes you will see:

- `output/santek_base_model.json` created/updated  
- Final lines in the terminal with “Model saved”, edges count, vocab size  

You can then use that file for `generate` and `chat` without running train again.

## Check that you have a real model

```powershell
python santek_base_model.py info
```

If the model file exists, this prints path, edge count, vocab size, and metadata. If you see “Model not found”, train once with `--minimal` (or `--quick` / full) and wait for it to finish.
