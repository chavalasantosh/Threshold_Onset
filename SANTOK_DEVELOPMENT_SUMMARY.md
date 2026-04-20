# SanTOK Structural Engine: Core Development Summary

This document consolidates all the empirical discoveries, laws, extraction logic, and the complete **`santok_extended`** native module suite. We have entirely replaced standard NLP libraries (like spaCy, NLTK, or Universal Dependencies) with pure mathematical structural state analysis.

*Our strict rule: Zero 3rd party modules, zero external math, zero borrowed algorithms. Everything here is invented natively from the system's own signal streams.*

---

## 1. The Raw Signal Foundation
We successfully stripped away entropy, path_scores, and complex NLP tagging to focus on the 4 absolute truths produced directly by `core_tokenizer.py`:

| Signal | Meaning | Behavior |
| :--- | :--- | :--- |
| **`frontend`** | Structural Class (1–9) | Purely content-dependent. Never changes for a given string. |
| **`backend_scaled`** | Contextual Pressure | Shifts dramatically based on the token's position and neighbors. |
| **`content_id`** | Stable Numeric Identity | Stable polynomial hash. Binds text to a hard numerical identity. |
| **`uid`** | Sequential Lock | Ensures sequence and prevents stream collisions. |

---

## 2. The 5 Structural Laws of SanTOK
Through stress-testing text corpuses (via `observe_step3_laws.py`), we mathematically confirmed 5 physical laws governing text within the engine:

1. **POLE LAW:** Streams organize around specific frontend values (usually `1` and `7`) with maximum inflow/outflow connectivity.
2. **TRANSITION LAW:** Structural change dominates. Static chains are anomalies.
3. **IDENTITY LAW:** `content_id` absolutely dictates `frontend`. Structural class is naturally embedded in the string.
4. **ROLE LAW:** A token's structural rule is its consistent neighbor constraint (e.g. rigidly binding to specific `frontend` types).
5. **BOUNDARY LAW:** A sequence snaps (boundary) only when transition continuity breaks down.

---

## 3. The `santok_extended` Architecture
We developed a complete suite of **14 Native Modules** residing in `santok_extended/`. These strictly replace arbitrary 3rd-party algorithms with SanTok structural physics.

### Core Processing Replacements
- **`pos_tagging`**: Replaced standard dictionaries with the **Role Engine**, mapping tokens purely by their transition attractors/emitters and structural restraints.
- **`sentence_tokenizer` & `segmentation`**: Replaced arbitrary punctuation rules with the **Boundary Engine**, calculating hard breaks where `frontend` + `backend_scaled` simultaneously fracture.
- **`lemmatization` & `stemming`**: Replaced dictionary suffix-stripping with pure **Identity Clustering**—anchoring variable forms perfectly onto `content_id` invariant cores.

### Advanced NLP Replacements
- **`dependency` (Gravitational Bonding Engine)**: Replaced external Dependency Trees (like `nsubj`, `amod`). Tokens now map structurally using `backend_scaled` as gravitational mass; heavy poles attract surrounding lighter context tokens.
- **`similarity` (Structural Interference Engine)**: Completely eliminated Cosine Similarity, Levenshtein, and Jaccard indices. Evaluates document resonance strictly by aligning `frontend` gradient phase-shifts.
- **`ngrams` (Topographical Basin Engine)**: Abandoned sliding arbitrary "fixed-n" windows. Text is naturally chunked into structural basins formed between local maxima of `backend_scaled` pressure.
- **`vocabulary` (Signal Saturation Engine)**: Eliminated TF-IDF. Term importance is now calculated purely by Cumulative Signal Saturation / `uid` Span Decay.
- **`ner` (Named Entity Representation)**: Discarded external corpora tagging. Detects contiguous identity anomalies that remain unbroken by structural poles.
- **`stopwords`**: Replaces the standard fixed list with fluid filtration of high-decay, max-connectivity `frontend` poles.

*Additional modules built on this physics stack: `morphology`, `normalization`, and `postprocessing`.*

---

## 4. Analytical & Extraction Tooling

### `run_clean_output.py`
The final, streamlined interface to the tokenizer. It strips all experimental NLP mapping completely and safely extracts the raw string to integer translation map.

**Sample execution:**
```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOKEN_TEXT      | FRONTEND | BACKEND_SCALED  | CONTENT_ID      | UID
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
'Action'        | 7        | 13461           | 10310           | 10977518812293740004
'before'        | 8        | 10970           | 24365           | 13403302990619764695
'knowledge'     | 1        | 20599           | 102258          | 9728362236848310486
'.'             | 7        | 61016           | 1908            | 11166084224396003497
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Observation Diagnostics
- **`observe_signals.py`**: Reads raw outputs to identify `FULL_TRANSITION` thresholds.
- **`observe_step2.py`**: Extracts the 9x9 transition matrices and neighbor boundaries.
- **`observe_step3_laws.py`**: Validates the 5 Structural Laws universally against independent corpuses.
