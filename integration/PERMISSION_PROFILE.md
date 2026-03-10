# Identity Permission Profile

**Mechanical counting only. No interpretation.**

---

## Summary

- **Total identity symbols:** 26
- **Symbols with self-loops (allowed):** 0
- **Symbols without self-loops (refused):** 26
- **Total allowed self-transitions:** 0
- **Total refused self-transitions (structural):** 26
- **Total observed refusals:** 6

---

## Key Findings (Mechanical Facts Only)

1. **No identity has self-loops in graph**
   - All 26 symbols: `self-loop exists = False`
   - All 26 symbols: `allowed = 0`, `refused = 1`

2. **Self-transitions are structurally refused for all identities**
   - This is a structural property, not an observation artifact
   - The graph contains no self-loops

3. **Only 6 self-transitions were actually observed during continuation**
   - Symbol 4: 6 observed refusals
   - Symbol 18: 1 observed refusal
   - Other 24 symbols: 0 observed refusals

4. **Observation vs Structure**
   - Structural refusal: 26 (all symbols)
   - Observed refusal: 6 (only symbols 4 and 18)
   - Gap: 20 symbols have structural refusal but were not observed

---

## Pattern

**All symbols:**
```
allowed: 0
refused (structural): 1
self-loop exists: False
```

**Observed refusals:**
- Symbol 4: 6 occurrences
- Symbol 18: 1 occurrence
- All other symbols: 0 occurrences

---

**End of Record**
