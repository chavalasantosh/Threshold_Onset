#!/usr/bin/env python3
"""
Fluency-based Text Generator

Wires FluencyGenerator (Phases 5-9) into text output.
Uses consequence field, roles, constraints for generation.
Then decodes symbols to text via structural decoder.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def generate_text_via_fluency(
    tokens: List[str],
    residue_sequences: List[List[float]],
    phase2_metrics: Dict[str, Any],
    phase3_metrics: Dict[str, Any],
    phase4_metrics: Dict[str, Any],
    start_symbol: Optional[int] = None,
    length: int = 30,
    seed: Optional[int] = 42,
) -> str:
    """
    Generate text using FluencyGenerator (consequence + roles + constraints).

    Pipeline: Phase 5-9 → FluencyGenerator.generate → structural decoder → text.

    Args:
        tokens: Original tokens
        residue_sequences: Phase 0 residues
        phase2_metrics, phase3_metrics, phase4_metrics: Phase 2-4 outputs
        start_symbol: Starting symbol (default: first available)
        length: Sequence length
        seed: Random seed

    Returns:
        Generated text string
    """
    from integration.continuation_observer import ContinuationObserver
    from threshold_onset.semantic.phase5.consequence_field import ConsequenceFieldEngine
    from threshold_onset.semantic.phase6.meaning_discovery import MeaningDiscoveryEngine
    from threshold_onset.semantic.phase7.role_emergence import RoleEmergenceEngine
    from threshold_onset.semantic.phase8.constraint_discovery import ConstraintDiscoveryEngine
    from threshold_onset.semantic.phase9.fluency_generator import FluencyGenerator
    from threshold_onset.semantic.phase9.symbol_decoder import (
        build_structural_decoder,
        decode_symbol_sequence,
    )

    observer = ContinuationObserver(phase4_metrics, phase3_metrics, phase2_metrics)

    try:
        from threshold_onset.phase10 import phase10_jsonable_from_model_state

        _ms = {
            "phase2_metrics": phase2_metrics,
            "phase3_metrics": phase3_metrics,
            "phase4_metrics": phase4_metrics,
            "residue_sequences": residue_sequences,
        }
        phase10_snap = phase10_jsonable_from_model_state(_ms)
    except Exception:  # pylint: disable=broad-exception-caught
        phase10_snap = None

    consequence_engine = ConsequenceFieldEngine(
        phase2_identities=phase2_metrics,
        phase3_relations=phase3_metrics,
        phase4_symbols=phase4_metrics,
        continuation_observer=observer,
        phase10_metrics=phase10_snap,
    )
    # Cap rollouts adaptively: large graphs (many identities) are expensive per rollout.
    # Use fewer rollouts for large graphs to keep generation under ~2s.
    num_identities = len(phase4_metrics.get('identity_to_symbol', {}))
    if num_identities >= 100:
        _rollouts = 10
    elif num_identities >= 30:
        _rollouts = 20
    else:
        _rollouts = 50
    consequence_field = consequence_engine.build(k=5, num_rollouts=_rollouts, seed=seed or 42)

    meaning_engine = MeaningDiscoveryEngine(consequence_field)
    meaning_map = meaning_engine.discover(seed=seed or 42)

    role_engine = RoleEmergenceEngine(
        meaning_map=meaning_map,
        consequence_field=consequence_field,
        continuation_observer=observer,
    )
    roles = role_engine.emerge()

    identity_to_symbol = phase4_metrics.get('identity_to_symbol', {})
    symbol_sequences = []
    for residues in residue_sequences[:1]:
        seq = []
        for i in range(len(residues) - 1):
            seg = tuple(residues[i:i + 2])
            seg_hash = _hash_segment(seg)
            if seg_hash in phase2_metrics.get('identity_mappings', {}):
                identity = phase2_metrics['identity_mappings'][seg_hash]
                sym = identity_to_symbol.get(identity)
                if sym is not None:
                    seq.append(sym)
        if seq:
            symbol_sequences.append(seq)

    constraint_engine = ConstraintDiscoveryEngine(
        roles=roles,
        symbol_sequences=symbol_sequences or [[0]],
        edge_deltas=consequence_field.edge_deltas,
        continuation_observer=observer,
        identity_to_symbol=identity_to_symbol,
        config={
            "phase8": {
                "adaptive_min_frequency": True,
            }
        },
    )
    constraints = constraint_engine.discover()

    generator = FluencyGenerator(
        consequence_field=consequence_field,
        roles=roles,
        constraints=constraints,
        phase3_relations=phase3_metrics,
        phase4_symbols=phase4_metrics,
        continuation_observer=observer,
    )

    symbol_to_identity = phase4_metrics.get('symbol_to_identity', {})
    if start_symbol is None and symbol_to_identity:
        start_symbol = next(iter(symbol_to_identity.keys()))

    if start_symbol is None:
        return ""

    symbol_seq = generator.generate(start_symbol=start_symbol, length=length, seed=seed)
    symbol_to_token = build_structural_decoder(
        tokens, residue_sequences, phase2_metrics, phase4_metrics
    )
    return decode_symbol_sequence(symbol_seq, symbol_to_token)


def _hash_segment(segment):
    import hashlib
    return hashlib.md5(str(segment).encode()).hexdigest()
