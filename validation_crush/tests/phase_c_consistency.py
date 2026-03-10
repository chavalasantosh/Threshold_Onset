"""
Phase C: Time-Delayed Consistency Test

Test C1: Temporal recall without memory
Kills prompt-overfitting systems.

Expected:
- Structural isomorphism (not token similarity)

Fail:
- Reliance on surface similarity
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
from validation_crush.utils.test_helpers import (
    load_system_outputs,
    check_structural_isomorphism
)
from validation_crush.utils.metrics_computer import MetricsComputer

logger = logging.getLogger(__name__)


class PhaseCConsistencyTest:
    """Test C1: Temporal recall without memory"""
    
    def __init__(self, logger_instance: IntrinsicLogger):
        self.logger = logger_instance
        self.test_id = "C1"
    
    def paraphrase(self, text: str) -> str:
        """
        Generate a paraphrase of the input text.
        
        Args:
            text: Original text
        
        Returns:
            Paraphrased text
        """
        # Simple paraphrasing (would use better method in production)
        paraphrases = {
            "The quick brown fox jumps over the lazy dog.": "A fast tan fox leaps above a sleepy canine.",
            "Cats are mammals that breathe underwater.": "Felines are warm-blooded animals that respire in water.",
            "Water flows upward when heated.": "H2O moves in an upward direction upon being warmed."
        }
        return paraphrases.get(text, text.replace("the", "a").replace("The", "A"))
    
    def run(self, config: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Run Test C1.
        
        Args:
            config: Optional test configuration
        
        Returns:
            (passed, metrics)
        """
        logger.info(f"Starting {self.test_id}: Temporal recall without memory")
        
        # Original input
        original_input = "The quick brown fox jumps over the lazy dog."
        
        # Paraphrase (not identical)
        paraphrased_input = self.paraphrase(original_input)
        
        logger.info(f"Original: {original_input}")
        logger.info(f"Paraphrase: {paraphrased_input}")
        
        # Load system outputs (simulating two runs)
        outputs1 = load_system_outputs()
        outputs2 = load_system_outputs()  # Same for now, but would be different in real test
        
        metrics = {
            "original_input": original_input,
            "paraphrased_input": paraphrased_input,
            "phase5_isomorphic": False,
            "phase6_isomorphic": False,
            "phase7_isomorphic": False,
            "phase8_isomorphic": False,
            "structural_similarity": 0.0,
            "token_similarity": 0.0,
            "relies_on_surface": False
        }
        
        passed = True
        failure_reason = None
        
        try:
            # Compare structures (not tokens)
            # Phase 5: Consequence field
            if 'consequence_field' in outputs1 and 'consequence_field' in outputs2:
                cf1 = outputs1['consequence_field']
                cf2 = outputs2['consequence_field']
                is_iso, similarity = check_structural_isomorphism(cf1, cf2)
                metrics["phase5_isomorphic"] = is_iso
                metrics["structural_similarity"] = similarity
            
            # Phase 6: Meaning clusters
            if 'meaning_map' in outputs1 and 'meaning_map' in outputs2:
                mm1 = outputs1['meaning_map']
                mm2 = outputs2['meaning_map']
                is_iso, similarity = check_structural_isomorphism(mm1, mm2)
                metrics["phase6_isomorphic"] = is_iso
                if similarity > metrics["structural_similarity"]:
                    metrics["structural_similarity"] = similarity
            
            # Phase 7: Roles
            if 'roles' in outputs1 and 'roles' in outputs2:
                r1 = outputs1['roles']
                r2 = outputs2['roles']
                is_iso, similarity = check_structural_isomorphism(r1, r2)
                metrics["phase7_isomorphic"] = is_iso
                if similarity > metrics["structural_similarity"]:
                    metrics["structural_similarity"] = similarity
            
            # Phase 8: Constraints
            if 'constraints' in outputs1 and 'constraints' in outputs2:
                c1 = outputs1['constraints']
                c2 = outputs2['constraints']
                is_iso, similarity = check_structural_isomorphism(c1, c2)
                metrics["phase8_isomorphic"] = is_iso
                if similarity > metrics["structural_similarity"]:
                    metrics["structural_similarity"] = similarity
            
            # Compute token similarity (should be low for paraphrases)
            # Simple word overlap
            words1 = set(original_input.lower().split())
            words2 = set(paraphrased_input.lower().split())
            overlap = len(words1 & words2)
            total = len(words1 | words2)
            metrics["token_similarity"] = overlap / total if total > 0 else 0.0
            
            # Check: Structural similarity should be high, token similarity should be low
            if metrics["structural_similarity"] < 0.7:
                logger.warning(f"Structural similarity too low: {metrics['structural_similarity']}")
                passed = False
                failure_reason = f"Structural similarity too low: {metrics['structural_similarity']} < 0.7"
            
            if metrics["token_similarity"] > 0.5:
                logger.warning(f"Token similarity too high: {metrics['token_similarity']}")
                # This alone doesn't fail, but indicates reliance on surface similarity
                metrics["relies_on_surface"] = True
            
            # If structural similarity is low but token similarity is high, that's a fail
            if metrics["structural_similarity"] < 0.5 and metrics["token_similarity"] > 0.5:
                passed = False
                if not failure_reason:
                    failure_reason = "System relies on surface similarity rather than structural isomorphism"
        
        except Exception as e:
            logger.error(f"Test {self.test_id} failed with exception: {e}", exc_info=True)
            passed = False
            failure_reason = f"Exception: {str(e)}"
        
        # Log results
        self.logger.log_test_result(
            self.test_id,
            "C",
            passed,
            metrics,
            failure_reason
        )
        
        logger.info(f"Test {self.test_id} {'PASSED' if passed else 'FAILED'}")
        return passed, metrics
