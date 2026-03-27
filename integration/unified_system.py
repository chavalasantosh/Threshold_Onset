#!/usr/bin/env python3
"""
UNIFIED SYSTEM: threshold_onset <-> santok

कार्य (kārya) happens before ज्ञान (jñāna)

This system unifies:
- santok: Text tokenization (action)
- threshold_onset: Structure emergence (knowledge)

Text tokens become actions.
Token patterns become residues.
Structure emerges naturally.
Semantics emerge automatically.

NO embeddings.
NO transformers.
NO neural networks.
NO BERT.
NO sentence piece.
NO backpropagation.

Just: Tokenization → Structure → Semantics (emergent)
"""

import sys
from pathlib import Path
import hashlib

# Add paths for imports
project_root = Path(__file__).parent.parent  # Go up from integration/ to project root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
# Use internal pip-installed modules: santok, santek, somaya
# These are our own projects: pip install santok, pip install santek, pip install somaya


class TokenAction:
    """
    Converts text tokens into Phase 0 actions.

    Tokens become numeric residues (hash-based, opaque, no meaning).
    Phase 0 compliant: numeric, opaque, no labels, no interpretation.
    """
    def __init__(self, tokens):
        """
        Args:
            tokens: List of token strings from santok
        """
        self.tokens = tokens
        self.index = 0

    def __call__(self):
        """
        Returns numeric residue from token.
        Uses hash to convert token to number (opaque, no meaning).
        """
        if self.index >= len(self.tokens):
            # Cycle back to beginning (repetition enables structure)
            self.index = 0

        token = self.tokens[self.index]
        self.index += 1

        # Convert token to numeric residue using hash
        # Phase 0 compliant: numeric, opaque, no meaning
        token_bytes = token.encode('utf-8')
        hash_obj = hashlib.sha256(token_bytes)
        hash_int = int(hash_obj.hexdigest()[:8], 16)  # First 8 hex chars = 32-bit int
        residue = float(hash_int % 10000) / 10000.0  # Normalize to [0, 1)

        return residue


def tokenize_text_to_actions(text, tokenization_method="word"):
    """
    Tokenize text using santok, then convert tokens to Phase 0 actions.

    Args:
        text: Input text string
        tokenization_method: One of: "whitespace", "word", "character", "grammar", "subword", "byte"

    Returns:
        List of TokenAction objects (one per token sequence)
    """
    # Import santok tokenization
    try:
        # Use internal pip-installed santok module
        from santok import (  # pylint: disable=import-outside-toplevel
            tokenize_space,
            tokenize_word,
            tokenize_char,
            tokenize_grammar,
            tokenize_subword,
        )
    except ImportError:
        try:
            # Try alternative import path
            from santok.core import (  # pylint: disable=import-outside-toplevel
                tokenize_space,
                tokenize_word,
                tokenize_char,
                tokenize_grammar,
                tokenize_subword,
            )
        except ImportError:
            # Fallback to tokenize_text function (santok uses tokenization_method)
            from santok import tokenize_text as santok_tokenize_text  # pylint: disable=import-outside-toplevel
            result = santok_tokenize_text(text, tokenization_method=tokenization_method)
            tokens = result.get('tokens', [])
    else:
        # Use core tokenizers
        if tokenization_method == "whitespace":
            tokens = tokenize_space(text)
        elif tokenization_method == "word":
            tokens = tokenize_word(text)
        elif tokenization_method == "character":
            tokens = tokenize_char(text)
        elif tokenization_method == "grammar":
            tokens = tokenize_grammar(text)
        elif tokenization_method == "subword":
            tokens = tokenize_subword(text, chunk_size=3)
        else:
            tokens = tokenize_word(text)  # Default to word

    # Extract token strings from tokenizer output
    # Tokenizers may return dicts or strings
    token_strings = []
    for token in tokens:
        if isinstance(token, dict):
            # Extract 'text' field from token dict
            token_strings.append(token.get('text', str(token)))
        elif isinstance(token, str):
            token_strings.append(token)
        else:
            token_strings.append(str(token))

    # Convert tokens to actions
    # Each token becomes a callable that returns a numeric residue
    action = TokenAction(token_strings)

    return action, token_strings


