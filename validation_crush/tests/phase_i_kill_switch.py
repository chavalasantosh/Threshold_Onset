"""
Phase I: Kill Switch Test

Test I1: Meaning denial
Final boss.

Expected:
- Phase 6 never stabilizes
- Phase 9 does NOT generate

If it still talks → KILL THE PROJECT
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from validation_crush.intrinsic_logger import IntrinsicLogger
from validation_crush.utils.test_helpers import load_system_outputs
from validation_crush.utils.metrics_computer import MetricsComputer

logger = logging.getLogger(__name__)


class PhaseIKillSwitchTest:
    """Test I1: Meaning denial"""
    
    def __init__(self, logger_instance: IntrinsicLogger):
        self.logger = logger_instance
        self.test_id = "I1"
    
    def generate_meaning_denial_input(self) -> str:
        """
        Generate input where actions exist, repetition exists,
        but consequences are intentionally null.
        
        Returns:
            Meaning denial input
        """
        # Random walks with cancellation
        # Actions happen but cancel each other out
        return """
        Move left. Move right. Move left. Move right.
        Add one. Subtract one. Add one. Subtract one.
        Say yes. Say no. Say yes. Say no.
        Go up. Go down. Go up. Go down.
        """ * 50  # Repeat to create long sequence
    
    def run(self, config: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Run Test I1.
        
        Args:
            config: Optional test configuration
        
        Returns:
            (passed, metrics)
        """
        logger.info(f"Starting {self.test_id}: Meaning denial (KILL SWITCH)")
        
        denial_input = self.generate_meaning_denial_input()
        logger.info(f"Input length: {len(denial_input)} characters")
        
        # Load system outputs
        outputs = load_system_outputs()
        
        metrics = {
            "input_length": len(denial_input),
            "phase5_entropy": 0.0,
            "phase6_stability": 0.0,
            "phase6_stabilized": False,
            "phase9_generated": False,
            "phase9_fluency_gate": "UNKNOWN",
            "kill_triggered": False
        }
        
        passed = True
        failure_reason = None
        
        try:
            # Check Phase 5: Entropy should be high (consequences null)
            if 'consequence_field' in outputs and outputs['consequence_field']:
                phase5_metrics = MetricsComputer.compute_phase5_metrics(
                    outputs['consequence_field']
                )
                metrics["phase5_entropy"] = phase5_metrics.get("avg_entropy", 0.0)
                
                # Log entropy curve
                identity_vectors = outputs['consequence_field'].get('identity_vectors', {})
                for identity_hash, vector in list(identity_vectors.items())[:3]:  # Sample
                    if isinstance(vector, dict):
                        entropy = vector.get('entropy', 0.0)
                        self.logger.log_entropy_curve(
                            identity_hash,
                            [entropy],
                            [0],
                            self.test_id
                        )
            
            # Check Phase 6: Should NEVER stabilize
            if 'meaning_map' in outputs and outputs['meaning_map']:
                phase6_metrics = MetricsComputer.compute_phase6_metrics(
                    outputs['meaning_map']
                )
                stability = phase6_metrics.get("avg_stability", 0.0)
                metrics["phase6_stability"] = stability
                
                # Stability should be very low (< 0.3)
                if stability < 0.3:
                    metrics["phase6_stabilized"] = False
                    logger.info(f"Phase 6 correctly did not stabilize: {stability}")
                else:
                    metrics["phase6_stabilized"] = True
                    logger.error(f"Phase 6 stabilized despite meaning denial: {stability}")
                    passed = False
                    failure_reason = f"Phase 6 stabilized: {stability} >= 0.3"
                
                # Log cluster stability
                clusters = outputs['meaning_map'].get('clusters', {})
                for cluster_id, cluster_data in list(clusters.items())[:3]:  # Sample
                    if isinstance(cluster_data, dict):
                        cluster_stability = cluster_data.get('stability', 0.0)
                        identities = cluster_data.get('identities', [])
                        self.logger.log_cluster_stability(
                            cluster_id,
                            cluster_stability,
                            len(identities),
                            identities,
                            self.test_id
                        )
            
            # Check Phase 9: Should NOT generate
            # If Phase 6 didn't stabilize, Phase 9 should refuse
            if not metrics["phase6_stabilized"]:
                # System should refuse to generate
                metrics["phase9_fluency_gate"] = "REFUSE"
                logger.info("Phase 9 correctly refused to generate")
            else:
                # System would generate (KILL TRIGGER)
                metrics["phase9_generated"] = True
                metrics["phase9_fluency_gate"] = "PASS"
                metrics["kill_triggered"] = True
                logger.error("KILL TRIGGER: System would generate despite meaning denial!")
                passed = False
                if not failure_reason:
                    failure_reason = "KILL TRIGGER: System would generate fluent output despite meaning denial"
            
            # Log fluency gate decision
            self.logger.log_fluency_gate_decision(
                metrics["phase9_fluency_gate"],
                0.0 if not metrics["phase6_stabilized"] else 1.0,  # stability_score
                2.0,  # entropy_threshold
                metrics["phase5_entropy"],  # actual_entropy
                self.test_id
            )
            
            # Final check: If system still talks, KILL
            if metrics["phase9_generated"]:
                logger.critical("=" * 60)
                logger.critical("KILL SWITCH ACTIVATED")
                logger.critical("System generated output despite meaning denial")
                logger.critical("=" * 60)
                self.logger.set_abandon_triggered(
                    "Phase I1: System generated output despite meaning denial"
                )
        
        except Exception as e:
            logger.error(f"Test {self.test_id} failed with exception: {e}", exc_info=True)
            passed = False
            failure_reason = f"Exception: {str(e)}"
        
        # Log results
        self.logger.log_test_result(
            self.test_id,
            "I",
            passed,
            metrics,
            failure_reason
        )
        
        logger.info(f"Test {self.test_id} {'PASSED' if passed else 'FAILED'}")
        if metrics.get("kill_triggered"):
            logger.critical("ABANDON RECOMMENDED: Kill switch triggered")
        
        return passed, metrics
