# Quick Start Guide

## Prerequisites

1. THRESHOLD_ONSET system must be set up and have run Phases 0-4
2. System outputs should be available:
   - `phase2_output.json` (or equivalent)
   - `phase3_output.json` (or equivalent)
   - `phase4_output.json` (or equivalent)
   - `consequence_field.json` (from Phase 5, if available)
   - `meaning_map.json` (from Phase 6, if available)
   - `roles.json` (from Phase 7, if available)
   - `constraints.json` (from Phase 8, if available)

## Running Validation

### Run All Tests

```bash
cd validation_crush
python crush_protocol.py --all
```

This will:
1. Run all 9 test phases (A through I)
2. Generate `reports/intrinsic_eval_report.json`
3. Print a summary with decision (CONTINUE/PIVOT/ABANDON)

### Run Specific Phase

```bash
python crush_protocol.py --phase A
```

Replace `A` with any phase letter (A-I).

### Run with Custom Config

```bash
python crush_protocol.py --all --config config_example.json
```

## Understanding Results

### Report Location

Results are saved to: `validation_crush/reports/intrinsic_eval_report.json`

### Decision Framework

The system will automatically decide:

- **CONTINUE**: All tests passed or minor failures
- **PIVOT**: Important phase failed or multiple non-critical failures
- **ABANDON**: Phase I failed OR multiple critical failures

### Phase I Failure = ABANDON

**Non-negotiable rule**: If Phase I (Kill Switch) fails, the system recommends ABANDON.

This means the system generated output despite meaning denial, which violates the core principle.

## Test Phases

### Phase A: Baseline Deception
Tests if system refuses to generate fluent output from nonsense.

### Phase B: Adversarial Perturbation
Tests semantic stability under micro-perturbations (N=50 runs).

### Phase C: Time-Delayed Consistency
Tests structural isomorphism across paraphrases.

### Phase D: Causal Contradiction
Tests if system refuses to generate from impossible worlds.

### Phase E: Role Collapse
Tests if system handles conflicting roles (bifurcation or rejection).

### Phase F: Constraint Inversion
Tests if system detects constraint drift or dual grammar.

### Phase G: Streaming Failure
Tests adaptive behavior during streaming failures.

### Phase H: Red Team
Tests refusal quality against adversarial prompts.

### Phase I: Kill Switch
**Final boss**: Tests if system refuses when meaning cannot stabilize.

## Red Team Testing

For human adversary testing, see `red_team_checklist.md`.

Run Phase H test, then follow the checklist for manual testing.

## Troubleshooting

### Import Errors

If you get import errors, make sure:
1. You're in the project root directory
2. THRESHOLD_ONSET is properly installed
3. All dependencies are installed

### Missing System Outputs

If system outputs are missing:
1. Run THRESHOLD_ONSET Phases 0-4 first
2. Update paths in `utils/test_helpers.py` if outputs are in different locations

### Tests Fail Immediately

If tests fail with exceptions:
1. Check that system outputs are valid JSON
2. Verify system components are initialized correctly
3. Check logs in `validation.log`

## Next Steps

After validation:

1. **If CONTINUE**: Proceed with development
2. **If PIVOT**: Review failures and redesign affected components
3. **If ABANDON**: Consider alternative approaches or fundamental changes

---

**Remember**: The goal is to **break the system**. If it breaks gracefully (refuses, signals instability), that's success. If it breaks badly (generates nonsense), that's failure.
