"""
Decision Framework

Automated abandon/pivot decision logic based on test results.
"""

import logging
from typing import Dict, Any, Optional, List
from validation_crush.intrinsic_logger import IntrinsicLogger

logger = logging.getLogger(__name__)


class DecisionFramework:
    """
    Decision framework for abandon/pivot criteria.
    
    Rules:
    - Phase I failure → ABANDON (non-negotiable)
    - Multiple critical failures → ABANDON
    - Single non-critical failure → PIVOT
    - All pass → CONTINUE
    """
    
    def __init__(self, logger_instance: IntrinsicLogger):
        """
        Initialize decision framework.
        
        Args:
            logger_instance: IntrinsicLogger instance
        """
        self.logger = logger_instance
        
        # Critical phases (failure = abandon)
        self.critical_phases = ['I']  # Phase I is non-negotiable
        
        # Important phases (multiple failures = abandon)
        self.important_phases = ['A', 'D', 'E']  # Baseline, Causal, Role collapse
    
    def should_abandon(self, phase: str, metrics: Dict[str, Any]) -> bool:
        """
        Check if we should abandon after a phase failure.
        
        Args:
            phase: Phase letter
            metrics: Phase metrics
        
        Returns:
            True if should abandon
        """
        # Phase I failure is non-negotiable
        if phase == 'I':
            if metrics.get("kill_triggered", False):
                logger.critical("Phase I kill switch triggered - ABANDON")
                return True
        
        # Other critical failures
        if phase in self.critical_phases:
            logger.warning(f"Critical phase {phase} failed - considering abandon")
            return True
        
        return False
    
    def get_decision(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get final decision based on all test results.
        
        Args:
            results: Dictionary of phase results
        
        Returns:
            Decision dictionary
        """
        decision = {
            "action": "CONTINUE",
            "reason": "",
            "abandon": False,
            "pivot": False
        }
        
        # Count failures
        failed_phases = [p for p, r in results.items() if not r.get("passed", False)]
        num_failures = len(failed_phases)
        
        # Check for Phase I failure (non-negotiable abandon)
        if 'I' in failed_phases:
            decision["action"] = "ABANDON"
            decision["reason"] = "Phase I (Kill Switch) failed - system generated output despite meaning denial"
            decision["abandon"] = True
            self.logger.set_abandon_triggered(decision["reason"])
            return decision
        
        # Check for critical phase failures
        critical_failures = [p for p in failed_phases if p in self.critical_phases]
        if critical_failures:
            decision["action"] = "ABANDON"
            decision["reason"] = f"Critical phases failed: {', '.join(critical_failures)}"
            decision["abandon"] = True
            self.logger.set_abandon_triggered(decision["reason"])
            return decision
        
        # Check for multiple important phase failures
        important_failures = [p for p in failed_phases if p in self.important_phases]
        if len(important_failures) >= 2:
            decision["action"] = "ABANDON"
            decision["reason"] = f"Multiple important phases failed: {', '.join(important_failures)}"
            decision["abandon"] = True
            self.logger.set_abandon_triggered(decision["reason"])
            return decision
        
        # Check for single important phase failure
        if len(important_failures) == 1:
            decision["action"] = "PIVOT"
            decision["reason"] = f"Important phase failed: {important_failures[0]} - consider redesign"
            decision["pivot"] = True
            return decision
        
        # Check for multiple non-critical failures
        non_critical_failures = [p for p in failed_phases if p not in self.important_phases and p not in self.critical_phases]
        if len(non_critical_failures) >= 3:
            decision["action"] = "PIVOT"
            decision["reason"] = f"Multiple non-critical phases failed: {', '.join(non_critical_failures)} - consider fixes"
            decision["pivot"] = True
            return decision
        
        # All passed or minor failures
        if num_failures == 0:
            decision["action"] = "CONTINUE"
            decision["reason"] = "All tests passed"
        elif num_failures <= 2:
            decision["action"] = "CONTINUE"
            decision["reason"] = f"Minor failures in {', '.join(failed_phases)} - acceptable"
        else:
            decision["action"] = "PIVOT"
            decision["reason"] = f"Multiple failures: {', '.join(failed_phases)} - consider fixes"
            decision["pivot"] = True
        
        return decision
    
    def get_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """
        Get recommendations based on test results.
        
        Args:
            results: Dictionary of phase results
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Phase-specific recommendations
        if not results.get('A', {}).get("passed", True):
            recommendations.append("Phase A: System generates fluent output from nonsense - fix Phase 9 fluency gate")
        
        if not results.get('B', {}).get("passed", True):
            recommendations.append("Phase B: System shows discrete changes under perturbation - improve stability")
        
        if not results.get('C', {}).get("passed", True):
            recommendations.append("Phase C: System relies on surface similarity - improve structural understanding")
        
        if not results.get('D', {}).get("passed", True):
            recommendations.append("Phase D: System generates output from impossible worlds - fix Phase 5 entropy handling")
        
        if not results.get('E', {}).get("passed", True):
            recommendations.append("Phase E: System silently merges conflicting roles - fix Phase 7 role assignment")
        
        if not results.get('F', {}).get("passed", True):
            recommendations.append("Phase F: System averages constraints instead of detecting drift - fix Phase 8")
        
        if not results.get('G', {}).get("passed", True):
            recommendations.append("Phase G: System shows filler behavior during streaming - fix Phase 9 streaming")
        
        if not results.get('H', {}).get("passed", True):
            recommendations.append("Phase H: System has poor refusal quality - improve refusal mechanisms")
        
        if not results.get('I', {}).get("passed", True):
            recommendations.append("Phase I: KILL SWITCH - System generates despite meaning denial - ABANDON PROJECT")
        
        return recommendations
