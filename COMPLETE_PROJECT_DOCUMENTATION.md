# THRESHOLD_ONSET — Complete End-to-End Project Documentation

**Single reference for the entire project. Recursive coverage of every folder and file.**

---

## Is this comprehensive?

**Yes, for a single reference doc.** This document has:

- **Recursive file index** — Every folder and file with a one-line purpose (PART II).
- **All phases** — 0–4 and 5–9 with entry points, signatures, outputs, helpers (PART III–IV).
- **main.py** — All config variables, all `run_phase*` functions, execution flow, and startup order (PART V, XIII).
- **SanTOK** — Role, in-tree locations, nine tokenization methods (PART VI).
- **Validation** — How to run, report path, every test A–I with pass/fail, decision framework, test helpers (PART VII, XIV).
- **Integration** — unified_system, ContinuationObserver, and full script list (PART VIII).
- **Operational** — Install, dependencies, every run command, output files, troubleshooting, glossary (PART IX–X).
- **Reference** — Doc index, cheat sheet, end-to-end pipeline narrative (PART XI–XV).

**What would make it “next level” (optional):** Full JSON schemas for every output file, every function signature with default args, exception types per phase, and ASCII/Mermaid diagrams. Those belong in a separate API/spec or “reference” doc; this file stays the single place for **structure, behavior, and ops** without duplicating code.

---

## Sub-projects within this repo

The repository (project root) contains **several distinct projects/subsystems** in one tree:

| Sub-project | Path | What it is | Installable alone? |
|-------------|------|------------|--------------------|
| **THRESHOLD_ONSET (core)** | `threshold_onset/` | Main system: Phases 0–9 (foundation + semantic discovery). | Yes, via root `pip install -e .` (installs threshold-onset). |
| **SanTOK** | `santok_complete/` | Text tokenization (word, char, grammar, subword, byte, etc.). Own package name `santok-complete`, own `setup.py`, README, CHANGELOG, LICENSE. | Yes, `cd santok_complete && pip install -e .` |
| **Integration** | `integration/` | Unified system: threshold_onset + santok (unified_system.py, ContinuationObserver, scripts: topology, refusals, transition matrix, train, generate, etc.). | No; run from repo with project root on path. |
| **Validation CRUSH** | `validation_crush/` | Crush-to-death validation (Phases A–I), intrinsic_eval_report.json, decision framework, red-team checklist. | No; run `python validation_crush/crush_protocol.py --all` from project root. |

So: **one repo, multiple projects** — core (threshold_onset), tokenization (santok_complete), integration layer, and validation framework. The root `main.py` and `run_semantic_discovery.py` use the core + (optionally) santok and integration; validation_crush stresses the full pipeline.

---

## PART I — Overview

### 1. What This Document Is

- **One file**: Single place describing the full project end-to-end.
- **Complete**: Installation, structure, **every phase**, **every component**, **every command**, **every config**, and a **file-by-file index** of the repository.
- **Correct**: Paths and names match the repository.
- **Unified**: Foundation (Phases 0–4), Semantic Discovery (Phases 5–9), SanTOK, integration, validation.

### 2. What the Project Is

**THRESHOLD_ONSET** is a system where structure emerges from action and repetition before any symbols or meaning. Text (or action streams) → residues → boundaries → identities → relations → symbols → consequence field → meaning clusters → roles → constraints → fluency. All from first principles; no external linguistics or neural nets.

**Core principle (design constraint):** **कार्य (kārya) happens before ज्ञान (jñāna)** — action before knowledge. Order is fixed.

### 3. Philosophy and Axioms

- **Layer 0:** Function stabilizes before knowledge. No meaning, no symbols in Phase 0.
- **Phase 0 allowed:** action, interaction, trace, repetition, persistence, stabilization.
- **Phase 0 forbidden:** symbols, letters, meaning, tokens, embeddings, plots, coordinates.
- **Phase 0 outputs only:** traces, survival patterns, invariants — no IDs, no names.
- **Later phases:** Each adds one kind of structure without breaking the previous layer.

Full text: `docs/axioms/AXIOMS.md`.

### 4. Prerequisites

- **Python:** 3.8+.
- **OS:** Any. Paths here use forward slashes.
- **Core pipeline:** Python standard library only. Optional: `watchfiles`, `pylint`, `numpy` (see Dependencies).

### 5. Installation

```bash
git clone https://github.com/chavalasantosh/THRESHOLDONSET.git
cd THRESHOLDONSET
pip install -r requirements.txt    # optional
pip install -e .                    # optional, for imports from anywhere
```

SanTOK: use in-tree `santok_complete/` (project root on `sys.path`) or install external `santok`.

---

## PART II — Complete File-by-File Index

Every folder and file under the project root, with a one-line purpose. Paths are relative to the project root.

### Root (project root)

| Path | Purpose |
|------|---------|
| `main.py` | Primary entry: 10-step suite (decoder, validation, stress, benchmark, baselines, external validation, stability, structural scaling, full pipeline). Modes: `--user`, `--check` |
| `run_all.py` | Equivalent to main.py. Full project run: 10 steps |
| `run_all.bat` | Windows batch to run run_all.py |
| `main.bat` | Windows batch to run main.py |
| `PROJECT_FREEZE.md` | **FROZEN** Project-wide freeze declaration |
| `PRE_FREEZE_AUDIT.md` | Pre-freeze audit record |
| `run_semantic_discovery.py` | Standalone Phases 5–9 with placeholder or loaded Phase 2–4 data |
| `requirements.txt` | Optional deps: watchfiles, pylint, numpy |
| `setup.py` | setuptools setup; find_packages(where="threshold_onset"), package_dir |
| `pyproject.toml` | Build metadata, optional-deps, python_requires |
| `README.md` | Project overview |
| `SIMPLE_GUIDE.md` | Non-technical explanation |
| `START_HERE.md` | Quick start for non-devs |
| `QUICK_START.md` | Short run instructions |
| `PROJECT_STRUCTURE.md` | Structure description |
| `COMPLETE_PROJECT_DOCUMENTATION.md` | This file |
| `DOCUMENTATION_LOGIC.md` | Methodology for building this doc — scope, recursive index rules, LLM instructions |
| `CHANGELOG.md` | Version history |
| `CONTRIBUTING.md` | Contribution guidelines |
| `LICENSE` | MIT |
| `MANIFEST.in` | Package manifest |
| `ENHANCEMENT_PLAN.md` | Enhancement notes |
| `LARGE_CONTEXT_USAGE.md` | Large-context usage |
| `VISUAL_SUMMARY.txt` | Visual summary |
| `test_large_context.py` | Large-context test script |
| `.gitignore` | Git ignore patterns |
| `consequence_field.json` | Generated by Phase 5 (if run) |
| `meaning_map.json` | Generated by Phase 6 |
| `roles.json` | Generated by Phase 7 |
| `constraints.json` | Generated by Phase 8 |

### .github/

| Path | Purpose |
|------|---------|
| `.github/README.md` | GitHub config readme |
| `.github/SECURITY.md` | Security policy |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template |

### .github/workflows

