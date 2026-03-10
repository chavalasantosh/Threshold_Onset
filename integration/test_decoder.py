#!/usr/bin/env python3
"""Quick test for structural symbol decoder."""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Minimal run: tokenize, phases 0-4, build decoder
text = "Action before knowledge. Structure emerges."

# Tokenize
tokens = text.split()

# Phase 0 style residues (multiple runs for persistence)
import hashlib

def token_to_residue(token):
    h = hashlib.sha256(token.encode()).hexdigest()[:8]
    return float(int(h, 16) % 10000) / 10000.0

from threshold_onset.phase1.phase1 import phase1

residue_sequences = []
phase1_metrics_list = []
for _ in range(3):
    residues = [token_to_residue(t) for t in tokens] * 2  # Repeat for structure
    residue_sequences.append(residues)
    phase1_metrics_list.append(phase1(residues))

# Phase 2
from threshold_onset.phase2.phase2 import phase2_multi_run
phase2_metrics = phase2_multi_run(residue_sequences, phase1_metrics_list)

# Phase 3
from threshold_onset.phase3.phase3 import phase3_multi_run
phase3_metrics = phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)

# Phase 4
from threshold_onset.phase4.phase4 import phase4
phase4_metrics = phase4(phase2_metrics, phase3_metrics)
if phase4_metrics is None:
    print("Phase 4 gate failed - need more data")
    sys.exit(1)

# Build structural decoder
from threshold_onset.semantic.phase9.symbol_decoder import (
    build_structural_decoder,
    decode_symbol_sequence,
)

symbol_to_token = build_structural_decoder(
    tokens,
    residue_sequences,
    phase2_metrics,
    phase4_metrics,
)

print("Decoder built:", len(symbol_to_token), "symbols")
for s, t in sorted(symbol_to_token.items())[:5]:
    print(f"  Symbol {s} -> {t!r}")

# Test decode
symbol_seq = list(phase4_metrics.get('identity_to_symbol', {}).values())[:5]
text_out = decode_symbol_sequence(symbol_seq, symbol_to_token)
print("Decoded:", text_out)
print("OK")
