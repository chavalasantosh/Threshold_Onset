"""
Phase 10 — operational constants (single source of truth).

These values are intentionally explicit so production callers can audit gates
and thresholds without hunting through implementation details.
"""

from __future__ import annotations

# Gate: minimum observed directed transitions across all streams before Phase 10
# metrics are considered structurally grounded.
MIN_TRANSITIONS_FOR_GATE: int = 1

# Default mass fraction on the dominant outgoing edge for "necessity" labeling.
# 1.0 means a single empirical successor accounts for all mass from that source
# (no tied maximum counts).
DEFAULT_NECESSITY_MASS_THRESHOLD: float = 1.0

# JSON / logging: delimiter must not appear in MD5 hex identity hashes (0-9a-f).
PAIR_KEY_SEP: str = "||"
