# Model Contract: Constraint-First Sequence Model (CFSM)

## What This Model Guarantees

### 1. Structural Invariants

- **No self-transitions**: An identity cannot transition to itself. Structure never supports self-transitions.
- **Persistent relations only**: Only relations that survive multi-run stability are allowed
- **Deterministic structure**: Given the same input and tokenization, structure emerges identically

### 2. Constraint Enforcement

- **Refusal is structural**: When a transition is refused, it is because no persistent relation exists
- **No forbidden paths unlocked**: Learning cannot create new structural relations
- **Constraint-first**: Structure is immutable; only preference can change

### 3. Output Guarantees

- **Allowed paths only**: All generated sequences respect structural constraints
- **No self-repetition**: Immediate self-transitions are forbidden
- **Stable continuation**: Given the same structure, refusals occur in the same places

---

## What This Model Refuses

### 1. Semantic Guarantees

- **No meaning**: The model does not guarantee semantic correctness
- **No fluency**: The model does not guarantee human-readable output
- **No intelligence**: The model does not guarantee understanding

### 2. Neural Guarantees

- **No probability distributions**: Scores are mechanical, not probabilistic
- **No gradient learning**: Learning is event-driven, not gradient-based
- **No weight optimization**: No global optimization occurs

### 3. Language Guarantees

- **No grammar**: The model does not enforce grammatical rules
- **No coherence**: The model does not guarantee narrative coherence
- **No context window**: The model does not maintain explicit context buffers

---

## What Learning Can Change

### 1. Preference Adjustment

- **Bias values**: Learning adjusts preference scores for allowed transitions
- **Path ranking**: Learning can change which allowed path is preferred
- **Selection weighting**: Learning affects ranking and optional stochastic choice among allowed paths, without changing allowed sets

### 2. Adaptation

- **Refusal avoidance**: Learning can bias away from paths that lead to refusals
- **Loop prevention**: Learning can penalize paths that create short cycles
- **Stability preference**: Learning can reinforce paths that remain valid

### 3. Constraints

- **Learning rate**: `alpha` parameter controls speed of adaptation
- **Bias bounds**: `bound` parameter limits maximum bias adjustment
- **Update frequency**: `step()` frequency controls adaptation rate

---

## What Learning Can Never Change

### 1. Structure

- **Identities**: Learning cannot create or destroy identities
- **Relations**: Learning cannot add or remove structural relations
- **Constraints**: Learning cannot modify constraint rules

### 2. Validity

- **Forbidden paths**: Learning cannot allow previously forbidden transitions
- **Self-transitions**: Learning cannot enable self-transitions
- **Structural rules**: Learning cannot violate structural invariants

### 3. Foundation

- **Phase 0-4 output**: Learning cannot modify structure emergence
- **Multi-run stability**: Learning cannot change what persists across runs
- **Refusal behavior**: Learning cannot change structural refusal logic

---

## What Output Actually Means

### 1. Output is NOT Text

Text is a **surface projection** of the real output.

Real output is:
- A **path through constrained identity space**
- A **sequence of allowed transitions**
- A **demonstration of structural possibility**

### 2. Output is NOT Meaning

Output does not represent:
- Semantic content
- Linguistic meaning
- Conceptual understanding

Output represents:
- **Structural possibility**
- **Constraint satisfaction**
- **Allowed continuation**

### 3. Output is NOT Intelligence

Output is:
- **Mechanical continuation**
- **Constraint-driven selection**
- **Structure-guided navigation**

Output is NOT:
- Creative generation
- Intelligent reasoning
- Semantic understanding

---

## Model Definition

### Formal Name

**Constraint-First Sequence Model (CFSM)**

Alternative names:
- Structural Continuation Engine (SCE)
- Identity-Topology Generator (ITG)

### Core Promise

> "Given structure and constraints,
> I will produce the **most stable allowed continuation**."

### What It Is

A deterministic, constraint-governed continuation system where:
- Structure emerges from token patterns
- Constraints are enforced mechanically
- Learning adjusts preference, not possibility
- Output is structural, not semantic

### What It Is NOT

- ❌ Not an LLM
- ❌ Not a neural network
- ❌ Not a transformer
- ❌ Not a language model
- ❌ Not an AI system

---

## Core Engine Declaration

**STATUS: FROZEN**

> **"Core Engine (Phases 0–4 + constraints) is frozen and must not change."**

This is not a technical statement — this is a **psychological safety boundary**.

No more second-guessing the foundation.

---

## Architecture Layers

### Layer A: Core Engine (FROZEN)

**Status**: ✅ Complete and stable

Components:
- Structure emergence (Phases 0-4)
- Constraint enforcement
- Path scoring
- Selection mechanism

**Rule**: This layer is immutable. No modifications allowed.

### Layer B: Surface Adapter (ACTIVE)

**Status**: 🟡 In development

Components:
- Symbol → token mapping
- Text rendering
- Output formatting

**Rule**: This layer can be improved without touching Layer A.

### Layer C: Learning Layer (BOUNDED)

**Status**: ✅ Complete and bounded

Components:
- Preference adjustment
- Bias updates
- Event-driven adaptation

**Rule**: This layer can only adjust preference, never structure.

---

## Validation Criteria

### Model is "correct" when:

1. ✅ Structure emerges deterministically
2. ✅ Constraints are enforced mechanically
3. ✅ Refusals occur in predictable places
4. ✅ Learning adjusts preference only
5. ✅ Output respects structural constraints

### Model is "broken" when:

1. ❌ Structure changes during learning
2. ❌ Forbidden paths become allowed
3. ❌ Self-transitions occur
4. ❌ Constraints are violated
5. ❌ Refusal behavior becomes inconsistent

---

## Usage Contract

### Input Contract

- **Input**: Text string (any language, any content)
- **Tokenization**: Method must be specified (word, character, etc.)
- **Runs**: Multi-run mode for stability

### Output Contract

- **Output**: Sequence of symbols (structural)
- **Surface**: Text projection (optional, for readability)
- **Guarantee**: All transitions are structurally allowed

### Learning Contract

- **Observations**: Transition outcomes (ok, refusal, dead_end, loop)
- **Updates**: Bias adjustments only
- **Frequency**: Periodic (not every token)
- **Bounds**: Clipped to [-bound, +bound]

---

## Success Metrics

### Structural Metrics

- Multi-run stability ratio = 1.0
- Refusal consistency across runs
- Constraint violation count = 0

### Learning Metrics

- Bias convergence (not divergence)
- Preference drift (slow, bounded)
- Edge count growth (new preferences, not new structure)

### Output Metrics

- Self-transition count = 0
- Constraint violation count = 0
- Structural consistency

---

## Failure Modes

### Structural Failure

- Structure changes between runs
- Constraints are violated
- Refusals become inconsistent

**Response**: Freeze structure, debug emergence

### Learning Failure

- Bias values diverge unbounded
- Structure is modified
- Forbidden paths become allowed

**Response**: Reset learning, verify bounds

### Output Failure

- Self-transitions occur
- Constraint violations in sequences
- Structural inconsistency

**Response**: Debug selection mechanism, verify constraints

---

## Version

**Model Contract Version**: 1.0.0

**Date**: 2025-01-13

**Status**: FROZEN - Foundation locked

---

## Notes

- This contract defines what the model IS, not what it should become
- All future development must respect this contract
- Violations of this contract indicate bugs, not features
- This contract is the foundation - it does not change
