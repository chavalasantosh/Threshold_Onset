# Executable Scripts in Integration Directory

## Main/Complete Systems (Run These First)
1. **run_complete.py** - Main end-to-end unified system (RECOMMENDED)
2. **main_complete.py** - Alternative main entry point
3. **main_end_to_end.py** - Another main variant
4. **unified_system.py** - Core unified system
5. **train.py** - Training loop for preference learner

## Core Components (Modules - can be run standalone)
6. **scoring.py** - Path scoring system
7. **generate.py** - Sequence generation
8. **surface.py** - Surface token mapping
9. **preference_learner.py** - Minimal learner component

## Analysis/Observation Tools
10. **continuation_observer.py** - Continuation observation
11. **escape_topology.py** - Escape topology measurement
12. **near_refusal_observer.py** - Near-refusal observation
13. **topology_clusters.py** - Topology clustering analysis
14. **compare_topologies.py** - Compare topologies across inputs
15. **transition_matrix.py** - Transition permission matrix
16. **identity_permissions.py** - Identity permission profiles
17. **refusal_signatures.py** - Refusal signature analysis

## Test Scripts
18. **test_invariant.py** - Universal invariant testing
19. **test_permuted.py** - Permuted continuation testing
20. **test_continuation.py** - Continuation testing
21. **observe_refusals.py** - Refusal observation tool

## Execution Order Recommendation:
1. `run_complete.py` - See full system
2. `train.py --epochs 50` - See learning progress
3. `scoring.py` - See path scoring
4. `test_invariant.py` - Verify universal law
5. Other analysis tools as needed
