# GitHub

GitHub configuration for THRESHOLD_ONSET.

## workflows/

CI, documentation, lint, phase validation, publish, and release workflows.

| File | Purpose |
|------|---------|
| `ci.yml` | Push/PR on main, develop; matrix Python 3.8–3.12; run main.py; verify phase0–4 imports |
| `documentation.yml` | Doc check: README, docs/, phase freeze files, markdown validation, link check |
| `lint.yml` | Linting |
| `phase-validation.yml` | Phase validation |
| `publish-pypi.yml` | PyPI publish |
| `release.yml` | Release workflow |
