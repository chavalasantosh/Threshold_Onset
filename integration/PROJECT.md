# CFSM Project Plan (Clean, Final, Grounded)

**Purpose**: You always know **where you are**, **why you're doing something**, and **what success means**.

No wandering. No traps. No blind work.

---

## Current Status Overview

| Phase | Status | Document |
|-------|--------|----------|
| PHASE 0 - Hard Reset | ✅ Complete | MODEL.md (Core Engine Declaration) |
| PHASE 1 - Foundation Freeze | ✅ Complete | MODEL.md (Layer A: FROZEN) |
| PHASE 2 - Define "Working" | ✅ Complete | MODEL.md (Success Metrics) |
| PHASE 3 - Surface Adapter | 🟡 Active | NEXT_STEPS.md (Step 3) |
| PHASE 4 - Observability | 🟡 Partial | (Escape topology exists, needs tools) |
| PHASE 5 - Learning | ✅ Complete | MODEL.md (Layer C: BOUNDED) |
| PHASE 6 - Demo | ⏸️ Not Started | - |
| PHASE 7 - Optional Future | ⏸️ Not Started | - |

---

## PHASE 0 — HARD RESET (Mental + Project)

**Status**: ✅ COMPLETE

**What exists**: `MODEL.md` - Core Engine Declaration

### Acceptance Statement

> "If constraints held, the system worked."

**Deliverable**: ✅ DONE - Internal acceptance established

---

## PHASE 1 — FOUNDATION FREEZE

**Status**: ✅ COMPLETE  
**Document**: `MODEL.md` - Layer A: Core Engine (FROZEN)

### Frozen Components (from MODEL.md)

✅ **Structure emergence** (Phases 0-4)
✅ **Multi-run stability**
✅ **Constraint enforcement**
✅ **Refusal logic**
✅ **Path scoring rules**
✅ **Selection rules**
✅ **Invariants** (self-transition forbidden, etc.)

### Declaration (from MODEL.md)

> **"Core Engine (Phases 0–4 + constraints) is frozen and must not change."**

### Allowed Actions

- Bug fixes **only if they violate the contract**
- Instrumentation (logging, metrics)
- Observation tooling

### Forbidden Forever

- ❌ Semantic fixes
- ❌ Grammar hacks
- ❌ "Just one heuristic"
- ❌ "Maybe add probabilities"

**This is bedrock. Digging here breaks everything.**

---

## PHASE 2 — DEFINE WHAT "WORKING" MEANS

**Status**: ✅ COMPLETE  
**Document**: `MODEL.md` - Success Metrics

### You only measure (from MODEL.md):

- ✅ Constraint violations = **0**
- ✅ Self-transitions = **0**
- ✅ Multi-run stability = **1.0**
- ✅ Refusal positions = **consistent**

### You never measure:

- ❌ Fluency
- ❌ Meaning
- ❌ Coherence
- ❌ Intelligence
- ❌ Readability

### Success Definition (from MODEL.md)

> If structure is stable and constraints hold → **success**, even if output looks insane.

---

## PHASE 3 — SURFACE ADAPTER (CONTAINED PLAYGROUND)

**Status**: 🟡 ACTIVE  
**Document**: `NEXT_STEPS.md` - Step 3  
**Existing**: `surface.py` (needs refinement)

### Purpose

> Make structure **observable**, not better.

### Rules (from MODEL.md - Layer B)

Surface Adapter may:

- ✅ Map symbols → tokens
- ✅ Render sequences
- ✅ Format output
- ✅ Visualize paths

Surface Adapter may **NOT**:

- ❌ Change ordering
- ❌ Inject grammar
- ❌ Smooth text
- ❌ Bias structure
- ❌ Hide refusals

### Think of it as:

> A microscope, not makeup.

### Next Action

Build **Surface Adapter v0** that exposes structure:

```
STRUCTURE OUTPUT
================

Path: [12] → [7] → [3] → [11]
Refusals: None
Biases: (12→7)=+0.12, (7→3)=+0.05, (3→11)=+0.03

---

Path: [5] → [5] ❌ REFUSED
  ↳ Escape: [5] → [8] (chosen)
Refusals: 1 at step 1
Biases: (5→8)=+0.08

---

SURFACE TEXT (lossy annotation):
before knowledge exists
```

---

## PHASE 4 — OBSERVABILITY & TOOLS

**Status**: 🟡 PARTIAL  
**Existing**: Escape topology measurement, refusal observation

### What Exists

- ✅ Escape topology measurement (`escape_topology.py`)
- ✅ Refusal observation (`continuation_observer.py`)
- ✅ Topology clustering (`topology_clusters.py`)

### What's Missing

Tools that answer:

