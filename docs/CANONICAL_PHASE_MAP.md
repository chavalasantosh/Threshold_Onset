# Canonical phase map (no duplicates)

There is **exactly one** “Phase 5” in this repo: **semantic** consequence field.

| Phase(s) | Path | Meaning |
|----------|------|--------|
| **0–4** | `threshold_onset/phase0` … `phase4` | Structural pipeline (frozen foundation) |
| **10** | `threshold_onset/phase10` | Directed continuation on identity streams (structural metrics, **not** semantic) |
| **5–9** | `threshold_onset/semantic/phase5` … `phase9` | Semantic discovery (consequence field = **phase5** here only) |
| *(unnumbered)* | `threshold_onset/identity_conditioned/` | Empirical `(source_id, content_id, outcome_key)` counts — **not** “Phase 5”; see `docs/IDENTITY_CONDITIONED_CONTINUATION.md` |

**Removed confusion:** The old top-level package `threshold_onset/phase5/` (a tiny shim around directed counts) **no longer exists**. Use **`threshold_onset.phase10`** for that behavior.

**External writeups** sometimes say “continuation sits at the Phase 5 boundary.” In **this repo**, **structural** directed continuation is **Phase 10**; **semantic** Phase 5 is the **consequence field** under `semantic/phase5/`. Those are different folders and contracts.

**Config keys:** JSON `phase5` under semantic config refers to **semantic** Phase 5 (rollouts, k, etc.), not `threshold_onset/phase10`.
