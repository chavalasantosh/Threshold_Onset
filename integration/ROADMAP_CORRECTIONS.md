# Roadmap Corrections: What Was Wrong & What's Fixed

**Date**: 2025-01-13  
**Source**: Critical feedback analysis  
**Purpose**: Document corrections to remove hidden imports

---

## Critical Issues Identified

### ❌ Issue 1: "Meaning Discovery" Was Actually Role Discovery

**What Was Wrong**:
- Phase 5 was called "Meaning Discovery"
- But it was classifying identities as "active/passive/neutral"
- That's structural role typing, not meaning

**Why It's Wrong**:
- Confusing labels will cause circular reasoning later
- "Meaning" should be about consequences, not roles

**Fix Applied**:
- ✅ Renamed Phase 5 to "Consequence Layer"
- ✅ Renamed Phase 6 to "Role Induction" (not "Meaning")
- ✅ Meaning comes from consequences, roles come from behavior

---

### ❌ Issue 2: Imported POS Rules (Silent Cheating)

**What Was Wrong**:
- Phase 7 had rules like:
  - "Noun appears after determiners"
  - "Verb appears after nouns"
  - "Adjective appears before nouns"
- This is imported linguistic theory, not discovered

**Why It's Wrong**:
- Violates first-principles rule
- No libraries needed, but still imported knowledge
- Assumes grammar rules exist before discovery

**Fix Applied**:
- ✅ Removed all POS rules
- ✅ Discover role patterns from data only
- ✅ No "noun/verb/determiner" labels
- ✅ Just role_0, role_1, role_2 (numbers, not labels)
- ✅ Patterns discovered, not imported

---

### ❌ Issue 3: "Text → Tokens" Violates Phase 0

**What Was Wrong**:
- Roadmap showed "Text → Tokens → Residues"
- But Phase 0 is about Action → Residue
- "Tokens" assumes language segmentation already happened

**Why It's Wrong**:
- Violates Phase 0 discipline
- Assumes input is already tokenized
- Skips the action layer

**Fix Applied**:
- ✅ Changed to "Input Stream → Action Events → Residue"
- ✅ No assumption about tokens
- ✅ Actions come from input stream
- ✅ Phases 0-4 handle the rest

---

### ❌ Issue 4: Topology-Only Measurement (Not Real Meaning)

**What Was Wrong**:
- `future_expansion` was just "reachable nodes count"
- That's graph topology, not meaning
- Missing context dependence, pressure, consequences

**Why It's Wrong**:
- Meaning needs counterfactual change
- "What futures become possible/impossible BECAUSE of this structure?"
- Topology alone misses context and pressure

**Fix Applied**:
- ✅ Added rollout-based measurement
- ✅ Contextual consequence: C(identity | context)
- ✅ Counterfactual deltas: M(transition | context)
- ✅ Measures survival, refusal, pressure, entropy
- ✅ Not just static counts

---

### ❌ Issue 5: Node-Only Meaning (Should Be Transition-Based)

**What Was Wrong**:
- Focused on node consequence vectors
- But meaning is in transitions, not nodes
- "eat" alone is weak, "eat + apple" produces consequence

**Why It's Wrong**:
- Meaning emerges in edge effects
- Motif effects (A→B→C)
- Template effects (slot filling)
- Node-only is too coarse

**Fix Applied**:
- ✅ Meaning on transitions, not just nodes
- ✅ Transition outcome table
- ✅ Counterfactual deltas for edges
- ✅ Template-based meaning

---

### ❌ Issue 6: Hand-Picked Thresholds (Not Emergent)

**What Was Wrong**:
- Used thresholds like `threshold_stable`, `threshold_expansion`
- These were hand-picked, not derived from data

**Why It's Wrong**:
- Violates first-principles
- Should be emergent from data
- Percentile-based or clustering-based

**Fix Applied**:
- ✅ Emergent thresholds
- ✅ Percentile-based similarity
- ✅ Data-driven clustering
- ✅ No hand-picked values

---

### ❌ Issue 7: Boolean Signatures (Too Lossy)

**What Was Wrong**:
- Meaning signatures were booleans:
  - `'expands_futures': bool`
  - `'stabilizes_continuation': bool`
- Too lossy, collapses distinct meanings

**Why It's Wrong**:
- Loses information
- Different meanings become same bucket
- Should be continuous vectors

