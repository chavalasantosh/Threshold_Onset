"""
Role Sequence Extraction

Enterprise-grade role sequence extraction from symbol sequences.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger('threshold_onset.semantic.phase8')


def extract_role_sequences(
    symbol_sequences: List[List[int]],
    symbol_to_role: Dict[Any, str]
) -> List[List[str]]:
    """
    Convert symbol sequences to role sequences.
    
    No grammar rules. Just role sequences.
    
    Args:
        symbol_sequences: List of symbol sequences
        symbol_to_role: Dictionary mapping symbol -> role
        
    Returns:
        List of role sequences
    """
    role_sequences = []
    
    for symbol_seq in symbol_sequences:
        role_seq = [symbol_to_role.get(s, 'unclassified') for s in symbol_seq]
        role_sequences.append(role_seq)
    
    logger.info(f"Extracted {len(role_sequences)} role sequences")
    
    return role_sequences
