# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-14

### Added - Enterprise Upgrade

#### Config & CLI
- `config/default.json` — Central config with env overrides
- `threshold-onset` CLI — run, check, suite, validate, benchmark, config, health
- `--config`, `--log-level`, `--output-dir`, `--quiet`

#### API & REST
- `threshold_onset.api.process()` — Programmatic API
- POST `/process` — REST endpoint in `scripts/health_server.py`
- `ProcessResult` dataclass with `to_dict()`

#### Deployment
- Dockerfile, docker-compose.yml, .dockerignore
- K8s Deployment and systemd unit examples in docs
- Makefile for common tasks

#### Observability
- Structured logging with RotatingFileHandler
- `threshold_onset.metrics` — PipelineMetrics, Prometheus export
- Health CLI and HTTP `/health`, `/ready`

#### Docs
- `docs/API.md` — API reference
- `docs/DEPLOYMENT.md` — Docker, K8s, systemd, Makefile
- `docs/RUNBOOK.md` — Troubleshooting
- `docs/ENTERPRISE_ROADMAP.md` — Gap analysis and implementation status

#### Security
- Input length limits (`max_input_length` in config)
- `ValidationError` for invalid input

---

## [1.1.0] - 2025-02-06

### Added - Full Freeze (Phases 5-9, Decoder, Integration)

#### Phase 5-9: Semantic (FROZEN)
- Phase 5: Possibility exploration
- Phase 6: Clustering
- Phase 7: Rule learning
- Phase 8: Synthesis
- Phase 9: FluencyGenerator, structural symbol decoder
- **Status**: ✅ FROZEN FOREVER

#### Structural Decoder (FROZEN)
- `symbol_decoder.py`: build_structural_decoder(), decode_symbol_sequence()
- Symbol → identity → residue → token inversion
- **Status**: ✅ FROZEN FOREVER

#### Integration (FROZEN)
- `run_all.py`, `run_all.bat`: full project run
- `validate_pipeline.py`, `stress_test.py`, `fluency_text_generator.py`, `test_decoder.py`
- **Status**: ✅ FROZEN FOREVER

### Documentation
- `PROJECT_FREEZE.md`: project-wide freeze declaration
- `threshold_onset/semantic/PHASE5-9_FREEZE.md`: semantic phases freeze
- `COMPLETE_PROJECT_DOCUMENTATION.md`: updated with all frozen components
- `CONTRIBUTING.md`: frozen scope updated

---

## [1.0.0] - 2024-01-13

### Added - Initial Release

#### Phase 0: THRESHOLD_ONSET (FROZEN)
- Action variants: noise_baseline, inertia, random_walk, oscillator, decay_noise, finite
- Residue generation and tracking
- Repetition and collision detection
- Trace functionality
- **Status**: ✅ FROZEN FOREVER

#### Phase 1: SEGMENTATION (FROZEN)
- Boundary detection in residue sequences
- Clustering algorithms
- Distance measurements
- Pattern detection
- Survival tracking
- **Status**: ✅ FROZEN FOREVER

#### Phase 2: IDENTITY (FROZEN)
- Multi-run persistence measurement
- Repeatable unit detection
- Identity hash assignment
- Stability metrics
- Cross-run identity tracking
- **Status**: ✅ FROZEN FOREVER

#### Phase 3: RELATION (FROZEN)
- Graph construction (hash-based)
- Interaction detection
- Dependency measurement
- Influence metrics
- Relation persistence tracking
- Relation stability measurement
- Convergence validation tests
- **Status**: ✅ FROZEN FOREVER

#### Phase 4: SYMBOL (FROZEN)
- Integer symbol assignment to identities
- Integer symbol assignment to relations
- Reversible lookup tables
- Pure aliasing layer (no structure added)
- Freeze validation tests
- **Status**: ✅ FROZEN FOREVER

### Documentation
- Comprehensive README with phase-by-phase guide
- Core axioms and constraints documentation
- Architecture documentation
- Non-technical explanations
- Phase-specific freeze declarations
- Project history and work logs
- Execution modes documentation

### Testing
- Phase 3 convergence tests (`test_phase3_convergence.py`)
- Phase 4 freeze validation tests (`test_phase4_freeze.py`)

### Tools
- Optional version control system with file watching
- SQLite-based metadata storage
- Unified diff generation

### Submodules
- SanTOK tokenization system integration
- Complete tokenization package with examples and tests

### Infrastructure
- Package setup with `setup.py` and `pyproject.toml`
- Project structure documentation
- Git ignore configuration
- MIT License

---

## Version History

### v0.1.0 - 2024-01-12
- Initial development snapshot
- Core phase implementations
- Basic documentation structure

### v1.0.0 - 2024-01-13
- All phases frozen and validated
- Complete documentation
- Full test coverage
- Production-ready release

---

## Notes

**All phases (0-9), decoder, and integration are FROZEN FOREVER** - Core implementations should not be modified. This is a foundational system exploring structure emergence before language.

See [PROJECT_FREEZE.md](PROJECT_FREEZE.md) for full freeze declaration.
