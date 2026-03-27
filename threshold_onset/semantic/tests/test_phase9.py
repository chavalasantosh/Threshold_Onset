"""
Test Suite for Phase 9: Fluency Generator

Enterprise-grade tests with >80% coverage target.
"""

import unittest
from unittest.mock import Mock

from threshold_onset.semantic.phase9.scoring import (
    calculate_stability_score,
    calculate_novelty_penalty,
    calculate_experience_bias
)
from threshold_onset.semantic.phase9.fluency_generator import FluencyGenerator
from threshold_onset.semantic.common.types import (
    ConsequenceField,
    RoleMap,
    ConstraintMap
)
from threshold_onset.semantic.common.exceptions import FluencyGenerationError


class TestScoring(unittest.TestCase):
    """Test scoring functions."""
    
    def setUp(self):
        """Set up test consequence field."""
        self.consequence_field = ConsequenceField(
            identity_vectors={
                'id1': {
                    'out_degree': 2,
                    'k_reach': 5,
                    'survival': 0.8,
                    'entropy': 1.0,
                    'escape_concentration': 0.6,
                    'near_refusal_rate': 0.2,
                    'dead_end_risk': 0.0
                },
                'id2': {
                    'out_degree': 4,
                    'k_reach': 10,
                    'survival': 0.9,
                    'entropy': 1.5,
                    'escape_concentration': 0.8,
                    'near_refusal_rate': 0.1,
                    'dead_end_risk': 0.1
                }
            },
            edge_deltas={},
            metadata={}
        )
    
    def test_calculate_stability_score(self):
        """Test stability score calculation."""
        transition = ('id1', 'id2')
        stability = calculate_stability_score(transition, self.consequence_field)
        
        self.assertGreaterEqual(stability, 0.0)
        self.assertLessEqual(stability, 1.0)
    
    def test_calculate_novelty_penalty(self):
        """Test novelty penalty calculation."""
        recent_sequence = [0, 1, 2, 3, 0]  # 0 repeats
        penalty = calculate_novelty_penalty(0, recent_sequence, window=5)
        
        self.assertGreater(penalty, 0.0)
        self.assertLessEqual(penalty, 1.0)
        
        # Test with no repetition
        penalty2 = calculate_novelty_penalty(5, recent_sequence, window=5)
        self.assertEqual(penalty2, 0.0)
    
    def test_calculate_experience_bias(self):
        """Test experience bias calculation."""
        experience_table = {
            (0, 1): 0.5,
            (1, 2): -0.3
        }
        
        bias1 = calculate_experience_bias((0, 1), experience_table)
        self.assertEqual(bias1, 0.5)
        
        bias2 = calculate_experience_bias((1, 2), experience_table)
        self.assertEqual(bias2, -0.3)
        
        bias3 = calculate_experience_bias((2, 3), experience_table)
        self.assertEqual(bias3, 0.0)  # Not in table


class TestFluencyGenerator(unittest.TestCase):
    """Test FluencyGenerator."""
    
    def setUp(self):
        """Set up test generator."""
        self.consequence_field = ConsequenceField(
            identity_vectors={
                'id1': {
                    'out_degree': 2,
                    'k_reach': 5,
                    'survival': 0.8,
                    'entropy': 1.0,
                    'escape_concentration': 0.6,
                    'near_refusal_rate': 0.2,
                    'dead_end_risk': 0.0
                },
                'id2': {
                    'out_degree': 4,
                    'k_reach': 10,
                    'survival': 0.9,
                    'entropy': 1.5,
                    'escape_concentration': 0.8,
                    'near_refusal_rate': 0.1,
                    'dead_end_risk': 0.1
                }
            },
            edge_deltas={
                ('id1', 'id2'): {
                    'survival_delta': 0.1,
                    'k_reach_delta': 5,
                    'entropy_delta': 0.5,
                    'refusal_delta': -0.1
                }
            },
            metadata={}
        )
        
        self.roles: RoleMap = {
            'symbol_to_role': {
                0: 'anchor',
                1: 'driver'
            },
            'cluster_roles': {},
            'role_properties': {}
        }
        
        self.constraints: ConstraintMap = {
            'role_patterns': {
                ('anchor', 'driver'): {'frequency': 5, 'length': 2}
            },
            'forbidden_patterns': set(),
            'templates': [
                {'pattern': ['anchor', 'driver'], 'frequency': 5, 'length': 2}
            ]
        }
        
        self.phase3_relations = {}
        self.phase4_symbols = {
            'symbol_to_identity': {0: 'id1', 1: 'id2'},
            'identity_to_symbol': {'id1': 0, 'id2': 1}
        }
        
        self.observer = Mock()
        self.observer.adjacency = {
            'id1': {'id2'},
            'id2': {'id1'}
        }
        self.observer._check_transition_allowed = Mock(return_value=True)
        
        self.generator = FluencyGenerator(
            consequence_field=self.consequence_field,
            roles=self.roles,
            constraints=self.constraints,
            phase3_relations=self.phase3_relations,
            phase4_symbols=self.phase4_symbols,
            continuation_observer=self.observer
        )
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.stability_weight, 0.4)
        self.assertEqual(self.generator.template_weight, 0.3)
        self.assertEqual(self.generator.novelty_window, 5)
    
    def test_build_experience_table(self):
        """Test experience table building."""
        self.generator.build_experience_table()
        
        self.assertGreater(len(self.generator.experience_table), 0)
        
        # Check experience values are in [-1, 1] range
        for bias in self.generator.experience_table.values():
            self.assertGreaterEqual(bias, -1.0)
            self.assertLessEqual(bias, 1.0)
    
    def test_score_transition(self):
        """Test transition scoring."""
        self.generator.build_experience_table()
        
        transition = (0, 1)
        current_roles = ['anchor']
        recent_symbols = [0]
        
        score = self.generator.score_transition(
            transition,
            current_roles,
            recent_symbols
        )
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_generate(self):
        """Test sequence generation."""
        self.generator.build_experience_table()
        
        sequence = self.generator.generate(
            start_symbol=0,
            length=5,
            seed=42
        )
        
        self.assertIsInstance(sequence, list)
        self.assertGreater(len(sequence), 0)
        self.assertEqual(sequence[0], 0)  # Starts with start_symbol
    
    def test_generate_text(self):
        """Test text generation."""
        self.generator.build_experience_table()
        
        symbol_to_text = {
            0: 'hello',
            1: 'world'
        }
        
        text = self.generator.generate_text(
            start_symbol=0,
            length=5,
            symbol_to_text=symbol_to_text,
            seed=42
        )

        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)

    def test_generate_invalid_start(self):
        """Test generation with invalid start symbol."""
        with self.assertRaises(FluencyGenerationError):
            self.generator.generate(start_symbol=999, length=5)

    def test_generate_no_transitions(self):
        """Test generation when no transitions available."""
        # Set up observer with no allowed transitions
        self.observer.adjacency = {'id1': set()}

        sequence = self.generator.generate(start_symbol=0, length=5, seed=42)

        # Should return sequence with just start symbol
        self.assertEqual(len(sequence), 1)
        self.assertEqual(sequence[0], 0)


if __name__ == '__main__':
    unittest.main()
