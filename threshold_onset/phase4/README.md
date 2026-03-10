# Phase 4 — SYMBOL

**Status:** ✅ **FROZEN FOREVER**

Phase 4 is the **pure aliasing layer** — integer symbols for identities and relations. No structural modification. No semantic content.

## What Phase 4 Does

- `assign_identity_aliases(identity_hashes)` — deterministic integer symbols for identities
- `assign_relation_aliases(relation_hashes)` — deterministic integer symbols for relations
- Gate: `MIN_PERSISTENT_IDENTITIES`, `MIN_PERSISTENT_RELATIONS` (both 1)

## Files

- `phase4.py` — Main pipeline: `phase4(phase2_metrics, phase3_metrics)` → identity_to_symbol, symbol_to_identity, relation_to_symbol, symbol_to_relation
- `alias.py` — `assign_identity_aliases`, `assign_relation_aliases`
- `phase4/` — Freeze declaration, implementation plan

## See Also

- [PHASE4_FREEZE.md](phase4/PHASE4_FREEZE.md)
- [PROJECT_FREEZE.md](../../../PROJECT_FREEZE.md)
