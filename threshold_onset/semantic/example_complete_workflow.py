#!/usr/bin/env python3
"""
Complete Semantic Discovery Workflow Example

Enterprise-grade example demonstrating all 5 phases.
Runs the full pipeline in-memory first to obtain Phase 2-4, then Phases 5-9.
"""

import hashlib
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from threshold_onset.semantic import (
    ConsequenceFieldEngine,
    MeaningDiscoveryEngine,
    RoleEmergenceEngine,
    ConstraintDiscoveryEngine,
    FluencyGenerator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DEFAULT_SAMPLE_TEXT = (
    "chinni gunde lo anni asala. inka yenni dhachi navoo dhanni lona. "
    "oohaa lo illa telave ala."
)


def _segment_hash(segment):
    """Match Phase 2 identity hashing (segment = tuple of residues)."""
    return hashlib.md5(str(segment).encode("utf-8")).hexdigest()


def _symbol_sequences_from_model_state(model_state):
    """Build symbol_sequences from pipeline model_state."""
    residue_sequences = model_state.get("residue_sequences") or []
    phase2 = model_state.get("phase2_metrics") or {}
    phase4 = model_state.get("phase4_metrics") or {}
    identity_mappings = phase2.get("identity_mappings", {})
    identity_to_symbol = phase4.get("identity_to_symbol", {})

    symbol_sequences = []
    for residues in residue_sequences:
        seq = []
        for i in range(len(residues) - 1):
            seg = (float(residues[i]), float(residues[i + 1]))
            seg_hash = _segment_hash(seg)
            identity_hash = identity_mappings.get(seg_hash)
            if identity_hash is not None:
                sym = identity_to_symbol.get(identity_hash)
                if sym is not None:
                    seq.append(sym)
        if seq:
            symbol_sequences.append(seq)
    return symbol_sequences


def example_complete_workflow():
    """
    Complete workflow example for semantic discovery.
    Runs the full pipeline in-memory first to get Phase 2-4, then Phases 5-9.
    """
    logger.info("=" * 60)
    logger.info("Semantic Discovery Module - Complete Workflow")
    logger.info("=" * 60)

    # ============================================================
    # PREREQUISITES: Run full pipeline to get Phase 2-4 in memory
    # ============================================================
    logger.info("\n[PREREQ] Running full pipeline (Phases 0-4) in-memory...")
    try:
        from integration.run_complete import run  # pylint: disable=import-outside-toplevel
        result = run(
            text_override=DEFAULT_SAMPLE_TEXT,
            return_result=True,
            return_model_state=True,
        )
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Pipeline run failed: %s", e)
        return

    if result is None or result.model_state is None:
        logger.error("Pipeline returned no model_state. Cannot run semantic discovery.")
        return

    model_state = result.model_state
    phase2_metrics = model_state.get("phase2_metrics") or {}
    phase3_metrics = model_state.get("phase3_metrics") or {}
    phase4_output = model_state.get("phase4_metrics") or {}
    symbol_sequences = _symbol_sequences_from_model_state(model_state)

    if not phase4_output.get("identity_to_symbol"):
        logger.error(
            "Pipeline produced no Phase 4 identities. Use longer or richer input."
        )
        return

    logger.info("✓ Pipeline finished: %d identity symbols, %d symbol sequences",
                len(phase4_output.get("identity_to_symbol", {})), len(symbol_sequences))

    try:
        from threshold_onset.phase10 import phase10_jsonable_from_model_state

        phase10_snap = phase10_jsonable_from_model_state(model_state)
    except Exception:  # pylint: disable=broad-exception-caught
        phase10_snap = None

    # ============================================================
    # SETUP: Continuation Observer
    # ============================================================
    logger.info("\n[SETUP] Initializing ContinuationObserver...")

    try:
        from integration.continuation_observer import ContinuationObserver
        observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)
        logger.info("✓ ContinuationObserver initialized")
    except ImportError as e:
        logger.error("Failed to import ContinuationObserver: %s", e)
        logger.info("Skipping integration test - ContinuationObserver not available")
        return
    except (AttributeError, TypeError, ValueError) as e:
        logger.error("Failed to initialize observer: %s", e)
        return

    # ============================================================
    # PHASE 5: CONSEQUENCE FIELD ENGINE
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 5: Consequence Field Engine")
    logger.info("=" * 60)

    try:
        consequence_engine = ConsequenceFieldEngine(
            phase2_identities=phase2_metrics,
            phase3_relations=phase3_metrics,
            phase4_symbols=phase4_output,
            continuation_observer=observer,
            phase10_metrics=phase10_snap,
        )

        logger.info("Building consequence field (k=5, rollouts=100)...")
        consequence_field = consequence_engine.build(
            k=5,
            num_rollouts=100,
            seed=42
        )

        logger.info(
            "✓ Consequence field built: %d identities",
            len(consequence_field.identity_vectors)
        )
        logger.info("  Edge deltas: %d", len(consequence_field.edge_deltas))

        # Save intermediate result
        consequence_engine.save('consequence_field.json')
        logger.info("✓ Saved to consequence_field.json")

    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error("Phase 5 failed: %s", e)
        return

    # ============================================================
    # PHASE 6: MEANING DISCOVERY
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 6: Meaning Discovery")
    logger.info("=" * 60)

    try:
        meaning_engine = MeaningDiscoveryEngine(consequence_field)

        logger.info("Discovering meaning clusters...")
        meaning_map = meaning_engine.discover(seed=42)

        logger.info("✓ Meaning discovered: %d clusters", len(meaning_map.clusters))
        for cluster_id, signature in meaning_map.clusters.items():
            # MeaningSignature is a TypedDict, access as dict
            size = signature.get('size', len(signature.get('identities', [])))
            logger.info("  %s: size=%d", cluster_id, size)

        # Save intermediate result
        meaning_engine.save('meaning_map.json')
        logger.info("✓ Saved to meaning_map.json")

    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error("Phase 6 failed: %s", e)
        return

    # ============================================================
    # PHASE 7: ROLE EMERGENCE
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 7: Role Emergence")
    logger.info("=" * 60)

    try:
        role_engine = RoleEmergenceEngine(
            meaning_map=meaning_map,
            consequence_field=consequence_field,
            continuation_observer=observer
        )

        logger.info("Emerging functional roles...")
        roles = role_engine.emerge()

        logger.info("✓ Roles emerged: %d role assignments", len(roles['cluster_roles']))
        for cluster_id, role in roles['cluster_roles'].items():
            logger.info("  %s: %s", cluster_id, role)

        # Save intermediate result
        role_engine.save('roles.json')
        logger.info("✓ Saved to roles.json")

    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error("Phase 7 failed: %s", e)
        return

    # ============================================================
    # PHASE 8: CONSTRAINT DISCOVERY
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 8: Constraint Discovery")
    logger.info("=" * 60)

    try:
        constraint_engine = ConstraintDiscoveryEngine(
            roles=roles,
            symbol_sequences=symbol_sequences,
            edge_deltas=consequence_field.edge_deltas,
            continuation_observer=observer,
            identity_to_symbol=phase4_output.get('identity_to_symbol', {}),
            config={
                "phase8": {
                    "adaptive_min_frequency": True,
                }
            },
        )

        logger.info("Discovering constraints and templates...")
        constraints = constraint_engine.discover()

        logger.info("✓ Constraints discovered:")
        logger.info("  Patterns: %d", len(constraints['role_patterns']))
        logger.info("  Forbidden: %d", len(constraints['forbidden_patterns']))
        logger.info("  Templates: %d", len(constraints['templates']))

        # Save intermediate result
        constraint_engine.save('constraints.json')
        logger.info("✓ Saved to constraints.json")

    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error("Phase 8 failed: %s", e)
        return

    # ============================================================
    # PHASE 9: FLUENCY GENERATOR
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 9: Fluency Generator")
    logger.info("=" * 60)

    try:
        generator = FluencyGenerator(
            consequence_field=consequence_field,
            roles=roles,
            constraints=constraints,
            phase3_relations=phase3_metrics,
            phase4_symbols=phase4_output,
            continuation_observer=observer
        )

        logger.info("Building experience table...")
        generator.build_experience_table()
        logger.info("✓ Experience table built: %d entries", len(generator.experience_table))

        logger.info("Generating fluent sequence...")
        sequence = generator.generate(
            start_symbol=0,
            length=50,
            seed=42
        )

        logger.info("✓ Generated sequence: %d symbols", len(sequence))
        logger.info("  Sequence: %s...", sequence[:10])  # Show first 10

        # Generate text if mapping available
        # symbol_to_text = {...}  # Your symbol to text mapping
        # text = generator.generate_text(
        #     start_symbol=0,
        #     length=50,
        #     symbol_to_text=symbol_to_text,
        #     seed=42
        # )
        # logger.info(f"✓ Generated text: {text}")

    except (ValueError, TypeError, AttributeError, RuntimeError) as e:
        logger.error("Phase 9 failed: %s", e)
        return

    # ============================================================
    # COMPLETE
    # ============================================================
    logger.info("\n" + "=" * 60)
    logger.info("✅ COMPLETE WORKFLOW FINISHED")
    logger.info("=" * 60)
    logger.info("\nGenerated files:")
    logger.info("  - consequence_field.json")
    logger.info("  - meaning_map.json")
    logger.info("  - roles.json")
    logger.info("  - constraints.json")
    logger.info("\nAll phases completed successfully!")


if __name__ == '__main__':
    example_complete_workflow()
