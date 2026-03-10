# How to Run All Scripts in CMD (Command Prompt)

## Quick Start

### Option 1: Run full project from root (recommended)
```cmd
cd your-project-root
python main.py
```
Or double-click `main.bat` or `run_all.bat` in the project root.

### Option 2: Run integration scripts
```cmd
cd integration
run_all_scripts.bat
```

### Option 3: Run scripts individually in CMD

Open Command Prompt (cmd.exe), then:

```cmd
cd your-project-root\integration
set PYTHONIOENCODING=utf-8

REM Main systems
python run_complete.py
python train.py --epochs 20 --interval 5
python scoring.py
python main_complete.py
python unified_system.py

REM Analysis tools
python test_invariant.py
python escape_topology.py
python topology_clusters.py
python transition_matrix.py
python identity_permissions.py
python refusal_signatures.py
python near_refusal_observer.py
python observe_refusals.py
python test_permuted.py
python test_continuation.py
python compare_topologies.py
```

## Why CMD instead of PowerShell?

- CMD handles Python f-strings better
- No `{}` parsing issues
- Simpler syntax for batch scripts
- Better compatibility with Python scripts

## Executable Scripts

1. run_complete.py - Main end-to-end system
2. run_user_result.py - User-facing output (used by main.py --check)
3. run_user_input.py - Quick benchmark-style pipeline
4. train.py - Training loop
5. scoring.py - Path scoring
6. main_complete.py - Alternative main
7. unified_system.py - Core system
8. test_invariant.py - Universal law test
9. escape_topology.py - Topology measurement
10. topology_clusters.py - Clustering analysis
11. transition_matrix.py - Permission matrix
12. identity_permissions.py - Permission profiles
13. refusal_signatures.py - Signature analysis
14. near_refusal_observer.py - Near-refusal observation
15. observe_refusals.py - Refusal recording
16. test_permuted.py - Permuted testing
17. test_continuation.py - Continuation testing
18. compare_topologies.py - Topology comparison

## Status: ALL OPERATIONAL ✅
