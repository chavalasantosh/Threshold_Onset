"""
Type definitions for semantic discovery module.

Enterprise-grade type definitions with full type hints.
"""

from typing import TypedDict, Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass


class ConsequenceVector(TypedDict):
    """Consequence vector for an identity."""
    out_degree: int
    k_reach: int
    survival: float  # [0.0, 1.0]
    entropy: float  # >= 0.0
    escape_concentration: float  # [0.0, 1.0]
    near_refusal_rate: float  # [0.0, 1.0]
    dead_end_risk: float  # [0.0, 1.0]


class ConsequenceDelta(TypedDict):
    """Counterfactual delta for a transition."""
    survival_delta: float
    k_reach_delta: int
    entropy_delta: float
    refusal_delta: float


class MeaningSignature(TypedDict):
    """Meaning signature for a cluster."""
    centroid: Dict[str, float]
    size: int
    identities: List[str]


class RoleMap(TypedDict):
    """Role mapping for symbols."""
    symbol_to_role: Dict[int, str]
    cluster_roles: Dict[str, str]
    role_properties: Dict[str, Dict[str, float]]


class ConstraintMap(TypedDict):
    """Constraint and template map."""
    role_patterns: Dict[Tuple[str, ...], Dict[str, Any]]
    forbidden_patterns: Set[Tuple[str, ...]]
    templates: List[Dict[str, Any]]


@dataclass
class ConsequenceField:
    """Consequence field container."""
    identity_vectors: Dict[str, ConsequenceVector]
    edge_deltas: Dict[Tuple[str, str], ConsequenceDelta]
    metadata: Dict[str, Any]


@dataclass
class MeaningMap:
    """Meaning map container."""
    clusters: Dict[str, MeaningSignature]
    identity_to_cluster: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class RolloutResult:
    """Result of a single rollout."""
    survival_length: int
    refusal_occurred: bool
    pressure_accumulated: float
    entropy_trajectory: List[float]
    path_taken: List[str]
    near_refusal_states: Optional[List[str]] = None