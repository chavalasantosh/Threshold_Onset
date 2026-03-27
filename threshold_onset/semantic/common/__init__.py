"""
Common utilities and shared components for semantic discovery module.

Enterprise-grade shared utilities.
"""

from threshold_onset.semantic.common.types import (
    ConsequenceVector,
    ConsequenceDelta,
    MeaningSignature,
    RoleMap,
    ConstraintMap
)
from threshold_onset.semantic.common.exceptions import (
    SemanticDiscoveryError,
    ConsequenceFieldError,
    MeaningDiscoveryError,
    RoleEmergenceError,
    ConstraintDiscoveryError,
    FluencyGenerationError
)
from threshold_onset.semantic.common.validators import (
    validate_identity_hash,
    validate_symbol,
    validate_transition
)
from threshold_onset.semantic.common.utils import (
    calculate_entropy,
    calculate_percentile,
    normalize_vector,
    calculate_similarity
)

__all__ = [
    # Types
    'ConsequenceVector',
    'ConsequenceDelta',
    'MeaningSignature',
    'RoleMap',
    'ConstraintMap',
    # Exceptions
    'SemanticDiscoveryError',
    'ConsequenceFieldError',
    'MeaningDiscoveryError',
    'RoleEmergenceError',
    'ConstraintDiscoveryError',
    'FluencyGenerationError',
    # Validators
    'validate_identity_hash',
    'validate_symbol',
    'validate_transition',
    # Utils
    'calculate_entropy',
    'calculate_percentile',
    'normalize_vector',
    'calculate_similarity',
]
