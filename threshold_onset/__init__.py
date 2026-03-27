"""
THRESHOLD_ONSET - Foundational System for Structure Emergence

A system that proves structure emerges before language exists.
"""

from threshold_onset.phase10 import (
    Phase10Result,
    phase10_jsonable_from_model_state,
    run_phase10,
    run_phase10_from_model_state,
)
from threshold_onset.identity_conditioned import IdentityConditionedAccumulator

__version__ = "1.2.0"

__all__ = [
    "__version__",
    "IdentityConditionedAccumulator",
    "Phase10Result",
    "phase10_jsonable_from_model_state",
    "run_phase10",
    "run_phase10_from_model_state",
]
