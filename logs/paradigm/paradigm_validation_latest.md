# THRESHOLD_ONSET Paradigm Validation

- Generated: `2026-03-14T12:10:51.163972+00:00`
- Profile: `quick`
- Prompts: `4`
- Repeats: `3`
- Success rate: `100.00%`
- Structural valid rate: `100.00%`
- Determinism rate: `100.00%`
- Latency p50: `4486.9 ms`
- Latency p95: `6912.4 ms`
- Baseline wins: `3`

## Baseline Comparisons (Internal)

| System | Avg self-transition | Avg violations | Decoder consistency | Samples |
|---|---:|---:|---:|---:|
| threshold_onset | 0.00% | 0.00 | 80.00% | 12 |
| echo | 0.00% | 0.00 | 100.00% | 12 |
| markov1 | 10.53% | 2.00 | 100.00% | 12 |
| random | 36.84% | 7.00 | 100.00% | 12 |
| uniform | 100.00% | 19.00 | 100.00% | 12 |

## Samples
| prompt_idx | repeat | success | failure_code | tokens | ids | relations | refusals | latency_ms |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 0 | 1 | `` | 3 | 3 | 45 | 6 | 3060.6 |
| 0 | 1 | 1 | `` | 3 | 3 | 45 | 6 | 2030.2 |
| 0 | 2 | 1 | `` | 3 | 3 | 45 | 6 | 1797.6 |
| 1 | 0 | 1 | `` | 4 | 4 | 84 | 6 | 2942.4 |
| 1 | 1 | 1 | `` | 4 | 4 | 84 | 6 | 3104.2 |
| 1 | 2 | 1 | `` | 4 | 4 | 84 | 6 | 3527.9 |
| 2 | 0 | 1 | `` | 5 | 5 | 135 | 2 | 5890.3 |
| 2 | 1 | 1 | `` | 5 | 5 | 135 | 2 | 5445.8 |
| 2 | 2 | 1 | `` | 5 | 5 | 135 | 2 | 5815.0 |
| 3 | 0 | 1 | `` | 6 | 6 | 186 | 5 | 6912.4 |
| 3 | 1 | 1 | `` | 6 | 6 | 186 | 5 | 7378.3 |
| 3 | 2 | 1 | `` | 6 | 6 | 186 | 5 | 6640.3 |
