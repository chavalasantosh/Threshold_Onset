"""
Test Suite for Phase 8: Constraint Discovery

Enterprise-grade tests with >80% coverage target.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock

from threshold_onset.semantic.phase8.sequences import extract_role_sequences
from threshold_onset.semantic.phase8.pattern_miner import (
    discover_role_patterns,
    discover_forbidden_patterns,
    build_templates,
    compute_prefix_match_score
)
from threshold_onset.semantic.phase8.constraint_discovery import ConstraintDiscoveryEngine
from threshold_onset.semantic.common.types import RoleMap
from threshold_onset.semantic.common.exceptions import ConstraintDiscoveryError


class TestSequences(unittest.TestCase):
    """Test role sequence extraction."""
    
    def test_extract_role_sequences(self):
        """Test role sequence extraction."""
        symbol_sequences = [
            [0, 1, 2],
            [1, 2, 3],
            [2, 3, 0]
        ]
        
        symbol_to_role = {
            0: 'anchor',
            1: 'driver',
            2: 'anchor',
            3: 'driver'
        }
        
        role_sequences = extract_role_sequences(symbol_sequences, symbol_to_role)
        
        self.assertEqual(len(role_sequences), 3)
        self.assertEqual(role_sequences[0], ['anchor', 'driver', 'anchor'])
    
    def test_extract_with_missing_roles(self):
        """Test extraction with missing roles."""
        symbol_sequences = [[0, 1]]
        symbol_to_role = {0: 'anchor'}  # Missing role for 1
        
        role_sequences = extract_role_sequences(symbol_sequences, symbol_to_role)
        
        self.assertEqual(role_sequences[0][1], 'unclassified')


class TestPatternMiner(unittest.TestCase):
    """Test pattern mining."""
    
    def test_discover_role_patterns(self):
        """Test role pattern discovery."""
        role_sequences = [
            ['anchor', 'driver', 'anchor'],
            ['anchor', 'driver', 'anchor'],
            ['driver', 'anchor', 'driver']
        ]
        
        patterns = discover_role_patterns(
            role_sequences,
            min_frequency=2,
            max_pattern_length=3
        )
        
        self.assertGreater(len(patterns), 0)
        
        # Check pattern structure
        for pattern, data in patterns.items():
            self.assertIn('frequency', data)
            self.assertIn('length', data)
            self.assertGreaterEqual(data['frequency'], 2)
    
    def test_discover_forbidden_patterns(self):
        """Test forbidden pattern discovery."""
        role_patterns = {
            ('anchor', 'driver'): {'frequency': 5, 'length': 2},
            ('terminator', 'driver'): {'frequency': 2, 'length': 2}
        }
        
        edge_deltas = {
            ('id1', 'id2'): {'refusal_delta': 0.1},
            ('id3', 'id4'): {'refusal_delta': 0.9}  # High refusal
        }
        
        symbol_to_role = {1: 'anchor', 2: 'driver', 3: 'terminator', 4: 'driver'}
        identity_to_symbol = {'id1': 1, 'id2': 2, 'id3': 3, 'id4': 4}
        
        observer = Mock()
        observer.adjacency = {}
        
        forbidden = discover_forbidden_patterns(
            role_patterns,
            edge_deltas,
            symbol_to_role,
            identity_to_symbol,
            observer
        )
        
        self.assertIsInstance(forbidden, set)

    def test_discover_forbidden_patterns_with_ngrams(self):
        """Test forbidden discovery scores n-grams via transition aggregation."""
        role_patterns = {
            ('anchor', 'driver'): {'frequency': 5, 'length': 2},
            ('anchor', 'driver', 'terminator'): {'frequency': 4, 'length': 3},
        }

        edge_deltas = {
            ('id1', 'id2'): {'refusal_delta': 0.8},
            ('id2', 'id3'): {'refusal_delta': 0.9},
            ('id4', 'id5'): {'refusal_delta': 0.1},
        }

        symbol_to_role = {
            1: 'anchor',
            2: 'driver',
            3: 'terminator',
            4: 'anchor',
            5: 'anchor',
        }
        identity_to_symbol = {
            'id1': 1,
            'id2': 2,
            'id3': 3,
            'id4': 4,
            'id5': 5,
        }

        observer = Mock()
        observer.adjacency = {}

        forbidden = discover_forbidden_patterns(
            role_patterns,
            edge_deltas,
            symbol_to_role,
            identity_to_symbol,
            observer
        )

        self.assertIn(('anchor', 'driver', 'terminator'), forbidden)
    
    def test_build_templates(self):
        """Test template building."""
        role_patterns = {
            ('anchor', 'driver'): {'frequency': 5, 'length': 2},
            ('driver', 'anchor'): {'frequency': 3, 'length': 2}
        }
        
        forbidden_patterns = {('terminator', 'driver')}
        
        templates = build_templates(role_patterns, forbidden_patterns)
        
        self.assertGreater(len(templates), 0)
        for template in templates:
            self.assertIn('pattern', template)
            self.assertIn('frequency', template)
            self.assertIn('length', template)
    
    def test_compute_prefix_match_score(self):
        """Test prefix-match scoring."""
        current_roles = ['anchor', 'driver']
        template_pattern = ['driver', 'anchor']
        
        score = compute_prefix_match_score(current_roles, template_pattern)
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Test exact match
        current_roles2 = ['anchor', 'driver', 'anchor']
        template_pattern2 = ['anchor', 'driver', 'anchor']
        score2 = compute_prefix_match_score(current_roles2, template_pattern2)
        self.assertEqual(score2, 1.0)


class TestConstraintDiscoveryEngine(unittest.TestCase):
    """Test ConstraintDiscoveryEngine."""
    
    def setUp(self):
        """Set up test engine."""
        self.roles: RoleMap = {
            'symbol_to_role': {
                0: 'anchor',
                1: 'driver',
                2: 'anchor',
                3: 'driver'
            },
            'cluster_roles': {
                'cluster_0': 'anchor',
                'cluster_1': 'driver'
            },
            'role_properties': {}
        }
        
        self.symbol_sequences = [
            [0, 1, 2],
            [1, 2, 3],
            [0, 1, 2, 3]
        ]
        
        self.edge_deltas = {
            ('id1', 'id2'): {'refusal_delta': 0.1},
            ('id2', 'id3'): {'refusal_delta': 0.2}
        }
        
        self.observer = Mock()
        self.observer.adjacency = {}
        
        self.identity_to_symbol = {'id1': 0, 'id2': 1, 'id3': 2}
        
        self.engine = ConstraintDiscoveryEngine(
            roles=self.roles,
            symbol_sequences=self.symbol_sequences,
            edge_deltas=self.edge_deltas,
            continuation_observer=self.observer,
            identity_to_symbol=self.identity_to_symbol
        )
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertEqual(self.engine.min_frequency, 3)
        self.assertEqual(self.engine.max_pattern_length, 4)
    
    def test_discover_constraints(self):
        """Test constraint discovery."""
        constraints = self.engine.discover()
        
        self.assertIsNotNone(constraints)
        self.assertIn('role_patterns', constraints)
        self.assertIn('forbidden_patterns', constraints)
        self.assertIn('templates', constraints)
    
    def test_get_templates(self):
        """Test get templates."""
        constraints = self.engine.discover()
        
        templates = self.engine.get_templates()
        self.assertIsInstance(templates, list)
    
    def test_is_forbidden(self):
        """Test forbidden pattern check."""
        constraints = self.engine.discover()
        
        is_forbidden = self.engine.is_forbidden(('anchor', 'driver'))
        self.assertIsInstance(is_forbidden, bool)
    
    def test_compute_template_score(self):
        """Test template score computation."""
        constraints = self.engine.discover()
        
        current_roles = ['anchor', 'driver']
        score = self.engine.compute_template_score(current_roles)
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_save_constraints(self):
        """Test saving constraints to JSON."""
        constraints = self.engine.discover()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            self.engine.save(temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            import json
            with open(temp_path, 'r') as f:
                data = json.load(f)
                self.assertIn('role_patterns', data)
                self.assertIn('forbidden_patterns', data)
                self.assertIn('templates', data)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_discover_empty_sequences(self):
        """Test discovery with empty sequences."""
        engine = ConstraintDiscoveryEngine(
            roles=self.roles,
            symbol_sequences=[],
            edge_deltas={},
            continuation_observer=self.observer,
            identity_to_symbol={}
        )
        
        with self.assertRaises(ConstraintDiscoveryError):
            engine.discover()


if __name__ == '__main__':
    unittest.main()
