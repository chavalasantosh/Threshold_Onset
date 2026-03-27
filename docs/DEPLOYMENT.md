# THRESHOLD_ONSET — Deployment Guide

## Docker

### Build

```bash
docker build -t threshold-onset:latest .
```

### Docker Compose

```bash
# Run pipeline (default)
docker compose up

# Run full suite (profile)
docker compose --profile suite up threshold-onset-suite
```

### Run

```bash
# Default: run pipeline with built-in corpus
docker run --rm threshold-onset:latest

# With custom input
docker run --rm threshold-onset:latest threshold-onset run "Your input text"

# Override config via env
docker run --rm -e THRESHOLD_ONSET_TOKENIZATION=character -e THRESHOLD_ONSET_NUM_RUNS=5 threshold-onset:latest
```

### Mount custom config

```bash
docker run --rm -v /path/to/your/config.json:/app/config/custom.json \
  -e THRESHOLD_ONSET_CONFIG=/app/config/custom.json \
  threshold-onset:latest
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `THRESHOLD_ONSET_CONFIG` | Path to config JSON | `/app/config/prod.json` |
| `THRESHOLD_ONSET_TOKENIZATION` | Tokenization method | `word`, `character`, `grammar` |
| `THRESHOLD_ONSET_NUM_RUNS` | Number of Phase 0 runs | `5` |
| `THRESHOLD_ONSET_LOG_LEVEL` | Log level | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `THRESHOLD_ONSET_OUTPUT_DIR` | Output directory | `./output` |

## Makefile (Optional)

```bash
make install        # pip install -e .
make run            # threshold-onset run
make check          # Quick check (default text)
make check TEXT="Your text"
make health         # Health check
make test-api       # API integration tests
make docker-build   # Build image
make health-server  # Start HTTP server
```

## CLI (Local Install)

```bash
pip install -e .
threshold-onset run
threshold-onset check "Your text"
threshold-onset suite
threshold-onset config
```

## Health

**CLI:** `threshold-onset health` — JSON status (config, version). Use `-v` for pipeline smoke test.

**HTTP server:** `python scripts/health_server.py` — Serves `/health`, `/ready`, and POST `/process` on port 8080 (or `HEALTH_PORT`).

POST `/process` JSON body (defaults in parentheses):

- `text` (required) — input string  
- `silent` (`true`) — suppress pipeline stdout  
- `max_input_length`, `timeout_seconds`  
- `return_model_state` (`false`) — include full pipeline state in the response (**large**)  
- `include_phase10_metrics` (`false`) — when combined with `return_model_state`, may attach `phase10_metrics`

## Kubernetes (Optional)

```yaml
# deployment.yaml (minimal)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: threshold-onset
spec:
  replicas: 1
  selector:
    matchLabels:
      app: threshold-onset
  template:
    metadata:
      labels:
        app: threshold-onset
    spec:
      containers:
        - name: threshold-onset
          image: threshold-onset:latest
          env:
            - name: THRESHOLD_ONSET_CONFIG
              value: /app/config/default.json
          livenessProbe:
            exec:
              command: ["threshold-onset", "config"]
            initialDelaySeconds: 5
            periodSeconds: 30
```

For one-shot jobs (e.g. batch processing), use a `Job` instead of `Deployment`.

## systemd (Optional)

```ini
# /etc/systemd/system/threshold-onset.service
[Unit]
Description=THRESHOLD_ONSET Health Server
After=network.target

[Service]
Type=simple
User=threshold
WorkingDirectory=/opt/threshold-onset
ExecStart=/usr/bin/python3 scripts/health_server.py
Environment=HEALTH_PORT=8080
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Pipeline or command failure |
| 2 | Config load/validation error |
