# Paper Development Roadmap

## ✅ Implemented (Ready for Paper)

### Benchmark (THRESHOLD_ONSETBench)
- **39 samples** across 20 categories
- **Metrics:** success rate, constraint violations, decoder consistency, self-transition rate
- **Run:** `python integration/benchmark.py`
- **Results:** 100% success, 0 violations, 100% consistency

### Baselines
- **4 methods:** Random, Markov-1, Echo, Uniform
- **Corpus:** 10 samples (default) or 39 benchmark samples (`--benchmark`)
- **Run:** `python integration/baselines.py` or `python integration/baselines.py --benchmark`
- **Results (39 samples):** Random 43.9%, Markov-1 24.3%, Echo 17.1%, Uniform 100% self-transitions

### External Validation
- **136 samples** (philosophy, tech, literary, synthetic)
- **Run:** `python integration/external_validation.py`
- **Results:** 100% success, 0 violations

### Stability Mode (Phase Transition)
- **Parameter sweep:** drop_prob, K, θ
- **Run:** `python integration/stability_experiments.py`
- **Theory:** \(p^* = 1 - \sqrt{\theta/K}\) (mean-field collapse boundary)
- **Validates:** Binomial model, fixed-denominator fraction vs \(P(X \geq \theta)\)
- **Flags:** `--csv` (plot data), `--plot` (matplotlib)

### Structural Scaling
- **Metrics:** Tokens, Identities, Relations, Avg escape paths, Pressure, Diversity
- **Run:** `python integration/structural_scaling.py`
- **Honest claim:** Escape topology width does not scale linearly with token count under current recurrence thresholds. Identity count \(I = f(R)\), not \(f(N)\)—identity collapse under uniformity observed.

---

## 🔧 Optional Enhancements

1. **End-user output quality:** ✅ Input-order boost added (bigrams/trigrams from input get scoring boost). Start from first token for natural flow. No 3rd party. Further: sentence boundaries, diversity tuning.
2. **Run on same corpus:** ✅ Baselines support `--benchmark` to run on full 39 samples for fair comparison
3. **Statistical tests:** Add confidence intervals or significance tests
4. **More baselines:** e.g., n-gram with explicit no-repeat filter
5. **Domain corpora:** Add external validation on real-world text (news, books)
6. **Figures:** Add plot of self-transition rate comparison (bar chart)
7. **Timing table:** Add inference time (benchmark: ~2s for 39 samples; external: ~0.7s for 136)

---

## 📝 Paper Updates Applied

- **Framing:** Identity as induced (not primitive); deterministic structural dynamics system
- **Formal:** Phase boundary \(p^* = 1 - \sqrt{\theta/K}\); binomial model; graph-theoretic invariant \(A_{ii} = 0\)
- **Stability:** Fixed-denominator normalization; theoretical \(P(X \geq \theta)\) overlay
- **Honest scaling:** No overclaim; identity collapse under uniformity; \(I = f(R)\) not \(f(N)\)
- **Constraint:** No self-transition is corollary of topology, not filtering

---

## 🚀 Quick: Regenerate All Results

```bash
python main.py
# or: python run_all.py
```

Single entry point: `main.py` runs all 10 pipeline steps. Modes:
- `python main.py` — full suite (default text)
- `python main.py --user "Your text"` — run with your input
- `python main.py --check "Your text"` — quick pipeline check only

Paper tables use numbers from:
- `integration/benchmark.py` → Table 1 (THRESHOLD_ONSET benchmark)
- `integration/external_validation.py` → Table 1 (THRESHOLD_ONSET external)
- `integration/baselines.py` → Table 1 (baselines)
- `integration/stability_experiments.py` → Table 3 (stability)
