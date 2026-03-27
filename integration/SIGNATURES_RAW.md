# Refusal Signature Aggregation

**Mechanical counting only. No interpretation.**

---

## Raw Counts

- **Total refusals collected:** 7
- **Distinct refusal signatures:** 2

---

## Tests Run

1. `original`: word, permuted=False, refusals=1
2. `permuted_seed42`: word, permuted=True, refusals=2
3. `permuted_seed123`: word, permuted=True, refusals=2
4. `character_tokenization`: character, permuted=False, refusals=1
5. `longer_continuation`: word, permuted=False, refusals=1

---

## Signature Counts

### Signature: (4, 4, False)

- **Count:** 6
- **Step indices:** [10, 11]
- **Appears in:** original, permuted_seed42, permuted_seed123, longer_continuation
- **Pattern:** current_symbol = attempted_next_symbol = 4, relation_exists = False

### Signature: (18, 18, False)

- **Count:** 1
- **Step indices:** [26]
- **Appears in:** character_tokenization
- **Pattern:** current_symbol = attempted_next_symbol = 18, relation_exists = False

---

## Observations (Mechanical Facts Only)

1. **Signature (4, 4, False)** appears in 4 out of 5 tests
2. **Signature (4, 4, False)** appears across:
   - Different permutations (original, permuted_seed42, permuted_seed123)
   - Different continuation lengths (original, longer_continuation)
   - Same tokenization method (word)
3. **Signature (18, 18, False)** appears only in character tokenization test
4. All signatures show: current_symbol == attempted_next_symbol, relation_exists == False

---

**End of Record**
