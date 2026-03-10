#!/usr/bin/env python3
"""
THRESHOLD_ONSET — CRUSH-TO-DEATH VALIDATION PROTOCOL

Enterprise-grade validation orchestrator.
Runs all test phases and generates intrinsic_eval_report.json.
"""

import sys
import argparse
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from validation_crush.intrinsic_logger import IntrinsicLogger
from validation_crush.decision_framework import DecisionFramework
from validation_crush.tests.phase_a_baseline import PhaseABaselineTest
from validation_crush.tests.phase_b_perturbation import PhaseBPerturbationTest
from validation_crush.tests.phase_c_consistency import PhaseCConsistencyTest
from validation_crush.tests.phase_d_causal import PhaseDCausalTest
from validation_crush.tests.phase_e_role_collapse import PhaseERoleCollapseTest
from validation_crush.tests.phase_f_constraint_inversion import PhaseFConstraintInversionTest
from validation_crush.tests.phase_g_streaming import PhaseGStreamingTest
from validation_crush.tests.phase_h_red_team import PhaseHRedTeamTest
from validation_crush.tests.phase_i_kill_switch import PhaseIKillSwitchTest

# Configure logging
log_file = Path(__file__).parent / 'validation.log'
# Use UTF-8 encoding for file handler to avoid Windows encoding issues
file_handler = logging.FileHandler(log_file, encoding='utf-8')
stream_handler = logging.StreamHandler()
# Set encoding for stream handler if possible (Windows may still use cp1252)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger(__name__)


class CrushProtocol:
    """Main validation orchestrator."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize crush protocol.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = IntrinsicLogger()
        self.decision_framework = DecisionFramework(self.logger)
        
        # Initialize all test phases
        self.tests = {
            'A': PhaseABaselineTest(self.logger),
            'B': PhaseBPerturbationTest(self.logger),
            'C': PhaseCConsistencyTest(self.logger),
            'D': PhaseDCausalTest(self.logger),
            'E': PhaseERoleCollapseTest(self.logger),
            'F': PhaseFConstraintInversionTest(self.logger),
            'G': PhaseGStreamingTest(self.logger),
            'H': PhaseHRedTeamTest(self.logger),
            'I': PhaseIKillSwitchTest(self.logger)
        }
    
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from file."""
        if config_path is None:
            return {}
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}")
            return {}
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def run_phase(self, phase: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Run a specific test phase.
        
        Args:
            phase: Phase letter (A-I)
        
        Returns:
            (passed, metrics)
        """
        phase = phase.upper()
        
        if phase not in self.tests:
            logger.error(f"Unknown phase: {phase}")
            return False, {"error": f"Unknown phase: {phase}"}
        
        logger.info("=" * 60)
        logger.info(f"Running Phase {phase}")
        logger.info("=" * 60)
        
        test = self.tests[phase]
        passed, metrics = test.run(self.config)
        
        return passed, metrics
    
    def run_all(self) -> Dict[str, Any]:
        """
        Run all test phases.
        
        Returns:
            Summary dictionary
        """
        logger.info("=" * 60)
        logger.info("THRESHOLD_ONSET — CRUSH-TO-DEATH VALIDATION")
        logger.info("=" * 60)
        logger.info("")
        
        results = {}
        all_passed = True
        
        # Run phases in order
        phases = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        
        for phase in phases:
            try:
                passed, metrics = self.run_phase(phase)
                results[phase] = {
                    "passed": passed,
                    "metrics": metrics
                }
                
                if not passed:
                    all_passed = False
                    logger.warning(f"Phase {phase} FAILED")
                    
                    # Check if we should stop early
                    if self.decision_framework.should_abandon(phase, metrics):
                        logger.critical(f"ABANDON triggered after Phase {phase}")
                        break
                else:
                    logger.info(f"Phase {phase} PASSED")
            
            except Exception as e:
                logger.error(f"Phase {phase} failed with exception: {e}", exc_info=True)
                results[phase] = {
                    "passed": False,
                    "error": str(e)
                }
                all_passed = False
        
        # Save report
        self.logger.save()
        
        # Get decision
        decision = self.decision_framework.get_decision(results)
        
        # Print summary
        self._print_summary(results, decision)
        
        return {
            "all_passed": all_passed,
            "results": results,
            "decision": decision
        }
    
    def _print_summary(self, results: Dict[str, Any], decision: Dict[str, Any]):
        """Print validation summary."""
        logger.info("")
        logger.info("=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)
        
        for phase, result in results.items():
            status = "[PASS]" if result.get("passed", False) else "[FAIL]"
            logger.info(f"Phase {phase}: {status}")
        
        logger.info("")
        logger.info(f"Decision: {decision.get('action', 'UNKNOWN')}")
        logger.info(f"Reason: {decision.get('reason', 'N/A')}")
        
        if decision.get("abandon"):
            logger.critical("=" * 60)
            logger.critical("ABANDON RECOMMENDED")
            logger.critical("=" * 60)
        
        logger.info("")
        logger.info(f"Report saved to: {self.logger.report_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="THRESHOLD_ONSET — CRUSH-TO-DEATH VALIDATION PROTOCOL"
    )
    parser.add_argument(
        '--phase',
        type=str,
        help='Run specific phase (A-I)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all phases'
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Create protocol
    protocol = CrushProtocol(config_path=args.config)
    
    if args.all:
        # Run all phases
        protocol.run_all()
    elif args.phase:
        # Run specific phase
        passed, metrics = protocol.run_phase(args.phase)
        protocol.logger.save()
        sys.exit(0 if passed else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
