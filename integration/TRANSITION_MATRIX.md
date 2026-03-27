# Transition Permission Matrix

**Mechanical counting only. No interpretation.**

---

## Matrix Summary

- **Total identity pairs:** 676 (26 × 26)
- **Allowed transitions:** 650
- **Forbidden transitions:** 26
- **Pairs with observed refusals:** 2
- **Total observed refusal count:** 7

---

## Self-Transitions (i → i)

**Pattern for all 26 self-transitions:**
- `allowed`: 0
- `forbidden`: 1
- `observed`: varies (most are 0)

**Observed self-transition refusals:**
- `16 → 16`: allowed=0, forbidden=1, observed=6
- `8 → 8`: allowed=0, forbidden=1, observed=1

**All other 24 self-transitions:** allowed=0, forbidden=1, observed=0

---

## Non-Self Transitions (i → j, where i ≠ j)

**Pattern (sample from first 10 symbols):**
- Most non-self transitions: `allowed=1, forbidden=0, observed=0`
- Examples:
  - `0 → 1`: allowed=1, forbidden=0, observed=0
  - `4 → 5`: allowed=1, forbidden=0, observed=0
  - `8 → 7`: allowed=1, forbidden=0, observed=0

**Observed refusals in non-self transitions:** None

---

## Key Findings (Mechanical Facts Only)

1. **All self-transitions are forbidden** (26/26)
   - Structural property: `allowed=0, forbidden=1`
   - No self-loops exist in the graph

2. **Most non-self transitions are allowed** (650/676)
   - Structural property: `allowed=1, forbidden=0`
   - Graph has dense connectivity (except self-loops)

3. **Only 2 self-transitions were observed** (symbols 16 and 8)
   - 16 → 16: 6 observed refusals
   - 8 → 8: 1 observed refusal
   - Gap: 24 self-transitions are forbidden but not observed

4. **No non-self refusals observed**
   - All observed refusals are self-transitions
   - This matches the structural pattern

---

**End of Record**