| Path | Purpose |
|------|---------|
| `.github/workflows/README.md` | Workflows readme |
| `.github/workflows/ci.yml` | CI: push/PR on main, develop; matrix Python 3.8–3.12; run main.py; verify phase0–4 imports |
| `.github/workflows/documentation.yml` | Doc check: README, docs/, phase freeze files, markdown validation, link check |
| `.github/workflows/lint.yml` | Linting |
| `.github/workflows/module-development.yml` | Module development |
| `.github/workflows/phase-validation.yml` | Phase validation |
| `.github/workflows/publish-pypi.yml` | PyPI publish |
| `.github/workflows/release.yml` | Release workflow |

### threshold_onset/ (main package)

| Path | Purpose |
|------|---------|
| `threshold_onset/__init__.py` | Package init |
| `threshold_onset/README.md` | Package readme |

### threshold_onset/phase0/

| Path | Purpose |
|------|---------|
| `threshold_onset/phase0/__init__.py` | Package init |
| `threshold_onset/phase0/phase0.py` | `phase0(actions, steps)` — yields (trace, len(traces), step_count) |
| `threshold_onset/phase0/actions.py` | Action variants: InertiaAction, BoundedWalk, DecayNoise, WeakOscillator, FiniteAction |
| `threshold_onset/phase0/action.py` | Constraint reminder (action concept) |
| `threshold_onset/phase0/trace.py` | Constraint reminder (trace concept) |
| `threshold_onset/phase0/repetition.py` | Constraint reminder (repetition concept) |
| `threshold_onset/phase0/README.md` | Phase 0 readme |
| `threshold_onset/phase0/phase0/PHASE0_FREEZE.md` | Freeze declaration |
| `threshold_onset/phase0/phase0/docs/PHASE0_FINAL_VERIFICATION.md` | Verification doc |
| `threshold_onset/phase0/phase0/docs/README.md` | Phase0 docs readme |

### threshold_onset/phase1/

| Path | Purpose |
|------|---------|
| `threshold_onset/phase1/__init__.py` | Package init |
| `threshold_onset/phase1/phase1.py` | `phase1(residues)` — boundary, cluster, distance, pattern → metrics dict |
| `threshold_onset/phase1/boundary.py` | `detect_boundaries(residues, threshold)` — BOUNDARY_THRESHOLD = 0.1 |
| `threshold_onset/phase1/cluster.py` | `cluster_residues(residues, threshold)` — CLUSTER_THRESHOLD = 0.1 |
| `threshold_onset/phase1/distance.py` | `pairwise_distances(residues)` |
| `threshold_onset/phase1/pattern.py` | `detect_repetition(residues)` |
| `threshold_onset/phase1/README.md` | Phase 1 readme |
| `threshold_onset/phase1/docs/PHASE1_COMPLIANCE_VERIFICATION.md` | Compliance verification |
| `threshold_onset/phase1/docs/README.md` | Docs readme |
| `threshold_onset/phase1/phase1/PHASE1_FREEZE.md` | Freeze declaration |
| `threshold_onset/phase1/phase1/README.md` | Phase1 sub readme |
| `threshold_onset/phase1/phase1/PHASE1_IMPLEMENTATION_PROMPT*.md` | Implementation prompts |
| `threshold_onset/phase1/phase1/PHASE1_TRANSITION.md` | Transition doc |

### threshold_onset/phase2/

| Path | Purpose |
|------|---------|
| `threshold_onset/phase2/__init__.py` | Package init |
| `threshold_onset/phase2/phase2.py` | `phase2(residues, phase1_metrics)`, `phase2_multi_run(residue_sequences, phase1_metrics_list)` |
| `threshold_onset/phase2/persistence.py` | `measure_persistence(residue_sequences)` — PERSISTENCE_THRESHOLD = 2 |
| `threshold_onset/phase2/repeatable.py` | `detect_repeatable_units(residues)` |
| `threshold_onset/phase2/identity.py` | `assign_identity_hashes(residue_sequences)` |
| `threshold_onset/phase2/stability.py` | `measure_stability(cluster_sequences)` |
| `threshold_onset/phase2/README.md` | Phase 2 readme |
| `threshold_onset/phase2/docs/PHASE2_COMPLIANCE_VERIFICATION.md` | Compliance verification |
| `threshold_onset/phase2/docs/README.md` | Docs readme |
| `threshold_onset/phase2/phase2/PHASE2_FREEZE.md` | Freeze declaration |
| `threshold_onset/phase2/phase2/README.md` | Phase2 sub readme |
| `threshold_onset/phase2/phase2/PHASE2_*.md` | Implementation prompts/summary |

### threshold_onset/phase3/

| Path | Purpose |
|------|---------|
| `threshold_onset/phase3/__init__.py` | Package init |
| `threshold_onset/phase3/phase3.py` | `phase3(...)`, `phase3_multi_run(...)`; MIN_PERSISTENT_RELATIONS, MIN_STABILITY_RATIO |
| `threshold_onset/phase3/graph.py` | `build_graph(phase2_metrics)` |
| `threshold_onset/phase3/interaction.py` | `detect_interactions(residues, phase2_metrics)` |
| `threshold_onset/phase3/dependency.py` | `measure_dependencies(residues, phase2_metrics)` |
| `threshold_onset/phase3/influence.py` | `measure_influence(residues, phase2_metrics)` |
| `threshold_onset/phase3/relation.py` | Relation helpers |
| `threshold_onset/phase3/persistence.py` | Persistence helpers |
| `threshold_onset/phase3/stability.py` | Stability helpers |
| `threshold_onset/phase3/phase3/PHASE3_FREEZE*.md` | Freeze declarations |
| `threshold_onset/phase3/phase3/README.md` | Phase3 sub readme |
| `threshold_onset/phase3/phase3/PHASE3_*.md` | Implementation/persistence docs |

### threshold_onset/phase4/

| Path | Purpose |
|------|---------|
| `threshold_onset/phase4/__init__.py` | Package init |
| `threshold_onset/phase4/phase4.py` | `phase4(phase2_metrics, phase3_metrics)` — gate then assign_identity_aliases, assign_relation_aliases |
| `threshold_onset/phase4/alias.py` | `assign_identity_aliases(identity_hashes)`, `assign_relation_aliases(relation_hashes)` |
| `threshold_onset/phase4/README.md` | Phase 4 folder readme |
| `threshold_onset/phase4/phase4/README.md` | Phase 4 docs readme |
| `threshold_onset/phase4/phase4/PHASE4_FREEZE.md` | Freeze declaration |
| `threshold_onset/phase4/phase4/PHASE4_IMPLEMENTATION_PLAN_FINAL.md` | Implementation plan |

### threshold_onset/semantic/

