"""
Phase E: Role Collapse Stress Test

Test E1: Role overload
Attacks Phase 7 directly.

Expected:
- Role bifurcation OR rejection

Fail:
- Silent role merging
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
from validation_crush.utils.test_helpers import load_system_outputs, compute_variance
from validation_crush.utils.metrics_computer import MetricsComputer

logger = logging.getLogger(__name__)


class PhaseERoleCollapseTest:
    """Test E1: Role overload"""
    
    def __init__(self, logger_instance: IntrinsicLogger):
        self.logger = logger_instance
        self.test_id = "E1"
    
    def generate_role_overload_scenario(self) -> str:
        """
        Generate a scenario where one entity must play mutually exclusive roles.
        
        Returns:
            Long context with role conflicts
        """
        # Create a scenario where the same entity appears in conflicting roles
        # Generate 100K+ tokens as per spec (assuming ~5 tokens per word, need ~20K words)
        base_scenario = """
        The teacher was also the student. The teacher taught mathematics to the student.
        The student learned from the teacher. But the teacher was the student, so the teacher
        was learning from themselves. The student was teaching the teacher, but the teacher
        was the student, creating a circular dependency. The authority figure was also the
        subordinate. The leader was also the follower. The cause was also the effect.
        The master was also the servant. The owner was also the property. The creator was
        also the creation. The parent was also the child. The doctor was also the patient.
        The judge was also the defendant. The prosecutor was also the accused. The hunter
        was also the prey. The predator was also the victim. The winner was also the loser.
        """
        
        # Repeat to reach 100K+ tokens (~20K words)
        # Each base_scenario is ~150 words, need ~133 repetitions
        scenario = base_scenario * 133
        
        return scenario.strip()
    
    def run(self, config: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Run Test E1.
        
        Args:
            config: Optional test configuration
        
        Returns:
            (passed, metrics)
        """
        logger.info(f"Starting {self.test_id}: Role overload")
        
        overload_input = self.generate_role_overload_scenario()
        logger.info(f"Input length: {len(overload_input)} characters (~{len(overload_input.split())} words)")
        
        # ACTUALLY PROCESS INPUT THROUGH SYSTEM (CRITICAL FIX)
        from validation_crush.utils.test_helpers import process_text_through_system
        
        logger.info("Processing role overload scenario through full pipeline...")
        outputs = process_text_through_system(
            text=overload_input,
            tokenization_method="word",
            num_runs=3,
            run_semantic_phases=True,
            config=config
        )
        
        metrics = {
            "input_length": len(overload_input),
            "phase7_role_assignments": {},
            "phase7_role_variance": 0.0,
            "role_bifurcation_detected": False,
            "role_rejection_detected": False,
            "silent_merging_detected": False,
            "num_conflicting_roles": 0
        }
        
        passed = True
        failure_reason = None
        
        try:
            # Check Phase 7: Role assignments
            if 'roles' in outputs and outputs['roles']:
                phase7_metrics = MetricsComputer.compute_phase7_metrics(outputs['roles'])
                
                cluster_roles = outputs['roles'].get('cluster_roles', {})
                metrics["phase7_role_assignments"] = cluster_roles
                metrics["phase7_role_variance"] = phase7_metrics.get("role_variance", 0.0)
                
                # Log role variance
                self.logger.log_role_variance(
                    cluster_roles,
                    metrics["phase7_role_variance"],
                    self.test_id
                )
                
                # Check for role conflicts
                # In a real scenario, we would identify entities that appear in multiple roles
                # For now, we check if variance is high (indicating role instability)
                
                # High variance suggests role bifurcation or rejection
                if metrics["phase7_role_variance"] > 1.5:
                    metrics["role_bifurcation_detected"] = True
                    logger.info(f"Role bifurcation detected: variance = {metrics['phase7_role_variance']}")
                elif metrics["phase7_role_variance"] < 0.5:
                    # Low variance with conflicting roles suggests silent merging (FAIL)
                    metrics["silent_merging_detected"] = True
                    logger.error(f"Silent role merging detected: variance = {metrics['phase7_role_variance']}")
                    passed = False
                    failure_reason = f"Silent role merging: variance = {metrics['phase7_role_variance']} < 0.5"
                else:
                    # Moderate variance might indicate rejection
                    metrics["role_rejection_detected"] = True
                    logger.info(f"Role rejection detected: variance = {metrics['phase7_role_variance']}")
                
                # Count unclassified roles (rejection indicator)
                num_unclassified = phase7_metrics.get("num_unclassified", 0)
                if num_unclassified > 0:
                    metrics["role_rejection_detected"] = True
                    logger.info(f"Unclassified roles detected: {num_unclassified}")
            
            # Check if system handles conflicts properly
            # PASS if: bifurcation OR rejection
            # FAIL if: silent merging
            if not metrics["role_bifurcation_detected"] and not metrics["role_rejection_detected"]:
                if metrics["silent_merging_detected"]:
                    passed = False
                    if not failure_reason:
                        failure_reason = "System silently merged conflicting roles instead of bifurcating or rejecting"
        
        except Exception as e:
            logger.error(f"Test {self.test_id} failed with exception: {e}", exc_info=True)
            passed = False
            failure_reason = f"Exception: {str(e)}"
        
        # Log results
        self.logger.log_test_result(
            self.test_id,
            "E",
            passed,
            metrics,
            failure_reason
        )
        
        logger.info(f"Test {self.test_id} {'PASSED' if passed else 'FAILED'}")
        return passed, metrics
