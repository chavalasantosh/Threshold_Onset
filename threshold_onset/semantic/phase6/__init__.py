"""
Phase 6: Meaning Discovery

Enterprise-grade meaning clustering system.

CORRECTED: Stability-based cluster selection, not hand-chosen.
"""

from threshold_onset.semantic.phase6.meaning_discovery import MeaningDiscoveryEngine
from threshold_onset.semantic.phase6.normalization import normalize_vectors
from threshold_onset.semantic.phase6.clustering import (
    cluster_consequence_vectors,
    k_medoids_pam,
    select_optimal_k,
    compute_cluster_stability
)

__all__ = [
    'MeaningDiscoveryEngine',
    'normalize_vectors',
    'cluster_consequence_vectors',
    'k_medoids_pam',
    'select_optimal_k',
    'compute_cluster_stability',
]
