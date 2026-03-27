"""
Input validation utilities.

Enterprise-grade validation with clear error messages.
"""

import re
from typing import Tuple
from threshold_onset.semantic.common.exceptions import (
    ConsequenceFieldError,
    FluencyGenerationError
)


def validate_identity_hash(identity_hash: str) -> None:
    """
    Validate identity hash format.
    
    Accepts any non-empty string as valid identity hash.
    (Phase 2 identities may use various formats)
    
    Args:
        identity_hash: Identity hash string
        
    Raises:
        TypeError: If not a string
        ValueError: If empty
    """
    if not isinstance(identity_hash, str):
        raise TypeError(f"identity_hash must be string, got {type(identity_hash)}")
    
    if not identity_hash:
        raise ValueError("identity_hash cannot be empty")


def validate_symbol(symbol: int) -> None:
    """
    Validate symbol ID.
    
    Args:
        symbol: Symbol ID integer
        
    Raises:
        TypeError: If not an integer
        ValueError: If negative
    """
    if not isinstance(symbol, int):
        raise TypeError(f"symbol must be integer, got {type(symbol)}")
    
    if symbol < 0:
        raise ValueError(f"symbol must be non-negative, got {symbol}")


def validate_transition(transition: Tuple[str, str]) -> None:
    """
    Validate transition tuple.
    
    Args:
        transition: (source_hash, target_hash) tuple
        
    Raises:
        TypeError: If not a tuple or wrong types
        ValueError: If invalid format
    """
    if not isinstance(transition, tuple):
        raise TypeError(f"transition must be tuple, got {type(transition)}")
    
    if len(transition) != 2:
        raise ValueError(f"transition must have 2 elements, got {len(transition)}")
    
    source, target = transition
    
    if not isinstance(source, str) or not isinstance(target, str):
        raise TypeError(
            f"transition elements must be strings, "
            f"got {type(source)} and {type(target)}"
        )
    
    validate_identity_hash(source)
    validate_identity_hash(target)


def validate_k(k: int) -> None:
    """
    Validate k-step horizon parameter.
    
    Args:
        k: k-step horizon
        
    Raises:
        TypeError: If not an integer
        ValueError: If out of valid range
    """
    if not isinstance(k, int):
        raise TypeError(f"k must be integer, got {type(k)}")
    
    if k < 1 or k > 20:
        raise ValueError(f"k must be in range [1, 20], got {k}")


def validate_num_rollouts(num_rollouts: int) -> None:
    """
    Validate number of rollouts parameter.
    
    Args:
        num_rollouts: Number of rollouts
        
    Raises:
        TypeError: If not an integer
        ValueError: If out of valid range
    """
    if not isinstance(num_rollouts, int):
        raise TypeError(f"num_rollouts must be integer, got {type(num_rollouts)}")
    
    if num_rollouts < 1 or num_rollouts > 10000:
        raise ValueError(
            f"num_rollouts must be in range [1, 10000], got {num_rollouts}"
        )