| Path | Purpose |
|------|---------|
| `threshold_onset/semantic/__init__.py` | Exports ConsequenceFieldEngine, MeaningDiscoveryEngine, RoleEmergenceEngine, ConstraintDiscoveryEngine, FluencyGenerator |
| `threshold_onset/semantic/common/README.md` | Common module readme |
| `threshold_onset/semantic/common/__init__.py` | Package init |
| `threshold_onset/semantic/common/types.py` | ConsequenceVector, ConsequenceDelta, MeaningSignature, RoleMap, ConstraintMap, ConsequenceField, MeaningMap, RolloutResult (TypedDict/dataclass) |
| `threshold_onset/semantic/common/exceptions.py` | ConsequenceFieldError, MeaningDiscoveryError, RoleEmergenceError, ConstraintDiscoveryError, FluencyGenerationError |
| `threshold_onset/semantic/common/validators.py` | validate_identity_hash, validate_k, validate_num_rollouts, validate_symbol, etc. |
| `threshold_onset/semantic/common/utils.py` | mean, other helpers |
| `threshold_onset/semantic/config/README.md` | Config module readme |
| `threshold_onset/semantic/config/__init__.py` | Package init |
| `threshold_onset/semantic/config/defaults.py` | DEFAULT_K, DEFAULT_NUM_ROLLOUTS, DEFAULT_MAX_STEPS; phase6/7/8/9 defaults; get_default_config() |
| `threshold_onset/semantic/config/validation.py` | Config validation |
| `threshold_onset/semantic/phase5/__init__.py` | Package init |
| `threshold_onset/semantic/phase5/consequence_field.py` | ConsequenceFieldEngine — build(), save(); identity vectors, edge_deltas, policies (greedy, stochastic_topk, novelty) |
| `threshold_onset/semantic/phase5/rollout.py` | rollout_from_identity, rollout_from_identity_forced_first |
| `threshold_onset/semantic/phase5/metrics.py` | compute_k_reach, get_escape_concentration, compute_near_refusal_rate_from_rollouts |
| `threshold_onset/semantic/phase5/policies.py` | Probe policies for rollouts |
| `threshold_onset/semantic/phase5/README.md` | Phase 5 readme |
| `threshold_onset/semantic/phase5/IMPLEMENTATION_COMPLETE.md` | Implementation status |
| `threshold_onset/semantic/phase6/__init__.py` | Package init |
| `threshold_onset/semantic/phase6/meaning_discovery.py` | MeaningDiscoveryEngine — discover(num_clusters, seed) → MeaningMap |
| `threshold_onset/semantic/phase6/normalization.py` | normalize_vectors |
| `threshold_onset/semantic/phase6/clustering.py` | cluster_consequence_vectors (k-medoids, stability) |
| `threshold_onset/semantic/phase6/README.md` | Phase 6 readme |
| `threshold_onset/semantic/phase7/__init__.py` | Package init |
| `threshold_onset/semantic/phase7/role_emergence.py` | RoleEmergenceEngine — emerge() → RoleMap |
| `threshold_onset/semantic/phase7/properties.py` | compute_cluster_properties |
| `threshold_onset/semantic/phase7/role_assigner.py` | assign_roles_from_properties (quantile-based) |
| `threshold_onset/semantic/phase7/README.md` | Phase 7 readme |
| `threshold_onset/semantic/phase8/__init__.py` | Package init |
| `threshold_onset/semantic/phase8/constraint_discovery.py` | ConstraintDiscoveryEngine — discover() → ConstraintMap |
| `threshold_onset/semantic/phase8/sequences.py` | extract_role_sequences |
| `threshold_onset/semantic/phase8/pattern_miner.py` | discover_role_patterns, discover_forbidden_patterns, build_templates, compute_prefix_match_score |
| `threshold_onset/semantic/phase8/README.md` | Phase 8 readme |
| `threshold_onset/semantic/phase9/__init__.py` | Package init |
| `threshold_onset/semantic/phase9/fluency_generator.py` | FluencyGenerator — build_experience_table(), generate(start_symbol, length, seed) |
| `threshold_onset/semantic/phase9/symbol_decoder.py` | **FROZEN** Structural decoder: build_structural_decoder(), decode_symbol_sequence() — symbol -> identity -> residue -> token |
| `threshold_onset/semantic/phase9/scoring.py` | calculate_stability_score, calculate_novelty_penalty, calculate_experience_bias |
| `threshold_onset/semantic/phase9/README.md` | Phase 9 readme |
| `threshold_onset/semantic/PHASE5-9_FREEZE.md` | Phases 5-9 freeze declaration |
| `threshold_onset/semantic/large_context.py` | LargeContextProcessor, StreamingGenerator for large-context/streaming |
| `threshold_onset/semantic/example_complete_workflow.py` | Example workflow script |
| `threshold_onset/semantic/tests/__init__.py` | Package init |
| `threshold_onset/semantic/tests/test_phase5.py` | Phase 5 tests |
| `threshold_onset/semantic/tests/test_phase6.py` | Phase 6 tests |
| `threshold_onset/semantic/tests/test_phase7.py` | Phase 7 tests |
| `threshold_onset/semantic/tests/test_phase8.py` | Phase 8 tests |
| `threshold_onset/semantic/tests/test_phase9.py` | Phase 9 tests |
| `threshold_onset/semantic/tests/test_integration.py` | Integration tests |
| `threshold_onset/semantic/tests/README.md` | Tests readme |
| `threshold_onset/semantic/README.md` | Semantic module readme |
| `threshold_onset/semantic/PROGRESS_SUMMARY.md` | Progress summary |
| `threshold_onset/semantic/QUICK_START.md` | Quick start |
| `threshold_onset/semantic/ARCHITECTURE.md` | Architecture |
| `threshold_onset/semantic/CONTRACTS.md` | Contracts |
| `threshold_onset/semantic/STATUS_SUMMARY.md` | Status summary |
| `threshold_onset/semantic/TESTING_GUIDE.md` | Testing guide |
| `threshold_onset/semantic/IMPLEMENTATION_*.md` | Implementation docs |
| `threshold_onset/semantic/PHASE5_CORRECTED_SPEC.md` | Phase 5 corrected spec |
| `threshold_onset/semantic/ALL_BUGS_FIXED.md`, `BUGS_FIXED.md`, `LINTER_FIXES.md` | Bug/linter docs |
| `threshold_onset/semantic/COMPLETION_SUMMARY.md`, `FINAL_*.md`, `CORRECTIONS_APPLIED.md` | Completion/correction docs |
| `threshold_onset/semantic/PROJECT_STATUS.md` | Project status |

### threshold_onset/tools/

| Path | Purpose |
|------|---------|
| `threshold_onset/tools/version_control.py` | Version control (hash, diff, snapshot) |
| `threshold_onset/tools/watch_version.py` | Watcher entry point |
| `threshold_onset/tools/README.md` | Tools readme |
| `threshold_onset/tools/docs/README.md` | Docs readme |
| `threshold_onset/tools/docs/VERSION_CONTROL.md` | Version control doc |

### integration/

