# THRESHOLD_ONSET Paradigm Validation

- Generated: `2026-03-14T19:25:49.821430+00:00`
- Profile: `quick`
- Prompts: `4`
- Repeats: `3`
- Success rate: `100.00%`
- Structural valid rate: `100.00%`
- Determinism rate: `100.00%`
- Latency p50: `681.1 ms`
- Latency p95: `1493.9 ms`
- Baseline wins: `3`

## Baseline Comparisons (Internal)

| System | Avg self-transition | Avg violations | Decoder consistency | Samples |
|---|---:|---:|---:|---:|
| threshold_onset | 0.00% | 0.00 | 68.00% | 12 |
| echo | 0.00% | 0.00 | 100.00% | 12 |
| markov1 | 10.53% | 2.00 | 100.00% | 12 |
| random | 36.84% | 7.00 | 100.00% | 12 |
| uniform | 100.00% | 19.00 | 100.00% | 12 |

## Samples
| prompt_idx | repeat | success | failure_code | tokens | ids | relations | refusals | latency_ms |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 0 | 0 | 1 | `` | 3 | 3 | 45 | 6 | 388.2 |
| 0 | 1 | 1 | `` | 3 | 3 | 45 | 6 | 360.1 |
| 0 | 2 | 1 | `` | 3 | 3 | 45 | 6 | 351.9 |
| 1 | 0 | 1 | `` | 4 | 4 | 84 | 6 | 541.9 |
| 1 | 1 | 1 | `` | 4 | 4 | 84 | 6 | 537.2 |
| 1 | 2 | 1 | `` | 4 | 4 | 84 | 6 | 544.1 |
| 2 | 0 | 1 | `` | 5 | 5 | 135 | 2 | 818.0 |
| 2 | 1 | 1 | `` | 5 | 5 | 135 | 2 | 908.3 |
| 2 | 2 | 1 | `` | 5 | 5 | 135 | 2 | 971.8 |
| 3 | 0 | 1 | `` | 6 | 6 | 186 | 5 | 1271.4 |
| 3 | 1 | 1 | `` | 6 | 6 | 186 | 5 | 1507.2 |
| 3 | 2 | 1 | `` | 6 | 6 | 186 | 5 | 1493.9 |
