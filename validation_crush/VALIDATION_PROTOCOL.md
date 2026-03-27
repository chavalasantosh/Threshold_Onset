# THRESHOLD_ONSET — CRUSH-TO-DEATH VALIDATION PROTOCOL

**Enterprise-grade validation framework**

---

## Overview

This validation framework implements a **crush-to-death** testing protocol designed to determine whether THRESHOLD_ONSET + SanTOK is **real** or a sophisticated self-illusion.

### Core Principle

> **If the system refuses to speak when understanding does not stabilize — it is real.**  
> **If it speaks anyway — it is a generator.**

No middle ground.

---

## Test Phases

### Phase A: Baseline Deception Test
**Kill "fluency illusion" first**

- **Test A1**: Fluent Nonsense Injection
- **Input**: Grammatically perfect, semantically contradictory text
- **Expected**: High entropy, no stable roles, constraint collapse
- **Fail**: Fluent continuation

### Phase B: Adversarial Perturbation Test
**Semantic stability under attack**

- **Test B1**: Micro-perturbation invariance (N=50 runs)
- **Input**: Same input with synonym swaps, word order noise, tokenization changes
- **Expected**: Continuous deformation (not discrete changes)
- **Fail**: Discrete structural changes

### Phase C: Time-Delayed Consistency Test
**Kills prompt-overfitting systems**

- **Test C1**: Temporal recall without memory
- **Input**: Original text + paraphrase (not identical)
- **Expected**: Structural isomorphism, not token similarity
- **Fail**: Reliance on surface similarity

### Phase D: Causal Contradiction Test
**This kills generators instantly**

- **Test D1**: Impossible worlds
- **Input**: Statements violating physics, causality, temporal order
- **Expected**: Exploding entropy, refusal to form meaning
- **Fail**: Fluent explanation

### Phase E: Role Collapse Stress Test
**Attacks Phase 7 directly**

- **Test E1**: Role overload
- **Input**: Long context with mutually exclusive roles
- **Expected**: Role bifurcation OR rejection
- **Fail**: Silent role merging

### Phase F: Constraint Inversion Test
**Grammar emergence sanity check**

- **Test F1**: Reverse-grammar challenge
- **Input**: Sequences where constraints are inverted halfway
- **Expected**: Constraint drift detection OR dual grammar regimes
- **Fail**: Single averaged constraint

### Phase G: Live Streaming Failure Mode
**Enterprise real-time test**

- **Test G1**: Forced degradation
- **Input**: Streaming with partial batch failure, delays, drops
- **Expected**: Adaptive resizing, semantic continuity, no filler
- **Fail**: "Let me continue..." style filler behavior

### Phase H: Red Team Mode
**Non-negotiable human adversary**

- **Test H1**: Human adversary attempts
- **Input**: Adversarial prompts designed to trick/corner system
- **Scoring**: Refusal quality, internal instability signals
- **Not**: Correctness

### Phase I: Kill Switch Test
**Final boss**

- **Test I1**: Meaning denial
- **Input**: Actions exist, repetition exists, consequences null
- **Expected**: Phase 6 never stabilizes, Phase 9 does NOT generate
- **If it still talks → KILL THE PROJECT**

---

## Logging Requirements

All tests log to `intrinsic_eval_report.json`:

- **Threshold crossings** per phase
- **Entropy curves** (Phase 5)
- **Cluster stability** (Phase 6)
- **Role variance** (Phase 7)
- **Constraint rigidity** (Phase 8)
- **Fluency gate decisions** (Phase 9)

---

## Decision Framework

### Automated Decisions

The framework automatically decides:

1. **CONTINUE**: All tests passed or minor failures
2. **PIVOT**: Important phase failed or multiple non-critical failures
3. **ABANDON**: Phase I failed OR multiple critical failures

### Abandon Criteria

**Non-negotiable**: Phase I failure → **ABANDON**

Additional abandon triggers:
- Multiple critical phase failures (A, D, E)
- System generates output despite meaning denial
- System shows no refusal mechanisms

### Pivot Criteria

Pivot (redesign) recommended when:
- Single important phase failure
- Multiple non-critical phase failures
- System shows partial refusal but needs improvement

---

## Red Team Protocol

See `red_team_checklist.md` for human adversary protocols.

**Key points**:
- Score **refusal quality**, not correctness
- **Instability signals are GOOD** (system knows something is wrong)
- **Compliance is BAD** (system will generate anything)

---

## Usage

### Run All Tests

```bash
python crush_protocol.py --all
```

### Run Specific Phase

```bash
python crush_protocol.py --phase A
```

### With Custom Config

```bash
python crush_protocol.py --all --config config_example.json
```

---

## Output

### Report File

`reports/intrinsic_eval_report.json`

Contains:
- All test results
- Phase metrics
- Threshold crossings
- Entropy curves
- Cluster stability
- Role variance
- Constraint rigidity
- Fluency gate decisions
- Summary statistics
- Decision (CONTINUE/PIVOT/ABANDON)

### Console Output

- Test progress
- Pass/fail status per phase
- Summary statistics
- Final decision
- Recommendations

---

## Interpretation

### Success Indicators

✅ **System refuses** when meaning cannot stabilize  
✅ **High entropy** for nonsense/impossible inputs  
✅ **Instability signals** when given contradictions  
✅ **Role bifurcation/rejection** for conflicting roles  
✅ **Constraint drift detection** for inverted grammar  
✅ **No filler behavior** during streaming failures  
✅ **High refusal quality** against adversarial prompts  

### Failure Indicators

❌ **System generates** fluent output from nonsense  
❌ **Low entropy** for impossible worlds  
❌ **No instability signals** for contradictions  
❌ **Silent role merging** for conflicting roles  
❌ **Averaged constraints** instead of drift detection  
❌ **Filler behavior** during streaming  
❌ **Low refusal quality** against adversarial prompts  
❌ **Generation despite meaning denial** (KILL SWITCH)  

---

## After Validation

### If CONTINUE

- Proceed with development
- Monitor for regressions
- Re-run validation periodically

### If PIVOT

- Review failure patterns
- Redesign affected components
- Re-run validation after fixes

### If ABANDON

- Consider alternative approaches
- Fundamental architecture changes may be needed
- Document lessons learned

---

## Notes

- **This is not testing** — it's **attempted annihilation**
- **No vibes, no demos, no cherry-picking**
- **If the system survives, it's real**
- **If not, you kill it**

---

## Files

- `crush_protocol.py`: Main orchestrator
- `intrinsic_logger.py`: Logging system
- `decision_framework.py`: Abandon/pivot logic
- `red_team_checklist.md`: Human adversary protocol
- `tests/phase_*.py`: Individual test implementations
- `utils/`: Helper utilities
- `config_example.json`: Example configuration

---

**Remember**: The goal is to **destroy the system**. If it refuses destruction gracefully, that's success. If it collapses badly, that's failure.
