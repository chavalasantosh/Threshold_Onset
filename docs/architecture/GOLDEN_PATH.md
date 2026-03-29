# Canonical developer path (golden path)

Use this when the repo feels too large or unclear. **One spine**: install → smoke tests → everything else is optional.

## 1. Environment

From the repository root:

```bash
pip install -e ".[dev]"
```

(`pytest` comes from the `dev` extra; core library code is still stdlib-oriented.)

## 2. Fast verification (required before “the project is broken”)

```bash
python scripts/dev_check.py
```

This runs a **small** pytest subset (line codec + API smoke). If this passes, the **packaging import path and core API wiring** are OK.

Full test sweep (slower, may need more deps for some files):

```bash
python -m pytest tests/ -q
```

## 3. What to run for “the system” (pick one)

| Goal | Command |
|------|---------|
| Full scripted pipeline | `python integration/run_complete.py` (see `docs/EXECUTION.md`) |
| Legacy entry | `python main.py` or `python run_all.py` |
| HTTP health / process API | `python scripts/health_server.py` then hit `/health` (see `scripts/health_server.py` docstring) |
| CLI (if installed) | `threshold-onset health` (after `pip install -e .`) |

Do **not** treat all of these as mandatory every day—pick the path that matches what you are debugging.

## 4. Mental model (one sentence)

**`threshold_onset/`** = phased + semantic library; **`integration/`** = wiring and runners; **`santok_complete/`** = tokenizer subsystem; **`scripts/`** = tools. If lost, start from **`threshold_onset.api`** (`process`) or **`integration/run_complete.py`**, not from every doc at once.

## 5. Data and Git (avoid repeat disasters)

- **Huge corpora and generated files stay out of Git** — use local paths, `.gitignore`, optional submodules, or separate storage.
- Do not commit multi‑GB or >100 MB blobs into normal Git history; GitHub will reject them.

## 6. Where to read next

- `QUICK_START.md` — short run instructions
- `docs/API.md` — programmatic API
- `docs/EXECUTION.md` — execution modes
