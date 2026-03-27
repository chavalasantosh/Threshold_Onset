# Structure-First Language Model: Architecture

## Summary

A structurally emergent language model that produces text from text via constraint-driven symbol generation. No embeddings, no transformers, no neural networks. Architecture is first-principles: structure emerges from action and repetition; decoding is structural inversion.

---

## Pipeline Overview

```
Input text
    → Tokenization (santok or whitespace)
    → Phase 0: token → residue (hash-based, opaque)
    → Phase 1: segmentation, boundaries
    → Phase 2: identity (persistent segments)
    → Phase 3: relations (graph)
    → Phase 4: symbols (aliasing)
    → Phase 5–9: consequence, meaning, roles, constraints, fluency
    → Generation: FluencyGenerator or path-scored
    → Decoder: symbol → identity → residue → token
    → Output text
```

---

## Core Principles

1. **Action before knowledge**
   - Tokens become actions.
   - Residues are numeric, opaque.
   - No meaning at Phase 0–4.

2. **Structure emerges**
   - Persistence: segments that repeat across runs become identities.
   - Relations: co-occurrence forms graph edges.
   - Symbols: pure aliasing for identities and relations.

3. **Decoder is structural inversion**
   - Forward: token → residue → identity → symbol
   - Reverse: symbol → identity → residue → token
   - No heuristics. No probability. Pure backward walk through structure.

4. **Generation is constraint-bound**
   - Only allowed transitions (graph edges) are valid.
   - No self-transitions.
   - Scoring: frequency + pressure + learned bias (optional).

---

## Components

### Symbol Decoder

- **Location:** `threshold_onset/semantic/phase9/symbol_decoder.py`
- **Function:** `build_structural_decoder(tokens, residue_sequences, phase2_metrics, phase4_metrics)`
- **Space:** O(|symbols| + |identities| + |vocab|)
- **Time:** O(n) build, O(1) decode per symbol
- **Logic:** Residue → token from first occurrence; identity → residues from segment hash; symbol → token via identity → residue.

### Generation Paths

1. **Path-scored:** `generate.py` + `generate_sequence` → uses `path_scores`, `ContinuationObserver`
2. **Fluency:** `generate_text_via_fluency` → uses `FluencyGenerator` (Phases 5–9)

---

## Design Decisions

| Decision | Rationale |
|----------|------------|
| Hash-based residues | No external semantics; deterministic token→residue |
| Segment window = 2 | Balances identity granularity and persistence |
| Structural decoder | Faithful to pipeline; no external probability |
| Two generation paths | Path-scored: fast. Fluency: consequence-aware. |

---

## Dependencies

- **Runtime:** Python stdlib only
- **No:** numpy, torch, transformers, sklearn, etc.
- **Internal:** santok (tokenization) is project-owned

---

## Invariants

- Decoder maps symbols to tokens that produced them in the forward pass.
- Generation respects graph edges.
- No self-transitions allowed.

---

## References

- `COMPLETE_PROJECT_DOCUMENTATION.md` – full project
- `threshold_onset/semantic/phase9/symbol_decoder.py` – decoder implementation
- `integration/run_complete.py` – end-to-end flow
