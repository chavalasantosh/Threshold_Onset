"""
Test Suite for Phase 5: Consequence Field Engine

Enterprise-grade tests with >80% coverage target.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, MagicMock
from collections import Counter

from threshold_onset.semantic.phase5.policies import (
    policy_greedy,
    policy_stochastic_topk,
    policy_novelty_seeking,
    get_policy
)
from threshold_onset.semantic.phase5.rollout import (
    rollout_from_identity,
    rollout_from_identity_forced_first
)
from threshold_onset.semantic.phase5.metrics import (
    compute_k_reach_from_path,
    compute_near_refusal_rate_from_rollouts
)
from threshold_onset.semantic.phase5.consequence_field import ConsequenceFieldEngine
from threshold_onset.semantic.common.types import RolloutResult
from threshold_onset.semantic.common.exceptions import ConsequenceFieldError


class TestPolicies(unittest.TestCase):
    """Test probe policies."""
    
    def setUp(self):
        """Set up test observer mock."""
        self.observer = Mock()
        self.observer.adjacency = {
            'identity_1': {'identity_2', 'identity_3'},
            'identity_2': {'identity_3', 'identity_4'},
            'identity_3': {'identity_4'},
            'identity_4': set()
        }
        self.observer._identity_hash_to_symbol = Mock(return_value=1)
    
    def test_policy_greedy(self):
        """Test greedy policy selects max continuation options."""
        result = policy_greedy('identity_1', self.observer)
        # identity_2 has 2 options, identity_3 has 1 option
        # Should select identity_2
        self.assertEqual(result, 'identity_2')
    
    def test_policy_greedy_no_allowed(self):
        """Test greedy policy returns None when no allowed transitions."""
        self.observer.adjacency = {'identity_1': set()}
        result = policy_greedy('identity_1', self.observer)
        self.assertIsNone(result)
    
    def test_policy_stochastic_topk(self):
        """Test stochastic top-k policy."""
        result = policy_stochastic_topk('identity_1', self.observer, k=2, seed=42)
        # Should return one of identity_2 or identity_3
        self.assertIn(result, ['identity_2', 'identity_3'])
    
    def test_policy_novelty_seeking(self):
        """Test novelty-seeking policy avoids recent path."""
        recent_path = ['identity_2']
        result = policy_novelty_seeking('identity_1', self.observer, recent_path)
        # Should avoid identity_2, select identity_3
        self.assertEqual(result, 'identity_3')
    
    def test_get_policy(self):
        """Test policy factory function."""
        policy = get_policy('greedy')
        self.assertEqual(policy, policy_greedy)
        
        with self.assertRaises(ValueError):
            get_policy('unknown_policy')


class TestRollout(unittest.TestCase):
    """Test rollout system."""
    
    def setUp(self):
        """Set up test observer."""
        self.observer = Mock()
        self.observer.adjacency = {
            'identity_1': {'identity_2', 'identity_3'},
            'identity_2': {'identity_3'},
            'identity_3': {'identity_2'}
        }
        self.observer._check_transition_allowed = Mock(return_value=True)
        self.observer._identity_hash_to_symbol = Mock(return_value=1)
        
        self.phase3_relations = {}
        self.phase4_symbols = {
            'identity_to_symbol': {
                'identity_1': 1,
                'identity_2': 2,
                'identity_3': 3
            }
        }
    
    def test_rollout_from_identity(self):
        """Test basic rollout."""
        result = rollout_from_identity(
            'identity_1',
            self.phase3_relations,
            self.phase4_symbols,
            self.observer,
            policy='greedy',
            max_steps=5,
            seed=42
        )
        
        self.assertIsInstance(result, RolloutResult)
        self.assertGreater(result.survival_length, 0)
        self.assertIsInstance(result.refusal_occurred, bool)
        self.assertIsInstance(result.entropy_trajectory, list)
    
    def test_rollout_with_refusal(self):
        """Test rollout with refusal."""
        # Make transition fail
        self.observer._check_transition_allowed = Mock(return_value=False)
        
        result = rollout_from_identity(
            'identity_1',
            self.phase3_relations,
            self.phase4_symbols,
            self.observer,
            policy='greedy',
            max_steps=5,
            seed=42
        )
        
        self.assertTrue(result.refusal_occurred)
        self.assertGreater(len(result.near_refusal_states), 0)
    
    def test_rollout_forced_first(self):
        """Test forced-first-step rollout."""
        result = rollout_from_identity_forced_first(
            'identity_1',
            'identity_2',
            self.phase3_relations,
            self.phase4_symbols,
            self.observer,
            policy='greedy',
            max_steps=5,
            seed=42
        )
        
        self.assertIsInstance(result, RolloutResult)
        # Path should start with identity_1 -> identity_2
        self.assertEqual(result.path_taken[0], 'identity_1')
        self.assertEqual(result.path_taken[1], 'identity_2')


class TestMetrics(unittest.TestCase):
    """Test metric computation."""
    
    def test_compute_k_reach_from_path(self):
        """Test k-reach computation from path."""
        path = ['id1', 'id2', 'id3', 'id4', 'id5']
        k_reach = compute_k_reach_from_path(path, k=2)
        # Should count unique identities within 2 steps
        self.assertGreater(k_reach, 0)
    
    def test_compute_near_refusal_rate(self):
        """Test near-refusal rate computation."""
        results = [
            RolloutResult(
                survival_length=5,
                refusal_occurred=False,
                pressure_accumulated=1.0,
                entropy_trajectory=[1.0, 1.5],
                path_taken=['id1', 'id2', 'id3'],
                near_refusal_states=['id1']
            ),
            RolloutResult(
                survival_length=3,
                refusal_occurred=True,
                pressure_accumulated=0.5,
                entropy_trajectory=[1.0],
                path_taken=['id1', 'id2'],
                near_refusal_states=['id1', 'id2']
            )
        ]
        
        rate = compute_near_refusal_rate_from_rollouts('id1', results)
        # id1 appears in both paths and in near-refusal states
        self.assertGreaterEqual(rate, 0.0)
        self.assertLessEqual(rate, 1.0)


class TestConsequenceFieldEngine(unittest.TestCase):
    """Test ConsequenceFieldEngine."""
    
    def setUp(self):
        """Set up test engine."""
        self.observer = Mock()
        self.observer.adjacency = {
            'identity_1': {'identity_2', 'identity_3'},
            'identity_2': {'identity_3'},
            'identity_3': {'identity_2'}
        }
        self.observer._check_transition_allowed = Mock(return_value=True)
        self.observer._identity_hash_to_symbol = Mock(return_value=1)
        
        self.phase2_identities = {}
        self.phase3_relations = {}
        self.phase4_symbols = {
            'identity_to_symbol': {
                'identity_1': 1,
                'identity_2': 2,
                'identity_3': 3
            },
            'symbol_to_identity': {
                1: 'identity_1',
                2: 'identity_2',
                3: 'identity_3'
            }
        }
        
        self.engine = ConsequenceFieldEngine(
            phase2_identities=self.phase2_identities,
            phase3_relations=self.phase3_relations,
            phase4_symbols=self.phase4_symbols,
            continuation_observer=self.observer
        )
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertEqual(self.engine.k, 5)  # Default
        self.assertEqual(self.engine.num_rollouts, 100)  # Default
        self.assertIn('greedy', self.engine.policies)
    
    def test_compute_consequence_vector(self):
        """Test consequence vector computation."""
        vector = self.engine.compute_consequence_vector('identity_1', seed=42)
        
        self.assertIn('out_degree', vector)
        self.assertIn('k_reach', vector)
        self.assertIn('survival', vector)
        self.assertIn('entropy', vector)
        self.assertIn('escape_concentration', vector)
        self.assertIn('near_refusal_rate', vector)
        self.assertIn('dead_end_risk', vector)
        
        # Check types
        self.assertIsInstance(vector['out_degree'], int)
        self.assertIsInstance(vector['k_reach'], int)
        self.assertIsInstance(vector['survival'], float)
        self.assertIsInstance(vector['entropy'], float)
        
        # Check ranges
        self.assertGreaterEqual(vector['survival'], 0.0)
        self.assertLessEqual(vector['survival'], 1.0)
        self.assertGreaterEqual(vector['entropy'], 0.0)
    
    def test_compute_counterfactual_edge_delta(self):
        """Test counterfactual edge delta computation."""
        delta = self.engine.compute_counterfactual_edge_delta(
            'identity_1', 'identity_2', seed=42
        )
        
        self.assertIn('survival_delta', delta)
        self.assertIn('k_reach_delta', delta)
        self.assertIn('entropy_delta', delta)
        self.assertIn('refusal_delta', delta)
        
        # Check types
        self.assertIsInstance(delta['survival_delta'], float)
        self.assertIsInstance(delta['k_reach_delta'], int)
        self.assertIsInstance(delta['entropy_delta'], float)
        self.assertIsInstance(delta['refusal_delta'], float)
    
    def test_get_vector_cached(self):
        """Test vector retrieval from cache."""
        # Compute first time
        vector1 = self.engine.compute_consequence_vector('identity_1', seed=42)
        
        # Get from cache
        vector2 = self.engine.get_vector('identity_1')
        
        self.assertEqual(vector1, vector2)
    
    def test_get_vector_not_found(self):
        """Test get_vector raises KeyError if not found."""
        with self.assertRaises(KeyError):
            self.engine.get_vector('unknown_identity')
    
    def test_build_consequence_field(self):
        """Test building complete consequence field."""
        # Use smaller rollouts for faster test
        field = self.engine.build(k=3, num_rollouts=10, seed=42)
        
        self.assertIsNotNone(field)
        self.assertIn('identity_1', field.identity_vectors)
        self.assertGreater(len(field.identity_vectors), 0)
        self.assertIsNotNone(field.edge_deltas)
        self.assertIsNotNone(field.metadata)
    
    def test_save_consequence_field(self):
        """Test saving consequence field to JSON."""
        # Build field first
        self.engine.build(k=3, num_rollouts=5, seed=42)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            self.engine.save(temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify file is valid JSON
            import json
            with open(temp_path, 'r') as f:
                data = json.load(f)
                self.assertIn('identity_vectors', data)
                self.assertIn('edge_deltas', data)
                self.assertIn('metadata', data)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_build_requires_observer(self):
        """Test build fails without observer."""
        engine = ConsequenceFieldEngine(
            phase2_identities={},
            phase3_relations={},
            phase4_symbols={},
            continuation_observer=None
        )
        
        with self.assertRaises(ConsequenceFieldError):
            engine.build()
    
    def test_set_topology_data(self):
        """Test setting topology data."""
        topology_data = {
            1: {'pressure': 0.5, 'escape_concentration': 0.8}
        }
        
        self.engine.set_topology_data(topology_data)
        self.assertEqual(self.engine.topology_data, topology_data)
        self.assertIn('pressure_min', self.engine.policies)


if __name__ == '__main__':
    unittest.main()
