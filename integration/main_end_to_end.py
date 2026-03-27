#!/usr/bin/env python3
"""
Complete End-to-End Unified System

threshold_onset <-> santok

Full pipeline:
1. Tokenization (santok) - ACTION
2. Structure Emergence (threshold_onset Phases 0-4) - STRUCTURE
3. Continuation Observation - REFUSAL
4. Escape Topology Measurement - NECESSITY
5. Topology Clustering - ORGANIZATION

कार्य (kārya) happens before ज्ञान (jñāna)

This is the complete system. Everything in one place.
"""

import sys
from pathlib import Path
import hashlib
from collections import defaultdict, Counter
import math

# ============================================================================
# PATH SETUP
# ============================================================================
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
# Use internal pip-installed modules: santok, santek, somaya
# These are our own projects: pip install santok, pip install santek, pip install somaya


# ============================================================================
# COMPONENT 1: TOKENIZATION (santok)
# ============================================================================

class TokenAction:
    """Converts text tokens into Phase 0 actions."""
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def __call__(self):
        """Returns numeric residue from token (hash-based, opaque)."""
        if self.index >= len(self.tokens):
            self.index = 0

        token = self.tokens[self.index]
        self.index += 1

        token_bytes = token.encode('utf-8')
        hash_obj = hashlib.sha256(token_bytes)
        hash_int = int(hash_obj.hexdigest()[:8], 16)
        residue = float(hash_int % 10000) / 10000.0

        return residue


def tokenize_text(input_text, tokenization_method="word"):
    """Tokenize text using santok."""
    try:
        # Use internal pip-installed santok module
        from santok import (  # pylint: disable=import-outside-toplevel
            tokenize_space, tokenize_word, tokenize_char,
            tokenize_grammar, tokenize_subword
        )
    except ImportError:
        try:
            # Try alternative import path
            from santok.core import (  # pylint: disable=import-outside-toplevel
                tokenize_space, tokenize_word, tokenize_char,
                tokenize_grammar, tokenize_subword
            )
        except ImportError:
            # Fallback to tokenize_text function (santok uses tokenization_method)
            from santok import tokenize_text as santok_tokenize_text  # pylint: disable=import-outside-toplevel
            result = santok_tokenize_text(input_text, tokenization_method=tokenization_method)
            tokens = result.get('tokens', [])
    else:
        if tokenization_method == "whitespace":
            tokens = tokenize_space(input_text)
        elif tokenization_method == "word":
            tokens = tokenize_word(input_text)
        elif tokenization_method == "character":
            tokens = tokenize_char(input_text)
        elif tokenization_method == "grammar":
            tokens = tokenize_grammar(input_text)
        elif tokenization_method == "subword":
            tokens = tokenize_subword(input_text, chunk_size=3)
        else:
            tokens = tokenize_word(input_text)

    # Extract token strings
    token_strings = []
    for token in tokens:
        if isinstance(token, dict):
            token_strings.append(token.get('text', str(token)))
        elif isinstance(token, str):
            token_strings.append(token)
        else:
            token_strings.append(str(token))

    return token_strings


# ============================================================================
# COMPONENT 2: STRUCTURE EMERGENCE (threshold_onset Phases 0-4)
# ============================================================================

def run_structure_emergence(input_text, tokenization_method="word", num_runs=3):
    """Run threshold_onset Phases 0-4."""
    from threshold_onset.phase0.phase0 import phase0
    from threshold_onset.phase1.phase1 import phase1
    from threshold_onset.phase2.phase2 import phase2_multi_run
    from threshold_onset.phase3.phase3 import phase3_multi_run
    from threshold_onset.phase4.phase4 import phase4

    # Tokenize
    tokens = tokenize_text(input_text, tokenization_method)
    action = TokenAction(tokens)

    # Multi-run: collect residues
    residue_sequences = []
    phase1_metrics_list = []

    for _ in range(num_runs):
        action.index = 0
        steps = len(tokens) * 2

        residues = []
        for residue, _count, _step in phase0([action], steps=steps):
            residues.append(residue)

        residue_sequences.append(residues)
        phase1_metrics = phase1(residues)
        phase1_metrics_list.append(phase1_metrics)

    # Phase 2: Identity
    phase2_metrics = phase2_multi_run(residue_sequences, phase1_metrics_list)

    if phase2_metrics is None:
        return None

    # Phase 3: Relation
    phase3_metrics = phase3_multi_run(residue_sequences, phase1_metrics_list, phase2_metrics)

    if phase3_metrics is None:
        return None

    # Phase 4: Symbol
    phase4_metrics = phase4(phase2_metrics, phase3_metrics)

    if phase4_metrics is None:
        return None

    return {
        'tokens': tokens,
        'residues': residue_sequences,
        'phase1': phase1_metrics_list,
        'phase2': phase2_metrics,
        'phase3': phase3_metrics,
        'phase4': phase4_metrics
    }


