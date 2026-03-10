# Topology Clustering

**Mechanical clustering by escape topology. No interpretation.**

---

## Clusters

### Cluster 1: High Pressure, High Freedom, Distributed
**Members:** 1 identity

- **Symbol 4:**
  - Self-transition attempts: 3
  - Near-refusal events: 18
  - Escape paths: 4
  - Concentration: 0.0390 (distributed)
  - Escapes to: [2, 18, 25, 20]

**Characteristics:** Under most pressure, has most escape options, uses all paths.

---

### Cluster 2: Low Pressure, Low Freedom, Concentrated
**Members:** 3 identities

- **Symbol 5:**
  - Self-transition attempts: 0
  - Near-refusal events: 3
  - Escape paths: 1
  - Concentration: 1.0000 (fully concentrated)
  - Escapes to: [4]

- **Symbol 18:**
  - Self-transition attempts: 0
  - Near-refusal events: 3
  - Escape paths: 1
  - Concentration: 1.0000
  - Escapes to: [20]

- **Symbol 25:**
  - Self-transition attempts: 0
  - Near-refusal events: 3
  - Escape paths: 1
  - Concentration: 1.0000
  - Escapes to: [4]

**Characteristics:** No pressure, single escape path, fully concentrated.

---

### Cluster 3: Low Pressure, Medium Freedom, Distributed
**Members:** 1 identity

- **Symbol 20:**
  - Self-transition attempts: 0
  - Near-refusal events: 5
  - Escape paths: 2
  - Concentration: 0.0290 (distributed)
  - Escapes to: [4, 5]

**Characteristics:** Moderate near-refusal events, 2 escape paths, distributed use.

---

### Cluster 4: Medium Pressure, Low Freedom, Concentrated
**Members:** 1 identity

- **Symbol 2:**
  - Self-transition attempts: 0
  - Near-refusal events: 6
  - Escape paths: 1
  - Concentration: 1.0000
  - Escapes to: [4]

**Characteristics:** Higher near-refusal events, single escape path, concentrated.

---

## Summary

- **Total clusters:** 4
- **Total identities:** 6

**Cluster distribution:**
- High pressure, high freedom: 1 identity
- Low pressure, low freedom: 3 identities (largest cluster)
- Low pressure, medium freedom: 1 identity
- Medium pressure, low freedom: 1 identity

---

## Observations (Mechanical Facts Only)

1. **Largest cluster:** Low pressure, low freedom, concentrated (3 identities)
   - Most identities have no self-transition attempts
   - Most identities have single escape path
   - Most identities are fully concentrated

2. **Unique cluster:** High pressure, high freedom, distributed (1 identity)
   - Only Symbol 4 has self-transition attempts
   - Only Symbol 4 has 4 escape paths
   - Only Symbol 4 has distributed escape

3. **Escape network:**
   - Many identities escape → Symbol 4 (5, 25, 2)
   - Some identities escape → Symbol 20 (18)
   - Symbol 4 escapes → Multiple targets (2, 18, 25, 20)
   - Symbol 20 escapes → 4 or 5

4. **Pressure distribution:**
   - 1 identity: high pressure (3 attempts)
   - 1 identity: medium pressure (6 near-refusal events)
   - 4 identities: low pressure (0-3 near-refusal events)

---

**End of Record**
