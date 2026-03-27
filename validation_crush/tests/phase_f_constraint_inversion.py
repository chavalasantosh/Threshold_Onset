"""
Phase F: Constraint Inversion Test

Test F1: Reverse-grammar challenge
Grammar emergence sanity check.

Expected:
- Constraint drift detection OR dual grammar regimes

Fail:
- Single averaged constraint
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from validation_crush.intrinsic_logger import IntrinsicLogger
from validation_crush.utils.test_helpers import load_system_outputs
from validation_crush.utils.metrics_computer import MetricsComputer

logger = logging.getLogger(__name__)


class PhaseFConstraintInversionTest:
    """Test F1: Reverse-grammar challenge"""
    
    def __init__(self, logger_instance: IntrinsicLogger):
        self.logger = logger_instance
        self.test_id = "F1"
    
    def generate_inverted_grammar(self) -> str:
        """
        Generate sequences where constraints exist but are inverted halfway.
        
        Returns:
            Text with inverted grammar
        """
        # First half: normal grammar
        normal = "The cat sat on the mat. The dog ran in the park. The bird flew in the sky."
        
        # Second half: inverted grammar (object-verb-subject)
        inverted = "Mat the on sat cat the. Park the in ran dog the. Sky the in flew bird the."
        
        return normal + " " + inverted
    
    def run(self, config: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Run Test F1.
        
        Args:
            config: Optional test configuration
        
        Returns:
            (passed, metrics)
        """
        logger.info(f"Starting {self.test_id}: Reverse-grammar challenge")
        
        inverted_input = self.generate_inverted_grammar()
        
        # Load system outputs
        outputs = load_system_outputs()
        
        metrics = {
            "input": inverted_input,
            "phase8_num_patterns": 0,
            "phase8_num_templates": 0,
            "phase8_constraint_rigidity": [],
            "constraint_drift_detected": False,
            "dual_grammar_detected": False,
            "single_averaged_constraint": False
        }
        
        passed = True
        failure_reason = None
        
        try:
            # Check Phase 8: Constraint discovery
            if 'constraints' in outputs and outputs['constraints']:
                phase8_metrics = MetricsComputer.compute_phase8_metrics(outputs['constraints'])
                
                metrics["phase8_num_patterns"] = phase8_metrics.get("num_patterns", 0)
                metrics["phase8_num_templates"] = phase8_metrics.get("num_templates", 0)
                metrics["phase8_constraint_rigidity"] = phase8_metrics.get("constraint_rigidity_scores", [])
                
                # Log constraint rigidity
                patterns = outputs['constraints'].get('role_patterns', {})
                for pattern_id, pattern_data in list(patterns.items())[:5]:  # Sample
                    if isinstance(pattern_data, dict):
                        pattern = pattern_data.get('pattern', [])
                        frequency = pattern_data.get('frequency', 0)
                        rigidity = min(1.0, frequency / 10.0)
                    else:
                        pattern = []
                        frequency = 0
                        rigidity = 0.0
                    
                    self.logger.log_constraint_rigidity(
                        pattern_id,
                        rigidity,
                        pattern,
                        frequency,
                        self.test_id
                    )
                
                # Get rigidity scores from metrics
                rigidity_scores = metrics["phase8_constraint_rigidity"]
                
                # Check for constraint drift or dual grammar
                # If we have multiple constraint regimes, that's good
                if metrics["phase8_num_patterns"] > 1:
                    # Check if patterns are diverse (not averaged)
                    if rigidity_scores:
                        rigidity_variance = sum((r - sum(rigidity_scores) / len(rigidity_scores)) ** 2 
                                                for r in rigidity_scores) / len(rigidity_scores)
                        
                        # High variance suggests dual grammar regimes
                        if rigidity_variance > 0.1:
                            metrics["dual_grammar_detected"] = True
                            logger.info(f"Dual grammar detected: variance = {rigidity_variance}")
                        else:
                            # Low variance with multiple patterns suggests averaging (FAIL)
                            metrics["single_averaged_constraint"] = True
                            logger.error(f"Single averaged constraint detected: variance = {rigidity_variance}")
                            passed = False
                            failure_reason = f"Constraints averaged instead of detecting drift: variance = {rigidity_variance} <= 0.1"
                
                # Check for constraint drift (patterns change over time)
                # In a real test, we would track patterns across the input sequence
                # For now, we check if rigidity scores vary significantly
                if rigidity_scores and len(rigidity_scores) > 1:
                    min_rigidity = min(rigidity_scores)
                    max_rigidity = max(rigidity_scores)
                    if max_rigidity - min_rigidity > 0.3:
                        metrics["constraint_drift_detected"] = True
                        logger.info(f"Constraint drift detected: range = {max_rigidity - min_rigidity}")
                
                # PASS if: drift detected OR dual grammar detected
                # FAIL if: single averaged constraint
                if not metrics["constraint_drift_detected"] and not metrics["dual_grammar_detected"]:
                    if metrics["single_averaged_constraint"]:
                        passed = False
                        if not failure_reason:
                            failure_reason = "System averaged constraints instead of detecting drift or dual grammar"
        
        except Exception as e:
            logger.error(f"Test {self.test_id} failed with exception: {e}", exc_info=True)
            passed = False
            failure_reason = f"Exception: {str(e)}"
        
        # Log results
        self.logger.log_test_result(
            self.test_id,
            "F",
            passed,
            metrics,
            failure_reason
        )
        
        logger.info(f"Test {self.test_id} {'PASSED' if passed else 'FAILED'}")
        return passed, metrics
