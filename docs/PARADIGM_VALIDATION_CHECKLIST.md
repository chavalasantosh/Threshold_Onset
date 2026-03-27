# THRESHOLD_ONSET Paradigm Validation Checklist

This checklist is for validating THRESHOLD_ONSET as a real, deployable paradigm
(not a toy and not a transformer clone).

## Core Validation Axes

1. **Claim Registry**
   - Define 3-5 explicit claims the system must satisfy.
   - Example claims:
     - Structural gate reliability
     - Deterministic behavior under fixed config
     - Low failure rate on diverse prompt sets
     - Bounded latency at target throughput

2. **Reproducibility Gate**
   - Run repeated inference on the same prompt set with fixed config.
   - Require deterministic signature stability above threshold.
   - Require structural success rate above threshold.

3. **Failure Taxonomy**
   - Bucket every failure into stable categories:
     - input validation
     - phase gate failure
     - scoring/generation contract
     - runtime/timeouts
   - Track trends over time.

4. **Baseline Comparisons**
   - Compare against at least 2 internal baselines for the same tasks.
   - Keep prompt sets, budget, and stopping conditions fixed.

5. **Production Hardening**
   - API reliability under concurrent load
   - timeout policies
   - structured logs + trace IDs
   - health/readiness checks

## Implemented Now

- Item 1 + Item 2 + Item 3 + Item 4 + Item 5 are implemented through:
  - `scripts/paradigm_validation.py`
  - `threshold_onset/api.py`
  - `scripts/health_server.py`
  - `threshold_onset/cli.py`
  - Output reports under `logs/paradigm/`

This script produces:

- success rate
- structural validity rate
- determinism rate
- latency metrics

And enforces threshold gates via CLI flags.

Failure taxonomy is emitted as stable `failure_code` values in report records
and aggregated in `failure_code_counts`.

Baseline comparisons are emitted as:

- `model_baseline_metrics`
- `baseline_metrics`
- `baseline_wins`

Production hardening now includes:

- trace IDs in API and server responses
- timeout policy (`api_timeout_seconds` or per-request timeout override)
- threaded health server for concurrent API requests
- split health/readiness endpoints (`/health`, `/ready`)
- structured JSON event logging in API/server paths

## Usage

Quick validation:

`python scripts/paradigm_validation.py --profile quick --repeats 3`

Stricter gate example:

`python scripts/paradigm_validation.py --profile quick --repeats 5 --min-success-rate 0.95 --min-determinism-rate 0.90 --max-p95-ms 4000`
