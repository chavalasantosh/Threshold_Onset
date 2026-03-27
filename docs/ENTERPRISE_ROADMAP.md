# THRESHOLD_ONSET — Enterprise Product Roadmap

**Goal:** Elevate from research/college grade to enterprise product grade.

**Status:** ✅ Enterprise transformation complete. All phases implemented.

---

## Gap Analysis: Research vs Enterprise

| Dimension | Current (Research) | Enterprise Target |
|-----------|-------------------|-------------------|
| **CLI** | Manual argv parsing | argparse, --config, --log-level, --output |
| **Config** | Hardcoded in scripts | YAML/JSON config file, env overrides |
| **Logging** | print(), scattered logging | Structured logging, levels, file rotation |
| **Errors** | Ad-hoc exceptions | Exception hierarchy, error codes, graceful degradation |
| **API** | Scripts only | Programmatic API + REST (POST /process) |
| **Deployment** | pip install, run scripts | Docker, docker-compose, health check |
| **Monitoring** | None | Metrics, health endpoint |
| **Docs** | README, paper | API docs, deployment guide, runbook |
| **Tests** | Unit tests | CI, coverage, integration, smoke ✅ |
| **Security** | Minimal | Input validation, no secrets in code |

---

## Phase 1: Foundation (Weeks 1–2) ✅ DONE

### 1.1 Config Management ✅
- [x] `config/default.json` — Default configuration
- [x] `threshold_onset/config/loader.py` — Load config, env overrides
- [x] Support `THRESHOLD_ONSET_CONFIG` env var
- [x] Env overrides: `THRESHOLD_ONSET_TOKENIZATION`, `THRESHOLD_ONSET_NUM_RUNS`, `THRESHOLD_ONSET_LOG_LEVEL`, `THRESHOLD_ONSET_OUTPUT_DIR`

### 1.2 Structured Logging ✅
- [x] `threshold_onset/core/logging_config.py`
- [x] Log levels: DEBUG, INFO, WARNING, ERROR
- [x] File + console handlers (optional log_dir)
- [x] RotatingFileHandler (10MB, 5 backups)
- [x] Logger in run_complete for errors and gate failures (gradual)

### 1.3 Professional CLI ✅
- [x] `threshold_onset/cli.py` — Single entry point
- [x] Subcommands: `run`, `check`, `suite`, `validate`, `benchmark`, `config`
- [x] `--config`, `--log-level`, `--output-dir`, `--quiet`
- [x] Exit codes: 0 success, 1 failure, 2 config error
- [x] Entry point: `threshold-onset` (pip install -e .)

### 1.4 Exception Hierarchy ✅
- [x] `threshold_onset/exceptions.py` — ThresholdOnsetError, ConfigError, PipelineError, ValidationError
- [x] Error codes for programmatic handling

---

## Phase 2: Deployment (Weeks 2–3) ✅ DONE

### 2.1 Containerization ✅
- [x] `Dockerfile` — Slim Python 3.11 image
- [x] `docker-compose.yml` — Service definition
- [x] `.dockerignore` — Exclude dev artifacts

### 2.2 Health & Readiness ✅
- [x] Health check in Dockerfile (`threshold-onset config`)
- [x] `threshold-onset health` — JSON status, `-v` for pipeline smoke test
- [x] `scripts/health_server.py` — HTTP /health and /ready on port 8080

### 2.3 Programmatic API ✅
- [x] `threshold_onset.api` — Clean Python API
- [x] `process(text, config) -> ProcessResult`
- [x] Type hints, docstrings, input validation
- [x] REST: POST `/process` in `scripts/health_server.py`

---

## Phase 3: Observability (Weeks 3–4) ✅ DONE

### 3.1 Metrics ✅
- [x] `threshold_onset.metrics` — PipelineMetrics, duration, token_count, identity_count
- [x] `to_prometheus_lines()` — Optional Prometheus export

### 3.2 Operational Docs ✅
- [x] `docs/DEPLOYMENT.md` — Docker, env vars
- [x] `docs/RUNBOOK.md` — Troubleshooting, common failures
- [x] `docs/API.md` — API reference (process, config, REST, metrics)

---

## Phase 4: Polish (Ongoing)

### 4.1 CI/CD ✅
- [x] GitHub Actions: added Enterprise CLI and API smoke test to ci.yml
- [x] Test coverage step (pytest-cov)

### 4.2 Security ✅
- [x] Input length limits (`max_input_length` in config, ValidationError)
- [x] No eval/exec of user input (stdlib only in core)

---

## Implementation Order

1. **Config** — Enables everything else
2. **Logging** — Operational visibility
3. **CLI** — Professional interface
4. **Exceptions** — Error handling
5. **Dockerfile** — Deployment
6. **API** — Programmatic access

---

## Dependencies (Minimal)

- **Core:** stdlib only (no new deps for Phase 1.1–1.4)
- **Config:** Use `json` for config (stdlib); optional `pyyaml` for YAML
- **Docker:** No Python deps; use `python:3.11-slim` base

---

## Success Criteria

- [x] `threshold-onset run --config config/prod.json` works
- [x] Logs go to file + console with configurable level (logging_config)
- [x] Docker image builds and runs
- [x] Clear error messages with actionable guidance (exceptions, RUNBOOK)
- [x] Single entry point: `python -m threshold_onset` or `threshold-onset`
- [x] Programmatic API: `process(text) -> ProcessResult`
