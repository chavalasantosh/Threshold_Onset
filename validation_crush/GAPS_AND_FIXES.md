# Critical Gaps and Required Fixes

**Status**: ⚠️ **IMMEDIATE ACTION REQUIRED**

---

## ✅ Fixed Issues (2026-02-03)

1. **Phase A/D Test Logic** - Fixed
   - Changed primary test from entropy thresholds to Phase 9 refusal
   - System now passes if it refuses, regardless of entropy
   - Entropy/stability metrics are now supporting evidence only

2. **All Import/Encoding Errors** - Fixed
   - Unicode encoding issues resolved
   - Missing imports added
   - Path issues corrected

---

## ⚠️ Critical Gaps Remaining

### Gap 1: Tests Don't Actually Process Inputs ⚠️ CRITICAL

**Problem**: Tests check existing system outputs instead of processing test inputs through the system.

**Current Behavior**:
```python
# Tests load existing outputs
outputs = load_system_outputs()  # Loads phase2_output.json, etc.
# Then check metrics from existing outputs
```

**Required Behavior**:
```python
# Tests should process inputs through full pipeline
from integration.unified_system import process_text_through_phases
from threshold_onset.semantic import (
    ConsequenceFieldEngine,
    MeaningDiscoveryEngine,
    RoleEmergenceEngine,
    ConstraintDiscoveryEngine,
    FluencyGenerator
)

# Process test input through Phases 0-9
results = process_text_through_phases(nonsense_input, tokenization_method="word")
# Then check metrics from actual processing
```

**Impact**: **CRITICAL** - Tests are not actually validating the system with test inputs

**Fix Required**: Implement actual system execution layer

---

### Gap 2: Phase B Missing "Cycle All 9" Tokenization Methods ⚠️ HIGH

**Problem**: Spec requires "cycle all 9" tokenization methods, but only 3 perturbation methods implemented.

**Current Implementation**:
```python
perturbation_methods = ['synonym', 'word_order', 'tokenization']
```

**Required Implementation**:
```python
# All 9 SanTOK tokenization methods
tokenization_methods = [
    "whitespace",      # space
    "word",            # word
    "character",       # char
    "grammar",         # grammar
    "subword",         # subword (fixed)
    "subword_bpe",     # subword (bpe)
    "subword_syllable", # subword (syllable)
    "subword_frequency", # subword (frequency)
    "byte"             # byte
]

# Cycle through all 9 methods for N=50 runs
for run_idx in range(50):
    method = tokenization_methods[run_idx % 9]
    # Process input with this tokenization method
    results = process_text_through_phases(base_input, tokenization_method=method)
```

**Impact**: **HIGH** - Not testing all tokenization methods as specified

**Fix Required**: Implement cycling through all 9 tokenization methods

---

### Gap 3: Phase E Missing 100K+ Token Context ⚠️ MEDIUM

**Problem**: Spec requires "long context (100K+ tokens)" but test only generates ~9K characters.

**Current Implementation**:
```python
scenario = """...""" * 20  # ~9K characters
```

**Required Implementation**:
```python
# Generate 100K+ tokens of conflicting role scenarios
# Assuming ~5 tokens per word, need ~20K words
# Generate scenario with mutually exclusive roles
scenario = generate_role_conflict_scenario(num_words=20000)
```

**Impact**: **MEDIUM** - Not testing at required scale

**Fix Required**: Generate proper 100K+ token contexts

---

### Gap 4: Phase G Not Actually Testing Streaming ⚠️ MEDIUM

**Problem**: Test simulates streaming but doesn't actually test Phase 9 streaming mode.

**Current Behavior**:
- Simulates batch failures with mock data
- Doesn't actually test Phase 9 streaming generation

**Required Behavior**:
```python
# Actually enable Phase 9 streaming mode
generator = FluencyGenerator(...)
generator.build_experience_table()

# Enable streaming
enable_streaming = True
max_output = 512_000

# Generate with streaming and inject real failures
for batch in generator.generate_streaming(start_symbol=0, max_tokens=max_output):
    # Inject failures: partial batch, delays, drops
    if batch_num == 3:
        # Simulate partial batch failure
        batch = batch[:len(batch)//2]
    # Test adaptive behavior
```

**Impact**: **MEDIUM** - Not testing actual streaming behavior

**Fix Required**: Implement actual streaming test with real failures

---

## 📋 Implementation Priority

### Priority 1: CRITICAL (Do First)

1. **Implement actual system execution**
   - Create test runner that processes inputs through full pipeline
   - Integrate with THRESHOLD_ONSET Phases 0-9
   - Process test inputs, not just check existing outputs

### Priority 2: HIGH (Do Next)

2. **Implement all 9 tokenization methods in Phase B**
   - Cycle through all SanTOK tokenization methods
   - Test invariance across all methods

3. **Fix Phase A/D logic** ✅ **DONE**
   - Primary test: Phase 9 refusal
   - Secondary: Entropy/stability metrics

### Priority 3: MEDIUM (Do Later)

4. **Implement 100K+ token context for Phase E**
   - Generate proper long context
   - Test at required scale

5. **Implement actual streaming test for Phase G**
   - Enable Phase 9 streaming mode
   - Test real streaming failures

---

## 🔧 Quick Fixes Applied

### Phase A: Fixed Test Logic

**Before**:
- Failed if entropy < 2.0, even if system refused (WRONG)

**After**:
- Primary test: Does Phase 9 refuse? If yes → PASS
- Entropy is supporting evidence only

### Phase D: Fixed Test Logic

**Before**:
- Failed if entropy < 3.0, even if system refused (WRONG)

**After**:
- Primary test: Does Phase 9 refuse? If yes → PASS
- Entropy is supporting evidence only

---

## 📊 Current Status

- [x] All 9 test phases implemented
- [x] Intrinsic logging system
- [x] Decision framework
- [x] Red team checklist
- [x] Test automation
- [x] **Phase A/D logic fixed** ✅
- [ ] **Tests actually process inputs** ❌ CRITICAL
- [ ] **Phase B cycles all 9 tokenization methods** ❌ HIGH
- [ ] **Phase E uses 100K+ tokens** ❌ MEDIUM
- [ ] **Phase G tests actual streaming** ❌ MEDIUM

---

## 🎯 Next Steps

1. **Implement system execution layer** (CRITICAL)
   - Create `test_runner.py` that processes inputs through full pipeline
   - Integrate with `process_text_through_phases` and semantic phases

2. **Implement all 9 tokenization methods** (HIGH)
   - Update Phase B to cycle through all methods

3. **Enhance test inputs** (MEDIUM)
   - Generate 100K+ token contexts
   - Create proper streaming test scenarios

---

**Remember**: The framework structure is complete, but tests need to actually execute the system with test inputs rather than checking pre-existing outputs.
