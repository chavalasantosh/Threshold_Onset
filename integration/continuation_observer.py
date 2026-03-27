#!/usr/bin/env python3
"""
Continuation Observer

A recorder of failed continuations under existing constraints.

This does NOT:
- Add meaning
- Interpret anything
- Create new structure
- Add a new phase

This DOES:
- Continue tokenization after Phase 4
- Check if continuations are possible given existing structure
- Record refusals when continuations fail
- Record facts only (no interpretation)

कार्य (kārya) happens before ज्ञान (jñāna)
"""

import sys
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
# Use internal pip-installed modules: santok, santek, somaya
# These are our own projects: pip install santok, pip install santek, pip install somaya


class ContinuationRefusal:
    """
    Records a single refusal event.

    No interpretation. Just facts.
    """
    def __init__(self, step_index, current_symbol, attempted_next_symbol, reason, relation_exists):
        """
        Args:
            step_index: Position in continuation sequence
            current_symbol: Current identity symbol (from Phase 4)
            attempted_next_symbol: Attempted next identity symbol (from Phase 4)
            reason: Reason for refusal (plain text, no interpretation)
            relation_exists: Boolean - does relation exist in graph (mechanical check)
        """
        self.step_index = step_index
        self.current_symbol = current_symbol
        self.attempted_next_symbol = attempted_next_symbol
        self.reason = reason
        self.relation_exists = relation_exists

    def to_dict(self):
        """Convert to plain dictionary (no interpretation)."""
        return {
            'step_index': self.step_index,
            'current_symbol': self.current_symbol,
            'attempted_next_symbol': self.attempted_next_symbol,
            'reason_for_refusal': self.reason,
            'relation_exists': self.relation_exists
        }