# ============================================================================
# COMPONENT 3: CONTINUATION OBSERVATION
# ============================================================================

class ContinuationRefusal:
    """Records a single refusal event."""
    def __init__(self, step_index, current_symbol, attempted_next_symbol, reason, relation_exists):
        self.step_index = step_index
        self.current_symbol = current_symbol
        self.attempted_next_symbol = attempted_next_symbol
        self.reason = reason
        self.relation_exists = relation_exists

    def to_dict(self):
        """Convert refusal to dict for serialization."""
        return {
            'step_index': self.step_index,
            'current_symbol': self.current_symbol,
            'attempted_next_symbol': self.attempted_next_symbol,
            'reason_for_refusal': self.reason,
            'relation_exists': self.relation_exists
        }


class ContinuationObserver:
    """Observes continuation after Phase 4 and records refusals."""

    def __init__(self, phase4_output, phase3_metrics, phase2_metrics):
        self.phase4_output = phase4_output
        self.phase3_metrics = phase3_metrics
        self.phase2_metrics = phase2_metrics

        self.identity_to_symbol = phase4_output.get('identity_to_symbol', {})
        self.symbol_to_identity = phase4_output.get('symbol_to_identity', {})

        self.graph_nodes = phase3_metrics.get('graph_nodes', set())
        self.graph_edges = phase3_metrics.get('graph_edges', set())

        self.adjacency = self._build_adjacency()
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
        """Map residue to identity hash."""
        persistent_segment_hashes = self.phase2_metrics.get('persistent_segment_hashes', [])
        identity_mappings = self.phase2_metrics.get('identity_mappings', {})

        identity_hashes = set()
        if persistent_segment_hashes:
            for seg_hash in persistent_segment_hashes:
                if seg_hash in identity_mappings:
                    identity_hashes.add(identity_mappings[seg_hash])
        identity_hashes.update(identity_mappings.values())

        if not identity_hashes:
            return None

        identity_list = list(identity_hashes)
        residue_int = int(abs(residue * 10000)) % len(identity_list)
        return identity_list[residue_int]

    def _identity_hash_to_symbol(self, identity_hash):
        """Convert identity hash to Phase 4 symbol."""
        return self.identity_to_symbol.get(identity_hash)

    def _check_transition_allowed(self, from_identity_hash, to_identity_hash):
        """Check if transition is allowed."""
        if from_identity_hash not in self.adjacency:
            return False
        return to_identity_hash in self.adjacency[from_identity_hash]

    def observe_continuation(self, continuation_tokens, max_steps=100):
        """Observe continuation and record refusals."""
        tokens = list(continuation_tokens)
        action = TokenAction(tokens)

        current_identity_hash = None
        current_symbol = None
        step_index = 0

        for step in range(max_steps):
            if step >= len(tokens):
                break

            residue = action()
            next_identity_hash = self._residue_to_identity_hash(residue)

            if next_identity_hash is None:
                continue

            next_symbol = self._identity_hash_to_symbol(next_identity_hash)

            if next_symbol is None:
                continue

            if current_identity_hash is not None:
                transition_allowed = self._check_transition_allowed(
                    current_identity_hash,
                    next_identity_hash
                )

                if not transition_allowed:
                    reason = "no_persistent_relation"
                    adj = self.adjacency.get(current_identity_hash, set())
                    relation_exists = next_identity_hash in adj
                    refusal = ContinuationRefusal(
                        step_index=step_index,
                        current_symbol=current_symbol,
                        attempted_next_symbol=next_symbol,
                        reason=reason,
                        relation_exists=relation_exists
                    )
                    self.refusals.append(refusal)
                    continue

            current_identity_hash = next_identity_hash
            current_symbol = next_symbol
            step_index += 1

        return self.refusals


