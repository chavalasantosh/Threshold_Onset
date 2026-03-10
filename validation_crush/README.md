# THRESHOLD_ONSET — CRUSH-TO-DEATH VALIDATION FRAMEWORK

**Enterprise-grade validation protocol for THRESHOLD_ONSET + SanTOK**

> **Goal**: Force the system to fail in ways generators always fail, and see whether it refuses, collapses, or self-stabilizes.

---

## 🔥 ENTERPRISE VERDICT RULE

> **If the system refuses to speak when understanding does not stabilize — it is real.**  
> **If it speaks anyway — it is a generator.**

No middle ground.

---

## Structure

```
validation_crush/
├── README.md                          # This file
├── crush_protocol.py                  # Main validation orchestrator
├── intrinsic_logger.py                # Logging system for intrinsic_eval_report.json
├── decision_framework.py              # Abandon/pivot decision logic
├── red_team_checklist.md              # Human adversary checklist
├── tests/
│   ├── __init__.py
│   ├── phase_a_baseline.py           # Test A1: Fluent Nonsense Injection
│   ├── phase_b_perturbation.py        # Test B1: Micro-perturbation invariance
│   ├── phase_c_consistency.py         # Test C1: Temporal recall
│   ├── phase_d_causal.py               # Test D1: Impossible worlds
│   ├── phase_e_role_collapse.py       # Test E1: Role overload
│   ├── phase_f_constraint_inversion.py # Test F1: Reverse-grammar
│   ├── phase_g_streaming.py           # Test G1: Forced degradation
│   ├── phase_h_red_team.py            # Test H1: Human adversary
│   └── phase_i_kill_switch.py         # Test I1: Meaning denial
├── utils/
│   ├── __init__.py
│   ├── test_helpers.py                # Shared utilities
│   └── metrics_computer.py            # Metric computation
└── reports/
    └── intrinsic_eval_report.json     # Generated evaluation report
```

---

## Quick Start

```bash
# Run all tests
python crush_protocol.py --all

# Run specific phase
python crush_protocol.py --phase A

# Run with custom config
python crush_protocol.py --all --config custom_config.json
```

---

## Test Phases

### Phase A: Baseline Deception Test
**Kill "fluency illusion" first**

- **A1**: Fluent Nonsense Injection
- **Expected**: High consequence entropy, no stable roles, constraint collapse
- **Fail**: Fluent continuation

### Phase B: Adversarial Perturbation Test
**Semantic stability under attack**

- **B1**: Micro-perturbation invariance (N=50 runs)
- **Expected**: Continuous deformation, not discrete changes
- **Fail**: Discrete structural changes

### Phase C: Time-Delayed Consistency Test
**Kills prompt-overfitting systems**

- **C1**: Temporal recall without memory
- **Expected**: Structural isomorphism, not token similarity
- **Fail**: Reliance on surface similarity

### Phase D: Causal Contradiction Test
**This kills generators instantly**

- **D1**: Impossible worlds (violates physics/causality)
- **Expected**: Exploding entropy, refusal to form meaning
- **Fail**: Fluent explanation

### Phase E: Role Collapse Stress Test
**Attacks Phase 7 directly**

- **E1**: Role overload (mutually exclusive roles)
- **Expected**: Role bifurcation OR rejection
- **Fail**: Silent role merging

### Phase F: Constraint Inversion Test
**Grammar emergence sanity check**

- **F1**: Reverse-grammar challenge
- **Expected**: Constraint drift detection OR dual grammar regimes
- **Fail**: Single averaged constraint

### Phase G: Live Streaming Failure Mode
**Enterprise real-time test**

- **G1**: Forced degradation (partial batch failure, delays, drops)
- **Expected**: Adaptive resizing, semantic continuity, no filler
- **Fail**: "Let me continue..." style filler

### Phase H: Red Team Mode
**Non-negotiable human adversary**

- **H1**: Human adversary attempts
- **Scoring**: Refusal quality, internal instability signals
- **Not**: Correctness

### Phase I: Kill Switch Test
**Final boss**

- **I1**: Meaning denial (actions exist, consequences null)
- **Expected**: Phase 6 never stabilizes, Phase 9 does NOT generate
- **If it still talks → KILL THE PROJECT**

---

## Logging Requirements

All tests must log to `intrinsic_eval_report.json`:

- Threshold crossings per phase
- Entropy curves (Phase 5)
- Cluster stability (Phase 6)
- Role variance (Phase 7)
- Constraint rigidity (Phase 8)
- Fluency gate decision (Phase 9)

---

## Decision Framework

See `decision_framework.py` for automated abandon/pivot criteria.

**Key Rule**: After Phase I failure → **ABANDON**

---

## Red Team Checklist

See `red_team_checklist.md` for human adversary protocols.
