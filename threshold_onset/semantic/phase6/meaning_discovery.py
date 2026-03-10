"""
Meaning Discovery Engine

Enterprise-grade meaning discovery through consequence vector clustering.

CORRECTED: Stability-based cluster selection, not hand-chosen.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from threshold_onset.semantic.common.types import (
    ConsequenceField,
    MeaningMap,
    MeaningSignature
)
from threshold_onset.semantic.common.exceptions import MeaningDiscoveryError
from threshold_onset.semantic.common.utils import mean
from threshold_onset.semantic.phase6.normalization import normalize_vectors
from threshold_onset.semantic.phase6.clustering import cluster_consequence_vectors

logger = logging.getLogger('threshold_onset.semantic.phase6')


class MeaningDiscoveryEngine:
    """
    Meaning Discovery Engine
    
    Discovers meaning clusters from consequence vectors using k-medoids clustering.
    All corrections applied:
    - Stability-based cluster selection
    - Deterministic clustering
    - Meaning signature extraction
    """
    
    def __init__(
        self,
        consequence_field: ConsequenceField,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize meaning discovery engine.
        
        Args:
            consequence_field: ConsequenceField from Phase 5
            config: Optional configuration overrides
        """
        self.consequence_field = consequence_field
        self.config = config or {}
        
        phase6_config = self.config.get('phase6', {})
        self.num_clusters = phase6_config.get('num_clusters', None)
        self.similarity_threshold = phase6_config.get('similarity_threshold', 0.7)
        
        # Cache
        self._meaning_map_cache: Optional[MeaningMap] = None
        
        logger.info(
            f"MeaningDiscoveryEngine initialized: "
            f"num_clusters={self.num_clusters or 'auto'}"
        )
    
    def discover(
        self,
        num_clusters: Optional[int] = None,
        seed: Optional[int] = None
    ) -> MeaningMap:
        """
        Discover meaning clusters from consequence vectors.
        
        CORRECTED: Uses stability-based cluster selection if num_clusters not specified.
        
        Args:
            num_clusters: Number of clusters (None = auto-select by stability)
            seed: Random seed for determinism
            
        Returns:
            MeaningMap object
            
        Raises:
            MeaningDiscoveryError: If discovery fails
        """
        if num_clusters is not None:
            self.num_clusters = num_clusters
        
        if self._meaning_map_cache is not None:
            logger.info("Returning cached meaning map")
            return self._meaning_map_cache
        
        logger.info("Starting meaning discovery")
        
        try:
            # Step 1: Normalize vectors
            normalized_vectors, ranges = normalize_vectors(
                self.consequence_field.identity_vectors
            )
            
            if not normalized_vectors:
                raise MeaningDiscoveryError("No vectors to cluster")
            
            # Step 2: Cluster vectors
            clusters = cluster_consequence_vectors(
                normalized_vectors,
                num_clusters=self.num_clusters,
                seed=seed
            )
            
            if not clusters:
                raise MeaningDiscoveryError("Clustering produced no clusters")
            
            logger.info(f"Discovered {len(clusters)} meaning clusters")
            
            # Step 3: Extract meaning signatures
            signatures = self._extract_meaning_signatures(
                clusters, normalized_vectors, ranges
            )
            
            # Step 4: Build identity-to-cluster mapping
            identity_to_cluster = {}
            for cluster_id, identity_hashes in clusters.items():
                for identity_hash in identity_hashes:
                    identity_to_cluster[identity_hash] = cluster_id
            
            metadata = {
                'num_clusters': len(clusters),
                'num_identities': len(identity_to_cluster),
                'normalization_ranges': ranges,
                'seed': seed
            }
            
            meaning_map = MeaningMap(
                clusters=signatures,
                identity_to_cluster=identity_to_cluster,
                metadata=metadata
            )
            
            self._meaning_map_cache = meaning_map
            
            logger.info("Meaning discovery complete")
            return meaning_map
            
        except Exception as e:
            logger.error(f"Meaning discovery failed: {e}")
            raise MeaningDiscoveryError(
                f"Failed to discover meaning clusters: {e}",
                details={'error': str(e)}
            ) from e
    
    def _extract_meaning_signatures(
        self,
        clusters: Dict[str, List[str]],
        normalized_vectors: Dict[str, Dict[str, float]],
        ranges: Dict[str, Dict[str, float]]
    ) -> Dict[str, MeaningSignature]:
        """
        Extract meaning signatures from clusters.
        
        Signature = centroid (average) of cluster vectors, denormalized.
        
        Args:
            clusters: Dictionary mapping cluster_id -> list of identity_hashes
            normalized_vectors: Normalized vectors
            ranges: Normalization ranges (for denormalization)
            
        Returns:
            Dictionary mapping cluster_id -> MeaningSignature
        """
        signatures = {}
        
        for cluster_id, identity_hashes in clusters.items():
            if not identity_hashes:
                continue
            
            # Get cluster vectors
            cluster_vectors = [
                normalized_vectors[h] for h in identity_hashes
                if h in normalized_vectors
            ]
            
            if not cluster_vectors:
                continue
            
            # Compute centroid (average of normalized vectors)
            centroid_normalized = {}
            for key in cluster_vectors[0].keys():
                centroid_normalized[key] = mean([
                    v[key] for v in cluster_vectors
                ])
            
            # Denormalize centroid
            centroid = {}
            for key, value in centroid_normalized.items():
                if key in ranges:
                    min_val = ranges[key]['min']
                    max_val = ranges[key]['max']
                    if max_val > min_val:
                        centroid[key] = min_val + value * (max_val - min_val)
                    else:
                        centroid[key] = min_val
                else:
                    centroid[key] = value
            
            signatures[cluster_id] = MeaningSignature(
                centroid=centroid,
                size=len(identity_hashes),
                identities=identity_hashes
            )
        
        return signatures
    
    def get_cluster(self, identity_hash: str) -> Optional[str]:
        """
        Get cluster ID for identity.
        
        Args:
            identity_hash: Identity hash
            
        Returns:
            Cluster ID, or None if not found
        """
        if self._meaning_map_cache is None:
            return None
        
        return self._meaning_map_cache.identity_to_cluster.get(identity_hash)
    
    def get_signature(self, cluster_id: str) -> Optional[MeaningSignature]:
        """
        Get meaning signature for cluster.
        
        Args:
            cluster_id: Cluster ID
            
        Returns:
            MeaningSignature, or None if not found
        """
        if self._meaning_map_cache is None:
            return None
        
        return self._meaning_map_cache.clusters.get(cluster_id)
    
    def save(self, filepath: str) -> None:
        """
        Save meaning map to JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        if self._meaning_map_cache is None:
            raise MeaningDiscoveryError("No meaning map discovered yet")
        
        # Convert to JSON-serializable format
        # MeaningSignature is a TypedDict, access as dict
        data = {
            'clusters': {
                cluster_id: {
                    'centroid': dict(sig.get('centroid', {})),
                    'size': sig.get('size', 0),
                    'identities': sig.get('identities', [])
                }
                for cluster_id, sig in self._meaning_map_cache.clusters.items()
            },
            'identity_to_cluster': self._meaning_map_cache.identity_to_cluster,
            'metadata': self._meaning_map_cache.metadata
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Meaning map saved to {filepath}")