# ============================================================================
# COMPONENT 4: ESCAPE TOPOLOGY MEASUREMENT
# ============================================================================

def measure_escape_topology(
    phase4_output,
    phase3_metrics,
    phase2_metrics,
    continuation_tokens,
    max_steps=200,
):
    """Measure escape topology for each symbol."""
    observer = ContinuationObserver(phase4_output, phase3_metrics, phase2_metrics)

    tokens = list(continuation_tokens)
    action = TokenAction(tokens)

    topology = defaultdict(lambda: {
        'self_transition_attempts': 0,
        'appearances': 0,
        'escape_paths': Counter(),
        'near_refusal_events': 0
    })

    current_identity_hash = None
    current_symbol = None

    for step in range(max_steps):
        if step >= len(tokens) * 3:
            break

        residue = action()
        next_identity_hash = observer._residue_to_identity_hash(residue)

        if next_identity_hash is None:
            continue

        next_symbol = observer._identity_hash_to_symbol(next_identity_hash)

        if next_symbol is None:
            continue

        topology[next_symbol]['appearances'] += 1

        if current_symbol is not None:
            topology[current_symbol]['near_refusal_events'] += 1

            if current_symbol == next_symbol:
                topology[current_symbol]['self_transition_attempts'] += 1
            else:
                topology[current_symbol]['escape_paths'][next_symbol] += 1

        if current_identity_hash != next_identity_hash:
            current_identity_hash = next_identity_hash
            current_symbol = next_symbol

    # Compute metrics
    for symbol in topology:
        data = topology[symbol]
        data['distinct_escape_paths'] = len(data['escape_paths'])

        total_escapes = sum(data['escape_paths'].values())
        if total_escapes > 0:
            probabilities = [count / total_escapes for count in data['escape_paths'].values()]
            entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in probabilities)
            ep_len = len(data['escape_paths'])
            max_entropy = math.log2(ep_len) if ep_len > 1 else 0

            if max_entropy > 0:
                data['escape_concentration'] = 1 - (entropy / max_entropy)
            else:
                data['escape_concentration'] = 1.0 if total_escapes > 0 else 0.0
        else:
            data['escape_concentration'] = 0.0

    return dict(topology)


# ============================================================================
# COMPONENT 5: TOPOLOGY CLUSTERING
# ============================================================================

