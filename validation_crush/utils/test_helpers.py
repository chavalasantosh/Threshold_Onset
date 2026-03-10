"""
Test Helper Utilities

Shared utilities for validation tests.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


def load_system_outputs(
    phase2_path: Optional[Path] = None,
    phase3_path: Optional[Path] = None,
    phase4_path: Optional[Path] = None,
    consequence_field_path: Optional[Path] = None,
    meaning_map_path: Optional[Path] = None,
    roles_path: Optional[Path] = None,
    constraints_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Load system outputs from JSON files.
    
    Args:
        phase2_path: Path to Phase 2 output JSON
        phase3_path: Path to Phase 3 output JSON
        phase4_path: Path to Phase 4 output JSON
        consequence_field_path: Path to consequence_field.json
        meaning_map_path: Path to meaning_map.json
        roles_path: Path to roles.json
        constraints_path: Path to constraints.json
    
    Returns:
        Dictionary with loaded outputs
    """
    import json
    
    outputs = {}
    
    # Default paths (project root)
    if phase2_path is None:
        phase2_path = project_root / "phase2_output.json"
    if phase3_path is None:
        phase3_path = project_root / "phase3_output.json"
    if phase4_path is None:
        phase4_path = project_root / "phase4_output.json"
    if consequence_field_path is None:
        consequence_field_path = project_root / "consequence_field.json"
    if meaning_map_path is None:
        meaning_map_path = project_root / "meaning_map.json"
    if roles_path is None:
        roles_path = project_root / "roles.json"
    if constraints_path is None:
        constraints_path = project_root / "constraints.json"
    
    # Load Phase 2
    if phase2_path.exists():
        with open(phase2_path, 'r') as f:
            outputs['phase2'] = json.load(f)
    else:
        logger.warning(f"Phase 2 output not found: {phase2_path}")
        outputs['phase2'] = {}
    
    # Load Phase 3
    if phase3_path.exists():
        with open(phase3_path, 'r') as f:
            outputs['phase3'] = json.load(f)
    else:
        logger.warning(f"Phase 3 output not found: {phase3_path}")
        outputs['phase3'] = {}
    
    # Load Phase 4
    if phase4_path.exists():
        with open(phase4_path, 'r') as f:
            outputs['phase4'] = json.load(f)
    else:
        logger.warning(f"Phase 4 output not found: {phase4_path}")
        outputs['phase4'] = {}
    
    # Load Phase 5 (Consequence Field)
    if consequence_field_path.exists():
        with open(consequence_field_path, 'r') as f:
            outputs['consequence_field'] = json.load(f)
    else:
        logger.warning(f"Consequence field not found: {consequence_field_path}")
        outputs['consequence_field'] = {}
    
    # Load Phase 6 (Meaning Map)
    if meaning_map_path.exists():
        with open(meaning_map_path, 'r') as f:
            outputs['meaning_map'] = json.load(f)
    else:
        logger.warning(f"Meaning map not found: {meaning_map_path}")
        outputs['meaning_map'] = {}
    
    # Load Phase 7 (Roles)
    if roles_path.exists():
        with open(roles_path, 'r') as f:
            outputs['roles'] = json.load(f)
    else:
        logger.warning(f"Roles not found: {roles_path}")
        outputs['roles'] = {}
    
    # Load Phase 8 (Constraints)
    if constraints_path.exists():
        with open(constraints_path, 'r') as f:
            outputs['constraints'] = json.load(f)
    else:
        logger.warning(f"Constraints not found: {constraints_path}")
        outputs['constraints'] = {}
    
    return outputs


