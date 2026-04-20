"""
Identity-conditioned continuation — empirical (source, content) -> outcome counts.

Not Phase 0–4. Complements Phase 10 (identity-only streams) when you have
observations keyed by both speaker/source handle and content handle.
"""

from __future__ import annotations

from threshold_onset.identity_conditioned.accumulator import IdentityConditionedAccumulator

__all__ = ["IdentityConditionedAccumulator"]
