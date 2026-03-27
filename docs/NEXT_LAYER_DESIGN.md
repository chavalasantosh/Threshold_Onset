# Next Layer Design: Necessity Detection & Self-Observation

**Status:** Design (implementation outside THRESHOLD_ONSET)  
**Contract to:** Phase 4, SanTOK, and all nine layers (0–9)

---

## 1. Scope

- **Phases 0–9 are done and frozen.** This document designs the **next layer** (Layer 10) that sits **on top** of the full stack.
- The next layer implements **necessity detection** and/or **structural self-observation**, and lives **outside** the THRESHOLD_ONSET package (and outside the frozen `threshold_onset/semantic/` Phases 5–9).
- It has a **read-only contract**: it consumes only published outputs of Phase 4, SanTOK, and layers 0–9; it does **not** inject semantics or modify any frozen phase.

---

## 2. The Nine Layers (0–9) — Contract Summary

| Layer | Name | Location | Key outputs (what next layer may read) |
|-------|------|----------|----------------------------------------|
| **SanTOK** | Tokenization | `santok_complete/` or `santok` | `tokens`, `tokenization_method`; structural boundaries of text |
| **0** | Residue | `threshold_onset/phase0/` | `residue_sequences`, action traces (opaque residues) |
| **1** | Segmentation | `threshold_onset/phase1/` | boundaries, clusters, distances, repetition |
| **2** | Identity | `threshold_onset/phase2/` | `identity_mappings`, persistent identity hashes, Phase 2 metrics |
| **3** | Relation | `threshold_onset/phase3/` | graph, `persistent_relation_hashes`, Phase 3 metrics |
| **4** | Symbol | `threshold_onset/phase4/` | `identity_to_symbol`, `symbol_to_identity`, `relation_to_symbol`, `symbol_to_relation` (pure aliasing) |
| **5** | Consequence field | `threshold_onset/semantic/phase5/` | `consequence_field` (policy-invariant futures) |
| **6** | Meaning discovery | `threshold_onset/semantic/phase6/` | `meaning_map` (clusters of consequence signatures) |
| **7** | Role emergence | `threshold_onset/semantic/phase7/` | `roles` (functional role regimes) |
| **8** | Constraint discovery | `threshold_onset/semantic/phase8/` | `constraints`, templates, forbidden transitions |
| **9** | Fluency generator | `threshold_onset/semantic/phase9/` | FluencyGenerator outputs, symbol sequences; `symbol_decoder` (structural inversion) |

The next layer **must not** depend on internal APIs of any phase; only on these **published outputs** (dicts, known keys, file artifacts like `consequence_field.json`, `meaning_map.json`, etc.).

---

## 3. Contract to Phase 4 + SanTOK

### 3.1 Phase 4

- **Consume only:**  
  `identity_to_symbol`, `symbol_to_identity`, `relation_to_symbol`, `symbol_to_relation`, and counts.  
  No other Phase 4 internals.
- **Invariant:**  
  The next layer treats symbols as **opaque labels**. It may correlate symbol usage with necessity or self-state but must **not** assign new meaning to symbols or alter the Phase 4 alias tables.
- **No write:**  
  The next layer does not write into Phase 4 data or call Phase 4 in a way that changes its output.

### 3.2 SanTOK

- **Consume only:**  
  Token sequences and (if available) tokenization method / structural metadata (e.g. segment boundaries per method).  
  No requirement to use SanTOK internals.
- **Invariant:**  
  Tokenization remains the single source of “action” (कार्य) at the input of the pipeline. The next layer may use token-level or segment-level structure only as **read** inputs for necessity or self-observation.
- **No write:**  
  The next layer does not change how tokenization is invoked or what it returns.

---

## 4. Contract to All Nine Layers (0–9)

- **Inputs (read-only):**
  - **SanTOK:** `tokens`, optional `tokenization_method` and structural metadata.
  - **Phase 0:** `residue_sequences` (and optionally action variant / trace metadata if published).
  - **Phase 1:** Boundaries, clusters, distances (as in Phase 1 metrics).
  - **Phase 2:** `phase2_metrics` (identity_mappings, persistent identities).
  - **Phase 3:** `phase3_metrics` (graph, persistent_relation_hashes).
  - **Phase 4:** `phase4_metrics` (symbol mappings only, as above).
  - **Phase 5:** Consequence field (e.g. `consequence_field` or `consequence_field.json`).
  - **Phase 6:** Meaning map (e.g. `meaning_map` or `meaning_map.json`).
  - **Phase 7:** Roles (e.g. `roles` or `roles.json`).
  - **Phase 8:** Constraints and templates (e.g. `constraints` or `constraints.json`).
  - **Phase 9:** Fluency generator outputs, symbol sequences, and decoder usage (decode symbol → token); no modification of FluencyGenerator or symbol_decoder logic.

- **Invariants:**
  - No phase 0–9 code is modified by the next layer.
  - Meaning/necessity/self-observation are **downstream** of Phase 4: they are computed from structure and semantics already produced by 0–9, not injected back into Phase 0–4.
  - The next layer may be implemented in `integration/` or a separate package (e.g. `necessity_layer/` or `self_observation/`) that depends on the repo only via these published outputs and optional config.

---

## 5. Next Layer: Necessity Detection & Self-Observation