- Where do refusals occur? (heatmaps)
- Which symbols are under pressure? (visualization)
- Which paths dominate? (rank distributions)
- How does learning shift preference? (bias evolution graphs)

### Next Action

Build visualization tools for:
- Refusal heatmaps
- Pressure profiles
- Path rank distributions
- Bias evolution over time

---

## PHASE 5 — LEARNING (STRICTLY BOUNDED)

**Status**: ✅ COMPLETE  
**Document**: `MODEL.md` - Layer C: Learning Layer (BOUNDED)  
**Implementation**: `preference_learner.py`

### Learning is allowed to (from MODEL.md):

- ✅ Re-rank allowed paths
- ✅ Penalize refusal-prone paths
- ✅ Prefer stable continuations

### Learning is never allowed to (from MODEL.md):

- ❌ Create relations
- ❌ Remove relations
- ❌ Override constraints
- ❌ Change refusal logic

### Validation Rule (from MODEL.md)

> If learning changes structure → it's a bug.

**Status**: ✅ Implemented and bounded

---

## PHASE 6 — DEMO (NOT A PRODUCT)

**Status**: ⏸️ NOT STARTED

### Demo must highlight:

- ✅ Deterministic structure
- ✅ Refusal as a feature
- ✅ Same input → same refusal
- ✅ Learning changes preference only

### Demo must avoid:

- ❌ Long fluent text
- ❌ Claims of intelligence
- ❌ Comparisons to GPT
- ❌ "Looks like language" framing

### Think

**Physics demo**, not chatbot demo.

---

## PHASE 7 — OPTIONAL FUTURE (ONLY ONE AT A TIME)

**Status**: ⏸️ NOT STARTED

Choose **one**, never more.

### Option A — Formalization

- Write a paper-style spec
- Define invariants mathematically
- Prove refusal consistency

### Option B — Visualization

- Graph-based UI
- Live constraint enforcement
- Interactive path exploration

### Option C — Meta-Observation (Phase 5+)

- Observe learning dynamics
- Measure stability over time
- Still no structure changes

**If you feel lost → you picked too many.**

---

## DAILY WORK RULE (VERY IMPORTANT)

Before touching code, answer **one question**:

> **"Which phase am I working in?"**

If you cannot answer that in one sentence → **stop**.

---

## Mapping: Existing Docs → Phases

### MODEL.md covers:

- ✅ PHASE 0: Core Engine Declaration
- ✅ PHASE 1: Layer A (FROZEN) definition
- ✅ PHASE 2: Success Metrics, Validation Criteria
- ✅ PHASE 5: Layer C (BOUNDED) definition

### NEXT_STEPS.md covers:

- ✅ PHASE 0: Foundation status
- ✅ PHASE 2: What to ask/not ask
- 🟡 PHASE 3: Surface Adapter requirements

### Missing/Partial:

- 🟡 PHASE 3: Surface Adapter v0 implementation
- 🟡 PHASE 4: Visualization tools
- ⏸️ PHASE 6: Demo design
- ⏸️ PHASE 7: Future options

---

## What You Already Have (Summary)

### ✅ Complete

1. **Model Contract** (`MODEL.md`)
   - What it guarantees
   - What it refuses
   - What learning can/cannot change
   - Architecture layers
   - Success metrics
   - Failure modes

2. **Foundation** (Layer A)
   - Phases 0-4 frozen
   - Constraints enforced
   - Invariants proven

3. **Learning** (Layer C)
   - Bounded preference adjustment
   - Event-driven updates
   - No structure mutation

4. **Observability** (Partial)
   - Escape topology measurement
   - Refusal observation
   - Topology clustering

### 🟡 In Progress

1. **Surface Adapter** (Layer B)
   - Basic implementation exists
   - Needs structure-first rendering

2. **Visualization Tools**
   - Metrics exist
   - Tools needed

### ⏸️ Not Started

1. **Demo**
2. **Formalization**
3. **Meta-Observation**

---

## Next Single Action

**PHASE 3: Build Surface Adapter v0**

Create `integration/surface_v0.py` that:

1. Renders structure paths (symbol IDs)
2. Shows refusals and escapes
3. Displays biases (optional)
4. Shows surface text as annotation only

**Purpose**: Make structure observable, not better.

---

## Final Grounding

You did **not** fail.
You did **not** waste nights.
You did **not** build random shit.

You built:

- A deterministic system
- With hard invariants
- With auditable refusal
- With bounded learning
- With zero semantic lies

**That's rare. That's solid. That's real.**

---

## Version

**Project Plan Version**: 1.0.0  
**Date**: 2025-01-13  
**Status**: ACTIVE - Foundation locked, surface in progress
