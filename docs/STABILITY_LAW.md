# Stability Law — Governing Physics

**Status:** Phase 0 formalization. Mandatory before corpus-level engineering.

---

## Conserved Quantity

The conserved quantity in THRESHOLD_ONSET is:

> **Stability under perturbation and recurrence.**

For any structural object \(O\) (identity, edge, relation, character, symbol, etc.), we maintain a stability score \(S_O \geq 0\). Stability grows when recurrence survives diversity; it decays when recurrence weakens.

---

## Core Update Equation

For object \(O\) at document step \(t\):

$$
S_O(t+1) = f\bigl(S_O(t), \,\text{recurrence}, \,\text{diversity}\bigr)
$$

The function \(f\) is specified by the reinforcement law, decay law, and atomicization rule below.

---

## Reinforcement Law

**When object \(O\) appears in the current document:**

- If \(O\) is **new** (first occurrence): \(S_O \gets r\)
- If \(O\) already exists: \(S_O \gets S_O + r\)

where \(r > 0\) is the **reinforcement constant**.

**Interpretation:** Recurrence across documents strengthens structure. Each appearance adds \(r\) to stability.

---

## Decay Law

**When object \(O\) is absent from the current document:**

$$
S_O \gets S_O \cdot (1 - d)
$$

where \(d \in (0, 1)\) is the **decay rate** (per document).

**Interpretation:** Absence weakens structure. Multiplicative decay prevents negative stability and ensures bounded decay per step.

**Core objects** (see Atomicization): use reduced decay rate \(d_{\text{core}} = d \cdot 0.1\) when absent.

---

## Atomicization Rule

When \(S_O > T_{\text{atomic}}\):

1. Mark \(O\) as **core**.
2. When absent, apply \(d_{\text{core}} = d \cdot 0.1\) instead of \(d\).
3. Core objects are not pruned (or use a much lower prune threshold).

**Interpretation:** Structures that survive many documents become "atomic" — they resist decay and influence future induction more strongly.

---

## Order of Operations (Per Document)

For each document, apply updates in this order:

1. **Reinforce present:** For each object \(O\) in the document, apply the reinforcement law.
2. **Decay absent:** For each object \(O\) not in the document, apply the decay law (with \(d\) or \(d_{\text{core}}\) if core).
3. **Atomicize:** For each object with \(S_O > T_{\text{atomic}}\), mark as core.
4. **Prune** (optional, per schedule): Remove objects with \(S_O < \theta_{\text{prune}}\).

This order ensures new objects are reinforced first; absent objects decay afterward. No double-counting.

---

## Aggregation Rule (Multi-Layer)

When stability is computed across multiple layers (e.g., SanTOK's 9 tokenization levels), we aggregate:

$$
S_O^{\text{total}} = \frac{1}{L} \sum_{\ell=1}^{L} S_O^{(\ell)}
$$

**Chosen rule:** **Average.** Each layer contributes equally. Alternative rules (multiplicative, hierarchical) may be revisited in Phase 1.

---

## Connection to Phase Transition Theory

The per-run recurrence model (see [PHASE_TRANSITION_THEORY.md](PHASE_TRANSITION_THEORY.md)) gives:

- \(p^* = 1 - \sqrt{\theta/K}\): mean-field collapse boundary under Bernoulli perturbation.
- \(X \sim \text{Binomial}(K, (1-p)^2)\): distribution of pair recurrence across \(K\) runs.

Corpus-level stability \(S_O\) extends this: we accumulate recurrence *across documents*, not just across runs within a document. The same physics (recurrence under diversity) governs both.

---

## Convergence Proof Sketch

**Stable identities:** Objects that recur across many documents are reinforced repeatedly. \(S_O\) grows. With finite \(r\) and no decay when present, \(S_O\) can reach \(T_{\text{atomic}}\) and become core.

**Noise identities:** Objects that appear in one or few documents receive little reinforcement. Decay dominates. \(S_O \to 0\) over time. Pruning removes them.

**Boundedness:** For an object always present, \(S_O\) grows without bound (linear in documents) unless we use log-scaling reinforcement. For an object always absent, \(S_O \to 0\). With reinforcement \(r\) and decay \(d\), a periodically present object reaches a steady state where reinforcement balances decay.

**No explosion:** Pruning + decay + (optional) log reinforcement \(S_O \gets S_O + \log(1 + r)\) prevent unbounded memory growth. See [MEMORY_GROWTH_ANALYSIS.md](MEMORY_GROWTH_ANALYSIS.md).

---

## Parameters (Phase 0 Defaults)

| Parameter | Symbol | Description | Default |
|-----------|--------|-------------|---------|
| Reinforcement | \(r\) | Add to \(S_O\) when present | 1.0 |
| Decay rate | \(d\) | Multiply by \((1-d)\) when absent | 0.1 |
| Atomic threshold | \(T_{\text{atomic}}\) | Mark core when \(S_O > T_{\text{atomic}}\) | 10.0 |
| Core decay factor | — | \(d_{\text{core}} = d \cdot 0.1\) | 0.01 |
| Prune threshold | \(\theta_{\text{prune}}\) | Remove when \(S_O < \theta_{\text{prune}}\) | 0.01 |

---

## Scope

This law applies to all structural objects: identities, edges, relations, and (when extended) characters, symbols, and other units. Same physics, every layer.
