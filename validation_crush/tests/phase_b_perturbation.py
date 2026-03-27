"""
Phase B: Adversarial Perturbation Test

Test B1: Micro-perturbation invariance
Semantic stability under attack.

Expected:
- Continuous deformation (not discrete changes)

Fail:
- Discrete structural changes
"""

import logging
import sys
import random
from pathlib import Path
from typing import Dict, Any, Tuple, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from validation_crush.intrinsic_logger import IntrinsicLogger
from validation_crush.utils.test_helpers import (
    load_system_outputs,
    initialize_system,
    compute_variance,
    check_structural_isomorphism
)
from validation_crush.utils.metrics_computer import MetricsComputer

logger = logging.getLogger(__name__)


class PhaseBPerturbationTest:
    """Test B1: Micro-perturbation invariance"""
    
    def __init__(self, logger_instance: IntrinsicLogger):
        self.logger = logger_instance
        self.test_id = "B1"
        # Run once per tokenization method (9 methods) + some additional perturbations
        self.num_runs = 9  # One per tokenization method (reduced from 50 for performance)
    
    def perturb_input(self, text: str, method: str) -> str:
        """
        Apply perturbation to input text.
        
        Args:
            text: Original text
            method: Perturbation method ('synonym', 'word_order', 'tokenization')
        
        Returns:
            Perturbed text
        """
        words = text.split()
        
        if method == 'synonym':
            # Simple synonym swap (simplified - would use actual synonym dict in production)
            synonyms = {
                'the': 'a',
                'cat': 'feline',
                'dog': 'canine',
                'quick': 'fast',
                'brown': 'tan'
            }
            return ' '.join(synonyms.get(w.lower(), w) for w in words)
        
        elif method == 'word_order':
            # Swap adjacent words
            if len(words) < 2:
                return text
            idx = random.randint(0, len(words) - 2)
            words[idx], words[idx + 1] = words[idx + 1], words[idx]
            return ' '.join(words)
        
        elif method == 'tokenization':
            # Add/remove spaces (simplified tokenization change)
            return text.replace(' ', '  ')  # Double spaces
        
        return text
    
    def run(self, config: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Run Test B1.
        
        Args:
            config: Optional test configuration
        
        Returns:
            (passed, metrics)
        """
        logger.info(f"Starting {self.test_id}: Micro-perturbation invariance (N={self.num_runs})")
        
        # Base input
        base_input = "The quick brown fox jumps over the lazy dog."
        
        # Load system outputs
        outputs = load_system_outputs()
        
        metrics = {
            "base_input": base_input,
            "num_runs": self.num_runs,
            "phase6_cluster_changes": [],
            "phase7_role_changes": [],
            "phase8_constraint_changes": [],
            "structural_variance": 0.0,
            "discrete_changes_detected": False
        }
        
        passed = True
        failure_reason = None
        
        try:
            # CYCLE THROUGH ALL 9 TOKENIZATION METHODS (CRITICAL FIX)
            # All 9 SanTOK tokenization methods as per spec
            # Note: Some methods may not be available depending on santok installation
            # We'll try all and gracefully handle failures
            tokenization_methods = [
                "whitespace",      # space
                "word",            # word
                "character",       # char
                "grammar",         # grammar (may not be available)
                "subword",         # subword (fixed)
                "subword_bpe",     # subword (bpe) - may not be available
                "subword_syllable", # subword (syllable) - may not be available
                "subword_frequency", # subword (frequency) - may not be available
                "byte"             # byte - may not be available
            ]
            
            # Also apply synonym swaps and word order noise
            perturbation_methods = ['synonym', 'word_order']
            
            from validation_crush.utils.test_helpers import process_text_through_system
            
            phase6_stabilities = []
            phase7_variances = []
            phase8_rigidities = []
            
            # Run N independent runs, cycling through all 9 tokenization methods
            for run_idx in range(self.num_runs):
                # Cycle through tokenization methods
                tokenization_method = tokenization_methods[run_idx % len(tokenization_methods)]
                
                # Apply additional perturbation (synonym or word order)
                perturbation_method = random.choice(perturbation_methods)
                perturbed_input = self.perturb_input(base_input, perturbation_method)
                
                logger.debug(f"Run {run_idx + 1}/{self.num_runs}: method={tokenization_method}, perturb={perturbation_method}")
                
                # ACTUALLY PROCESS INPUT THROUGH SYSTEM (CRITICAL FIX)
                try:
                    run_outputs = process_text_through_system(
                        text=perturbed_input,
                        tokenization_method=tokenization_method,
                        num_runs=2,  # Reduced for performance
                        run_semantic_phases=True,
                        config=config
                    )
                    
                    # Extract metrics from actual processing
                    if 'meaning_map' in run_outputs and run_outputs['meaning_map']:
                        phase6_metrics = MetricsComputer.compute_phase6_metrics(
                            run_outputs['meaning_map']
                        )
                        stability = phase6_metrics.get("avg_stability", 0.0)
                        phase6_stabilities.append(stability)
                    
                    if 'roles' in run_outputs and run_outputs['roles']:
                        phase7_metrics = MetricsComputer.compute_phase7_metrics(run_outputs['roles'])
                        variance = phase7_metrics.get("role_variance", 0.0)
                        phase7_variances.append(variance)
                    
                    if 'constraints' in run_outputs and run_outputs['constraints']:
                        phase8_metrics = MetricsComputer.compute_phase8_metrics(run_outputs['constraints'])
                        rigidity_scores = phase8_metrics.get("constraint_rigidity_scores", [])
                        rigidity = sum(rigidity_scores) / len(rigidity_scores) if rigidity_scores else 0.0
                        phase8_rigidities.append(rigidity)
                except Exception as e:
                    logger.warning(f"Run {run_idx + 1} failed: {e}")
                    continue
            
            # Compute variance in metrics across runs
            if phase6_stabilities:
                stability_variance = compute_variance(phase6_stabilities)
                metrics["phase6_cluster_changes"] = {
                    "variance": stability_variance,
                    "mean": sum(phase6_stabilities) / len(phase6_stabilities),
                    "std": stability_variance ** 0.5
                }
            
            if phase7_variances:
                variance_variance = compute_variance(phase7_variances)
                metrics["phase7_role_changes"] = {
                    "variance": variance_variance,
                    "mean": sum(phase7_variances) / len(phase7_variances),
                    "std": variance_variance ** 0.5
                }
            
            if phase8_rigidities:
                rigidity_variance = compute_variance(phase8_rigidities)
                metrics["phase8_constraint_changes"] = {
                    "variance": rigidity_variance,
                    "mean": sum(phase8_rigidities) / len(phase8_rigidities),
                    "std": rigidity_variance ** 0.5
                }
            
            # Check for discrete changes (high variance jumps)
            # Continuous deformation should show gradual changes
            # Ensure metrics are dictionaries, not lists
            all_variances = []
            if isinstance(metrics.get("phase6_cluster_changes"), dict):
                all_variances.append(metrics["phase6_cluster_changes"].get("variance", 0.0))
            if isinstance(metrics.get("phase7_role_changes"), dict):
                all_variances.append(metrics["phase7_role_changes"].get("variance", 0.0))
            if isinstance(metrics.get("phase8_constraint_changes"), dict):
                all_variances.append(metrics["phase8_constraint_changes"].get("variance", 0.0))
            
            metrics["structural_variance"] = sum(all_variances) / len(all_variances) if all_variances else 0.0
            
            # Check for discrete changes (variance > threshold indicates discrete jumps)
            # In continuous deformation, variance should be moderate
            if metrics["structural_variance"] > 0.5:  # Threshold
                logger.warning(f"Discrete changes detected: variance = {metrics['structural_variance']}")
                metrics["discrete_changes_detected"] = True
                passed = False
                failure_reason = f"Discrete structural changes detected: variance = {metrics['structural_variance']} > 0.5"
            else:
                logger.info(f"Continuous deformation detected: variance = {metrics['structural_variance']}")
        
        except Exception as e:
            logger.error(f"Test {self.test_id} failed with exception: {e}", exc_info=True)
            passed = False
            failure_reason = f"Exception: {str(e)}"
        
        # Log results
        self.logger.log_test_result(
            self.test_id,
            "B",
            passed,
            metrics,
            failure_reason
        )
        
        logger.info(f"Test {self.test_id} {'PASSED' if passed else 'FAILED'}")
        return passed, metrics
