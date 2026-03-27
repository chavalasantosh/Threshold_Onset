# THRESHOLD_ONSET — Operational Runbook

Troubleshooting and common failure modes.

---

## Quick Diagnostics

| Symptom | Check | Fix |
|---------|-------|-----|
| `Config file not found` | `THRESHOLD_ONSET_CONFIG` or `config/default.json` | Set env or ensure config exists |
| `No module named 'santok'` | Tokenization dependency | `pip install santok` |
| `No module named 'threshold_onset'` | Package not installed | `pip install -e .` from project root |
| Empty output | Input text empty | Provide non-empty text |
| Pipeline fails at Phase 2/3/4 | Input too short or degenerate | Use longer input (10+ tokens) |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Pipeline or command failure |
| 2 | Config load/validation error |

---

## Common Failures

### 1. Config Error (exit 2)

**Cause:** Config file missing or invalid JSON.

**Fix:**
```bash
# Verify config exists
ls config/default.json

# Or set explicit path
export THRESHOLD_ONSET_CONFIG=/path/to/config.json
```

### 2. Import Error (santok, santek, somaya)

**Cause:** Tokenization modules not installed.

**Fix:**
```bash
pip install santok santek somaya
# Or use fallback: tokenization will use text.split()
```

### 3. Phase 2 Gate Failed

**Cause:** No persistent segments detected. Often with very short input.

**Fix:** Use longer input (e.g. 5+ words). Multi-run mode needs sufficient tokens.

### 4. UnicodeEncodeError in Logs

**Cause:** Console encoding doesn't support Unicode.

**Fix:**
```bash
export PYTHONIOENCODING=utf-8
# Or on Windows: set PYTHONIOENCODING=utf-8
```

### 5. Docker Health Check Failing

**Cause:** `threshold-onset config` fails (e.g. config not mounted).

**Fix:**
```bash
# Ensure config is in image or mounted
docker run -v $(pwd)/config:/app/config threshold-onset
```

---

## Log Locations

- **Default:** stdout (no file)
- **With log_dir:** `{output_dir}/threshold_onset.log` or `{log_dir}/threshold_onset.log`
- **run_and_log.py:** `execution_log.txt` (or `--out FILE`)

---

## Health Check

```bash
# Verify pipeline can run
threshold-onset config

# Quick smoke test
threshold-onset check "Action before knowledge"
```

---

## Escalation

1. Check `docs/EXECUTION.md` for run modes
2. Check `docs/DEPLOYMENT.md` for Docker/env
3. Run with `--log-level DEBUG` for verbose output
4. Inspect `execution_log.txt` if using `run_and_log.py`
