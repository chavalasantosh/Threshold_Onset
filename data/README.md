# Data / corpus for SanTEK base model

**Canonical corpus (JSONL, recommended for V1)**

- One UTF-8 JSONL file: one JSON object per line.
- Each line: `{"id": "...", "text": "...", "lang": "...", "domain": "..."}` (domain optional).
- Set `santek_base_model.corpus_jsonl` in config (e.g. `data/corpus.jsonl`).
- Split is deterministic (stable hash) and stratified by `lang` into train/val/test (default 80/10/10).
- Training uses **train** only; eval uses train + val (or val from file if not using JSONL).

**Training corpus (public data by default)**

- **Default:** `santek_base_model.training_corpus_urls` — list of public-domain URLs. Each is downloaded once to `data/cache/corpus_<hash>.txt`. Current default:
  - **Bhagavad Gita** (The Song Celestial, Sir Edwin Arnold) — Project Gutenberg epub/2388
  - **The Light of Asia** (Buddha’s life in verse, Sir Edwin Arnold) — Project Gutenberg epub/8920  
  So training uses **real Hindu/Indic spiritual texts** from the start, no toy examples.
- **Single URL:** `santek_base_model.training_corpus_url` — one URL, cached as `data/cache/downloaded_corpus.txt`.
- **Local file:** `santek_base_model.training_corpus_file` — one document per line.
- **Inline list:** `santek_base_model.training_corpus` — array of strings in config.

Use `training_corpus_split`: `"paragraphs"` (split on blank lines) or `"lines"`.  
Order: `training_corpus_urls` → `training_corpus_url` → local file → list. To use only your own file, set `training_corpus_urls` to `[]` and `training_corpus_url` to `""`.

**Train / val / test (for eval)**

- Training uses only the **train** source above. No val/test data is used during training.
- For held-out evaluation (`python santek_base_model.py eval`), set in config:
  - `training_corpus_file_val` — path to a file with **one document per line** (validation set).
  Optionally `training_corpus_file_test` for a separate test set later.
- Eval reports model accuracy and a **frequency baseline** (most-common next symbol in train) on the same val data.

**Hindu spiritual corpus (real data only)**

- **Default: real public-domain texts.** `docs/Hindu spiritual corpus.py` downloads actual books from Project Gutenberg (Bhagavad Gita, Upanishads, Light of Asia). Cached under `data/cache/`. No generated or hand-typed content.
- Use **`--corpus-file path`** to train on your own JSONL instead.
  - `python "docs/Hindu spiritual corpus.py"` — train on real Gutenberg texts (300 epochs)
  - `python "docs/Hindu spiritual corpus.py" --info` — corpus stats
  - `python "docs/Hindu spiritual corpus.py" --corpus-file data/your_corpus.jsonl`

**Override from CLI**

```bash
python santek_base_model.py train --corpus "first document text" "second document text"
```

So the code does not assume or inject any fixed “test” text; it uses what you provide in config or on the command line.
