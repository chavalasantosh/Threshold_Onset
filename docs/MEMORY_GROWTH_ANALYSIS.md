# Memory Growth Analysis

**Status:** Phase 0. Conditions for sublinear or bounded memory.

---

## Problem

CorpusState accumulates identities and edges. Without control, memory can grow unbounded as the corpus grows.

---

## Worst Case: Linear Growth

If every document introduces new identities and none ever decay:

- \(N\) documents \(\Rightarrow\) \(O(N)\) new identities
- Memory grows linearly with corpus size

---

## Mitigations

### 1. Decay

With decay rate \(d > 0\), absent objects lose stability: \(S_O \gets S_O \cdot (1-d)\). After enough absences, \(S_O \to 0\). Pruning removes them.

**Effect:** Rare identities (appear in few docs) decay and are pruned. Only recurring identities persist.

### 2. Pruning

Remove objects with \(S_O < \theta_{\text{prune}}\) periodically (every \(N\) documents or when size exceeds threshold).

**Effect:** Bounds the number of low-stability objects.

### 3. Log-Scaling Reinforcement (Optional)

Instead of \(S_O \gets S_O + r\), use:

$$
S_O \gets S_O + \log(1 + r)
$$

**Effect:** Sublinear growth per object. Even always-present objects grow slowly.

### 4. Hard Caps

- `max_identities`: When exceeded, evict lowest-stability identities.
- `max_edges`: When exceeded, evict lowest-weight edges.

**Effect:** Hard upper bound on memory.

---

## Sublinear Condition

Memory growth is sublinear if:

1. **Decay dominates for rare objects:** Objects appearing in \(o(N)\) documents decay to zero and are pruned.
2. **Recurring objects are bounded:** The number of objects that recur across many documents is typically \(O(\sqrt{N})\) or \(O(N^\alpha)\) with \(\alpha < 1\) for natural language (vocabulary growth is sublinear).
3. **Pruning schedule:** Prune every \(N\) documents or when size \(> M\); keeps low-stability tail bounded.

**Conclusion:** With decay, pruning, and (optionally) log reinforcement, memory growth can be sublinear or at least controllable.

---

## Steady-State Bounds

For an object present in fraction \(f\) of documents:

- Reinforcement per doc (when present): \(+r\)
- Decay per doc (when absent): \(\times (1-d)\)

Rough steady state: \(S_O \approx \frac{f \cdot r}{d}\) (when reinforcement balances decay). With \(r=1\), \(d=0.1\), \(f=0.5\): \(S_O \approx 5\).

---

## Phase 1 Gate Criterion

**Memory growth must be sublinear or controllable.**

If memory grows linearly with tokens over 10k–100k docs, redesign:

- Increase decay rate
- Add log-scaling reinforcement
- Tighten prune threshold
- Add hard caps earlier

---

## Implementation Notes

- Monitor: `corpus_identities_count`, `corpus_edges_count` over documents
- Log growth rate: \(\Delta \text{count} / \Delta \text{docs}\)
- Alert if growth rate exceeds threshold (e.g., \(> 0.1\) new identities per doc sustained)