| Path | Purpose |
|------|---------|
| `integration/unified_system.py` | TokenAction, tokenize_text_to_actions, process_text_through_phases (tokenization + Phases 0–4) |
| `integration/continuation_observer.py` | ContinuationRefusal, ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics) — records refusals |
| `integration/example_unified.py` | Example usage of unified system |
| `integration/main_complete.py` | Complete main integration script |
| `integration/main_end_to_end.py` | End-to-end integration script |
| `integration/run_complete.py` | **FROZEN** Run complete pipeline (text -> structure -> text) |
| `integration/validate_pipeline.py` | **FROZEN** Validation on 7 input types |
| `integration/stress_test.py` | **FROZEN** Stress test (100-5000 tokens) |
| `integration/fluency_text_generator.py` | **FROZEN** FluencyGenerator path to text |
| `integration/test_decoder.py` | **FROZEN** Decoder test |
| `integration/generate.py` | Generation script |
| `integration/train.py` | Training script |
| `integration/compare_topologies.py` | Compare topologies |
| `integration/escape_topology.py` | Escape topology analysis |
| `integration/topology_clusters.py` | Topology clustering |
| `integration/transition_matrix.py` | Transition matrix |
| `integration/identity_permissions.py` | Identity permissions |
| `integration/near_refusal_observer.py` | Near-refusal observer |
| `integration/observe_refusals.py` | Observe refusals script |
| `integration/refusal_signatures.py` | Refusal signatures |
| `integration/preference_learner.py` | Preference learner |
| `integration/scoring.py` | Scoring helpers |
| `integration/surface.py` | Surface utilities |
| `integration/test_continuation.py` | Test continuation |
| `integration/test_invariant.py` | Test invariant |
| `integration/test_permuted.py` | Test permuted |
| `integration/run_all_scripts.bat` | Batch run scripts (Windows) |
| `integration/requirements_internal.txt` | Internal requirements |
| `integration/README.md` | Integration readme |
| `integration/UNIFIED_SYSTEM_README.md` | Unified system full doc |
| `integration/UNIFIED_SYSTEM_SUMMARY.md` | Unified system summary |
| `integration/CONTINUATION_OBSERVER.md` | Continuation observer doc |
| `integration/EXECUTABLE_SCRIPTS.md` | Executable scripts |
| `integration/RUN_IN_CMD.md` | Run in CMD |
| `integration/MODEL.md` | Model doc |
| `integration/PROJECT.md` | Project doc |
| `integration/MODULE_MAPPING.md` | Module mapping |
| `integration/README_COMPLETE.md` | Readme complete |
| `integration/README_CONTINUATION.md` | Readme continuation |
| `integration/ALL_FIXES_SUMMARY.md` | All fixes summary |
| `integration/ANALYSIS_INSIGHTS.md` | Analysis insights |
| `integration/CLUSTER_PATTERNS.md` | Cluster patterns |
| `integration/CORRECTED_ROADMAP_V2.md` | Corrected roadmap v2 |
| `integration/ESCAPE_TOPOLOGY.md` | Escape topology |
| `integration/FINAL_EXECUTABLE_ROADMAP.md` | Final executable roadmap |
| `integration/INTERNAL_MODULES.md` | Internal modules |
| `integration/INVARIANT_TEST.md` | Invariant test |
| `integration/MIGRATION_TO_INTERNAL_MODULES.md` | Migration to internal modules |
| `integration/NEAR_REFUSALS.md` | Near refusals |
| `integration/NEXT_STEPS.md` | Next steps |
| `integration/PERMISSION_PROFILE.md` | Permission profile |
| `integration/PRESSURE_BASED_MEANING_ROADMAP.md` | Pressure-based meaning roadmap |
| `integration/REFUSALS_PERMUTED.md` | Refusals permuted |
| `integration/REFUSALS_RAW.md` | Refusals raw |
| `integration/ROADMAP_CORRECTIONS.md` | Roadmap corrections |
| `integration/SEMANTIC_DISCOVERY_ROADMAP.md` | Semantic discovery roadmap |
| `integration/SIGNATURES_RAW.md` | Signatures raw |
| `integration/TOPOLOGY_CLUSTERS.md` | Topology clusters |
| `integration/TOPOLOGY_COMPARISON.md` | Topology comparison |
| `integration/TRANSITION_MATRIX.md` | Transition matrix |
| `integration/EXECUTION_SUMMARY.md` | Execution summary |
| `integration/ESCAPE_TOPOLOGY_RAW.txt` | Escape topology raw output |
| `integration/INVARIANT_TEST_RAW.txt` | Invariant test raw |
| `integration/NEAR_REFUSALS_RAW.txt` | Near refusals raw |
| `integration/PERMISSION_PROFILE_RAW.txt` | Permission profile raw |
| `integration/REFUSALS_PERMUTED_RAW.txt` | Refusals permuted raw |
| `integration/SIGNATURES_RAW.txt` | Signatures raw text |
| `integration/TOPOLOGY_CLUSTERS_RAW.txt` | Topology clusters raw |
| `integration/TOPOLOGY_COMPARISON_RAW.txt` | Topology comparison raw |
| `integration/TRANSITION_MATRIX_RAW.txt` | Transition matrix raw |
| `integration/refusals_recorded.txt` | Recorded refusals |

### santok_complete/

| Path | Purpose |
|------|---------|
| `santok_complete/__init__.py` | Package init |
| `santok_complete/core/README.md` | Core readme |
| `santok_complete/core/__init__.py` | Package init |
| `santok_complete/core/base_tokenizer.py` | tokenize_space, tokenize_char, tokenize_word, tokenize_grammar, tokenize_subword, tokenize_bytes |
| `santok_complete/core/core_tokenizer.py` | tokenize_space, tokenize_char, tokenize_word, tokenize_grammar, tokenize_subword(text, chunk_len, strategy), tokenize_bytes; tokenize_text(text, tokenizer_type, ...); multilang helpers |
| `santok_complete/core/parallel_tokenizer.py` | tokenize_parallel_threaded, tokenize_parallel_multiprocess, tokenize_multilang_parallel |
| `santok_complete/core/santok_engine.py` | tokenize_text(text, tokenization_method) — API entry |
| `santok_complete/santok/README.md` | Santok readme |
| `santok_complete/santok/__init__.py` | Package init |
| `santok_complete/santok/santok.py` | tokenize_text(text, tokenization_method) — high-level API |
| `santok_complete/santok/cli.py` | CLI entry |
| `santok_complete/santok/utils/README.md` | Santok utils readme |
| `santok_complete/santok/utils/config.py` | Config |
| `santok_complete/santok/utils/logging_config.py` | Logging |
| `santok_complete/santok/utils/validation.py` | Validation |
| `santok_complete/examples/README.md` | Examples readme |
| `santok_complete/examples/advanced_usage.py` | Advanced usage example |
| `santok_complete/examples/basic_usage.py` | Basic usage example |
| `santok_complete/tests/README.md` | Tests readme |
| `santok_complete/tests/__init__.py` | Package init |
| `santok_complete/tests/test_basic_tokenization.py` | Basic tokenization tests |
| `santok_complete/tests/test_core_tokenizers.py` | Core tokenizer tests |
| `santok_complete/README.md` | SanTOK readme |
| `santok_complete/CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE` | Standard files |
| `santok_complete/setup.py`, `MANIFEST.in`, `requirements.txt`, `.gitignore` | Build/config |

### validation_crush/

