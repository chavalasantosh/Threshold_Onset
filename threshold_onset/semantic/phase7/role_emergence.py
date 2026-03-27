"""
Role Emergence Engine

Enterprise-grade functional role discovery from meaning clusters.

CORRECTED: Quantile-based assignment, binder derived from topology.
"""

import logging
import json
from typing import Dict, Any, Optional

from threshold_onset.semantic.common.types import (
    MeaningMap,
    RoleMap
)
from threshold_onset.semantic.common.exceptions import RoleEmergenceError
from threshold_onset.semantic.phase7.role_assigner import assign_roles_from_properties

logger = logging.getLogger('threshold_onset.semantic.phase7')


class RoleEmergenceEngine:
    """
    Role Emergence Engine
    
    Emerges functional roles from meaning clusters using quantile-based assignment.
    All corrections applied:
    - Quantile-based thresholds (not hand-chosen)
    - Binder derived from topology (not default)
    - Unclassified role (not default binder)
    """
    
    def __init__(
        self,
        meaning_map: MeaningMap,
        consequence_field: Any,  # ConsequenceField
        continuation_observer: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize role emergence engine.
        
        Args:
            meaning_map: MeaningMap from Phase 6
            consequence_field: ConsequenceField from Phase 5
            continuation_observer: Optional ContinuationObserver (for binder computation)
            config: Optional configuration overrides
        """
        self.meaning_map = meaning_map
        self.consequence_field = consequence_field
        self.continuation_observer = continuation_observer
        self.config = config or {}
        
        phase7_config = self.config.get('phase7', {})
        self.percentile_high = phase7_config.get('percentile_high', 75)
        self.percentile_low = phase7_config.get('percentile_low', 25)
        
        # Cache
        self._role_map_cache: Optional[RoleMap] = None
        
        logger.info(
            f"RoleEmergenceEngine initialized: "
            f"percentiles=({self.percentile_low}, {self.percentile_high})"
        )
    
    def emerge(self) -> RoleMap:
        """
        Emerge functional roles from meaning clusters.
        
        CORRECTED: Uses quantiles, derives binder from topology.
        
        Returns:
            RoleMap object
            
        Raises:
            RoleEmergenceError: If emergence fails
        """
        if self._role_map_cache is not None:
            logger.info("Returning cached role map")
            return self._role_map_cache
        
        logger.info("Starting role emergence")
        
        try:
            # Get clusters and identity vectors
            # Handle both MeaningSignature objects and dicts
            clusters = {}
            for cluster_id, sig in self.meaning_map.clusters.items():
                if hasattr(sig, 'identities'):
                    clusters[cluster_id] = sig.identities
                elif isinstance(sig, dict):
                    clusters[cluster_id] = sig.get('identities', [])
                else:
                    clusters[cluster_id] = []
            identity_vectors = self.consequence_field.identity_vectors
            
            if not clusters:
                raise RoleEmergenceError("No clusters found in meaning map")
            
            # Assign roles from properties.
            # assign_roles_from_properties now returns (roles, cluster_properties)
            # so we reuse the already-computed properties instead of calling
            # compute_cluster_properties a second time.
            cluster_roles, cluster_properties = assign_roles_from_properties(
                clusters,
                identity_vectors,
                continuation_observer=self.continuation_observer,
                edge_deltas=self.consequence_field.edge_deltas,
                percentile_high=self.percentile_high,
                percentile_low=self.percentile_low
            )

            # Map identities to roles
            symbol_to_role = {}
            identity_to_symbol = self.consequence_field.metadata.get(
                'identity_to_symbol', {}
            )

            for cluster_id, role in cluster_roles.items():
                cluster_identities = clusters.get(cluster_id, [])
                for identity_hash in cluster_identities:
                    symbol = identity_to_symbol.get(identity_hash)
                    if symbol is not None:
                        symbol_to_role[symbol] = role
                    symbol_to_role[identity_hash] = role

            # Reuse cluster_properties already computed inside assign_roles_from_properties
            role_properties = {
                role: cluster_properties.get(cluster_id, {})
                for cluster_id, role in cluster_roles.items()
            }
            
            # RoleMap is TypedDict, so use dict literal
            role_map: RoleMap = {
                'symbol_to_role': symbol_to_role,
                'cluster_roles': cluster_roles,
                'role_properties': role_properties
            }
            
            self._role_map_cache = role_map
            
            logger.info(f"Role emergence complete: {len(cluster_roles)} roles assigned")
            return role_map
            
        except Exception as e:
            logger.error(f"Role emergence failed: {e}")
            raise RoleEmergenceError(
                f"Failed to emerge roles: {e}",
                details={'error': str(e)}
            ) from e
    
    def get_role(self, symbol: Any) -> Optional[str]:
        """
        Get role for symbol or identity hash.
        
        Args:
            symbol: Symbol ID or identity hash
            
        Returns:
            Role name, or None if not found
        """
        if self._role_map_cache is None:
            return None
        
        return self._role_map_cache.get('symbol_to_role', {}).get(symbol)
    
    def get_role_properties(self, role: str) -> Optional[Dict[str, float]]:
        """
        Get properties for role.
        
        Args:
            role: Role name
            
        Returns:
            Role properties, or None if not found
        """
        if self._role_map_cache is None:
            return None
        
        return self._role_map_cache.get('role_properties', {}).get(role)
    
    def save(self, filepath: str) -> None:
        """
        Save role map to JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        if self._role_map_cache is None:
            raise RoleEmergenceError("No role map emerged yet")
        
        # Convert to JSON-serializable format
        data = {
            'symbol_to_role': {
                str(k): v for k, v in self._role_map_cache.get('symbol_to_role', {}).items()
            },
            'cluster_roles': self._role_map_cache.get('cluster_roles', {}),
            'role_properties': self._role_map_cache.get('role_properties', {})
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Role map saved to {filepath}")