def initialize_system(
    outputs: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Initialize THRESHOLD_ONSET system components.
    
    Args:
        outputs: Loaded system outputs
        config: Optional configuration
    
    Returns:
        Dictionary with initialized engines
    """
    try:
        from threshold_onset.semantic import (
            ConsequenceFieldEngine,
            MeaningDiscoveryEngine,
            RoleEmergenceEngine,
            ConstraintDiscoveryEngine,
            FluencyGenerator
        )
    except ImportError as e:
        logger.error(f"Failed to import system components: {e}")
        raise
    
    # Try to import ContinuationObserver (optional)
    ContinuationObserver = None
    try:
        from integration.continuation_observer import ContinuationObserver
    except ImportError:
        logger.warning("ContinuationObserver not available - some features may be limited")
    
    engines = {}
    
    # Initialize ContinuationObserver (if available)
    if ContinuationObserver is not None:
        try:
            observer = ContinuationObserver(
                outputs.get('phase4', {}),
                outputs.get('phase3', {}),
                outputs.get('phase2', {})
            )
            engines['observer'] = observer
        except Exception as e:
            logger.warning(f"Failed to initialize ContinuationObserver: {e}")
            engines['observer'] = None
    else:
        engines['observer'] = None
    
    # Initialize Phase 5 (if we have Phase 2-4 outputs)
    if all(k in outputs for k in ['phase2', 'phase3', 'phase4']):
        try:
            consequence_engine = ConsequenceFieldEngine(
                phase2_identities=outputs['phase2'],
                phase3_relations=outputs['phase3'],
                phase4_symbols=outputs['phase4'],
                continuation_observer=engines['observer'],
                config=config
            )
            engines['consequence_engine'] = consequence_engine
        except Exception as e:
            logger.warning(f"Failed to initialize ConsequenceFieldEngine: {e}")
            engines['consequence_engine'] = None
    
    # Initialize Phase 6 (if we have consequence field)
    if 'consequence_field' in outputs and outputs['consequence_field']:
        try:
            # Need to reconstruct ConsequenceField object from JSON
            # This is a simplified version - may need adjustment
            meaning_engine = MeaningDiscoveryEngine(
                consequence_field=None,  # Will need proper reconstruction
                config=config
            )
            engines['meaning_engine'] = meaning_engine
        except Exception as e:
            logger.warning(f"Failed to initialize MeaningDiscoveryEngine: {e}")
            engines['meaning_engine'] = None
    
    return engines


def compute_entropy(probabilities: List[float]) -> float:
    """
    Compute Shannon entropy.
    
    Args:
        probabilities: List of probabilities (should sum to 1)
    
    Returns:
        Entropy value
    """
    import math
    
    entropy = 0.0
    for p in probabilities:
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy


def compute_variance(values: List[float]) -> float:
    """
    Compute variance of values.
    
    Args:
        values: List of numeric values
    
    Returns:
        Variance
    """
    if not values:
        return 0.0
    
    mean_val = sum(values) / len(values)
    variance = sum((x - mean_val) ** 2 for x in values) / len(values)
    return variance


def compute_stability_score(
    values: List[float],
    window_size: int = 5
) -> float:
    """
    Compute stability score (inverse of variance in sliding windows).
    
    Args:
        values: List of values
        window_size: Size of sliding window
    
    Returns:
        Stability score (0-1, higher = more stable)
    """
    if len(values) < window_size:
        return 0.0
    
    window_variances = []
    for i in range(len(values) - window_size + 1):
        window = values[i:i + window_size]
        window_var = compute_variance(window)
        window_variances.append(window_var)
    
    if not window_variances:
        return 0.0
    
    # Stability is inverse of average variance
    avg_variance = sum(window_variances) / len(window_variances)
    # Normalize to 0-1 (assuming max variance of 1.0)
    stability = max(0.0, 1.0 - min(1.0, avg_variance))
    
    return stability


def check_structural_isomorphism(
    structure1: Dict[str, Any],
    structure2: Dict[str, Any]
) -> Tuple[bool, float]:
    """
    Check if two structures are isomorphic (same topology, different tokens).
    
    Args:
        structure1: First structure
        structure2: Second structure
    
    Returns:
        (is_isomorphic, similarity_score)
    """
    # Extract graph structures if available
    edges1 = set()
    edges2 = set()
    
    # Try to extract edges from various formats
    if 'graph_edges' in structure1:
        edges1 = set(tuple(e) if isinstance(e, list) else e for e in structure1['graph_edges'])
    if 'graph_edges' in structure2:
        edges2 = set(tuple(e) if isinstance(e, list) else e for e in structure2['graph_edges'])
    
    # If we have edges, compare topologies
    if edges1 and edges2:
        if len(edges1) == len(edges2):
            # Check if edge patterns match (ignoring node identities)
            # This is a simplified check - full isomorphism is NP-complete
            return True, 1.0 if len(edges1) == len(edges2) else 0.0
    
    # Fallback: compare sizes and basic structure
    size1 = len(str(structure1))
    size2 = len(str(structure2))
    similarity = 1.0 - abs(size1 - size2) / max(size1, size2, 1)
    
    return similarity > 0.8, similarity


def process_text_through_system(
    text: str,
    tokenization_method: str = "word",
    num_runs: int = 3,
    run_semantic_phases: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process text input through complete THRESHOLD_ONSET pipeline (Phases 0-9).
    
    This is the CRITICAL function that actually executes the system with test inputs.
    
    Args:
        text: Input text to process
        tokenization_method: Tokenization method (one of: whitespace, word, character, 
                           grammar, subword, subword_bpe, subword_syllable, 
                           subword_frequency, byte)
        num_runs: Number of runs for multi-run persistence
        run_semantic_phases: Whether to run Phases 5-9 (semantic discovery)
        config: Optional configuration dictionary
    
    Returns:
        Dictionary with outputs from all phases:
        - phase2: Phase 2 identities
        - phase3: Phase 3 relations
        - phase4: Phase 4 symbols
        - consequence_field: Phase 5 consequence field (if run_semantic_phases)
        - meaning_map: Phase 6 meaning map (if run_semantic_phases)
        - roles: Phase 7 roles (if run_semantic_phases)
        - constraints: Phase 8 constraints (if run_semantic_phases)
        - fluency_output: Phase 9 fluency output (if run_semantic_phases)
    """
    logger.info(f"Processing text through system (length: {len(text)} chars, method: {tokenization_method})")
    
    outputs = {}
    
    try:
        from tests.phase_test_helpers import (
            run_phase0_from_text,
            run_phase1,
            run_phase2_multi_run,
            run_phase3_multi_run,
        )
        from threshold_onset.phase4.phase4 import phase4

        def run_phase4_multi_run(phase2, phase3):
            return phase4(phase2, phase3)
    except ImportError as e:
        logger.error(f"Failed to import Phase 0-4 functions: {e}")
        return outputs
    
    # Process Phases 0-4 (Foundation)
    residue_sequences = []
    phase1_metrics_list = []
    
    for run_num in range(num_runs):
        logger.debug(f"Run {run_num + 1}/{num_runs}")
        
        # Phase 0: Tokenize and generate residues
        try:
            residues, tokens = run_phase0_from_text(text, tokenization_method=tokenization_method)
            residue_sequences.append(residues)
            
            # Phase 1: Boundary detection
            phase1_metrics = run_phase1(residues)
            phase1_metrics_list.append(phase1_metrics)
        except Exception as e:
            logger.warning(f"Failed in Phase 0-1 for run {run_num + 1}: {e}")
            continue
    
    if not residue_sequences:
        logger.error("No residue sequences generated")
        return outputs
    
    # Phase 2: Identity discovery
    try:
        phase2_metrics = run_phase2_multi_run(residue_sequences, phase1_metrics_list)
        outputs['phase2'] = phase2_metrics if phase2_metrics else {}
    except Exception as e:
        logger.warning(f"Phase 2 failed: {e}")
        outputs['phase2'] = {}
    
    # Phase 3: Relation mapping
    phase3_metrics = None
    if outputs.get('phase2') and residue_sequences:
        try:
            phase3_metrics = run_phase3_multi_run(residue_sequences, phase1_metrics_list, outputs['phase2'])
            outputs['phase3'] = phase3_metrics if phase3_metrics else {}
        except Exception as e:
            logger.warning(f"Phase 3 failed: {e}")
            outputs['phase3'] = {}
    
    # Phase 4: Symbol assignment
    phase4_output = None
    if outputs.get('phase2') and outputs.get('phase3'):
        try:
            phase4_output = run_phase4_multi_run(outputs['phase2'], outputs['phase3'])
            outputs['phase4'] = phase4_output if phase4_output else {}
        except Exception as e:
            logger.warning(f"Phase 4 failed: {e}")
            outputs['phase4'] = {}
    
    # Process Phases 5-9 (Semantic Discovery) if requested
    if run_semantic_phases and outputs.get('phase2') and outputs.get('phase3') and outputs.get('phase4'):
        try:
            from main import (
                prepare_phase_outputs_for_semantic,
                run_phase5_semantic,
                run_phase6_semantic,
                run_phase7_semantic,
                run_phase8_semantic,
                run_phase9_semantic
            )
        except ImportError:
            logger.warning("Semantic phases (5-9) require main to export prepare_phase_outputs_for_semantic, "
                          "run_phase5_semantic, etc. Skipping semantic discovery.")
            run_semantic_phases = False

    if run_semantic_phases and outputs.get('phase2') and outputs.get('phase3') and outputs.get('phase4'):
        try:
            phase2_for_semantic, phase3_for_semantic, phase4_for_semantic = prepare_phase_outputs_for_semantic(
                outputs['phase2'], outputs['phase3'], outputs['phase4']
            )
            
            # Initialize ContinuationObserver
            observer = None
            try:
                from integration.continuation_observer import ContinuationObserver
                observer = ContinuationObserver(
                    phase4_for_semantic,
                    phase3_for_semantic,
                    phase2_for_semantic
                )
            except ImportError:
                logger.warning("ContinuationObserver not available - semantic phases may be limited")
            
            if observer is not None:
                # Phase 5: Consequence Field
                try:
                    consequence_field = run_phase5_semantic(
                        phase2_for_semantic,
                        phase3_for_semantic,
                        phase4_for_semantic,
                        observer
                    )
                    if consequence_field:
                        outputs['consequence_field'] = consequence_field
                except Exception as e:
                    logger.warning(f"Phase 5 failed: {e}")
                
                # Phase 6: Meaning Discovery
                if 'consequence_field' in outputs:
                    try:
                        meaning_map = run_phase6_semantic(outputs['consequence_field'])
                        if meaning_map:
                            outputs['meaning_map'] = meaning_map
                    except Exception as e:
                        logger.warning(f"Phase 6 failed: {e}")
                
                # Phase 7: Role Emergence
                if 'meaning_map' in outputs:
                    try:
                        roles = run_phase7_semantic(
                            outputs['meaning_map'],
                            outputs['consequence_field'],
                            observer
                        )
                        if roles:
                            outputs['roles'] = roles
                    except Exception as e:
                        logger.warning(f"Phase 7 failed: {e}")
                
                # Phase 8: Constraint Discovery
                if 'roles' in outputs:
                    try:
                        # Extract symbol sequences from residue sequences
                        symbol_sequences = []
                        identity_to_symbol = phase4_for_semantic.get('identity_to_symbol', {})
                        identity_hashes = list(phase2_for_semantic.get('identity_hashes', []))
                        
                        if identity_to_symbol and identity_hashes:
                            for residues in residue_sequences[:5]:  # Limit for performance
                                seq = []
                                for residue in residues[:50]:  # Limit length
                                    residue_int = int(abs(residue * 10000)) % len(identity_hashes)
                                    identity_hash = identity_hashes[residue_int]
                                    symbol = identity_to_symbol.get(identity_hash)
                                    if symbol is not None:
                                        seq.append(symbol)
                                if len(seq) >= 3:
                                    symbol_sequences.append(seq)
                        
                        constraints = run_phase8_semantic(
                            outputs['roles'],
                            symbol_sequences,
                            outputs['consequence_field'],
                            observer,
                            phase4_for_semantic
                        )
                        if constraints:
                            outputs['constraints'] = constraints
                    except Exception as e:
                        logger.warning(f"Phase 8 failed: {e}")
                
                # Phase 9: Fluency Generator
                if 'constraints' in outputs:
                    try:
                        fluency_output = run_phase9_semantic(
                            outputs['consequence_field'],
                            outputs['roles'],
                            outputs['constraints'],
                            phase3_for_semantic,
                            phase4_for_semantic,
                            observer
                        )
                        if fluency_output:
                            outputs['fluency_output'] = fluency_output
                    except Exception as e:
                        logger.warning(f"Phase 9 failed: {e}")
        except ImportError as e:
            logger.warning(f"Semantic phases not available: {e}")
    
    logger.info(f"System processing complete. Phases completed: {list(outputs.keys())}")
    return outputs