| Path | Purpose |
|------|---------|
| `validation_crush/crush_protocol.py` | CrushProtocol; --all, --phase A-I; runs Phase A–I tests, writes report |
| `validation_crush/intrinsic_logger.py` | IntrinsicLogger; report structure (phase5–9 metrics, tests, summary); save intrinsic_eval_report.json |
| `validation_crush/decision_framework.py` | DecisionFramework; should_abandon, should_pivot; Phase I → ABANDON |
| `validation_crush/tests/README.md` | Tests readme (Phase A–I) |
| `validation_crush/tests/__init__.py` | Package init |
| `validation_crush/tests/phase_a_baseline.py` | PhaseABaselineTest — fluent nonsense |
| `validation_crush/tests/phase_b_perturbation.py` | PhaseBPerturbationTest — micro-perturbation, all 9 tokenization methods |
| `validation_crush/tests/phase_c_consistency.py` | PhaseCConsistencyTest — temporal recall |
| `validation_crush/tests/phase_d_causal.py` | PhaseDCausalTest — impossible worlds |
| `validation_crush/tests/phase_e_role_collapse.py` | PhaseERoleCollapseTest — role overload (100K+ tokens) |
| `validation_crush/tests/phase_f_constraint_inversion.py` | PhaseFConstraintInversionTest — reverse-grammar |
| `validation_crush/tests/phase_g_streaming.py` | PhaseGStreamingTest — forced degradation |
| `validation_crush/tests/phase_h_red_team.py` | PhaseHRedTeamTest — human adversary |
| `validation_crush/tests/phase_i_kill_switch.py` | PhaseIKillSwitchTest — meaning denial |
| `validation_crush/utils/README.md` | Utils readme |
| `validation_crush/utils/__init__.py` | Package init |
| `validation_crush/utils/test_helpers.py` | load_system_outputs, initialize_system, process_text_through_system, compute_entropy, compute_variance, check_structural_isomorphism |
| `validation_crush/utils/metrics_computer.py` | Phase 5–9 metrics from outputs (handles dict/list for patterns/templates) |
| `validation_crush/reports/README.md` | Reports readme |
| `validation_crush/reports/.gitkeep` | Keep reports dir |
| `validation_crush/reports/intrinsic_eval_report.json` | Generated report |
| `validation_crush/validation.log` | Validation run log |
| `validation_crush/README.md` | Validation readme |
| `validation_crush/VALIDATION_PROTOCOL.md` | Protocol description |
| `validation_crush/QUICK_START.md` | Quick start |
| `validation_crush/red_team_checklist.md` | Red team checklist |
| `validation_crush/config_example.json` | Example config |
| `validation_crush/.gitignore` | Git ignore |
| `validation_crush/COMPLETE_REVIEW_SUMMARY.md`, `GAPS_AND_FIXES.md`, `IMPLEMENTATION_REVIEW.md`, `FIXES_APPLIED.md` | Review/fix docs |

### docs/

| Path | Purpose |
|------|---------|
| `docs/README.md` | Docs index |
| `docs/PHASE_STATUS_CANONICAL.md` | Authoritative phase status |
| `docs/PHASE_STATUS_ACCURATE.md` | Phase status (accurate) |
| `docs/EXECUTION_MODES.md` | Single-run vs multi-run |
| `docs/PHASE_GATES_EXPLANATION.md` | Phase gates |
| `docs/PHASE0_ACTION_VARIANTS.md` | Phase 0 action variants |
| `docs/PHASE1_VERIFICATION_SUMMARY.md` | Phase 1 verification |
| `docs/PHASE2_VERIFICATION_SUMMARY.md` | Phase 2 verification |
| `docs/ORGANIZATION.md` | Organization |
| `docs/Project_Readmes.md` | Project readmes |
| `docs/SYSTEM_REVIEW_20260113.md` | System review |
| `docs/axioms/AXIOMS.md` | Axioms (Layer 0–4) |
| `docs/axioms/README.md` | Axioms readme |
| `docs/architecture/ARCHITECTURE.md` | Architecture |
| `docs/architecture/README.md` | Architecture readme |
| `docs/PAPER_ARCHITECTURE.md` | Paper-ready architecture (structure-first, decoder, pipeline) |
| `docs/simple/PHASE0_TO_PHASE3_STORY.md` | Simple story |
| `docs/simple/INDEPENDENCE_CHECK.md` | Independence check |
| `docs/simple/README.md` | Simple readme |
| `docs/history/CORRECTIONS_APPLIED.md` | History corrections |
| `docs/history/README.md` | History readme |
| `docs/history/WORK_LOG.md` | Work log |

### tests/ (project-level)

| Path | Purpose |
|------|---------|
| `tests/README.md` | Project tests readme |
| `tests/__init__.py` | Package init |
| `tests/test_phase3_convergence.py` | Phase 3 convergence test |
| `tests/test_phase4_freeze.py` | Phase 4 freeze test |

### archive/

| Path | Purpose |
|------|---------|
| `archive/README.md` | Archive readme |
| `archive/REORGANIZATION_PLAN.md`, `REORGANIZATION_COMPLETE.md` | Reorganization docs |
| `archive/reference/README.md` | Reference readme |
| `archive/reference/chatgpt_language_formation.md`, `chatgpt.txt`, `CONVERSATION_SUMMARY.md` | Reference material |
| `archive/reference/log.txt`, `process.txt`, `to_AI.txt`, `upcoming plan.md` | Reference material |

### examples/, scripts/, versions/

| Path | Purpose |
|------|---------|
| `examples/README.md` | Examples readme |
| `scripts/README.md` | Scripts readme |
| `versions/README.md` | Versions readme |
| `versions/v0.1.0_*/README.md` | Version snapshot readme |
| `versions/v0.1.0_*/` | Version snapshots (AXIOMS, phase0 files, RUNBOOK, VERSIONS) |

---

## PART III — Phases 0–4 (Foundation)

All frozen. Key entry points and outputs.

### Phase 0 — THRESHOLD_ONSET

- **File:** `threshold_onset/phase0/phase0.py`
- **Signature:** `phase0(actions, steps)` — `actions`: list of callables; `steps`: int. Yields `(trace, len(traces), step_count)`.
- **Actions (threshold_onset/phase0/actions.py):** InertiaAction, BoundedWalk, DecayNoise, WeakOscillator, FiniteAction(finite_set_size).
- **From text (main.py):** `run_phase0_from_text(text, tokenization_method="word", steps=None, ...)` → residues (list). Uses `tokenize_text_to_actions` then Phase 0.

**Phase 0 action variants (one-line behavior):**

| Variant | Class | Behavior |
|---------|--------|----------|
| noise_baseline | random_action() | Pure random in [0,1]. |
| inertia | InertiaAction | Stateful: new = 0.7×old + 0.3×random. |
| random_walk | BoundedWalk | Random walk step ±0.05, reflected in [0,1]. |
| oscillator | WeakOscillator | 0.5 + 0.3×sin(phase) + noise; phase += 0.1. |
| decay_noise | DecayNoise | Decay 0.95 toward random target each step. |
| finite | FiniteAction(n) | Output from {0..n-1}; state += randint(-1,1) mod n. Default n=10. |

### Phase 1 — SEGMENTATION

- **File:** `threshold_onset/phase1/phase1.py`
- **Signature:** `phase1(residues)` → dict: boundary_positions, cluster_count, cluster_sizes, distances, repetition_count, survival_count.
- **Helpers:** boundary.py (BOUNDARY_THRESHOLD 0.1), cluster.py (CLUSTER_THRESHOLD 0.1), distance.py, pattern.py.

### Phase 2 — IDENTITY

