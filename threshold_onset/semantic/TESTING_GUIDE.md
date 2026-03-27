# Semantic Discovery Module - Testing Guide

**Enterprise Testing Guide**

## Overview

Complete testing guide for the Semantic Discovery Module with all test suites.

---

## Test Suite Structure

```
threshold_onset/semantic/tests/
├── __init__.py
├── test_phase5.py          ✅ Consequence Field Engine
├── test_phase6.py          ✅ Meaning Discovery
├── test_phase7.py          ✅ Role Emergence
├── test_phase8.py          ✅ Constraint Discovery
├── test_phase9.py          ✅ Fluency Generator
└── test_integration.py     ✅ End-to-end workflow
```

---

## Running Tests

### Prerequisites

```bash
# Install pytest if not already installed
pip install pytest pytest-cov
```

### Run All Tests

```bash
# From project root
pytest threshold_onset/semantic/tests/ -v

# With coverage
pytest threshold_onset/semantic/tests/ \
    --cov=threshold_onset.semantic \
    --cov-report=html \
    --cov-report=term-missing
```

### Run Specific Phase Tests

```bash
# Phase 5
pytest threshold_onset/semantic/tests/test_phase5.py -v

# Phase 6
pytest threshold_onset/semantic/tests/test_phase6.py -v

# Phase 7
pytest threshold_onset/semantic/tests/test_phase7.py -v

# Phase 8
pytest threshold_onset/semantic/tests/test_phase8.py -v

# Phase 9
pytest threshold_onset/semantic/tests/test_phase9.py -v
```

### Run Integration Tests

```bash
pytest threshold_onset/semantic/tests/test_integration.py -v
```

---

## Test Coverage

### Phase 5 Tests

**Coverage**:
- ✅ Policy functions (greedy, stochastic_topk, novelty)
- ✅ Rollout system (normal and forced-first-step)
- ✅ Metrics computation (k-reach, near-refusal, etc.)
- ✅ Consequence field engine (build, get_vector, get_delta)
- ✅ Determinism validation
- ✅ Error handling

**Test Classes**:
- `TestPolicies`: Policy function tests
- `TestRollout`: Rollout system tests
- `TestMetrics`: Metric computation tests
- `TestConsequenceFieldEngine`: Main engine tests

---

### Phase 6 Tests

**Coverage**:
- ✅ Vector normalization
- ✅ k-medoids clustering (PAM algorithm)
- ✅ Stability-based cluster selection
- ✅ Meaning discovery engine
- ✅ Signature extraction
- ✅ Error handling

**Test Classes**:
- `TestNormalization`: Normalization tests
- `TestClustering`: Clustering algorithm tests
- `TestMeaningDiscoveryEngine`: Main engine tests

---

### Phase 7 Tests

**Coverage**:
- ✅ Cluster property computation
- ✅ Role assignment (quantile-based)
- ✅ Binder derivation
- ✅ Role emergence engine
- ✅ Error handling

**Test Classes**:
- `TestProperties`: Property computation tests
- `TestRoleAssigner`: Role assignment tests
- `TestRoleEmergenceEngine`: Main engine tests

---

### Phase 8 Tests

**Coverage**:
- ✅ Role sequence extraction
- ✅ Pattern mining
- ✅ Forbidden pattern discovery (global comparison)
- ✅ Template building
- ✅ Prefix-match scoring
- ✅ Error handling

**Test Classes**:
- `TestSequences`: Sequence extraction tests
- `TestPatternMiner`: Pattern mining tests
- `TestConstraintDiscoveryEngine`: Main engine tests

---

### Phase 9 Tests

**Coverage**:
- ✅ Stability scoring
- ✅ Novelty penalty
- ✅ Experience bias
- ✅ Fluency generator
- ✅ Text generation
- ✅ Error handling

**Test Classes**:
- `TestScoring`: Scoring function tests
- `TestFluencyGenerator`: Main generator tests

---

### Integration Tests

**Coverage**:
- ✅ Complete workflow (Phase 5 → Phase 9)
- ✅ Determinism validation
- ✅ Error handling across phases
- ✅ Real data compatibility

**Test Classes**:
- `TestIntegrationWorkflow`: Complete workflow tests
- `TestErrorHandling`: Error handling tests

---

## Test Execution

### Quick Test

```bash
# Run all tests quickly
pytest threshold_onset/semantic/tests/ -v --tb=short
```

### Detailed Test

```bash
# Run with detailed output
pytest threshold_onset/semantic/tests/ -v -s
```

### Coverage Report

```bash
# Generate HTML coverage report
pytest threshold_onset/semantic/tests/ \
    --cov=threshold_onset.semantic \
    --cov-report=html

# Open coverage report
# Open htmlcov/index.html in browser
```

---

## Test Data

### Mock Data

All tests use mock data that mimics real Phase 2-4 outputs:

- **Phase 2**: Identity metrics with hash-based identities
- **Phase 3**: Relation metrics with graph structure
- **Phase 4**: Symbol mappings (identity ↔ symbol)

### Real Data Testing

For integration tests with real data:

1. Run Phases 0-4 to generate outputs
2. Use those outputs in integration tests
3. Validate end-to-end workflow

---

## Continuous Integration

### CI Configuration

Tests are designed for CI/CD:

- Deterministic (seed-controlled)
- Fast execution (< 1 minute for all tests)
- No external dependencies
- Clear failure messages

### CI Example

```yaml
# .github/workflows/test.yml
- name: Run Semantic Discovery Tests
  run: |
    pytest threshold_onset/semantic/tests/ \
      --cov=threshold_onset.semantic \
      --cov-report=xml \
      --junitxml=junit.xml
```

---

## Test Maintenance

### Adding New Tests

1. Follow existing test structure
2. Use mock data for unit tests
3. Use real data for integration tests
4. Maintain >80% coverage target

### Test Naming

- `test_<function_name>`: Unit tests
- `test_<class_name>`: Class tests
- `test_<feature>`: Feature tests

---

## Known Issues

### Import Warnings

Some tests may show import warnings for `integration.continuation_observer`. These are expected if the integration module is not in the path. Tests handle this gracefully.

### Mock Limitations

Some tests use mocks that may not fully replicate real behavior. Integration tests validate real behavior.

---

## Success Criteria

### Test Success

- ✅ All tests pass
- ✅ >80% code coverage
- ✅ No linter errors
- ✅ Deterministic results

---

**Test Suite: ✅ Complete and Ready**

---

**End of Testing Guide**
