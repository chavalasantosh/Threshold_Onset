"""
Phase 8: Constraint Discovery

Enterprise-grade constraint and template discovery.

CORRECTED: Global forbidden comparison, prefix-match templates.
"""

from threshold_onset.semantic.phase8.constraint_discovery import ConstraintDiscoveryEngine
from threshold_onset.semantic.phase8.sequences import extract_role_sequences
from threshold_onset.semantic.phase8.pattern_miner import (
    discover_role_patterns,
    discover_forbidden_patterns,
    build_templates,
    compute_prefix_match_score
)

__all__ = [
    'ConstraintDiscoveryEngine',
    'extract_role_sequences',
    'discover_role_patterns',
    'discover_forbidden_patterns',
    'build_templates',
    'compute_prefix_match_score',
]