- **File:** `threshold_onset/phase2/phase2.py`
- **Signatures:** `phase2(residues, phase1_metrics)`, `phase2_multi_run(residue_sequences, phase1_metrics_list)`.
- **Output:** persistence_counts, persistent_segment_hashes, repeatability_counts, repeatable_unit_hashes, identity_mappings, identity_persistence, stability_counts, stable_cluster_hashes.
- **Helpers:** persistence.py (PERSISTENCE_THRESHOLD 2), repeatable.py, identity.py, stability.py.

### Phase 3 — RELATION

- **File:** `threshold_onset/phase3/phase3.py`
- **Constants:** MIN_PERSISTENT_RELATIONS = 1, MIN_STABILITY_RATIO = 0.6.
- **Signatures:** `phase3(residues, phase1_metrics, phase2_metrics)`, `phase3_multi_run(...)`.
- **Output:** graph_nodes, graph_edges, node_count, edge_count, degree_counts, interaction_*, dependency_*, influence_*, path_lengths, persistent_relation_hashes, etc.
- **Helpers:** graph.py, interaction.py, dependency.py, influence.py, relation.py, persistence.py, stability.py.

### Phase 4 — SYMBOL

- **File:** `threshold_onset/phase4/phase4.py`
- **Signature:** `phase4(phase2_metrics, phase3_metrics)` → identity_to_symbol, symbol_to_identity, relation_to_symbol, symbol_to_relation, alias counts; or None if gate fails.
- **Gate:** MIN_PERSISTENT_IDENTITIES, MIN_PERSISTENT_RELATIONS (both 1).
- **Helpers:** alias.py — assign_identity_aliases, assign_relation_aliases (deterministic integer symbols).

---

## PART IV — Phases 5–9 (Semantic Discovery)

All under `threshold_onset/semantic/`. Use Phase 2–4 outputs and optional ContinuationObserver.

### Phase 5 — Consequence Field

- **Class:** `ConsequenceFieldEngine` — `threshold_onset/semantic/phase5/consequence_field.py`
- **Constructor:** (phase2_identities, phase3_relations, phase4_symbols, continuation_observer=None, config=None).
- **Methods:** build(), save(path). Policies: greedy, stochastic_topk, novelty. Output: ConsequenceField (identity_vectors, edge_deltas, metadata). Saved as consequence_field.json.

### Phase 6 — Meaning Discovery

- **Class:** `MeaningDiscoveryEngine` — `threshold_onset/semantic/phase6/meaning_discovery.py`
- **Constructor:** (consequence_field, config=None).
- **Method:** discover(num_clusters=None, seed=None) → MeaningMap. Uses normalize_vectors, cluster_consequence_vectors (k-medoids, stability). Saved as meaning_map.json.

### Phase 7 — Role Emergence

- **Class:** `RoleEmergenceEngine` — `threshold_onset/semantic/phase7/role_emergence.py`
- **Constructor:** (meaning_map, consequence_field, continuation_observer=None, config=None).
- **Method:** emerge() → RoleMap. Uses compute_cluster_properties, assign_roles_from_properties (quantile-based). Saved as roles.json.

### Phase 8 — Constraint Discovery

- **Class:** `ConstraintDiscoveryEngine` — `threshold_onset/semantic/phase8/constraint_discovery.py`
- **Constructor:** (roles, symbol_sequences, edge_deltas, continuation_observer=None, identity_to_symbol=None, config=None).
- **Method:** discover() → ConstraintMap. Uses extract_role_sequences, discover_role_patterns, discover_forbidden_patterns, build_templates, compute_prefix_match_score. Saved as constraints.json.

### Phase 9 — Fluency Generator

- **Class:** `FluencyGenerator` — `threshold_onset/semantic/phase9/fluency_generator.py`
- **Constructor:** (consequence_field, roles, constraints, phase3_relations, phase4_symbols, continuation_observer, config=None).
- **Methods:** build_experience_table(), generate(start_symbol, length, seed) → list of symbols. No file output; optional streaming via large_context.StreamingGenerator.

### Semantic types (threshold_onset/semantic/common/types.py)

ConsequenceVector, ConsequenceDelta, MeaningSignature, RoleMap, ConstraintMap (TypedDict); ConsequenceField, MeaningMap, RolloutResult (dataclass).

### Semantic config (threshold_onset/semantic/config/defaults.py)

DEFAULT_K=5, DEFAULT_NUM_ROLLOUTS=100, DEFAULT_MAX_STEPS=50; phase6 num_clusters, similarity_threshold; phase7 percentiles; phase8 min_frequency, max_pattern_length; phase9 novelty_window, stability/template/bias/novelty weights. get_default_config() returns full dict.

---

## PART V — main.py and run_all.py

- **Location:** Project root.
- **Run:** `python main.py` or `python run_all.py` (from project root).

**main.py** is an **orchestrator** — it runs 10 subprocess scripts in sequence. It does not contain pipeline config or phase logic.

### Modes

| Mode | Command | Behavior |
|------|---------|----------|
| Full suite | `python main.py` | Runs all 10 steps with default corpus |
| Custom input | `python main.py --user "text"` | Full suite; step 10 uses your text |
| Interactive | `python main.py --user` | Prompts for text, then runs full suite |
| Quick check | `python main.py --check "text"` | Runs `run_user_result.py` only (user-facing output) |

### 10 steps (in order)

1. Decoder test — `integration/test_decoder.py`
2. Validation — `integration/validate_pipeline.py`
3. Stress test — `integration/stress_test.py`
4. Benchmark — `integration/benchmark.py`
5. Baselines — `integration/baselines.py`
6. External validation — `integration/external_validation.py`
7. Stability mode — `integration/stability_mode.py`
8. Stability experiments — `integration/stability_experiments.py`
9. Structural scaling — `integration/structural_scaling.py`
10. Full pipeline — `integration/run_complete.py` (or with your text if `--user`)

### Pipeline configuration

Pipeline parameters live in **`integration/run_complete.py`** (and `integration/unified_system.py`):

- `tokenization_method` — e.g. "word", "character", "grammar" (default: "word")
- `num_runs` — Phase 0 runs for multi-run persistence (default: 3)

See `docs/EXECUTION.md` for full run instructions.

---

## PART VI — SanTOK and tokenization

- **Role:** Text → tokens → actions → residues. Used in main.py and validation_crush.
- **In-tree:** `santok_complete/core/core_tokenizer.py`: tokenize_space, tokenize_char, tokenize_word, tokenize_grammar, tokenize_subword(text, chunk_len=3, strategy="fixed"), tokenize_bytes; tokenize_text(text, tokenizer_type, ...). Strategy can be fixed, bpe, syllable, frequency for subword.
- **API:** `santok_complete/santok/santok.py` or `santok_complete/core/santok_engine.py`: tokenize_text(text, tokenization_method="whitespace").
- **Nine methods (main.py / validation):** whitespace, word, character, grammar, subword, subword_bpe, subword_syllable, subword_frequency, byte. Unavailable methods are skipped in validation.

---

## PART VII — Validation (validation_crush)