def cluster_by_topology(topology):
    """Cluster identities by escape topology characteristics."""
    clusters = defaultdict(list)

    for symbol, data in topology.items():
        attempts = data['self_transition_attempts']
        near_refusals = data['near_refusal_events']

        if attempts > 0:
            pressure_level = 'high'
        elif near_refusals > 5:
            pressure_level = 'medium'
        else:
            pressure_level = 'low'

        escape_paths = data['distinct_escape_paths']
        concentration = data['escape_concentration']

        if escape_paths >= 3:
            freedom_level = 'high'
        elif escape_paths == 2:
            freedom_level = 'medium'
        else:
            freedom_level = 'low'

        if concentration == 1.0:
            concentration_type = 'concentrated'
        elif concentration < 0.5:
            concentration_type = 'distributed'
        else:
            concentration_type = 'mixed'

        cluster_key = f"{pressure_level}_pressure_{freedom_level}_freedom_{concentration_type}"

        clusters[cluster_key].append({
            'symbol': symbol,
            'attempts': attempts,
            'near_refusals': near_refusals,
            'escape_paths': escape_paths,
            'concentration': concentration,
            'escape_targets': list(data['escape_paths'].keys())
        })

    return dict(clusters)


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_complete_system(
    input_text,
    cont_text=None,
    tokenization_method="word",
    num_runs=3,
):
    """
    Run complete end-to-end unified system.

    Args:
        input_text: Input text for structure emergence
        cont_text: Text for continuation (if None, uses input_text)
        tokenization_method: Tokenization method
        num_runs: Number of runs for multi-run persistence

    Returns:
        Complete results dictionary
    """
    print("=" * 70)
    print("COMPLETE UNIFIED SYSTEM")
    print("threshold_onset <-> santok")
    print("कार्य (kārya) happens before ज्ञान (jñāna)")
    print("=" * 70)
    print()

    # STEP 1: Tokenization
    print("STEP 1: TOKENIZATION (santok)")
    print("-" * 70)
    tokens = tokenize_text(input_text, tokenization_method)
    print(f"Tokens: {len(tokens)}")
    print()

    # STEP 2: Structure Emergence
    print("STEP 2: STRUCTURE EMERGENCE (threshold_onset Phases 0-4)")
    print("-" * 70)
    structure = run_structure_emergence(input_text, tokenization_method, num_runs)

    if structure is None:
        print("Structure emergence failed.")
        return None

    print("Phase 4 complete:")
    print(f"  Identities: {structure['phase4']['identity_alias_count']}")
    print(f"  Relations: {structure['phase4']['relation_alias_count']}")
    print()

    # STEP 3: Continuation Observation
    print("STEP 3: CONTINUATION OBSERVATION")
    print("-" * 70)

    if cont_text is None:
        cont_text = input_text

    continuation_tokens = tokenize_text(cont_text, tokenization_method)

    observer = ContinuationObserver(
        structure['phase4'],
        structure['phase3'],
        structure['phase2']
    )

    refusals = observer.observe_continuation(continuation_tokens, max_steps=100)

    print(f"Refusals observed: {len(refusals)}")
    if refusals:
        r = refusals[0]
        print(f"  First refusal: step={r.step_index}, "
              f"current={r.current_symbol}, attempted={r.attempted_next_symbol}")
    print()

    # STEP 4: Escape Topology
    print("STEP 4: ESCAPE TOPOLOGY MEASUREMENT")
    print("-" * 70)

    topology = measure_escape_topology(
        structure['phase4'],
        structure['phase3'],
        structure['phase2'],
        continuation_tokens,
        max_steps=200
    )

    symbols_with_attempts = [s for s, d in topology.items() if d['self_transition_attempts'] > 0]
    total_attempts = sum(d['self_transition_attempts'] for d in topology.values())

    print(f"Identities measured: {len(topology)}")
    print(f"Symbols with self-transition attempts: {len(symbols_with_attempts)}")
    print(f"Total attempts: {total_attempts}")
    print()

    # STEP 5: Topology Clustering
    print("STEP 5: TOPOLOGY CLUSTERING")
    print("-" * 70)

    clusters = cluster_by_topology(topology)

    print(f"Clusters: {len(clusters)}")
    for cluster_name, members in sorted(clusters.items()):
        print(f"  {cluster_name}: {len(members)} identities")
    print()

    # FINAL SUMMARY
    print("=" * 70)
    print("COMPLETE SYSTEM SUMMARY")
    print("=" * 70)
    print()
    print("Structure:")
    print(f"  Identities: {structure['phase4']['identity_alias_count']}")
    print(f"  Relations: {structure['phase4']['relation_alias_count']}")
    print()
    print("Continuation:")
    print(f"  Refusals: {len(refusals)}")
    all_self = all(
        r.current_symbol == r.attempted_next_symbol for r in refusals
    )
    print(f"  All self-transitions: {all_self}")
    print()
    print("Topology:")
    print(f"  Identities: {len(topology)}")
    print(f"  Under pressure: {len(symbols_with_attempts)}")
    print()
    print("Clusters:")
    print(f"  Total: {len(clusters)}")
    print()
    print("=" * 70)
    print("KEY RESULT")
    print("=" * 70)
    print()
    print("Structure → Constraint → Refusal → Necessity → Organization")
    print()
    print("No meaning added. No labels. No interpretation.")
    print("Difference emerges from topology, not semantics.")
    print()
    print("=" * 70)

    return {
        'structure': structure,
        'refusals': [r.to_dict() for r in refusals],
        'topology': {k: dict(v) if isinstance(v, Counter) else v for k, v in topology.items()},
        'clusters': clusters
    }


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Example usage
    SAMPLE_TEXT = """
    Action before knowledge.
    Function stabilizes before meaning appears.
    Structure emerges before language exists.
    """

    SAMPLE_CONTINUATION = "Tokens become actions. Patterns become residues."

    results = run_complete_system(
        input_text=SAMPLE_TEXT,
        cont_text=SAMPLE_CONTINUATION,
        tokenization_method="word",
        num_runs=3
    )

    if results:
        print("\nComplete system executed successfully.")
        print("All results available in returned dictionary.")
