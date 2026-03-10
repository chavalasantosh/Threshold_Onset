# Escape Topology Comparison

**Mechanical comparison only. No interpretation.**

---

## Metrics Per Input

### Philosophy Text
- **Total symbols:** 6
- **Symbols with attempts:** 1
- **Total attempts:** 3
- **Average escape paths:** 1.67
- **Average concentration:** 0.6780
- **Max attempts:** 3
- **Max escape paths:** 4

### Technical Text
- **Total symbols:** 8
- **Symbols with attempts:** 1
- **Total attempts:** 3
- **Average escape paths:** 1.75
- **Average concentration:** 0.7567
- **Max attempts:** 3
- **Max escape paths:** 6

### Literary Text
- **Total symbols:** 7
- **Symbols with attempts:** 0
- **Total attempts:** 0
- **Average escape paths:** 1.71
- **Average concentration:** 0.5791
- **Max attempts:** 0
- **Max escape paths:** 4

### Short Text
- **Total symbols:** 4
- **Symbols with attempts:** 1
- **Total attempts:** 3
- **Average escape paths:** 1.75
- **Average concentration:** 0.5073
- **Max attempts:** 3
- **Max escape paths:** 3

---

## Invariants vs Variations

### Invariants
**None found** - No metric is identical across all inputs.

### Variations
All metrics vary across inputs:

- **total_symbols:** 4-8 (varies by input size)
- **symbols_with_attempts:** 0-1 (literary has 0, others have 1)
- **total_attempts:** 0-3 (literary has 0, others have 3)
- **avg_escape_paths:** 1.67-1.75 (narrow range)
- **avg_concentration:** 0.51-0.76 (varies)
- **max_attempts:** 0-3 (literary has 0, others have 3)
- **max_escape_paths:** 3-6 (varies)

---

## Structural Patterns

### Pattern 1: Self-Transition Attempts
- **All inputs have self-transition attempts:** False
- **3 out of 4 inputs:** Have self-transition attempts
- **When attempts occur:** Always 3 attempts (in inputs that have them)
- **Exception:** Literary text has 0 attempts

### Pattern 2: Concentrated Escape Paths
- **All inputs have concentrated escape paths:** True
- **All inputs:** Have at least one symbol with concentration = 1.0
- **Invariant:** Concentrated escape exists in all inputs

### Pattern 3: Average Escape Paths
- **Range:** 1.67-1.75
- **Narrow variation:** Average escape paths is relatively stable
- **Pattern:** Most symbols have 1-2 escape paths

---

## Observations (Mechanical Facts Only)

1. **No strict invariants:** All metrics vary across inputs

2. **Near-invariant:** Average escape paths (1.67-1.75)
   - Narrow range suggests similar escape topology structure

3. **Conditional invariant:** Self-transition attempts
   - 3 out of 4 inputs show attempts
   - When attempts occur, always 3 attempts
   - Literary text is exception (0 attempts)

4. **True invariant:** Concentrated escape paths
   - All inputs have symbols with concentration = 1.0
   - All inputs have at least one symbol with single escape path

5. **Variation in structure size:**
   - Total symbols: 4-8 (depends on input)
   - Max escape paths: 3-6 (depends on structure)

---

**End of Record**