class ContinuationObserver:
    """
    Observes continuation after Phase 4 and records refusals.

    Minimal. Mechanical. Honest.
    """

    def __init__(self, phase4_output, phase3_metrics, phase2_metrics):
        """
        Initialize observer with Phase 4 output and Phase 3 structure.

        Args:
            phase4_output: Phase 4 symbol mappings
            phase3_metrics: Phase 3 relation metrics (contains graph structure)
            phase2_metrics: Phase 2 identity metrics (for residue-to-identity mapping)
        """
        self.phase4_output = phase4_output
        self.phase3_metrics = phase3_metrics
        self.phase2_metrics = phase2_metrics

        # Extract structure from Phase 4
        self.identity_to_symbol = phase4_output.get('identity_to_symbol', {})
        self.symbol_to_identity = phase4_output.get('symbol_to_identity', {})

        # Extract graph structure from Phase 3
        self.graph_nodes = phase3_metrics.get('graph_nodes', set())
        self.graph_edges = phase3_metrics.get('graph_edges', set())

        # Build adjacency from edges (for fast lookup)
        self.adjacency = self._build_adjacency()

        # Store refusals
        self.refusals = []

    def _build_adjacency(self):
        """Build adjacency list from graph edges."""
        adjacency = {}
        for node in self.graph_nodes:
            adjacency[node] = set()

        for edge in self.graph_edges:
            if len(edge) == 2:
                hash1, hash2 = edge
                adjacency[hash1].add(hash2)
                adjacency[hash2].add(hash1)

        return adjacency

    def _residue_to_identity_hash(self, residue):
        """
        Map residue to identity hash.

        In Phase 2, residues form segments, and segments map to identities.
        For continuation, we need to map a residue back to an identity.

        This is approximate - we match residues to existing segments.
        Mechanical only - no interpretation.
        """
        # Extract persistent segments from Phase 2
        persistent_segment_hashes = self.phase2_metrics.get('persistent_segment_hashes', [])
        identity_mappings = self.phase2_metrics.get('identity_mappings', {})

        if not persistent_segment_hashes and not identity_mappings:
            return None

        # Simple approach: use residue value to select an identity
        # This is mechanical - we're not interpreting what the residue "means"
        # We're just deterministically mapping it to an existing identity

        # Get all identity hashes
        identity_hashes = set()
        if persistent_segment_hashes:
            # These are segment hashes that might map to identities
            for seg_hash in persistent_segment_hashes:
                if seg_hash in identity_mappings:
                    identity_hashes.add(identity_mappings[seg_hash])

        # Also add direct identity hash values from mappings
        identity_hashes.update(identity_mappings.values())

        if not identity_hashes:
            return None

        # Deterministic mapping: use residue value to select identity
        # This is not semantic - just mechanical selection
        identity_list = list(identity_hashes)
        residue_int = int(abs(residue * 10000)) % len(identity_list)
        return identity_list[residue_int]

    def _identity_hash_to_symbol(self, identity_hash):
        """Convert identity hash to Phase 4 symbol."""
        return self.identity_to_symbol.get(identity_hash)

    def _check_transition_allowed(self, from_identity_hash, to_identity_hash):
        """
        Check if transition from one identity to another is allowed.

        Based on Phase 3 graph edges - if edge exists, transition is allowed.
        """
        if from_identity_hash not in self.adjacency:
            return False

        return to_identity_hash in self.adjacency[from_identity_hash]

    def observe_continuation(self, token_stream, max_steps=100):
        """
        Observe continuation of token stream after Phase 4.

        Args:
            token_stream: Iterator of tokens (continuing from after Phase 4)
            max_steps: Maximum number of continuation steps to observe

        Returns:
            List of ContinuationRefusal objects
        """
        from integration.unified_system import TokenAction

        # Convert tokens to residues (same as Phase 0)
        tokens = list(token_stream)
        action = TokenAction(tokens)

        # Track current identity
        current_identity_hash = None
        current_symbol = None
        step_index = 0

        # Continue observing
        for step in range(max_steps):
            if step >= len(tokens):
                # Reached end of token stream
                break

            # Get residue from token
            residue = action()

            # Map residue to identity hash
            next_identity_hash = self._residue_to_identity_hash(residue)

            if next_identity_hash is None:
                # Cannot map residue to identity
                # This is not a refusal - just means identity not found
                continue

            # Convert identity hash to symbol
            next_symbol = self._identity_hash_to_symbol(next_identity_hash)

            if next_symbol is None:
                # Identity exists but has no symbol (shouldn't happen if Phase 4 worked)
                continue

            # Check transition
            if current_identity_hash is not None:
                # Check if transition from current to next is allowed
                transition_allowed = self._check_transition_allowed(
                    current_identity_hash,
                    next_identity_hash
                )

                if not transition_allowed:
                    # REFUSAL: Transition is not allowed
                    reason = "no_persistent_relation"
                    # Mechanical check: does relation exist in graph?
                    relation_exists = next_identity_hash in self.adjacency.get(current_identity_hash, set())
                    refusal = ContinuationRefusal(
                        step_index=step_index,
                        current_symbol=current_symbol,
                        attempted_next_symbol=next_symbol,
                        reason=reason,
                        relation_exists=relation_exists
                    )
                    self.refusals.append(refusal)
                    # Don't update current - refusal blocks continuation
                    continue

            # Transition allowed (or no current identity)
            # Update current state
            current_identity_hash = next_identity_hash
            current_symbol = next_symbol
            step_index += 1

        return self.refusals

    def get_refusals(self):
        """Get list of recorded refusals."""
        return self.refusals

    def get_refusals_dict(self):
        """Get refusals as list of dictionaries (for output)."""
        return [refusal.to_dict() for refusal in self.refusals]


def observe_continuation_refusals(
    phase4_output,
    phase3_metrics,
    phase2_metrics,
    continuation_tokens,
    max_steps=100
):
    """
    Main function to observe continuation refusals.

    Args:
        phase4_output: Phase 4 symbol mappings
        phase3_metrics: Phase 3 relation metrics
        phase2_metrics: Phase 2 identity metrics
        continuation_tokens: List of tokens to continue with
        max_steps: Maximum steps to observe

    Returns:
        List of refusal dictionaries
    """
    observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)
    observer.observe_continuation(continuation_tokens, max_steps=max_steps)
    return observer.get_refusals_dict()
