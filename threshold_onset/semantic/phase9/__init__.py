"""
Phase 9: Fluency Generator

Enterprise-grade fluent text generation.

CORRECTED: Experience table (not "learner"), prefix-match templates.
"""

from threshold_onset.semantic.phase9.fluency_generator import FluencyGenerator
from threshold_onset.semantic.phase9.scoring import (
    calculate_stability_score,
    calculate_novelty_penalty,
    calculate_experience_bias
)
from threshold_onset.semantic.phase9.symbol_decoder import (
    build_structural_decoder,
    decode_symbol_sequence,
    get_decoder_stats,
)

__all__ = [
    'FluencyGenerator',
    'calculate_stability_score',
    'calculate_novelty_penalty',
    'calculate_experience_bias',
    'build_structural_decoder',
    'decode_symbol_sequence',
    'get_decoder_stats',
]
