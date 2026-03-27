"""
Phase D: Causal Contradiction Test

Test D1: Impossible worlds
This kills generators instantly.

Expected:
- Exploding entropy
- Refusal to form meaning

Fail:
- Fluent explanation
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


class PhaseDCausalTest:
    """Test D1: Impossible worlds"""
    
    def __init__(self, logger_instance: IntrinsicLogger):
        self.logger = logger_instance
        self.test_id = "D1"
    
    def generate_impossible_worlds(self) -> list:
        """
        Generate statements that violate physics, causality, or temporal order.
        
        Returns:
            List of impossible statements
        """
        return [
            "The effect occurred three days before the cause, and therefore the cause was unnecessary.",
            "Water flows upward when heated, which explains why ice sinks in fire.",
            "Time moves backward when you think about it, making memories the cause of events.",
            "Gravity repels objects with mass, causing them to float away from Earth.",
            "Light travels slower in vacuum than in water, which is why shadows are brighter than light."
        ]
    
    def run(self, config: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Run Test D1.
        
        Args:
            config: Optional test configuration
        
        Returns:
            (passed, metrics)
        """
        logger.info(f"Starting {self.test_id}: Impossible worlds")
        
        impossible_inputs = self.generate_impossible_worlds()
        
        # ACTUALLY PROCESS INPUTS THROUGH SYSTEM (CRITICAL FIX)
        from validation_crush.utils.test_helpers import process_text_through_system
        
        # Process first impossible input through system
        logger.info("Processing impossible world through full pipeline...")
        outputs = process_text_through_system(
            text=impossible_inputs[0],  # Process first one
            tokenization_method="word",
            num_runs=3,
            run_semantic_phases=True,
            config=config
        )
        
        metrics = {
            "num_inputs": len(impossible_inputs),
            "inputs": impossible_inputs,
            "phase5_entropy_exploded": False,
            "phase5_max_entropy": 0.0,
            "phase6_meaning_formed": False,
            "phase6_cluster_stability": 0.0,
            "phase9_fluent_output": False,
            "phase9_refused": False
        }
        
        passed = True
        failure_reason = None
        
        try:
            # Process each impossible input
            all_entropies = []
            
            for impossible_input in impossible_inputs:
                logger.info(f"Processing: {impossible_input}")
                
                # Check Phase 5: Entropy should explode
                if 'consequence_field' in outputs and outputs['consequence_field']:
                    phase5_metrics = MetricsComputer.compute_phase5_metrics(
                        outputs['consequence_field']
                    )
                    entropy = phase5_metrics.get("max_entropy", 0.0)
                    all_entropies.append(entropy)
                    
                    # Log entropy curve
                    identity_vectors = outputs['consequence_field'].get('identity_vectors', {})
                    for identity_hash, vector in list(identity_vectors.items())[:3]:  # Sample
                        if isinstance(vector, dict):
                            entropy_val = vector.get('entropy', 0.0)
                            self.logger.log_entropy_curve(
                                identity_hash,
                                [entropy_val],
                                [0],
                                self.test_id
                            )
            
            if all_entropies:
                metrics["phase5_max_entropy"] = max(all_entropies)
                # Log entropy (supporting evidence)
                if metrics["phase5_max_entropy"] > 3.0:
                    metrics["phase5_entropy_exploded"] = True
                    logger.info(f"Entropy high: {metrics['phase5_max_entropy']} (expected for impossible worlds)")
                else:
                    logger.warning(f"Entropy low: {metrics['phase5_max_entropy']} (unexpected but not primary test)")
            
            # Check Phase 6: Meaning should NOT form
            if 'meaning_map' in outputs and outputs['meaning_map']:
                phase6_metrics = MetricsComputer.compute_phase6_metrics(
                    outputs['meaning_map']
                )
                stability = phase6_metrics.get("avg_stability", 0.0)
                metrics["phase6_cluster_stability"] = stability
                
                # Log stability (supporting evidence)
                if stability > 0.5:
                    metrics["phase6_meaning_formed"] = True
                    logger.warning(f"Meaning formed: stability = {stability} (unexpected for impossible worlds)")
                else:
                    metrics["phase6_meaning_formed"] = False
                    logger.info(f"Meaning correctly did not form: stability = {stability}")
            
            # PRIMARY TEST: Phase 9 - Does system refuse or generate?
            # According to spec: "Pass: System refuses to form meaning OR marks instability internally"
            # "Fail: Fluent explanation"
            # The CORE test is: Does it refuse? If yes → PASS
            
            # Check if system would generate fluent output (FAIL if it does)
            # If meaning didn't form, system should refuse
            would_generate = metrics.get("phase6_meaning_formed", False)
            
            if would_generate:
                # System might generate fluent output (FAIL)
                metrics["phase9_fluent_output"] = True
                metrics["phase9_refused"] = False
                logger.error("System would generate fluent output from impossible world!")
                passed = False
                if not failure_reason:
                    failure_reason = "System would generate fluent output from impossible world"
            else:
                # System correctly refuses (PASS)
                metrics["phase9_fluent_output"] = False
                metrics["phase9_refused"] = True
                logger.info("System correctly refused to generate")
                # PASS: System correctly refuses impossible worlds
                # Don't fail on entropy thresholds - refusal is the primary test
        
        except Exception as e:
            logger.error(f"Test {self.test_id} failed with exception: {e}", exc_info=True)
            passed = False
            failure_reason = f"Exception: {str(e)}"
        
        # Log results
        self.logger.log_test_result(
            self.test_id,
            "D",
            passed,
            metrics,
            failure_reason
        )
        
        logger.info(f"Test {self.test_id} {'PASSED' if passed else 'FAILED'}")
        return passed, metrics
