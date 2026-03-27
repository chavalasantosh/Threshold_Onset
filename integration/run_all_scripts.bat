@echo off
REM ========================================================================
REM RUN ALL EXECUTABLE SCRIPTS - CMD VERSION
REM ========================================================================
setlocal enabledelayedexpansion
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

echo =======================================================================
echo EXECUTING ALL SCRIPTS - CMD VERSION
echo =======================================================================
echo.

echo [1/16] run_complete.py - Main end-to-end system
echo -----------------------------------------------------------------------
python run_complete.py
echo.
echo =======================================================================
echo.

echo [2/16] train.py - Training loop (10 epochs)
echo -----------------------------------------------------------------------
python train.py --epochs 10 --interval 3
echo.
echo =======================================================================
echo.

echo [3/16] scoring.py - Path scoring system
echo -----------------------------------------------------------------------
python scoring.py
echo.
echo =======================================================================
echo.

echo [4/16] main_complete.py - Alternative main entry
echo -----------------------------------------------------------------------
python main_complete.py
echo.
echo =======================================================================
echo.

echo [5/16] unified_system.py - Core unified system
echo -----------------------------------------------------------------------
python unified_system.py
echo.
echo =======================================================================
echo.

echo [6/16] test_invariant.py - Universal invariant test
echo -----------------------------------------------------------------------
python test_invariant.py
echo.
echo =======================================================================
echo.

echo [7/16] escape_topology.py - Escape topology measurement
echo -----------------------------------------------------------------------
python escape_topology.py
echo.
echo =======================================================================
echo.

echo [8/16] topology_clusters.py - Topology clustering
echo -----------------------------------------------------------------------
python topology_clusters.py
echo.
echo =======================================================================
echo.

echo [9/16] transition_matrix.py - Transition matrix
echo -----------------------------------------------------------------------
python transition_matrix.py
echo.
echo =======================================================================
echo.

echo [10/16] identity_permissions.py - Identity permissions
echo -----------------------------------------------------------------------
python identity_permissions.py
echo.
echo =======================================================================
echo.

echo [11/16] refusal_signatures.py - Refusal signatures
echo -----------------------------------------------------------------------
python refusal_signatures.py
echo.
echo =======================================================================
echo.

echo [12/16] near_refusal_observer.py - Near-refusal observation
echo -----------------------------------------------------------------------
python near_refusal_observer.py
echo.
echo =======================================================================
echo.

echo [13/16] observe_refusals.py - Refusal observation
echo -----------------------------------------------------------------------
python observe_refusals.py
echo.
echo =======================================================================
echo.

echo [14/16] test_permuted.py - Permuted testing
echo -----------------------------------------------------------------------
python test_permuted.py
echo.
echo =======================================================================
echo.

echo [15/16] test_continuation.py - Continuation testing
echo -----------------------------------------------------------------------
python test_continuation.py
echo.
echo =======================================================================
echo.

echo [16/16] compare_topologies.py - Topology comparison
echo -----------------------------------------------------------------------
python compare_topologies.py
echo.
echo =======================================================================
echo.
echo EXECUTION COMPLETE - ALL 16 SCRIPTS EXECUTED
echo =======================================================================
pause
