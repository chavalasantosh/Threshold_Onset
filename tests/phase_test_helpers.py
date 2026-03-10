"""
Phase 0–3 helpers for tests that need run_phase0_finite, run_phase1, run_phase2_multi_run, run_phase3_multi_run.

These are not exported by main.py (which runs subprocesses). Tests import from here.
"""

import hashlib
import sys
from pathlib import Path

# Ensure project root is on path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Fixed test text for deterministic Phase 0 output
_PHASE0_TEST_TEXT = "The quick brown fox jumps over the lazy dog."


class _TokenAction:
    """Minimal Phase 0 action: tokens -> numeric residues (hash-based)."""

    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.index = 0

    def __call__(self):
        if self.index >= len(self.tokens):
            self.index = 0
        token = self.tokens[self.index]
        self.index += 1
        h = hashlib.sha256(token.encode("utf-8")).hexdigest()[:8]
        return float(int(h, 16) % 10000) / 10000.0


def _tokenize_to_actions(text: str, tokenization_method: str = "word"):
    """Tokenize text and return Phase 0 action + token list."""
    try:
        from integration.unified_system import tokenize_text_to_actions
        return tokenize_text_to_actions(text, tokenization_method)
    except (ImportError, TypeError):
        try:
            from integration.run_complete import tokenize_text, TokenAction
            tokens = tokenize_text(text, tokenization_method)
            action = TokenAction(tokens)
        except ImportError:
            tokens = text.split() or [""]
            action = _TokenAction(tokens)
        return action, tokens


def run_phase0_from_text(text: str, tokenization_method: str = "word"):
    """Run Phase 0 with given text. Returns (residues, tokens)."""
    from threshold_onset.phase0.phase0 import phase0
    action, tokens = _tokenize_to_actions(text, tokenization_method)
    residues = []
    for trace, _, _ in phase0([action], steps=len(tokens) * 2):
        residues.append(trace)
    return residues, tokens


def run_phase0_finite(tokenization_method: str = "word"):
    """
    Run Phase 0 with fixed test text. Returns residues only.
    Used by test_phase3_convergence and test_phase4_freeze.
    """
    from threshold_onset.phase0.phase0 import phase0

    action, tokens = _tokenize_to_actions(_PHASE0_TEST_TEXT, tokenization_method)
    residues = []
    for trace, _, _ in phase0([action], steps=len(tokens) * 2):
        residues.append(trace)
    return residues


def run_phase1(residues):
    """Run Phase 1 boundary detection."""
    from threshold_onset.phase1.phase1 import phase1
    return phase1(residues)


def run_phase2_multi_run(residue_sequences, phase1_metrics_list):
    """Run Phase 2 identity discovery (multi-run)."""
    from threshold_onset.phase2.phase2 import phase2_multi_run
    return phase2_multi_run(residue_sequences, phase1_metrics_list)


def run_phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics):
    """Run Phase 3 relation mapping (multi-run)."""
    from threshold_onset.phase3.phase3 import phase3_multi_run
    return phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)
