"""
Constraint Discovery Engine

Enterprise-grade constraint and template discovery from role patterns.

CORRECTED: Global forbidden comparison, prefix-match templates.
"""

import logging
import json
from typing import Dict, Any, Optional, List, Tuple, Set

from threshold_onset.semantic.common.types import (
    RoleMap,
    ConstraintMap
)
from threshold_onset.semantic.common.exceptions import ConstraintDiscoveryError
from threshold_onset.semantic.phase8.sequences import extract_role_sequences
from threshold_onset.semantic.phase8.pattern_miner import (
    discover_role_patterns,
    discover_forbidden_patterns,
    build_templates,
    compute_prefix_match_score
)

logger = logging.getLogger('threshold_onset.semantic.phase8')


class ConstraintDiscoveryEngine:
    """
    Constraint Discovery Engine
    
    Discovers constraints and templates from role patterns.
    All corrections applied:
    - Global forbidden pattern comparison
    - Prefix-match template scoring
    - Discovered patterns (not imported)
    """
    
    def __init__(
        self,
        roles: RoleMap,
        symbol_sequences: List[List[int]],
        edge_deltas: Dict[Tuple[str, str], Dict[str, float]],
        continuation_observer: Optional[Any] = None,
        identity_to_symbol: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize constraint discovery engine.
        
        Args:
            roles: RoleMap from Phase 7
            symbol_sequences: List of symbol sequences
            edge_deltas: Edge deltas from Phase 5
            continuation_observer: Optional ContinuationObserver (for forbidden patterns)
            identity_to_symbol: Optional identity hash to symbol mapping
            config: Optional configuration overrides
        """
        self.roles = roles
        self.symbol_sequences = symbol_sequences
        self.edge_deltas = edge_deltas
        self.continuation_observer = continuation_observer
        self.identity_to_symbol = identity_to_symbol or {}
        self.config = config or {}
        
        phase8_config = self.config.get('phase8', {})
        self.min_frequency = phase8_config.get('min_frequency', 3)
        self.max_pattern_length = phase8_config.get('max_pattern_length', 4)
        
        # Cache
        self._constraint_map_cache: Optional[ConstraintMap] = None
        
        logger.info(
            f"ConstraintDiscoveryEngine initialized: "
            f"min_frequency={self.min_frequency}, "
            f"max_pattern_length={self.max_pattern_length}"
        )
    
    def discover(
        self,
        min_frequency: Optional[int] = None
    ) -> ConstraintMap:
        """
        Discover constraints and templates.
        
        CORRECTED: Global forbidden comparison, prefix-match templates.
        
        Args:
            min_frequency: Minimum pattern frequency (overrides config)
            
        Returns:
            ConstraintMap object
            
        Raises:
            ConstraintDiscoveryError: If discovery fails
        """
        if min_frequency is not None:
            self.min_frequency = min_frequency
        
        if self._constraint_map_cache is not None:
            logger.info("Returning cached constraint map")
            return self._constraint_map_cache
        
        logger.info("Starting constraint discovery")
        
        try:
            # Step 1: Extract role sequences
            symbol_to_role = self.roles.get('symbol_to_role', {})
            role_sequences = extract_role_sequences(
                self.symbol_sequences,
                symbol_to_role
            )
            
            if not role_sequences:
                raise ConstraintDiscoveryError("No role sequences extracted")
            
            # Step 2: Discover role patterns
            role_patterns = discover_role_patterns(
                role_sequences,
                min_frequency=self.min_frequency,
                max_pattern_length=self.max_pattern_length
            )
            
            if not role_patterns:
                logger.warning("No role patterns discovered")
                role_patterns = {}
            
            # Step 3: Discover forbidden patterns (CORRECTED: global comparison)
            forbidden_patterns = set()
            if self.continuation_observer is not None:
                forbidden_patterns = discover_forbidden_patterns(
                    role_patterns,
                    self.edge_deltas,
                    symbol_to_role,
                    self.identity_to_symbol,
                    self.continuation_observer
                )
            
            # Step 4: Build templates
            templates = build_templates(role_patterns, forbidden_patterns)
            
            constraint_map: ConstraintMap = {
                'role_patterns': role_patterns,
                'forbidden_patterns': forbidden_patterns,
                'templates': templates
            }
            
            self._constraint_map_cache = constraint_map
            
            logger.info(
                f"Constraint discovery complete: "
                f"{len(role_patterns)} patterns, "
                f"{len(forbidden_patterns)} forbidden, "
                f"{len(templates)} templates"
            )
            
            return constraint_map
            
        except Exception as e:
            logger.error(f"Constraint discovery failed: {e}")
            raise ConstraintDiscoveryError(
                f"Failed to discover constraints: {e}",
                details={'error': str(e)}
            ) from e
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """
        Get discovered templates.
        
        Returns:
            List of template dictionaries
        """
        if self._constraint_map_cache is None:
            return []
        
        return self._constraint_map_cache.get('templates', [])
    
    def is_forbidden(self, role_pattern: Tuple[str, ...]) -> bool:
        """
        Check if role pattern is forbidden.
        
        Args:
            role_pattern: Role pattern tuple
            
        Returns:
            True if forbidden, False otherwise
        """
        if self._constraint_map_cache is None:
            return False
        
        return role_pattern in self._constraint_map_cache.get('forbidden_patterns', set())
    
    def compute_template_score(
        self,
        current_role_sequence: List[str],
        window: int = 5
    ) -> float:
        """
        Compute template satisfaction score using prefix matching.
        
        CORRECTED: Prefix-match scoring guides continuation.
        
        Args:
            current_role_sequence: Current role sequence
            window: Window size for matching
            
        Returns:
            Template score [0.0, 1.0]
        """
        if self._constraint_map_cache is None:
            return 0.0
        
        templates = self.get_templates()
        if not templates:
            return 0.0
        
        # Compute prefix-match score for each template
        scores = []
        for template in templates:
            pattern = template['pattern']
            score = compute_prefix_match_score(
                current_role_sequence,
                pattern,
                window
            )
            if score > 0:
                # Weight by frequency
                weighted_score = score * (template['frequency'] / 100.0)
                scores.append(weighted_score)
        
        if not scores:
            return 0.0
        
        # Return maximum score (best matching template)
        return max(scores)
    
    def save(self, filepath: str) -> None:
        """
        Save constraint map to JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        if self._constraint_map_cache is None:
            raise ConstraintDiscoveryError("No constraint map discovered yet")
        
        # Convert to JSON-serializable format
        data = {
            'role_patterns': {
                ','.join(p): v for p, v in self._constraint_map_cache['role_patterns'].items()
            },
            'forbidden_patterns': [
                list(p) for p in self._constraint_map_cache['forbidden_patterns']
            ],
            'templates': self._constraint_map_cache['templates']
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Constraint map saved to {filepath}")