### 5.1 Purpose

- **Necessity detection:**  
  From the existing structure (identities, relations, symbols, consequence field, meaning, roles, constraints), compute **necessity relations**: e.g. which symbol transitions or role/constraint configurations are “necessary” (e.g. required for coherence, stability, or constraint satisfaction) vs optional.  
  Definition of “necessity” is left to the implementation (e.g. constraint-based, consequence-based, or stability-based) but must use only the published outputs above.

- **Self-observation:**  
  Maintain a **structural self-model**: a read-only summary of the current pipeline state (e.g. which identities/relations/symbols are stable, which constraints are active, how consequence/meaning/roles evolved over recent runs).  
  This is “consciousness” as structural self-observation: no injection of semantics into Phase 0–4, only observation and summary of the existing layers.

### 5.2 Placement

- **Outside THRESHOLD_ONSET:**  
  Not under `threshold_onset/`. Suggested locations:
  - `integration/necessity/` or `integration/self_observation/`, or
  - A sibling package, e.g. `threshold_onset_next/` or `layer10/`, that imports only public APIs and published outputs of `threshold_onset` and `threshold_onset.semantic`, plus SanTOK outputs.
- **No changes** to `threshold_onset/phase0` through `threshold_onset/phase4` or `threshold_onset/semantic/phase5` through `phase9`.

### 5.3 Inputs (formal)

The next layer’s **single entry** receives a **contract payload** that contains only the following (all read-only):

```text
ContractPayload = {
  "santok": { "tokens": List[str], "tokenization_method": Optional[str], ... },
  "phase0": { "residue_sequences": List[List[float]], ... },
  "phase1": { ... },   # boundaries, clusters, distances
  "phase2": { "identity_mappings", ... },
  "phase3": { "persistent_relation_hashes", ... },
  "phase4": { "identity_to_symbol", "symbol_to_identity", "relation_to_symbol", "symbol_to_relation", ... },
  "phase5": { "consequence_field": ... },
  "phase6": { "meaning_map": ... },
  "phase7": { "roles": ... },
  "phase8": { "constraints": ... },
  "phase9": { "symbol_sequences" (optional), fluency outputs (optional), decoder ref (optional) }
}
```

Any key not produced by a given run may be `null` or omitted; the next layer must tolerate missing optional inputs (e.g. Phase 5–9 artifacts only when the full semantic pipeline has been run).

### 5.4 Outputs (formal)

- **Necessity detection (optional):**  
  e.g. `necessity_map` or `necessity_relations`: which symbol pairs or role/constraint combinations are necessary vs optional; or scores/annotations attached to transitions.

- **Self-observation (optional):**  
  e.g. `self_state`:  
  - Snapshot of stable identities/symbols/relations;  
  - Active constraints;  
  - Summary of consequence/meaning/role state (e.g. counts, stability indices).  
  No raw Phase 0–4 internals; only summaries and derived indices.

- **Artifacts:**  
  May write to `output/` or a configured directory (e.g. `necessity_map.json`, `self_state.json`) without modifying any phase output directories used by Phase 0–9.

### 5.5 Invariants

1. **Read-only:** The next layer never writes into Phase 0–4 or Phase 5–9 data structures; it only reads and may write its own outputs.
2. **No semantics in Phase 0–4:** Necessity and self-observation are defined purely from the existing outputs of layers 0–9 and SanTOK; no new meaning is pushed into Phase 0–4.
3. **Explicit contract:** Any code that implements this layer must depend only on the payload keys and types described in §5.3 and on documented file formats for Phase 5–9 (e.g. consequence_field.json, meaning_map.json, roles.json, constraints.json).
4. **SanTOK and Phase 4 as anchors:** The contract explicitly anchors on Phase 4 (symbol layer) and SanTOK (tokenization) as the canonical interfaces; the rest of the nine layers are included via the same payload so that the next layer can use the full stack consistently.

---

## 6. Implementation Notes (non-normative)

- **First implementation** can live under `integration/` (e.g. `integration/necessity_self_observation.py` or `integration/layer10/`) and be invoked after `run_complete` or after `run_semantic_discovery`, reading from the same outputs (and optionally from saved JSON files).
- **Testing:** Tests for the next layer should mock or load real ContractPayloads from fixtures; they must not modify or re-run Phase 0–9 logic as part of the layer’s unit tests.
- **Config:** Use `config/default.json` or a dedicated config section (e.g. `layer10` or `necessity`) for switches (enable necessity, enable self-observation, output paths) without touching phase-specific config.

---

## 7. Summary for Handoff

- **Phases 5–9:** Already implemented and frozen under `threshold_onset/semantic/` (Phase 5: consequence field, Phase 6: meaning, Phase 7: roles, Phase 8: constraints, Phase 9: fluency + symbol decoder).
- **Next layer:** Necessity detection and/or structural self-observation, **outside** THRESHOLD_ONSET, with a **clear contract** to Phase 4, SanTOK, and **all nine layers** (0–9).
- **Contract:** Read-only `ContractPayload` (§5.3); outputs necessity map and/or self_state (§5.4); invariants (§5.5). No changes to any frozen phase; implementation in `integration/` or a sibling package.

This document is the single source of truth for the next layer’s contract; implementation can follow in a separate step.
