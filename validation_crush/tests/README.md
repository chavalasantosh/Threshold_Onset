# Validation Crush — Tests

Phase A–I crush-to-death tests.

| File | Phase | Test |
|------|-------|------|
| `phase_a_baseline.py` | A | Fluent nonsense |
| `phase_b_perturbation.py` | B | Micro-perturbation, 9 tokenization methods |
| `phase_c_consistency.py` | C | Temporal recall |
| `phase_d_causal.py` | D | Impossible worlds |
| `phase_e_role_collapse.py` | E | Role overload (100K+ tokens) |
| `phase_f_constraint_inversion.py` | F | Reverse-grammar |
| `phase_g_streaming.py` | G | Forced degradation |
| `phase_h_red_team.py` | H | Human adversary |
| `phase_i_kill_switch.py` | I | Meaning denial → ABANDON |

Run: `python validation_crush/crush_protocol.py --all` or `--phase A` through `--phase I`.
