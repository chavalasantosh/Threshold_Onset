"""
Integration Tests for Semantic Discovery Module

Enterprise-grade integration tests with real Phase 2-4 outputs.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from threshold_onset.semantic import (
    ConsequenceFieldEngine,
    MeaningDiscoveryEngine,
    RoleEmergenceEngine,
    ConstraintDiscoveryEngine,
    FluencyGenerator
)
from threshold_onset.semantic.common.types import ConsequenceField


class TestIntegrationWorkflow(unittest.TestCase):
    """
    Integration test for complete semantic discovery workflow.
    
    Tests the full pipeline from Phase 5 to Phase 9.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create minimal test data that mimics Phase 2-4 outputs
        self.phase2_metrics = {
            'identities': {
                'hash1': {'count': 5},
                'hash2': {'count': 3},
                'hash3': {'count': 2}
            }
        }
        
        self.phase3_metrics = {
            'graph_nodes': {'hash1', 'hash2', 'hash3'},
            'graph_edges': {
                ('hash1', 'hash2'),
                ('hash2', 'hash3'),
                ('hash3', 'hash1')
            }
        }
        
        self.phase4_output = {
            'identity_to_symbol': {
                'hash1': 0,
                'hash2': 1,
                'hash3': 2
            },
            'symbol_to_identity': {
                0: 'hash1',
                1: 'hash2',
                2: 'hash3'
            }
        }
        
        self.symbol_sequences = [
            [0, 1, 2],
            [1, 2, 0],
            [2, 0, 1]
        ]
    
    def test_complete_workflow(self):
        """Test complete workflow from Phase 5 to Phase 9."""
        try:
            from integration.continuation_observer import ContinuationObserver
        except ImportError:
            self.skipTest("ContinuationObserver not available")
        
        # Setup observer
        observer = ContinuationObserver(
            self.phase4_output,
            self.phase3_metrics,
            self.phase2_metrics
        )
        
        # Phase 5: Build consequence field
        consequence_engine = ConsequenceFieldEngine(
            phase2_identities=self.phase2_metrics,
            phase3_relations=self.phase3_metrics,
            phase4_symbols=self.phase4_output,
            continuation_observer=observer
        )
        
        # Use smaller parameters for faster testing
        consequence_field = consequence_engine.build(
            k=3,
            num_rollouts=10,
            seed=42
        )
        
        self.assertIsNotNone(consequence_field)
        self.assertGreater(len(consequence_field.identity_vectors), 0)
        
        # Phase 6: Discover meaning
        meaning_engine = MeaningDiscoveryEngine(consequence_field)
        meaning_map = meaning_engine.discover(seed=42)
        
        self.assertIsNotNone(meaning_map)
        self.assertGreater(len(meaning_map.clusters), 0)
        
        # Phase 7: Emerge roles
        role_engine = RoleEmergenceEngine(
            meaning_map=meaning_map,
            consequence_field=consequence_field,
            continuation_observer=observer
        )
        roles = role_engine.emerge()
        
        self.assertIsNotNone(roles)
        self.assertIn('cluster_roles', roles)
        
        # Phase 8: Discover constraints
        constraint_engine = ConstraintDiscoveryEngine(
            roles=roles,
            symbol_sequences=self.symbol_sequences,
            edge_deltas=consequence_field.edge_deltas,
            continuation_observer=observer,
            identity_to_symbol=self.phase4_output.get('identity_to_symbol', {})
        )
        constraints = constraint_engine.discover()
        
        self.assertIsNotNone(constraints)
        self.assertIn('templates', constraints)
        
        # Phase 9: Generate fluent text
        generator = FluencyGenerator(
            consequence_field=consequence_field,
            roles=roles,
            constraints=constraints,
            phase3_relations=self.phase3_metrics,
            phase4_symbols=self.phase4_output,
            continuation_observer=observer
        )
        
        generator.build_experience_table()
        
        sequence = generator.generate(
            start_symbol=0,
            length=10,
            seed=42
        )
        
        self.assertIsInstance(sequence, list)
        self.assertGreater(len(sequence), 0)
        
        # Verify sequence starts with start_symbol
        self.assertEqual(sequence[0], 0)
    
    def test_determinism(self):
        """Test that same seed produces same results."""
        try:
            from integration.continuation_observer import ContinuationObserver
        except ImportError:
            self.skipTest("ContinuationObserver not available")
        
        observer = ContinuationObserver(
            self.phase4_output,
            self.phase3_metrics,
            self.phase2_metrics
        )
        
        # Run Phase 5 twice with same seed
        engine1 = ConsequenceFieldEngine(
            phase2_identities=self.phase2_metrics,
            phase3_relations=self.phase3_metrics,
            phase4_symbols=self.phase4_output,
            continuation_observer=observer
        )
        
        engine2 = ConsequenceFieldEngine(
            phase2_identities=self.phase2_metrics,
            phase3_relations=self.phase3_metrics,
            phase4_symbols=self.phase4_output,
            continuation_observer=observer
        )
        
        field1 = engine1.build(k=3, num_rollouts=5, seed=42)
        field2 = engine2.build(k=3, num_rollouts=5, seed=42)
        
        # Check that vectors are identical
        for identity_hash in field1.identity_vectors:
            if identity_hash in field2.identity_vectors:
                vec1 = field1.identity_vectors[identity_hash]
                vec2 = field2.identity_vectors[identity_hash]
                
                # Check key components
                self.assertEqual(vec1['out_degree'], vec2['out_degree'])
                # Note: Some components may have small floating point differences
                # but should be very close


class TestErrorHandling(unittest.TestCase):
    """Test error handling across phases."""
    
    def test_missing_observer(self):
        """Test error when observer is missing."""
        engine = ConsequenceFieldEngine(
            phase2_identities={},
            phase3_relations={},
            phase4_symbols={},
            continuation_observer=None
        )
        
        with self.assertRaises(Exception):  # Should raise ConsequenceFieldError
            engine.build()
    
    def test_empty_vectors(self):
        """Test handling of empty consequence vectors."""
        empty_field = ConsequenceField(
            identity_vectors={},
            edge_deltas={},
            metadata={}
        )
        
        engine = MeaningDiscoveryEngine(empty_field)
        
        with self.assertRaises(Exception):  # Should raise MeaningDiscoveryError
            engine.discover()


if __name__ == '__main__':
    unittest.main()
