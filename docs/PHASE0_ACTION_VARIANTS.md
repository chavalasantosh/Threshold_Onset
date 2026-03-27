# Phase 0 Action Variants — Structured but Meaningless Actions

**Date:** 2026-01-13  
**Status:** 📋 **DESIGNED (not implemented)**

---

## The Problem

**Current Phase 0 produces pure noise:**
- `random.random()` - independent samples
- No temporal coupling
- No memory
- No structure

**Result:**
- Phase 1 detects segmentation correctly
- Phase 1 produces `repetition_count = 0` and `survival_count = 0`
- Phase 2 gate check fails (correctly)
- Phase 3 never runs (correctly)

**This is correct behavior.** Pure noise cannot produce persistence.

---

## The Solution

**Introduce structured but meaningless actions in Phase 0.**

These actions must:
- ✅ Be Phase 0 compliant (no meaning, no labels, no interpretation)
- ✅ Produce temporal correlation (weak structure)
- ✅ Enable persistence to emerge naturally
- ✅ Still be opaque and uninterpreted

---

## Allowed Action Variants

### 1. Random with Inertia
**Concept:** Action(t+1) depends slightly on Action(t)

```python
# Stateful action with carry-over (internal state, no naming)
class InertiaAction:
    def __init__(self):
        self._state = random.random()  # Internal state, not a name
    
    def __call__(self):
        # Weak correlation: new value = 0.7 * old + 0.3 * random
        self._state = 0.7 * self._state + 0.3 * random.random()
        return self._state
```

**Compliance:** ✅ State is internal, not named, not interpreted

### 2. Bounded Random Walk
**Concept:** Action drifts within bounds

```python
class BoundedWalk:
    def __init__(self):
        self._position = random.random()
        self._step_size = 0.1  # Fixed, not adaptive
    
    def __call__(self):
        # Random walk with reflection at boundaries
        step = (random.random() - 0.5) * self._step_size
        self._position = max(0.0, min(1.0, self._position + step))
        return self._position
```

**Compliance:** ✅ Position is internal state, not named

### 3. Decay + Noise
**Concept:** Action decays with added noise

```python
class DecayNoise:
    def __init__(self):
        self._value = random.random()
        self._decay = 0.95  # Fixed decay rate
    
    def __call__(self):
        # Decay towards random target
        target = random.random()
        self._value = self._decay * self._value + (1 - self._decay) * target
        return self._value
```

**Compliance:** ✅ Decay is mechanical, not interpreted

### 4. Weak Oscillator
**Concept:** Action oscillates with noise

```python
class WeakOscillator:
    def __init__(self):
        self._phase = random.random() * 2 * math.pi
        self._frequency = 0.1  # Fixed frequency
        self._amplitude = 0.3  # Fixed amplitude
    
    def __call__(self):
        # Oscillation with noise
        self._phase += self._frequency
        oscillation = 0.5 + self._amplitude * math.sin(self._phase)
        noise = random.random() * 0.2
        return max(0.0, min(1.0, oscillation + noise))
```

**Compliance:** ✅ Oscillation is mechanical, not interpreted

---

## Implementation Strategy

### Step 1: Freeze Current Phase 0
- Tag as baseline: `phase0_noise_baseline`
- Keep as reference
- Do not modify

### Step 2: Create Action Variants Module
- Location: `src/phase0/actions.py` (new file)
- Contains action generators (callable factories)
- All Phase 0 compliant
- All produce opaque residues

### Step 3: Test Each Variant
- Run Phase 0 with each action variant
- Run Phase 1 on results
- Observe when `repetition_count > 0` or `survival_count > 0`
- Document which variants enable persistence

### Step 4: Gate Logic Unlocks Naturally
- When persistence appears, Phase 2 gate passes
- Phase 2 produces identities
- Phase 3 gate passes
- System progresses naturally

---

## Phase 0 Compliance Check

All action variants must:
- ✅ Return float values (0.0 to 1.0)
- ✅ Be callable (function or callable object)
- ✅ Have no external names or labels
- ✅ Have no interpretation
- ✅ Use internal state only (not displayed)
- ✅ Be structureless from external view

**Internal state is allowed** as long as:
- It's not named externally
- It's not interpreted
- It's not displayed
- It's mechanical only

---

## What NOT to Do

❌ Do not relax gate logic  
❌ Do not hardcode persistence  
❌ Do not inject identity  
❌ Do not fake survival  
❌ Do not jump to Phase 3  
❌ Do not add meaning to actions  
❌ Do not label action types  
❌ Do not interpret action behavior

---

## Expected Outcome

With structured actions:
- Phase 0 still produces opaque residues
- Phase 1 detects segmentation
- Phase 1 detects repetition (repetition_count > 0)
- Phase 1 detects survival (survival_count > 0)
- Phase 2 gate passes
- Phase 2 produces identities
- Phase 3 gate passes
- Phase 3 detects relations

**All without violating Phase 0 constraints.**

---

## Status

**Action Variants:** 📋 **DESIGNED (not implemented)**

This is the correct next step. Do not modify gates. Do not force phases. Let persistence emerge naturally from structured actions.

---

## Next Steps

1. ✅ Understand the problem (done)
2. ⏭️ Design action variants (in progress)
3. ⏭️ Implement action variants
4. ⏭️ Test with Phase 1
5. ⏭️ Observe persistence emergence
6. ⏭️ Let gates unlock naturally

**The system is behaving correctly. Now change the world (actions), not the rules (gates).**
