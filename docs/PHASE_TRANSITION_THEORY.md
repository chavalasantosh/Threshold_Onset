# Identity Phase Transition — Formal Theory

**Status:** Implementation-consistent. For paper formalization.

---

## Definition 1 (Perturbation Model)

A sequence of tokens is perturbed by **independent Bernoulli deletion** with probability \(p\) per token. Each token is dropped independently with probability \(p\).

---

## Definition 2 (Pair Identity)

A token pair \((t_i, t_{i+1})\) is **persistent** if it appears in at least \(\theta\) out of \(K\) independent perturbation runs.

---

## Proposition 1 (Distribution of Recurrence)

For a fixed pair, let \(X\) = number of runs in which the pair appears.

Then:
$$X \sim \text{Binomial}(K, q), \quad q = (1-p)^2$$

**Proof:** Survival of both tokens per run is independent Bernoulli with probability \((1-p)^2\). Runs are independent.

---

## Proposition 2 (Mean-Field Collapse Boundary)

The **mean-field phase boundary** satisfies:
$$K(1-p)^2 = \theta$$

Thus:
$$p^* = 1 - \sqrt{\theta/K}$$

This is a **mean-field approximation** of the collapse transition. Above \(p^*\), expected recurrence falls below threshold; identities collapse.

**Wording:** "This defines the expected-value phase boundary for recurrence-defined identity." Do not call it a strict threshold.

---

## Empirical Comparison

- **Fraction persistent:** \(\frac{\text{persistent identities (from original)}}{\text{total unique pairs in original sequence}}\)
- **Theoretical curve:** \(P(X \geq \theta)\) for \(X \sim \text{Binomial}(K, (1-p)^2)\)
- **Overlay:** Mark \(p^*\) on the plot. Empirical curve should bend near \(p^*\).

---

## Invariant Corollary

Relation construction only creates edges between **distinct** identities. Thus \(A_{ii} = 0\) for all \(i\). Any walk on the graph satisfies \(s_{t+1} \neq s_t\). Constraint-safe generation is a **graph-theoretic corollary** of recurrence-induced topology.

---

## Scope

The binomial phase analysis applies to the **stability-mode pair identity model**. Extending the same analysis to residue-based identities in the full pipeline is future work.

---

## Implementation

- `integration/stability_experiments.py` — sweep, fixed-denominator, theoretical curve
- `python integration/stability_experiments.py --csv` — output for plotting
- `python integration/stability_experiments.py --plot` — generate plot (requires matplotlib)