- **Run all:** `python validation_crush/crush_protocol.py --all` (from project root).
- **Run one phase:** `python validation_crush/crush_protocol.py --phase A` (A through I).
- **Report:** `validation_crush/reports/intrinsic_eval_report.json` — metadata, phases (phase5–9: threshold_crossings, entropy_curves, cluster_stability, role_variance, constraint_rigidity, fluency_gate_decisions), tests, summary.
- **Log:** `validation_crush/validation.log` (UTF-8).
- **Tests:** A=baseline (fluent nonsense), B=perturbation (9 tokenization methods), C=temporal consistency, D=causal (impossible worlds), E=role collapse (100K+ tokens), F=constraint inversion, G=streaming, H=red team, I=kill switch (meaning denial). Pass/fail: A/D use Phase 9 refusal as primary; entropy/stability supporting.
- **Decision framework (decision_framework.py):** Phase I failure → ABANDON; critical_phases=['I'], important_phases=['A','D','E']. should_abandon(phase, metrics), should_pivot(...).
- **Test helpers (utils/test_helpers.py):** load_system_outputs(...), initialize_system(outputs, config), process_text_through_system(text, tokenization_method, num_runs, run_semantic_phases, config) — runs full pipeline via main.

**intrinsic_eval_report.json schema (top-level):**

| Key | Type | Content |
|-----|------|---------|
| metadata | object | created_at (ISO), system "THRESHOLD_ONSET", validation_type "crush_to_death" |
| phases | object | phase5, phase6, phase7, phase8, phase9 (each see below) |
| tests | object | Per-test results keyed by test id |
| summary | object | total_tests, passed, failed, abandon_triggered (bool) |

**Each phases.phaseN (N=5..9):**

| Key | Type | Content |
|-----|------|---------|
| threshold_crossings | array | { timestamp, threshold, value, crossed, test_id } |
| entropy_curves | array | (phase5) { identity_hash, entropy_values, steps, test_id } |
| cluster_stability | array | (phase6) stability entries |
| role_variance | array | (phase7) variance entries |
| constraint_rigidity | array | (phase8) rigidity entries |
| fluency_gate_decisions | array | (phase9) gate decision entries |
| metrics | object | Phase-specific metrics |

**validation_crush config (config_example.json):**

| Key | Purpose |
|-----|---------|
| phase5.k | k-step reach (default 5) |
| phase5.num_rollouts | Rollouts per identity (default 100) |
| phase5.max_steps | Max steps per rollout (default 50) |
| phase6.num_clusters | null = auto |
| phase6.similarity_threshold | 0.7 |
| phase7.percentile_high / percentile_low | 75 / 25 |
| phase8.min_frequency / max_pattern_length | 3 / 4 |
| phase9.stability_weight, template_weight, bias_weight, novelty_weight, novelty_window | Weights and window |
| validation.phase_b_num_runs | e.g. 50 |
| validation.entropy_threshold | e.g. 2 |
| validation.stability_threshold | e.g. 0.7 |
| validation.refusal_quality_threshold | e.g. 0.6 |

---

## PART VIII — Integration

- **unified_system.py:** TokenAction(tokens), tokenize_text_to_actions(text, tokenization_method), process_text_through_phases(text, tokenization_method, num_runs) — tokenization + Phases 0–4.
- **continuation_observer.py:** ContinuationRefusal (step_index, current_symbol, attempted_next_symbol, reason, relation_exists). ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics) — records refusals; used by Phase 5+.
- **Other integration scripts:** See PART II integration table (compare_topologies, escape_topology, transition_matrix, identity_permissions, near_refusal_observer, refusal_signatures, preference_learner, scoring, surface, test_*, main_complete, main_end_to_end, run_complete, generate, train).

---

## PART IX — Configuration, Dependencies, Run Commands, Outputs

### Configuration (consolidated)

See PART V for main.py. validation_crush: --config path optional; config_example.json in validation_crush.

### Dependencies

- **Required:** Python 3.8+ stdlib only for core + semantic.
- **requirements.txt:** watchfiles, pylint, numpy (optional).
- **setup.py/pyproject.toml:** No required runtime deps; extras dev, all.
- **SanTOK:** santok_complete in-tree or pip install santok.
- **integration.continuation_observer:** Optional; improves semantic behavior.

### Run commands

1. Full pipeline (text, 0–9): Set INPUT_MODE="text", RUN_SEMANTIC_PHASES=True, INPUT_TEXT. `python main.py`
2. Full pipeline (action variant): Set INPUT_MODE for variant, RUN_SEMANTIC_PHASES=True. `python main.py`
3. Semantic only: Fill/load Phase 2–4 in run_semantic_discovery.py. `python run_semantic_discovery.py`
4. Validation all: `python validation_crush/crush_protocol.py --all`
5. Validation one phase: `python validation_crush/crush_protocol.py --phase A` (A–I)
6. Phase 3 test: `python tests/test_phase3_convergence.py`
7. Phase 4 test: `python tests/test_phase4_freeze.py`

All from project root unless noted.

### Output files

| File | Producer | Location | Content |
|------|----------|----------|---------|
| consequence_field.json | Phase 5 | Project root | Consequence vectors, edge_deltas |
| meaning_map.json | Phase 6 | Project root | Clusters, signatures |
| roles.json | Phase 7 | Project root | Cluster roles, symbol_to_role |
| constraints.json | Phase 8 | Project root | Patterns, forbidden, templates |
| phase2_output.json, phase3_output.json, phase4_output.json | Optional save | Project root | Phase 2/3/4 metrics |
| intrinsic_eval_report.json | validation_crush | validation_crush/reports/ | All validation metrics |
| validation.log | validation_crush | validation_crush/ | Run log |

Phase 9 returns a symbol sequence; no file.

---

## PART X — Troubleshooting and Glossary

### Troubleshooting

- **ImportError threshold_onset / phase0…:** Run from project root or `pip install -e .`. main.py adds project_root and package_dir (threshold_onset) to sys.path.
- **ImportError santok:** Use santok_complete in-tree (project root on path) or install santok.
- **ImportError integration.continuation_observer:** Add project root to sys.path; semantic may skip or simplify.
- **Phase 5–9 not running:** RUN_SEMANTIC_PHASES=True; Phase 2/3/4 must complete; check logs for "Phase 5 failed" etc.
- **validation_crush fails / no report:** Run from project root; ensure validation_crush/reports/ exists; check validation.log.
- **Unicode/encoding (e.g. Windows):** Log files opened with encoding='utf-8'; avoid non-ASCII in paths if issues persist.

### Glossary

- **Action:** Callable returning residue; Phase 0 only.
- **Residue/trace:** Opaque output of action.
- **Identity:** Persistent unit (Phase 2); internal hash.
- **Relation:** Pair/structure connecting identities (Phase 3).
- **Symbol:** Integer alias (Phase 4).
- **Consequence field:** Per-identity "what happens next" (Phase 5).
- **Meaning cluster:** Group of identities with similar consequence vectors (Phase 6).
- **Role:** Functional label for cluster (Phase 7).
- **Constraint/template:** Allowed/forbidden role sequences (Phase 8).
- **Fluency gate:** Generate vs refuse (Phase 9).
- **ContinuationObserver:** Records continuation refusals.
- **SanTOK:** Tokenization library (in-tree or external).
- **Freeze:** Phases 0–4 behavior and interfaces fixed.