**Fix Applied**:
- ✅ Vector signatures (real values)
- ✅ Δsurvival, Δentropy, Δpressure, Δrefusal_risk
- ✅ Context-sensitivity index
- ✅ Stability variance
- ✅ Full information preserved

---

### ❌ Issue 8: Fluency = Low Entropy Only (Needs Novelty)

**What Was Wrong**:
- Only scored for low entropy
- Can produce boring loops
- Repetitive patterns
- Trivial fixed points

**Why It's Wrong**:
- Fluency needs stability AND novelty
- Continuation AND progress
- Low refusal AND non-degeneracy

**Fix Applied**:
- ✅ Added novelty constraint
- ✅ Penalize repeating recent patterns
- ✅ Anti-collapse term
- ✅ Balance stability + novelty

---

## Missing Core: Consequence Layer

### What Was Missing

**Consequence**: Some continuations succeed, others fail (or have different cost).

Meaning is an **expectation about consequences**, not a label about graph shape.

### What Was Added

**Phase 5: Consequence Layer**
- Transition outcome table
- Contextual consequence distributions
- Counterfactual deltas
- Pressure fields

**This makes meaning measurable.**

---

## Key Fixes Summary

| Issue | What Was Wrong | What's Fixed |
|-------|---------------|--------------|
| 1. Label Confusion | "Meaning" was actually roles | Renamed: Consequence → Role Induction |
| 2. POS Rules | Imported grammar rules | Discovered patterns only |
| 3. Input Assumption | "Text → Tokens" | "Input Stream → Actions" |
| 4. Topology Only | Static graph counts | Rollout-based measurement |
| 5. Node Only | Meaning on nodes | Meaning on transitions |
| 6. Hand Thresholds | Fixed values | Emergent, data-driven |
| 7. Boolean Signatures | Lossy booleans | Continuous vectors |
| 8. Low Entropy Only | Can collapse | Stability + Novelty |

---

## The Corrected Structure

### Phase 5: Consequence Layer
- **Purpose**: Attach outcome signals to transitions
- **Output**: Transition outcome table, contextual consequence, counterfactual deltas
- **No imports**: Pure measurement

### Phase 6: Role Induction
- **Purpose**: Discover behavioral roles (NOT "meaning")
- **Output**: Role clusters, role assignments (just IDs, no labels)
- **No imports**: Data-driven clustering

### Phase 7: Constraint & Template Discovery
- **Purpose**: Discover grammar-like constraints (NOT imported rules)
- **Output**: Role patterns, forbidden patterns, templates
- **No imports**: Discovered from data

### Phase 8: Generation
- **Purpose**: Generate fluent sequences
- **Output**: Quality, readable text
- **No imports**: Constraint + Stability + Novelty

---

## What Makes This Correct

### ✅ No Hidden Imports
- No grammar rules
- No POS tags
- No linguistic theory
- No hand thresholds

### ✅ Pure First Principles
- Everything from measurement
- Everything from data
- Everything from structure
- Everything from consequences

### ✅ Measurable & Operational
- Counterfactual deltas
- Contextual consequence
- Transition outcomes
- Rollout-based measurement

### ✅ Prevents Collapse
- Novelty constraint
- Anti-degeneracy
- Stability + progress
- Template satisfaction

---

## Implementation Priority

### Step 1: Minimal Kernel
**"Transition Outcome Table"**
- For each edge (s→t):
  - count
  - contexts
  - outcome/cost
  - stability over runs

### Step 2: Consequence Layer
- Rollout measurement
- Contextual consequence
- Counterfactual deltas

### Step 3: Role Induction
- Feature vectors
- Data-driven clustering
- Role assignments

### Step 4: Constraint Discovery
- Role patterns
- Forbidden patterns
- Templates

### Step 5: Generation
- Stability scoring
- Novelty constraint
- Template satisfaction

---

## Final Validation

### ✅ What's Correct Now
- No imported knowledge
- No hand thresholds
- No POS rules
- No grammar assumptions
- Pure measurement
- Data-driven discovery
- First principles only

### ✅ What Will Work
- Counterfactual measurement → real meaning
- Transition-based → fine-grained meaning
- Emergent thresholds → no cheating
- Vector signatures → full information
- Novelty constraint → prevents collapse

---

**All corrections applied. Roadmap is now logically airtight.**

---

**End of Corrections Document**
