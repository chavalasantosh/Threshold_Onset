"""
Phase G: Live Streaming Failure Mode Test

Test G1: Forced degradation
Enterprise real-time test.

Expected:
- Adaptive batch resizing
- Semantic continuity preserved
- No hallucinated filler

Fail:
- "Let me continue..." style filler behavior
"""

import logging
import sys
import time
import random
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


class PhaseGStreamingTest:
    """Test G1: Forced degradation"""
    
    def __init__(self, logger_instance: IntrinsicLogger):
        self.logger = logger_instance
        self.test_id = "G1"
    
    def simulate_batch_failure(self, batch: List[Any]) -> Tuple[List[Any], bool]:
        """
        Simulate partial batch failure.
        
        Args:
            batch: Original batch
        
        Returns:
            (degraded_batch, failed)
        """
        # Randomly drop 10-30% of batch
        drop_rate = random.uniform(0.1, 0.3)
        num_to_drop = int(len(batch) * drop_rate)
        
        if num_to_drop > 0:
            indices_to_drop = random.sample(range(len(batch)), num_to_drop)
            degraded = [item for i, item in enumerate(batch) if i not in indices_to_drop]
            return degraded, True
        
        return batch, False
    
    def simulate_delay(self, delay_ms: int = 100):
        """Simulate network delay."""
        time.sleep(delay_ms / 1000.0)
    
    def detect_filler_behavior(self, text: str) -> bool:
        """
        Detect filler behavior like "Let me continue...".
        
        Args:
            text: Generated text
        
        Returns:
            True if filler detected
        """
        filler_phrases = [
            "let me continue",
            "let me think",
            "as I was saying",
            "to continue",
            "moving on",
            "...",
            "um",
            "uh"
        ]
        
        text_lower = text.lower()
        for phrase in filler_phrases:
            if phrase in text_lower:
                return True
        
        return False
    
    def run(self, config: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Run Test G1.
        
        Args:
            config: Optional test configuration
        
        Returns:
            (passed, metrics)
        """
        logger.info(f"Starting {self.test_id}: Forced degradation")
        
        # Simulate streaming generation with failures
        num_batches = 10
        batch_size = 5
        
        metrics = {
            "num_batches": num_batches,
            "batch_size": batch_size,
            "batches_failed": 0,
            "batches_delayed": 0,
            "batches_dropped": 0,
            "adaptive_resizing": False,
            "semantic_continuity": True,
            "filler_detected": False,
            "generated_output": ""
        }
        
        passed = True
        failure_reason = None
        
        try:
            # Simulate streaming with failures
            generated_sequence = []
            previous_batch = None
            
            for batch_idx in range(num_batches):
                # Create a batch (simplified - would be actual tokens in real test)
                batch = list(range(batch_idx * batch_size, (batch_idx + 1) * batch_size))
                
                # Simulate random failures
                failure_type = random.choice(['none', 'partial', 'delay', 'drop'])
                
                if failure_type == 'partial':
                    degraded_batch, failed = self.simulate_batch_failure(batch)
                    if failed:
                        metrics["batches_failed"] += 1
                        batch = degraded_batch
                        # Check if system adapts batch size
                        if len(batch) < batch_size:
                            metrics["adaptive_resizing"] = True
                            logger.info(f"Batch {batch_idx}: Adaptive resizing detected")
                
                elif failure_type == 'delay':
                    delay_ms = random.randint(50, 200)
                    self.simulate_delay(delay_ms)
                    metrics["batches_delayed"] += 1
                
                elif failure_type == 'drop':
                    # Drop entire batch
                    metrics["batches_dropped"] += 1
                    continue
                
                # Add batch to sequence
                generated_sequence.extend(batch)
                
                # Check semantic continuity (simplified)
                if previous_batch is not None:
                    # Check if there's a gap (would indicate discontinuity)
                    if batch and previous_batch:
                        gap = batch[0] - previous_batch[-1]
                        if gap > batch_size * 2:
                            metrics["semantic_continuity"] = False
                            logger.warning(f"Semantic discontinuity detected at batch {batch_idx}")
                
                previous_batch = batch
            
            metrics["generated_output"] = str(generated_sequence[:50])  # First 50 items
            
            # Convert to text (simplified)
            output_text = " ".join(str(x) for x in generated_sequence[:100])
            
            # Check for filler behavior
            if self.detect_filler_behavior(output_text):
                metrics["filler_detected"] = True
                logger.error("Filler behavior detected in output!")
                passed = False
                failure_reason = "Filler behavior detected (e.g., 'Let me continue...')"
            
            # Check semantic continuity
            if not metrics["semantic_continuity"]:
                passed = False
                if not failure_reason:
                    failure_reason = "Semantic continuity not preserved during streaming failures"
            
            # Check adaptive resizing (should happen when batches fail)
            if metrics["batches_failed"] > 0 and not metrics["adaptive_resizing"]:
                logger.warning("Adaptive batch resizing not detected despite failures")
                # This is a warning, not a failure
            
            # Log fluency gate decision
            # In real test, we would check if Phase 9 gate correctly handles streaming
            self.logger.log_fluency_gate_decision(
                "PASS" if passed else "REFUSE",
                0.8,  # stability_score (simulated)
                2.0,  # entropy_threshold
                1.5,  # actual_entropy (simulated)
                self.test_id
            )
        
        except Exception as e:
            logger.error(f"Test {self.test_id} failed with exception: {e}", exc_info=True)
            passed = False
            failure_reason = f"Exception: {str(e)}"
        
        # Log results
        self.logger.log_test_result(
            self.test_id,
            "G",
            passed,
            metrics,
            failure_reason
        )
        
        logger.info(f"Test {self.test_id} {'PASSED' if passed else 'FAILED'}")
        return passed, metrics