def process_text_through_phases(text, tokenization_method="word", num_runs=5):
    """
    Process text through unified system:
    1. Tokenize text (santok) - ACTION
    2. Convert tokens to residues (Phase 0) - RESIDUE
    3. Detect boundaries (Phase 1) - SEGMENTATION
    4. Find identities (Phase 2) - IDENTITY
    5. Map relations (Phase 3) - RELATION
    6. Assign symbols (Phase 4) - SYMBOL

    Structure emerges. Semantics emerge automatically.

    Args:
        text: Input text to process
        tokenization_method: Tokenization method to use
        num_runs: Number of runs for multi-run persistence testing

    Returns:
        Dictionary with results from all phases
    """
    print("=" * 70)
    print("UNIFIED SYSTEM: threshold_onset <-> santok")
    # Print philosophy in ASCII-safe way to avoid encoding issues
    try:
        print("कार्य (kārya) happens before ज्ञान (jñāna)")
    except UnicodeEncodeError:
        print("Action (kārya) happens before Knowledge (jñāna)")
    print("=" * 70)
    print()
    print(f"Input text length: {len(text)} characters")
    print(f"Tokenization method: {tokenization_method}")
    print(f"Multi-run mode: {num_runs} runs")
    print()

    # Step 1: Tokenize text (santok)
    print("-" * 70)
    print("STEP 1: TOKENIZATION (santok)")
    print("-" * 70)
    action, tokens = tokenize_text_to_actions(text, tokenization_method)
    print(f"Tokens generated: {len(tokens)}")
    print(f"Sample tokens (first 10): {tokens[:10]}")
    print()

    # Step 2-6: Run through threshold_onset phases
    # Import threshold_onset phases
    from threshold_onset.phase0.phase0 import phase0
    from threshold_onset.phase1.phase1 import phase1
    from threshold_onset.phase2.phase2 import phase2_multi_run
    from threshold_onset.phase3.phase3 import phase3_multi_run
    from threshold_onset.phase4.phase4 import phase4

    # Multi-run mode: collect residues from multiple runs
    residue_sequences = []
    phase1_metrics_list = []

    for run_num in range(num_runs):
        print("-" * 70)
        print(f"RUN {run_num + 1}/{num_runs}")
        print("-" * 70)

        # Phase 0: Actions → Residues
        # Reset action index for each run
        action.index = 0
        steps = len(tokens) * 2  # Process tokens twice to enable repetition

        residues = []
        for residue, count, step_count in phase0([action], steps=steps):
            residues.append(residue)

        residue_sequences.append(residues)

        print(f"Phase 0: Generated {len(residues)} residues")
        print(f"  Unique residues: {len(set(residues))}")
        print(f"  Collision rate: {1.0 - (len(set(residues)) / len(residues)):.4f}")

        # Phase 1: Segmentation
        phase1_metrics = phase1(residues)
        phase1_metrics_list.append(phase1_metrics)

        print(f"Phase 1: Boundaries detected: {len(phase1_metrics['boundary_positions'])}")
        print(f"  Clusters: {phase1_metrics['cluster_count']}")
        print(f"  Repetitions: {phase1_metrics['repetition_count']}")
        print()

    # Phase 2: Identity (multi-run)
    print("-" * 70)
    print("PHASE 2: IDENTITY (Multi-Run)")
    print("-" * 70)
    phase2_metrics = phase2_multi_run(residue_sequences, phase1_metrics_list)

    if phase2_metrics:
        print(f"Persistent segments: {len(phase2_metrics['persistent_segment_hashes'])}")
        print(f"Identity mappings: {len(phase2_metrics['identity_mappings'])}")
        print()
    else:
        print("Phase 2 gate failed: insufficient persistence")
        return {
            'tokens': tokens,
            'residues': residue_sequences,
            'phase1': phase1_metrics_list,
            'phase2': None,
            'phase3': None,
            'phase4': None,
        }

    # Phase 3: Relation (multi-run)
    print("-" * 70)
    print("PHASE 3: RELATION (Multi-Run)")
    print("-" * 70)
    phase3_metrics = phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)

    if phase3_metrics:
        print(f"Nodes: {phase3_metrics['node_count']}")
        print(f"Edges: {phase3_metrics['edge_count']}")
        print(f"Persistent relations: {len(phase3_metrics['persistent_relation_hashes'])}")
        print(f"Stability ratio: {phase3_metrics['stability_ratio']:.4f}")
        print()
    else:
        print("Phase 3 gate failed: insufficient relations")
        return {
            'tokens': tokens,
            'residues': residue_sequences,
            'phase1': phase1_metrics_list,
            'phase2': phase2_metrics,
            'phase3': None,
            'phase4': None,
        }

    # Phase 4: Symbol (aliasing)
    print("-" * 70)
    print("PHASE 4: SYMBOL (Aliasing)")
    print("-" * 70)
    phase4_metrics = phase4(phase2_metrics, phase3_metrics)

    if phase4_metrics:
        print(f"Identity aliases: {phase4_metrics['identity_alias_count']}")
        print(f"Relation aliases: {phase4_metrics['relation_alias_count']}")
        print()
    else:
        print("Phase 4 gate failed")
        phase4_metrics = None

    print("=" * 70)
    print("UNIFIED SYSTEM: COMPLETE")
    print("=" * 70)
    print()
    print("Structure has emerged from text tokens.")
    print("Semantics emerge automatically from the structure.")
    print("No embeddings. No transformers. No neural networks.")
    print("Just: Tokenization → Structure → Semantics (emergent)")
    print()

    return {
        'tokens': tokens,
        'residues': residue_sequences,
        'phase1': phase1_metrics_list,
        'phase2': phase2_metrics,
        'phase3': phase3_metrics,
        'phase4': phase4_metrics,
    }


if __name__ == "__main__":
    # Example usage
    sample_text = """
    कार्य (kārya) happens before ज्ञान (jñāna)
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    Tokens become actions.
    Patterns become residues.
    Structure emerges naturally.
    Semantics emerge automatically.
    """

    # Process text through unified system
    results = process_text_through_phases(
        text=sample_text,
        tokenization_method="word",
        num_runs=5
    )

    print("\nResults summary:")
    print(f"- Tokens: {len(results['tokens'])}")
    print(f"- Runs: {len(results['residues'])}")
    if results['phase2']:
        print(f"- Persistent identities: {len(results['phase2']['persistent_segment_hashes'])}")
    if results['phase3']:
        print(f"- Persistent relations: {len(results['phase3']['persistent_relation_hashes'])}")
    if results['phase4']:
        print(f"- Identity aliases: {results['phase4']['identity_alias_count']}")
        print(f"- Relation aliases: {results['phase4']['relation_alias_count']}")
