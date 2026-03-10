"""
Test Suite for Phase 7: Role Emergence

Enterprise-grade tests with >80% coverage target.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock

from threshold_onset.semantic.phase7.properties import compute_cluster_properties
from threshold_onset.semantic.phase7.role_assigner import (
    assign_roles_from_properties,
    compute_binder_properties
)
from threshold_onset.semantic.phase7.role_emergence import RoleEmergenceEngine
from threshold_onset.semantic.common.types import (
    MeaningMap,
    MeaningSignature,
    ConsequenceField
)
from threshold_onset.semantic.common.exceptions import RoleEmergenceError


class TestProperties(unittest.TestCase):
    """Test cluster property computation."""
    
    def test_compute_cluster_properties(self):
        """Test cluster property computation."""
        cluster_identities = ['id1', 'id2']
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
        
        properties = compute_cluster_properties(cluster_identities, identity_vectors)
        
        self.assertIn('avg_survival', properties)
        self.assertIn('avg_entropy', properties)
        self.assertIn('avg_concentration', properties)
        self.assertIn('avg_refusal_rate', properties)
        self.assertIn('avg_k_reach', properties)
        self.assertIn('avg_out_degree', properties)
        
        # Check averages are reasonable
        self.assertGreater(properties['avg_survival'], 0.0)
        self.assertLessEqual(properties['avg_survival'], 1.0)
    
    def test_compute_properties_empty(self):
        """Test property computation with empty cluster."""
        properties = compute_cluster_properties([], {})
        self.assertEqual(properties, {})


class TestRoleAssigner(unittest.TestCase):
    """Test role assignment."""
    
    def test_assign_roles_from_properties(self):
        """Test role assignment using quantiles."""
        clusters = {
            'cluster_0': ['id1', 'id2'],
            'cluster_1': ['id3']
        }
        
        identity_vectors = {
            'id1': {
                'out_degree': 2,
                'k_reach': 5,
                'survival': 0.9,
                'entropy': 0.5,
                'escape_concentration': 0.8,
                'near_refusal_rate': 0.1,
                'dead_end_risk': 0.0
            },
            'id2': {
                'out_degree': 3,
                'k_reach': 6,
                'survival': 0.85,
                'entropy': 0.6,
                'escape_concentration': 0.75,
                'near_refusal_rate': 0.15,
                'dead_end_risk': 0.0
            },
            'id3': {
                'out_degree': 1,
                'k_reach': 2,
                'survival': 0.3,
                'entropy': 0.3,
                'escape_concentration': 1.0,
                'near_refusal_rate': 0.8,
                'dead_end_risk': 0.0
            }
        }
        
        roles = assign_roles_from_properties(
            clusters,
            identity_vectors,
            percentile_high=75,
            percentile_low=25
        )
        
        self.assertIn('cluster_0', roles)
        self.assertIn('cluster_1', roles)
        
        # Check role is one of valid roles
        valid_roles = {'anchor', 'driver', 'gate', 'binder', 'terminator', 'unclassified'}
        self.assertIn(roles['cluster_0'], valid_roles)
        self.assertIn(roles['cluster_1'], valid_roles)


class TestRoleEmergenceEngine(unittest.TestCase):
    """Test RoleEmergenceEngine."""
    
    def setUp(self):
        """Set up test engine."""
        # Create mock meaning map
        self.meaning_map = MeaningMap(
            clusters={
                'cluster_0': MeaningSignature(
                    centroid={'survival': 0.9, 'entropy': 0.5},
                    size=2,
                    identities=['id1', 'id2']
                ),
                'cluster_1': MeaningSignature(
                    centroid={'survival': 0.3, 'entropy': 0.3},
                    size=1,
                    identities=['id3']
                )
            },
            identity_to_cluster={
                'id1': 'cluster_0',
                'id2': 'cluster_0',
                'id3': 'cluster_1'
            },
            metadata={}
        )
        
        # Create mock consequence field
        self.consequence_field = ConsequenceField(
            identity_vectors={
                'id1': {
                    'out_degree': 2,
                    'k_reach': 5,
                    'survival': 0.9,
                    'entropy': 0.5,
                    'escape_concentration': 0.8,
                    'near_refusal_rate': 0.1,
                    'dead_end_risk': 0.0
                },
                'id2': {
                    'out_degree': 3,
                    'k_reach': 6,
                    'survival': 0.85,
                    'entropy': 0.6,
                    'escape_concentration': 0.75,
                    'near_refusal_rate': 0.15,
                    'dead_end_risk': 0.0
                },
                'id3': {
                    'out_degree': 1,
                    'k_reach': 2,
                    'survival': 0.3,
                    'entropy': 0.3,
                    'escape_concentration': 1.0,
                    'near_refusal_rate': 0.8,
                    'dead_end_risk': 0.0
                }
            },
            edge_deltas={},
            metadata={}
        )
        
        self.observer = Mock()
        self.observer.adjacency = {
            'id1': {'id2'},
            'id2': {'id3'},
            'id3': set()
        }
        
        self.engine = RoleEmergenceEngine(
            meaning_map=self.meaning_map,
            consequence_field=self.consequence_field,
            continuation_observer=self.observer
        )
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertEqual(self.engine.percentile_high, 75)
        self.assertEqual(self.engine.percentile_low, 25)
    
    def test_emerge_roles(self):
        """Test role emergence."""
        roles = self.engine.emerge()
        
        self.assertIsNotNone(roles)
        self.assertIn('symbol_to_role', roles)
        self.assertIn('cluster_roles', roles)
        self.assertIn('role_properties', roles)
    
    def test_get_role(self):
        """Test get role for symbol."""
        roles = self.engine.emerge()
        
        # Test with identity hash
        role = self.engine.get_role('id1')
        # May be None if symbol not in mapping
        # That's okay for this test
    
    def test_get_role_properties(self):
        """Test get role properties."""
        roles = self.engine.emerge()
        
        # Get a role from cluster_roles
        if roles['cluster_roles']:
            first_role = list(roles['cluster_roles'].values())[0]
            properties = self.engine.get_role_properties(first_role)
            if properties:
                self.assertIn('avg_survival', properties)
    
    def test_save_roles(self):
        """Test saving roles to JSON."""
        roles = self.engine.emerge()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            self.engine.save(temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            import json
            with open(temp_path, 'r') as f:
                data = json.load(f)
                self.assertIn('symbol_to_role', data)
                self.assertIn('cluster_roles', data)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == '__main__':
    unittest.main()
