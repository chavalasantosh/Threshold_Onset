# SanTEK-SLE — Check and Fixes Applied

**File:** `santek_sle.py` (repo root)  
**Checked against:** THRESHOLD_ONSET pipeline contract, Phase 2 identity hashing, Phase 4 output shape.

---

## Issues found and fixed

### 1. Segment hash did not match Phase 2 (critical)

**Problem:** `_get_symbol_sequence` used `seg_raw = f"{r_a:.6f}|{r_b:.6f}"` and `hashlib.md5(seg_raw.encode()).hexdigest()`. Phase 2 uses `str(segment).encode('utf-8')` with `segment = (r_a, r_b)` (tuple). So the hash was different and `identity_mappings.get(seg_hash)` almost always returned `None` → empty or wrong sequence.

**Fix:** Added `_segment_hash(segment: Tuple[float, float])` that uses `str(segment).encode("utf-8")` → MD5, and use it in `_get_symbol_sequence`. Sequence now matches pipeline identity_mappings.

---

### 2. Working in identity space instead of symbol space (critical)

**Problem:** Pipeline `path_scores` keys are `(from_symbol, to_symbol)` with **Phase 4 integer symbols**, not identity hashes. The script used identity hashes (strings) for sequence and prediction, so `path_scores.get((current_id, to_id))` never matched (string vs int).

**Fix:**  
- `_get_symbol_sequence` now returns `List[int]`: segment → identity_hash → **symbol** via `identity_to_symbol`.  
- `_predict_next_identity` → `_predict_next_symbol(current_sym: int, path_scores)`; prediction and path_scores use `(int, int)`.  
- `_santek_tension` and `_apply_structural_delta` take symbol ints; keys are `(int, int)`.

---

### 3. Wrong Phase 4 key: `identity_aliases`

**Problem:** Code used `p4.get("identity_aliases", {})`. Phase 4 returns `identity_to_symbol`, `symbol_to_identity`, `identity_alias_count`, etc. There is no `identity_aliases` dict.

**Fix:** Removed use of `identity_aliases`. Sequence is built with `identity_to_symbol`; prediction uses only `path_scores` (symbol keys). Initialisation print uses `len(p4.get("identity_to_symbol", {}))`.

---

### 4. Merging path_scores from corpus

**Problem:** Pipeline can attach non-edge keys (e.g. `_context_counts`). Merging must keep only `(tuple of 2) → float` to satisfy the contract.

**Fix:** When merging, iterate `ps.items()` and only add entries where `edge` is a tuple of length 2 and `score` is numeric; cast to `(int(fr), int(to))` and `float(score)`.

---

### 5. Residue fingerprint (documentation)

**Problem:** `_santek_fingerprint(token, residue_sequences)` does not use `token`; it averages all residues per run. So it is not a per-token fingerprint and is unused in the training loop.

**Fix:** Left the function in place for the family concept; added a comment that `token` is unused and that the training loop uses symbol sequences from segment→identity→symbol. `_fingerprint_distance` remains unused.

---

## Verification

Run:

```bash
python santek_sle.py --corpus "Action before knowledge." --epochs 2
```

Expected: non-empty `seq_len`, predictions and tension reported, no KeyError/type errors. Observed: seq_len=5, 4/4 correct, 6 path edges, training completes.

---

## Summary

| Item | Before | After |
|------|--------|--------|
| Segment hash | `f"{r_a:.6f}\|{r_b:.6f}"` | `str((r_a, r_b))` (match Phase 2) |
| Sequence type | List of identity hashes (str) | List of symbols (int) |
| path_scores keys | Assumed (identity, identity) | (symbol, symbol) = (int, int) |
| phase4 key | identity_aliases | identity_to_symbol |
| Merge filter | None | Only (tuple len 2, float) |

The script is now aligned with the pipeline and runs correctly.
