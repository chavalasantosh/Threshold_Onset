# Raw Refusals - Permuted Continuation

**Facts only. No interpretation.**

---

## Test 1: Original (No Permutation)

**Continuation:** "Tokens become actions. Patterns become residues."
**Tokenization:** word
**Permuted:** False

**Refusal:**
```
step_index: 11
current_symbol: 24
attempted_next_symbol: 24
reason_for_refusal: no_persistent_relation
relation_exists: False
```

**Total refusals: 1**

---

## Test 2: Permuted Seed 42

**Continuation:** "Tokens become actions. Patterns become residues." (permuted)
**Tokenization:** word
**Permuted:** True (seed 42)

**Refusal 1:**
```
step_index: 10
current_symbol: 24
attempted_next_symbol: 24
reason_for_refusal: no_persistent_relation
relation_exists: False
```

**Refusal 2:**
```
step_index: 10
current_symbol: 24
attempted_next_symbol: 24
reason_for_refusal: no_persistent_relation
relation_exists: False
```

**Total refusals: 2**

---

## Test 3: Permuted Seed 123

**Continuation:** "Tokens become actions. Patterns become residues." (permuted)
**Tokenization:** word
**Permuted:** True (seed 123)

**Refusal 1:**
```
step_index: 10
current_symbol: 24
attempted_next_symbol: 24
reason_for_refusal: no_persistent_relation
relation_exists: False
```

**Refusal 2:**
```
step_index: 10
current_symbol: 24
attempted_next_symbol: 24
reason_for_refusal: no_persistent_relation
relation_exists: False
```

**Total refusals: 2**

---

## Observations (Mechanical Facts Only)

1. **Refusal count changed:** Original = 1, Permuted = 2
2. **Refusal position shifted:** step_index 11 → 10
3. **Same symbol refused:** current_symbol 24, attempted_next_symbol 24
4. **Relation check consistent:** relation_exists = False in all cases

---

**End of Record**
