"""
Intrinsic Evaluation Logger

Enterprise-grade logging system for THRESHOLD_ONSET validation.
Generates intrinsic_eval_report.json with all required metrics.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class IntrinsicLogger:
    """
    Logs intrinsic evaluation metrics for THRESHOLD_ONSET validation.
    
    Required outputs:
    - Threshold crossings per phase
    - Entropy curves (Phase 5)
    - Cluster stability (Phase 6)
    - Role variance (Phase 7)
    - Constraint rigidity (Phase 8)
    - Fluency gate decision (Phase 9)
    """
    
    def __init__(self, report_path: Optional[Path] = None):
        """
        Initialize intrinsic logger.
        
        Args:
            report_path: Path to save intrinsic_eval_report.json
        """
        if report_path is None:
            report_path = Path(__file__).parent / "reports" / "intrinsic_eval_report.json"
        
        self.report_path = Path(report_path)
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize report structure
        self.report: Dict[str, Any] = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "system": "THRESHOLD_ONSET",
                "validation_type": "crush_to_death"
            },
            "phases": {
                "phase5": {
                    "threshold_crossings": [],
                    "entropy_curves": [],
                    "metrics": {}
                },
                "phase6": {
                    "threshold_crossings": [],
                    "cluster_stability": [],
                    "metrics": {}
                },
                "phase7": {
                    "threshold_crossings": [],
                    "role_variance": [],
                    "metrics": {}
                },
                "phase8": {
                    "threshold_crossings": [],
                    "constraint_rigidity": [],
                    "metrics": {}
                },
                "phase9": {
                    "threshold_crossings": [],
                    "fluency_gate_decisions": [],
                    "metrics": {}
                }
            },
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "abandon_triggered": False
            }
        }
    
    def log_threshold_crossing(
        self,
        phase: int,
        threshold_name: str,
        value: float,
        crossed: bool,
        test_id: Optional[str] = None
    ):
        """
        Log a threshold crossing event.
        
        Args:
            phase: Phase number (5-9)
            threshold_name: Name of the threshold
            value: Actual value
            crossed: Whether threshold was crossed
            test_id: Optional test identifier
        """
        phase_key = f"phase{phase}"
        if phase_key not in self.report["phases"]:
            self.report["phases"][phase_key] = {
                "threshold_crossings": [],
                "metrics": {}
            }
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "threshold": threshold_name,
            "value": value,
            "crossed": crossed,
            "test_id": test_id
        }
        
        self.report["phases"][phase_key]["threshold_crossings"].append(entry)
    
    def log_entropy_curve(
        self,
        identity_hash: str,
        entropy_values: List[float],
        steps: List[int],
        test_id: Optional[str] = None
    ):
        """
        Log entropy curve for Phase 5.
        
        Args:
            identity_hash: Identity hash
            entropy_values: List of entropy values over time
            steps: Corresponding step indices
            test_id: Optional test identifier
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "identity_hash": identity_hash,
            "entropy_curve": {
                "values": entropy_values,
                "steps": steps
            },
            "test_id": test_id
        }
        
        self.report["phases"]["phase5"]["entropy_curves"].append(entry)
    
    def log_cluster_stability(
        self,
        cluster_id: str,
        stability_score: float,
        cluster_size: int,
        identities: List[str],
        test_id: Optional[str] = None
    ):
        """
        Log cluster stability for Phase 6.
        
        Args:
            cluster_id: Cluster identifier
            stability_score: Stability score (0-1)
            cluster_size: Number of identities in cluster
            identities: List of identity hashes
            test_id: Optional test identifier
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "cluster_id": cluster_id,
            "stability_score": stability_score,
            "cluster_size": cluster_size,
            "identities": identities,
            "test_id": test_id
        }
        
        self.report["phases"]["phase6"]["cluster_stability"].append(entry)
    
    def log_role_variance(
        self,
        role_assignments: Dict[str, str],
        variance_score: float,
        test_id: Optional[str] = None
    ):
        """
        Log role variance for Phase 7.
        
        Args:
            role_assignments: Dict mapping cluster_id to role
            variance_score: Variance score (higher = more variance)
            test_id: Optional test identifier
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "role_assignments": role_assignments,
            "variance_score": variance_score,
            "test_id": test_id
        }
        
        self.report["phases"]["phase7"]["role_variance"].append(entry)
    
    def log_constraint_rigidity(
        self,
        constraint_id: str,
        rigidity_score: float,
        pattern: List[str],
        frequency: int,
        test_id: Optional[str] = None
    ):
        """
        Log constraint rigidity for Phase 8.
        
        Args:
            constraint_id: Constraint identifier
            rigidity_score: Rigidity score (0-1, higher = more rigid)
            pattern: Pattern sequence
            frequency: Pattern frequency
            test_id: Optional test identifier
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "constraint_id": constraint_id,
            "rigidity_score": rigidity_score,
            "pattern": pattern,
            "frequency": frequency,
            "test_id": test_id
        }
        
        self.report["phases"]["phase8"]["constraint_rigidity"].append(entry)
    
    def log_fluency_gate_decision(
        self,
        decision: str,  # "PASS", "REFUSE", "UNSTABLE"
        stability_score: float,
        entropy_threshold: float,
        actual_entropy: float,
        test_id: Optional[str] = None
    ):
        """
        Log fluency gate decision for Phase 9.
        
        Args:
            decision: Gate decision
            stability_score: Stability score
            entropy_threshold: Entropy threshold
            actual_entropy: Actual entropy value
            test_id: Optional test identifier
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "stability_score": stability_score,
            "entropy_threshold": entropy_threshold,
            "actual_entropy": actual_entropy,
            "test_id": test_id
        }
        
        self.report["phases"]["phase9"]["fluency_gate_decisions"].append(entry)
    
    def log_test_result(
        self,
        test_id: str,
        phase: str,
        passed: bool,
        metrics: Dict[str, Any],
        failure_reason: Optional[str] = None
    ):
        """
        Log test result.
        
        Args:
            test_id: Test identifier (e.g., "A1", "B1")
            phase: Phase letter (A-I)
            passed: Whether test passed
            metrics: Test-specific metrics
            failure_reason: Reason for failure if failed
        """
        if test_id not in self.report["tests"]:
            self.report["tests"][test_id] = {
                "phase": phase,
                "results": []
            }
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "passed": passed,
            "metrics": metrics,
            "failure_reason": failure_reason
        }
        
        self.report["tests"][test_id]["results"].append(result)
        
        # Update summary
        self.report["summary"]["total_tests"] += 1
        if passed:
            self.report["summary"]["passed"] += 1
        else:
            self.report["summary"]["failed"] += 1
    
    def set_abandon_triggered(self, reason: str):
        """
        Mark that abandon has been triggered.
        
        Args:
            reason: Reason for abandon
        """
        self.report["summary"]["abandon_triggered"] = True
        self.report["summary"]["abandon_reason"] = reason
        self.report["summary"]["abandon_timestamp"] = datetime.now().isoformat()
    
    def save(self):
        """Save report to JSON file."""
        self.report["metadata"]["updated_at"] = datetime.now().isoformat()
        
        with open(self.report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        logger.info(f"Intrinsic evaluation report saved to {self.report_path}")
    
    def load(self) -> Dict[str, Any]:
        """Load existing report from JSON file."""
        if not self.report_path.exists():
            logger.warning(f"Report file not found: {self.report_path}")
            return self.report
        
        with open(self.report_path, 'r') as f:
            self.report = json.load(f)
        
        logger.info(f"Loaded existing report from {self.report_path}")
        return self.report
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return self.report["summary"].copy()
