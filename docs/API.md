# THRESHOLD_ONSET — API Reference

## Programmatic API

### `process(text, config=None, *, max_input_length=1000000, silent=True) -> ProcessResult`

Process text through the full pipeline.

**Parameters:**
- `text` (str): Input text to process.
- `config` (dict, optional): Config override. If None, uses `get_config()`.
- `max_input_length` (int): Max allowed input length in chars. Default 1M.
- `silent` (bool): If True, suppress pipeline stdout. Default True.

**Returns:** `ProcessResult`

**Raises:** `ValidationError` if input is empty or exceeds `max_input_length`.

**Example:**
```python
from threshold_onset.api import process

result = process("Action before knowledge")
print(result.success, result.generated_outputs, result.token_count)
```

---

### `ProcessResult`

| Field | Type | Description |
|-------|------|-------------|
| `success` | bool | Whether pipeline completed successfully |
| `input_text` | str | Original input text |
| `generated_outputs` | list[str] | Generated text sequences |
| `token_count` | int | Number of tokens |
| `identity_count` | int | Number of identities |
| `duration_seconds` | float | Pipeline duration |
| `metrics` | dict | Extra metrics |
| `error` | str \| None | Error message if failed |

**Methods:**
- `to_dict()` — Convert to JSON-serializable dict.

---

## Config

### `load_config(config_path=None) -> dict`

Load config from JSON file with env overrides.

**Parameters:**
- `config_path` (Path, optional): Path to config. Uses `THRESHOLD_ONSET_CONFIG` or `config/default.json`.

**Returns:** Merged config dict.

**Raises:** `ConfigError` on load failure.

---

### `get_config() -> dict`

Return current config. Loads default if not yet loaded.

---

## Exceptions

| Exception | Code | When |
|-----------|------|------|
| `ThresholdOnsetError` | THRESHOLD_ONSET_ERROR | Base |
| `ConfigError` | CONFIG_ERROR | Config load/validation |
| `PipelineError` | PIPELINE_ERROR | Pipeline execution |
| `ValidationError` | VALIDATION_ERROR | Input validation |

---

## REST API (Optional)

Run `python scripts/health_server.py` to serve:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health`, `/ready` | Health status (JSON) |
| POST | `/process` | Process text. Body: `{"text": "..."}` |

**Example:**
```bash
curl -X POST http://localhost:8080/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Your input"}'
```

---

## Metrics

### `PipelineMetrics`

From `threshold_onset.metrics`:

- `duration_seconds`, `token_count`, `identity_count`, `success`
- `to_dict()` — Serialize to dict
- `to_prometheus_lines(prefix="threshold_onset")` — Prometheus text format

### `collect_from_result(result) -> PipelineMetrics`

Build metrics from a `ProcessResult`.