---

## PART XI — Other documentation index

| Path | Content |
|------|---------|
| docs/axioms/AXIOMS.md | Layer 0–4 axioms |
| docs/architecture/ARCHITECTURE.md | Architecture layers |
| docs/PAPER_ARCHITECTURE.md | Paper-ready architecture (structure-first, decoder) |
| docs/PHASE_STATUS_CANONICAL.md | Canonical phase status |
| docs/EXECUTION_MODES.md | Single vs multi-run |
| docs/simple/PHASE0_TO_PHASE3_STORY.md | Simple story |
| docs/PHASE0_ACTION_VARIANTS.md | Action variants |
| PROJECT_STRUCTURE.md | Structure |
| threshold_onset/semantic/PROGRESS_SUMMARY.md | Semantic progress |
| validation_crush/VALIDATION_PROTOCOL.md | Validation protocol |
| validation_crush/red_team_checklist.md | Red team checklist |
| integration/README.md | Integration overview |
| santok_complete/README.md | SanTOK overview |

(All other .md files are listed in PART II with one-line purpose.)

---

## PART XII — Single-page cheat sheet

- **Run full system:** `python main.py` (INPUT_TEXT, RUN_SEMANTIC_PHASES in main.py).
- **Run validation:** `python validation_crush/crush_protocol.py --all`.
- **Change input:** Edit INPUT_TEXT in main.py.
- **Outputs:** consequence_field.json, meaning_map.json, roles.json, constraints.json (root); intrinsic_eval_report.json (validation_crush/reports/).
- **Phases 0–4:** Foundation (action→residue→boundaries→identity→relation→symbol). Frozen.
- **Phases 5–9:** Consequence→meaning→roles→constraints→fluency. threshold_onset/semantic/.
- **Principle:** कार्य before ज्ञान. No meaning in Phase 0.

---

## PART XIII — main.py run_phase* reference

All Phase runner functions in `main.py` (quick lookup).

| Function | Purpose |
|----------|---------|
| `run_phase0_noise_baseline()` | Phase 0 with random actions; returns traces |
| `run_phase0_inertia()` | Phase 0 with InertiaAction |
| `run_phase0_random_walk()` | Phase 0 with BoundedWalk |
| `run_phase0_oscillator()` | Phase 0 with WeakOscillator |
| `run_phase0_decay_noise()` | Phase 0 with DecayNoise |
| `run_phase0_finite()` | Phase 0 with FiniteAction |
| `run_phase0_from_text(text, tokenization_method="word", steps=None, ...)` | Tokenize text → Phase 0 → residues |
| `run_phase1(residues)` | Phase 1 on one residue list → metrics dict |
| `run_phase2_multi_run(residue_sequences, phase1_metrics_list)` | Phase 2 multi-run → phase2 metrics |
| `run_phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)` | Phase 3 multi-run → phase3 metrics |
| `run_phase4_multi_run(phase2_metrics, phase3_metrics)` | Phase 4 → phase4 output (or None) |
| `run_phase5_semantic(phase2_metrics, phase3_metrics, phase4_output, observer)` | ConsequenceFieldEngine → consequence_field.json |
| `run_phase6_semantic(consequence_field)` | MeaningDiscoveryEngine → meaning_map.json |
| `run_phase7_semantic(meaning_map, consequence_field, observer)` | RoleEmergenceEngine → roles.json |
| `run_phase8_semantic(roles, symbol_sequences, consequence_field, observer, phase4_output)` | ConstraintDiscoveryEngine → constraints.json |
| `run_phase9_semantic(consequence_field, roles, constraints, phase3_metrics, phase4_output, observer)` | FluencyGenerator → symbol sequence (optional streaming) |

---

## PART XIV — Validation test classes (A–I)

Each test in `validation_crush/tests/` has a class with `run(config) -> (passed, metrics)`. Pass/fail: A and D use **Phase 9 refusal** as primary (refusal ⇒ pass); others use metrics/thresholds.

| Phase | Class | File | What run() does | Pass when |
|-------|--------|------|------------------|-----------|
| A | PhaseABaselineTest | phase_a_baseline.py | Generates fluent nonsense, runs process_text_through_system | System refuses or high entropy / no stable roles; fail if fluent continuation |
| B | PhaseBPerturbationTest | phase_b_perturbation.py | Micro-perturbation over **all 9 tokenization methods**, runs pipeline | Continuous deformation; variance/cluster behavior within bounds |
| C | PhaseCConsistencyTest | phase_c_consistency.py | Temporal recall test (two inputs, compare structure) | Structural isomorphism; fail if surface-token similarity driven |
| D | PhaseDCausalTest | phase_d_causal.py | Impossible-worlds input (causal contradiction) | **Refusal** or exploding entropy; fail if fluent explanation |
| E | PhaseERoleCollapseTest | phase_e_role_collapse.py | Role overload with **100K+ token** input via process_text_through_system | Role bifurcation or rejection; fail if silent role merging |
| F | PhaseFConstraintInversionTest | phase_f_constraint_inversion.py | Reverse-grammar challenge | Constraint drift or dual grammar; fail if single averaged constraint |
| G | PhaseGStreamingTest | phase_g_streaming.py | Forced degradation (partial failure, delays) | Adaptive resizing, semantic continuity; fail if filler output |
| H | PhaseHRedTeamTest | phase_h_red_team.py | Human-adversary scenarios | Refusal quality, instability signals; not correctness |
| I | PhaseIKillSwitchTest | phase_i_kill_switch.py | Meaning denial (actions exist, consequences null) | Phase 6 does not stabilize, Phase 9 **does not generate**; if it still talks → ABANDON |

---

## PART XV — End-to-end pipeline summary

**Text in:** `INPUT_TEXT` (or action variant). **Step 1:** Tokenize with SanTOK (one of 9 methods) → tokens. **Step 2:** Tokens → Phase 0 actions → residues (one or more runs). **Step 3:** Residues → Phase 1 (boundaries, clusters, distances, repetition). **Step 4:** Residue sequences + Phase 1 → Phase 2 multi-run (persistence, identity hashes). **Step 5:** Residues + Phase 1 + Phase 2 → Phase 3 multi-run (graph, relations). **Step 6:** Phase 2 + Phase 3 → Phase 4 (identity/symbol and relation/symbol mappings). **Step 7:** Phase 2–4 + ContinuationObserver → Phase 5 (consequence field) → consequence_field.json. **Step 8:** Consequence field → Phase 6 (meaning clusters) → meaning_map.json. **Step 9:** Meaning map + consequence field → Phase 7 (roles) → roles.json. **Step 10:** Roles + symbol sequences + edge deltas → Phase 8 (constraints, templates) → constraints.json. **Step 11:** Consequence field + roles + constraints + Phase 3/4 + observer → Phase 9 (experience table, fluency gate, generate) → symbol sequence (no file). **Validation:** Same pipeline stressed by nonsense, perturbation, causality, role overload, constraint inversion, streaming, red team, meaning denial; report in validation_crush/reports/intrinsic_eval_report.json; Phase I failure ⇒ ABANDON.

---

**End of document.** For code-level detail, see the listed files and their docstrings.
