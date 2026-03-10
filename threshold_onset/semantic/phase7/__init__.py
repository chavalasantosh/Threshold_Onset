"""
Phase 7: Role Emergence

Enterprise-grade functional role discovery.

CORRECTED: Quantile-based assignment, binder derived from topology.
"""

from threshold_onset.semantic.phase7.role_emergence import RoleEmergenceEngine
from threshold_onset.semantic.phase7.role_assigner import (
    assign_roles_from_properties,
    compute_binder_properties
)
from threshold_onset.semantic.phase7.properties import compute_cluster_properties

__all__ = [
    'RoleEmergenceEngine',
    'assign_roles_from_properties',
    'compute_binder_properties',
    'compute_cluster_properties',
]
