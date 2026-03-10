"""
Cluster Property Computation

Enterprise-grade property computation for role assignment.

Computes properties of clusters to determine functional roles.
"""

import logging
from typing import Dict, List, Any

from threshold_onset.semantic.common.utils import mean
from threshold_onset.semantic.common.types import ConsequenceVector

logger = logging.getLogger('threshold_onset.semantic.phase7')


def compute_cluster_properties(
    cluster_identities: List[str],
    identity_vectors: Dict[str, ConsequenceVector]
) -> Dict[str, float]:
    """
    Compute properties of cluster to determine role.
    
    Properties:
    - avg_survival: Average survival probability
    - avg_entropy: Average entropy
    - avg_concentration: Average escape concentration
    - avg_refusal_rate: Average near-refusal rate
    - avg_k_reach: Average k-reach
    - avg_out_degree: Average out-degree
    
    Args:
        cluster_identities: List of identity hashes in cluster
        identity_vectors: Dictionary mapping identity_hash -> ConsequenceVector
        
    Returns:
        Dictionary of property name -> average value
    """
    if not cluster_identities:
        return {}
    
    cluster_vectors = [
        identity_vectors[h] for h in cluster_identities
        if h in identity_vectors
    ]
    
    if not cluster_vectors:
        return {}
    
    properties = {
        'avg_survival': mean([v['survival'] for v in cluster_vectors]),
        'avg_entropy': mean([v['entropy'] for v in cluster_vectors]),
        'avg_concentration': mean([v['escape_concentration'] for v in cluster_vectors]),
        'avg_refusal_rate': mean([v['near_refusal_rate'] for v in cluster_vectors]),
        'avg_k_reach': mean([float(v['k_reach']) for v in cluster_vectors]),
        'avg_out_degree': mean([float(v['out_degree']) for v in cluster_vectors])
    }
    
    return properties
