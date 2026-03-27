"""
Test Suite for Phase 6: Meaning Discovery

Enterprise-grade tests with >80% coverage target.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, MagicMock

from threshold_onset.semantic.phase6.normalization import normalize_vectors
from threshold_onset.semantic.phase6.clustering import (
    k_medoids_pam,
    select_optimal_k,
    compute_cluster_stability
)
from threshold_onset.semantic.phase6.meaning_discovery import MeaningDiscoveryEngine
from threshold_onset.semantic.common.types import ConsequenceField, ConsequenceVector
from threshold_onset.semantic.common.exceptions import MeaningDiscoveryError


class TestNormalization(unittest.TestCase):
    """Test vector normalization."""
    
    def test_normalize_vectors(self):
        """Test vector normalization to [0, 1] range."""
        identity_vectors = {
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
        }
        
        normalized, ranges = normalize_vectors(identity_vectors)
        
        self.assertIn('id1', normalized)
        self.assertIn('id2', normalized)
        
        # Check normalization
        for key in normalized['id1'].keys():
            self.assertGreaterEqual(normalized['id1'][key], 0.0)
            self.assertLessEqual(normalized['id1'][key], 1.0)
        
        # Check ranges
        self.assertIn('out_degree', ranges)
        self.assertIn('min', ranges['out_degree'])
        self.assertIn('max', ranges['out_degree'])
    
    def test_normalize_empty(self):
        """Test normalization with empty vectors."""
        normalized, ranges = normalize_vectors({})
        self.assertEqual(normalized, {})
        self.assertEqual(ranges, {})


class TestClustering(unittest.TestCase):
    """Test clustering algorithms."""
    
    def test_k_medoids_pam(self):
        """Test k-medoids PAM algorithm."""
        vectors = [
            {'a': 0.1, 'b': 0.2},
            {'a': 0.2, 'b': 0.3},
            {'a': 0.8, 'b': 0.9},
            {'a': 0.9, 'b': 1.0}
        ]
        
        clusters = k_medoids_pam(vectors, k=2)
        
        self.assertEqual(len(clusters), 2)
        self.assertGreater(len(clusters[0]), 0)
        self.assertGreater(len(clusters[1]), 0)
    
    def test_k_medoids_single_cluster(self):
        """Test k-medoids with k=1."""
        vectors = [
            {'a': 0.1, 'b': 0.2},
            {'a': 0.2, 'b': 0.3}
        ]
        
        clusters = k_medoids_pam(vectors, k=1)
        self.assertEqual(len(clusters), 1)
    
    def test_select_optimal_k(self):
        """Test optimal k selection."""
        vectors = [
            {'a': 0.1, 'b': 0.2},
            {'a': 0.2, 'b': 0.3},
            {'a': 0.8, 'b': 0.9},
            {'a': 0.9, 'b': 1.0},
            {'a': 0.5, 'b': 0.6}
        ]
        
        optimal_k = select_optimal_k(vectors, k_min=2, k_max=3, seed=42)
        
        self.assertGreaterEqual(optimal_k, 2)
        self.assertLessEqual(optimal_k, 3)
    
    def test_compute_cluster_stability(self):
        """Test cluster stability computation."""
        vectors = [
            {'a': 0.1, 'b': 0.2},
            {'a': 0.2, 'b': 0.3},
            {'a': 0.8, 'b': 0.9},
            {'a': 0.9, 'b': 1.0}
        ]
        
        stability = compute_cluster_stability(vectors, k=2, num_bootstrap=5, seed=42)
        
        self.assertGreaterEqual(stability, 0.0)
        self.assertLessEqual(stability, 1.0)


class TestMeaningDiscoveryEngine(unittest.TestCase):
    """Test MeaningDiscoveryEngine."""
    
    def setUp(self):
        """Set up test engine."""
        # Create mock consequence field
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
                },
                'id3': {
                    'out_degree': 1,
                    'k_reach': 2,
                    'survival': 0.5,
                    'entropy': 0.5,
                    'escape_concentration': 1.0,
                    'near_refusal_rate': 0.5,
                    'dead_end_risk': 0.0
                }
            },
            edge_deltas={},
            metadata={}
        )
        
        self.engine = MeaningDiscoveryEngine(self.consequence_field)
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine.consequence_field)
        self.assertIsNone(self.engine.num_clusters)  # Auto-select
    
    def test_discover_meaning(self):
        """Test meaning discovery."""
        meaning_map = self.engine.discover(seed=42)
        
        self.assertIsNotNone(meaning_map)
        self.assertGreater(len(meaning_map.clusters), 0)
        self.assertGreater(len(meaning_map.identity_to_cluster), 0)
    
    def test_get_cluster(self):
        """Test get cluster for identity."""
        meaning_map = self.engine.discover(seed=42)
        
        cluster_id = self.engine.get_cluster('id1')
        self.assertIsNotNone(cluster_id)
    
    def test_get_signature(self):
        """Test get meaning signature."""
        meaning_map = self.engine.discover(seed=42)
        
        cluster_id = self.engine.get_cluster('id1')
        if cluster_id:
            signature = self.engine.get_signature(cluster_id)
            self.assertIsNotNone(signature)
            self.assertIn('centroid', signature)
            self.assertIn('size', signature)
    
    def test_save_meaning_map(self):
        """Test saving meaning map to JSON."""
        meaning_map = self.engine.discover(seed=42)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            self.engine.save(temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            import json
            with open(temp_path, 'r') as f:
                data = json.load(f)
                self.assertIn('clusters', data)
                self.assertIn('identity_to_cluster', data)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_discover_empty_vectors(self):
        """Test discovery with empty vectors."""
        empty_field = ConsequenceField(
            identity_vectors={},
            edge_deltas={},
            metadata={}
        )
        
        engine = MeaningDiscoveryEngine(empty_field)
        
        with self.assertRaises(MeaningDiscoveryError):
            engine.discover()


if __name__ == '__main__':
    unittest.main()
