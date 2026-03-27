#!/usr/bin/env python3
"""
Preference Learner

Minimal learning component that adjusts preference within immutable constraints.

Learning = persistent preference adjustment within valid space only.
"""

from collections import defaultdict


class PreferenceLearner:
    """
    Learns preference adjustments for allowed transitions only.

    Hard guarantees:
    - Never changes structure
    - Never allows forbidden paths
    - Only adjusts preference within E_allowed
    """

    def __init__(self, alpha=0.01, bound=1.0):
        """
        Args:
            alpha: Learning rate (very small, e.g. 0.01)
            bound: Maximum bias value (clipped to [-bound, +bound])
        """
        self.alpha = alpha
        self.bound = bound

        # Edge bias: {(current_symbol, next_symbol): bias_value}
        self.edge_bias = defaultdict(float)

        # Pending observations (accumulated before update)
        self.pending_observations = []

    def observe(self, transition, outcome):
        """
        Observe a transition outcome.

        Args:
            transition: (current_symbol, next_symbol) tuple
            outcome: "ok", "refusal", "dead_end", or "loop"
        """
        self.pending_observations.append((transition, outcome))

    def step(self):
        """
        Apply slow, bounded updates based on accumulated observations.
        Called occasionally (not every token).
        """
        if not self.pending_observations:
            return

        # Process observations
        for transition, outcome in self.pending_observations:
            current_bias = self.edge_bias[transition]

            if outcome == "ok":
                # Reinforce: successful transition
                delta = self.alpha * 0.1
            elif outcome in ("refusal", "dead_end", "loop"):
                # Penalize: transition led to failure
                delta = -self.alpha
            else:
                delta = 0.0

            # Update with clipping
            new_bias = current_bias + delta
            self.edge_bias[transition] = max(-self.bound, min(self.bound, new_bias))

        # Clear observations
        self.pending_observations = []

    def bias(self, transition):
        """
        Returns bias value for a transition.

        Args:
            transition: (current_symbol, next_symbol) tuple

        Returns:
            float: Bias value (default 0.0 if not observed)
        """
        return self.edge_bias.get(transition, 0.0)

    def get_stats(self):
        """Returns learning statistics (for debugging)."""
        if not self.edge_bias:
            return {"total_edges": 0, "avg_bias": 0.0}

        biases = list(self.edge_bias.values())
        return {
            "total_edges": len(self.edge_bias),
            "avg_bias": sum(biases) / len(biases),
            "min_bias": min(biases),
            "max_bias": max(biases)
        }
