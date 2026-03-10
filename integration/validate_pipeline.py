#!/usr/bin/env python3
"""
Validation script: run pipeline on varied inputs, detect edge cases.

Tests: short text, long text, repeated tokens, punctuation, empty, single token.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Avoid Unicode print issues on Windows
def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode('ascii'))


def tokenize_simple(text):
    """Simple tokenization (no santok dependency)."""
    return text.split()


def token_to_residue(token):
    import hashlib
    h = hashlib.sha256(token.encode()).hexdigest()[:8]
    return float(int(h, 16) % 10000) / 10000.0


def run_phases_and_decode(text, num_runs=3):
    """Run full pipeline and return (success, decoded_text, error)."""
    try:
        tokens = tokenize_simple(text)
        if not tokens:
            return False, "", "Empty tokens"

        from threshold_onset.phase1.phase1 import phase1
        from threshold_onset.phase2.phase2 import phase2_multi_run
        from threshold_onset.phase3.phase3 import phase3_multi_run
        from threshold_onset.phase4.phase4 import phase4
        from threshold_onset.semantic.phase9.symbol_decoder import (
            build_structural_decoder,
            decode_symbol_sequence,
        )

        residue_sequences = []
        phase1_list = []
        for _ in range(num_runs):
            residues = [token_to_residue(t) for t in tokens] * 2
            residue_sequences.append(residues)
            phase1_list.append(phase1(residues))

        phase2 = phase2_multi_run(residue_sequences, phase1_list)
        if not phase2 or not phase2.get('identity_mappings'):
            return False, "", "Phase 2 gate failed"

        phase3 = phase3_multi_run(residue_sequences, phase1_list, phase2)
        if not phase3:
            return False, "", "Phase 3 gate failed"

        phase4_metrics = phase4(phase2, phase3)
        if not phase4_metrics:
            return False, "", "Phase 4 gate failed"

        symbol_to_token = build_structural_decoder(
            tokens, residue_sequences, phase2, phase4_metrics
        )
        if not symbol_to_token:
            return False, "", "Decoder empty"

        symbols = list(phase4_metrics.get('identity_to_symbol', {}).values())[:20]
        decoded = decode_symbol_sequence(symbols, symbol_to_token)
        return True, decoded, None
    except Exception as e:
        return False, "", str(e)


def main():
    test_cases = [
        ("Short", "Hi there."),
        ("Normal", "Action before knowledge. Structure emerges before language."),
        ("Repeated", "the the the a a a"),
        ("Single", "word"),
        ("Long", " ".join(["word"] * 50)),
        ("Punctuation", "Hello, world! How are you?"),
        ("Mixed", "Action before knowledge. Structure emerges. Tokens become actions."),
    ]

    safe_print("=" * 60)
    safe_print("PIPELINE VALIDATION")
    safe_print("=" * 60)

    passed = 0
    failed = 0
    for name, text in test_cases:
        ok, decoded, err = run_phases_and_decode(text)
        if ok:
            passed += 1
            safe_print(f"PASS {name}: {decoded[:50]}...")
        else:
            failed += 1
            safe_print(f"FAIL {name}: {err}")

    safe_print("-" * 60)
    safe_print(f"Results: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
