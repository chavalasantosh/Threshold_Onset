"""
Consequence Field Engine

Enterprise-grade consequence field computation with all corrections applied.

Implements:
- Multiple probe policies
- Observer-based refusal checking
- Empirical entropy from rollout counts
- Counterfactual edge deltas
- Near-refusal tracking from rollout logs
"""

import logging
import json
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from threshold_onset.semantic.common.types import (
    ConsequenceVector,
    ConsequenceDelta,
    ConsequenceField
)
from threshold_onset.semantic.common.exceptions import ConsequenceFieldError
from threshold_onset.semantic.common.validators import (
    validate_identity_hash,
    validate_k,
    validate_num_rollouts
)
from threshold_onset.semantic.common.utils import mean
from threshold_onset.semantic.config.defaults import (
    DEFAULT_K,
    DEFAULT_NUM_ROLLOUTS,
    DEFAULT_MAX_STEPS
)
from threshold_onset.semantic.phase5.rollout import (
    rollout_from_identity,
    rollout_from_identity_forced_first
)
from threshold_onset.semantic.phase5.metrics import (
    compute_k_reach,
    get_escape_concentration,
    compute_near_refusal_rate_from_rollouts
)

logger = logging.getLogger('threshold_onset.semantic.phase5')


class ConsequenceFieldEngine:
    """
    Consequence Field Engine
    
    Computes consequence vectors for all identities using multiple probe policies.
    All corrections applied:
    - Multiple policies (not just greedy)
    - Observer-based refusal
    - Empirical entropy
    - Counterfactual edge deltas
    - Near-refusal from logs
    """
    
    def __init__(
        self,
        phase2_identities: Dict[str, Any],
        phase3_relations: Dict[str, Any],
        phase4_symbols: Dict[str, Any],
        continuation_observer: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize consequence field engine.
        
        Args:
            phase2_identities: Phase 2 identity metrics
            phase3_relations: Phase 3 relation metrics
            phase4_symbols: Phase 4 symbol mappings
            continuation_observer: Optional ContinuationObserver instance
            config: Optional configuration overrides
        """
        self.phase2_identities = phase2_identities
        self.phase3_relations = phase3_relations
        self.phase4_symbols = phase4_symbols
        self.continuation_observer = continuation_observer
        self.config = config or {}
        
        # Get config values
        phase5_config = self.config.get('phase5', {})
        self.k = phase5_config.get('k', DEFAULT_K)
        self.num_rollouts = phase5_config.get('num_rollouts', DEFAULT_NUM_ROLLOUTS)
        self.max_steps = phase5_config.get('max_steps', DEFAULT_MAX_STEPS)
        
        # Validate config
        validate_k(self.k)
        validate_num_rollouts(self.num_rollouts)
        
        # Policies to use (CORRECTED: multiple policies)
        self.policies = ['greedy', 'stochastic_topk', 'novelty']
        
        # Cache for computed vectors
        self._identity_vectors_cache: Dict[str, ConsequenceVector] = {}
        self._edge_deltas_cache: Dict[Tuple[str, str], ConsequenceDelta] = {}
        
        # Topology data (optional, for pressure-minimizing policy)
        self.topology_data: Optional[Dict[int, Dict[str, Any]]] = None
        
        logger.info(
            f"ConsequenceFieldEngine initialized: k={self.k}, "
            f"rollouts={self.num_rollouts}, policies={self.policies}"
        )
    
    def set_topology_data(self, topology_data: Dict[int, Dict[str, Any]]) -> None:
        """
        Set topology data for pressure-minimizing policy.
        
        Args:
            topology_data: Topology data dict (symbol -> topology info)
        """
        self.topology_data = topology_data
        if self.topology_data:
            self.policies.append('pressure_min')
            logger.info("Topology data set, pressure_min policy enabled")
    
    def build(
        self,
        k: Optional[int] = None,
        num_rollouts: Optional[int] = None,
        seed: Optional[int] = None
    ) -> ConsequenceField:
        """
        Build complete consequence field.
        
        CORRECTED: Uses multiple policies, empirical entropy, observer-based refusal.
        
        Args:
            k: k-step reachability horizon (overrides config)
            num_rollouts: Number of rollouts per identity (overrides config)
            seed: Random seed for determinism
            
        Returns:
            ConsequenceField object
            
        Raises:
            ConsequenceFieldError: If build fails
        """
        if k is not None:
            validate_k(k)
            self.k = k
        if num_rollouts is not None:
            validate_num_rollouts(num_rollouts)
            self.num_rollouts = num_rollouts
        
        logger.info(
            f"Building consequence field: k={self.k}, "
            f"rollouts={self.num_rollouts}, seed={seed}"
        )
        
        if self.continuation_observer is None:
            raise ConsequenceFieldError(
                "continuation_observer is required for building consequence field"
            )
        
        # Get all identity hashes
        identity_hashes = list(self.phase4_symbols.get('identity_to_symbol', {}).keys())
        
        if not identity_hashes:
            raise ConsequenceFieldError("No identities found in phase4_symbols")
        
        logger.info(f"Computing consequence vectors for {len(identity_hashes)} identities")
        
        # Compute vectors for all identities
        identity_vectors = {}
        for i, identity_hash in enumerate(identity_hashes):
            try:
                vector = self.compute_consequence_vector(
                    identity_hash, seed=seed
                )
                identity_vectors[identity_hash] = vector
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Computed {i + 1}/{len(identity_hashes)} vectors")
            except Exception as e:
                logger.error(f"Failed to compute vector for {identity_hash}: {e}")
                raise ConsequenceFieldError(
                    f"Failed to compute vector for {identity_hash}: {e}",
                    details={'identity_hash': identity_hash}
                ) from e
        
        logger.info("Computing edge deltas")
        
        # Compute edge deltas (counterfactual)
        edge_deltas = {}
        
        if self.continuation_observer is None or not hasattr(self.continuation_observer, 'adjacency') or self.continuation_observer.adjacency is None:
            logger.warning("No continuation observer or adjacency data, skipping edge deltas")
        else:
            # Count total edges
            total_edges = 0
            for source_hash in identity_hashes:
                outgoing = self.continuation_observer.adjacency.get(source_hash, set())
                total_edges += len(outgoing)
            
            computed_edges = 0
            for source_hash in identity_hashes:
                outgoing = self.continuation_observer.adjacency.get(source_hash, set())
                for target_hash in outgoing:
                    try:
                        delta = self.compute_counterfactual_edge_delta(
                            source_hash, target_hash, seed=seed
                        )
                        edge_deltas[(source_hash, target_hash)] = delta
                        computed_edges += 1
                        
                        if computed_edges % 50 == 0:
                            logger.info(f"Computed {computed_edges}/{total_edges} edge deltas")
                    except Exception as e:
                        logger.warning(
                            f"Failed to compute delta for ({source_hash}, {target_hash}): {e}"
                        )
                        # Continue with other edges
        
        metadata = {
            'k': self.k,
            'num_rollouts': self.num_rollouts,
            'max_steps': self.max_steps,
            'policies': self.policies,
            'num_identities': len(identity_hashes),
            'num_edges': total_edges,
            'seed': seed
        }
        
        consequence_field = ConsequenceField(
            identity_vectors=identity_vectors,
            edge_deltas=edge_deltas,
            metadata=metadata
        )
        
        logger.info("Consequence field build complete")
        return consequence_field
    
    def compute_consequence_vector(
        self,
        identity_hash: str,
        seed: Optional[int] = None
    ) -> ConsequenceVector:
        """
        Compute consequence vector for identity using multiple probe policies.
        
        CORRECTED: Multi-policy, empirical entropy, observer-based refusal.
        
        Args:
            identity_hash: Identity hash
            seed: Random seed
            
        Returns:
            ConsequenceVector
        """
        validate_identity_hash(identity_hash)
        
        # Check cache
        if identity_hash in self._identity_vectors_cache:
            return self._identity_vectors_cache[identity_hash]
        
        # Run rollouts for each policy
        all_results: Dict[str, List[Any]] = {}
        
        for policy in self.policies:
            results = []
            for i in range(self.num_rollouts):
                rollout_seed = seed + i if seed is not None else None
                
                try:
                    result = rollout_from_identity(
                        identity_hash,
                        self.phase3_relations,
                        self.phase4_symbols,
                        self.continuation_observer,
                        policy=policy,
                        max_steps=self.max_steps,
                        seed=rollout_seed,
                        topology_data=self.topology_data
                    )
                    results.append(result)
                except Exception as e:
                    logger.warning(
                        f"Rollout failed for {identity_hash} with policy {policy}: {e}"
                    )
                    # Continue with other rollouts
            
            all_results[policy] = results
        
        # Compute components (expectation over policies)
        if self.continuation_observer and hasattr(self.continuation_observer, 'adjacency') and self.continuation_observer.adjacency:
            out_degree = len(self.continuation_observer.adjacency.get(identity_hash, set()))
        else:
            out_degree = 0
        
        # k_reach: average across policies
        k_reaches = []
        for policy_results in all_results.values():
            for result in policy_results:
                # Compute k_reach from path
                from threshold_onset.semantic.phase5.metrics import compute_k_reach_from_path
                k_reach = compute_k_reach_from_path(result.path_taken, self.k)
                k_reaches.append(k_reach)
        k_reach = int(mean(k_reaches)) if k_reaches else 0
        
        # survival: average across policies
        survivals = []
        for policy_results in all_results.values():
            for result in policy_results:
                survivals.append(1.0 if not result.refusal_occurred else 0.0)
        survival = mean(survivals) if survivals else 0.0
        
        # entropy: empirical from transition counts (CORRECTED)
        from collections import Counter
        all_transitions = Counter()
        for policy_results in all_results.values():
            for result in policy_results:
                for i in range(len(result.path_taken) - 1):
                    transition = (result.path_taken[i], result.path_taken[i + 1])
                    all_transitions[transition] += 1
        
        # Compute entropy from identity's transitions
        from threshold_onset.semantic.common.utils import calculate_entropy_from_counts
        identity_transitions = [
            count for (src, tgt), count in all_transitions.items()
            if src == identity_hash
        ]
        if identity_transitions:
            entropy = calculate_entropy_from_counts(identity_transitions)
        else:
            from threshold_onset.semantic.common.utils import calculate_entropy_from_options
            entropy = calculate_entropy_from_options(out_degree)
        
        # escape_concentration: from topology (if available)
        symbol = self.phase4_symbols.get('identity_to_symbol', {}).get(identity_hash)
        escape_concentration = get_escape_concentration(symbol, self.topology_data)
        
        # near_refusal_rate: from rollout logs (CORRECTED)
        all_rollout_results = [
            r for results in all_results.values() for r in results
        ]
        near_refusal_rate = compute_near_refusal_rate_from_rollouts(
            identity_hash, all_rollout_results
        )
        
        # dead_end_risk: separate metric
        if self.continuation_observer and hasattr(self.continuation_observer, 'adjacency') and self.continuation_observer.adjacency:
            outgoing = self.continuation_observer.adjacency.get(identity_hash, set())
        else:
            outgoing = set()
        dead_end_count = 0
        for target in outgoing:
            if self.continuation_observer and hasattr(self.continuation_observer, 'adjacency') and self.continuation_observer.adjacency:
                target_outgoing = self.continuation_observer.adjacency.get(target, set())
            else:
                target_outgoing = set()
            if len(target_outgoing) == 0:
                dead_end_count += 1
        dead_end_risk = dead_end_count / max(out_degree, 1)
        
        vector = ConsequenceVector(
            out_degree=out_degree,
            k_reach=k_reach,
            survival=survival,
            entropy=entropy,
            escape_concentration=escape_concentration,
            near_refusal_rate=near_refusal_rate,
            dead_end_risk=dead_end_risk
        )
        
        # Cache
        self._identity_vectors_cache[identity_hash] = vector
        
        return vector
    
    def compute_counterfactual_edge_delta(
        self,
        source_hash: str,
        target_hash: str,
        seed: Optional[int] = None
    ) -> ConsequenceDelta:
        """
        Compute counterfactual edge delta: forced-first-step method.
        
        CORRECTED: Compares baseline vs conditioned distributions.
        
        Args:
            source_hash: Source identity hash
            target_hash: Target identity hash
            seed: Random seed
            
        Returns:
            ConsequenceDelta
        """
        validate_identity_hash(source_hash)
        validate_identity_hash(target_hash)
        
        # Check cache
        transition = (source_hash, target_hash)
        if transition in self._edge_deltas_cache:
            return self._edge_deltas_cache[transition]
        
        # Baseline: rollouts from source (normal policy)
        baseline_results = []
        for i in range(self.num_rollouts // 2):  # Use half for baseline
            rollout_seed = seed + i if seed is not None else None
            try:
                result = rollout_from_identity(
                    source_hash,
                    self.phase3_relations,
                    self.phase4_symbols,
                    self.continuation_observer,
                    policy='greedy',
                    max_steps=self.max_steps,
                    seed=rollout_seed
                )
                baseline_results.append(result)
            except Exception as e:
                logger.warning(f"Baseline rollout failed: {e}")
        
        # Conditioned: rollouts from source, but first step forced to target
        conditioned_results = []
        for i in range(self.num_rollouts // 2):  # Use half for conditioned
            rollout_seed = seed + 1000 + i if seed is not None else None
            try:
                result = rollout_from_identity_forced_first(
                    source_hash,
                    target_hash,
                    self.phase3_relations,
                    self.phase4_symbols,
                    self.continuation_observer,
                    policy='greedy',
                    max_steps=self.max_steps,
                    seed=rollout_seed
                )
                conditioned_results.append(result)
            except Exception as e:
                logger.warning(f"Conditioned rollout failed: {e}")
        
        # Compute deltas
        baseline_survival = mean([
            1.0 if not r.refusal_occurred else 0.0
            for r in baseline_results
        ]) if baseline_results else 0.0
        
        conditioned_survival = mean([
            1.0 if not r.refusal_occurred else 0.0
            for r in conditioned_results
        ]) if conditioned_results else 0.0
        
        survival_delta = conditioned_survival - baseline_survival
        
        # k_reach delta
        from threshold_onset.semantic.phase5.metrics import compute_k_reach_from_path
        baseline_k_reaches = [
            compute_k_reach_from_path(r.path_taken, self.k)
            for r in baseline_results
        ]
        conditioned_k_reaches = [
            compute_k_reach_from_path(r.path_taken, self.k)
            for r in conditioned_results
        ]
        
        baseline_k_reach = mean(baseline_k_reaches) if baseline_k_reaches else 0
        conditioned_k_reach = mean(conditioned_k_reaches) if conditioned_k_reaches else 0
        k_reach_delta = int(conditioned_k_reach - baseline_k_reach)
        
        # Entropy delta
        baseline_entropies = [
            r.entropy_trajectory[-1] if r.entropy_trajectory else 0.0
            for r in baseline_results
        ]
        conditioned_entropies = [
            r.entropy_trajectory[-1] if r.entropy_trajectory else 0.0
            for r in conditioned_results
        ]
        
        baseline_entropy = mean(baseline_entropies) if baseline_entropies else 0.0
        conditioned_entropy = mean(conditioned_entropies) if conditioned_entropies else 0.0
        entropy_delta = conditioned_entropy - baseline_entropy
        
        # Refusal delta
        baseline_refusal = compute_near_refusal_rate_from_rollouts(
            source_hash, baseline_results
        )
        conditioned_refusal = compute_near_refusal_rate_from_rollouts(
            source_hash, conditioned_results
        )
        refusal_delta = conditioned_refusal - baseline_refusal
        
        delta = ConsequenceDelta(
            survival_delta=survival_delta,
            k_reach_delta=k_reach_delta,
            entropy_delta=entropy_delta,
            refusal_delta=refusal_delta
        )
        
        # Cache
        self._edge_deltas_cache[transition] = delta
        
        return delta
    
    def get_vector(self, identity_hash: str) -> ConsequenceVector:
        """
        Get consequence vector for identity.
        
        Args:
            identity_hash: Identity hash
            
        Returns:
            ConsequenceVector
            
        Raises:
            KeyError: If identity_hash not found
        """
        if identity_hash not in self._identity_vectors_cache:
            raise KeyError(f"Consequence vector not computed for {identity_hash}")
        
        return self._identity_vectors_cache[identity_hash]
    
    def get_delta(self, transition: Tuple[str, str]) -> ConsequenceDelta:
        """
        Get counterfactual delta for transition.
        
        Args:
            transition: (source_hash, target_hash) tuple
            
        Returns:
            ConsequenceDelta
            
        Raises:
            KeyError: If transition not found
        """
        if transition not in self._edge_deltas_cache:
            raise KeyError(f"Edge delta not computed for {transition}")
        
        return self._edge_deltas_cache[transition]
    
    def save(self, filepath: str) -> None:
        """
        Save consequence field to JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        if not self._identity_vectors_cache:
            raise ConsequenceFieldError("No consequence field built yet")
        
        # Convert to JSON-serializable format
        data = {
            'identity_vectors': {
                k: dict(v) for k, v in self._identity_vectors_cache.items()
            },
            'edge_deltas': {
                f"{k[0]}:{k[1]}": dict(v)
                for k, v in self._edge_deltas_cache.items()
            },
            'metadata': {
                'k': self.k,
                'num_rollouts': self.num_rollouts,
                'max_steps': self.max_steps,
                'policies': self.policies
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Consequence field saved to {filepath}")
