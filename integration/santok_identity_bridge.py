#!/usr/bin/env python3
"""
THRESHOLD_ONSET <-> SantokEngine Identity Bridge
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is the single integration point between:
  - THRESHOLD_ONSET identity permission layer (structural state)
  - SantokEngine base model (physics generation)

Responsibilities:
  1. Load THRESHOLD_ONSET's identity permission profile from its Phase 4 output.
  2. Build a native identity_validator callable from that profile.
  3. Convert THRESHOLD_ONSET's current identity state into engine seed tokens.
  4. Call SantokEngine.generate() with identity_validator attached.
  5. Return the generated text — output from both systems acting as one.

No 3rd party libraries. No transformers. No embeddings.
One structural bridge. Two native systems. One output.
"""

import os
import sys
import json

# Add project root to path
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
if _root not in sys.path:
    sys.path.insert(0, _root)

from model.santok_engine import SantokEngine


# ── Identity Validator Builder ────────────────────────────────────────────────

def build_identity_validator(permission_profile):
    """
    Legacy v1 validator — kept for backward compatibility with standalone runs.
    Uses simple text-lookup permission profile from unified_system.
    """
    if not permission_profile:
        return None

    identity_gate = {}
    for symbol, data in permission_profile.items():
        allowed  = data.get("allowed", 0)
        refused  = data.get("refused", 0)
        stable = (allowed > 0) and (allowed >= refused)
        identity_gate[str(symbol).lower()] = stable

    def validator(token_dict):
        text_key = token_dict.get("text", "").strip().lower()
        return identity_gate.get(text_key, True)

    return validator


def build_production_validator(topology, path_scores, clusters, symbol_to_token=None):
    """
    PRODUCTION Identity Validator (v2).
    
    Reads the real PipelineResult outputs from run_complete.run():
      - topology  : Dict[str, TopologyData] — escape_concentration per identity symbol.
      - path_scores: Dict[(hash1,hash2), float] — scored structural transitions.
      - clusters  : Dict[str, List[ClusterMember]] — pressure/freedom groupings.
    
    Builds a live structural suppression gate for the SanTok physics engine.
    
    Rules (all Sovereign — zero borrowed math):
      1. Any symbol in 'high_pressure' cluster → structurally TRAPPED.
         Suppress it unless nothing else is available.
      2. Any symbol in 'high_freedom' cluster → structurally MOBILE.
         Always allow it. Promote it as preferred (weight boost).
      3. All other symbols → neutral. Physics friction decides normally.
    
    Returns:
        A callable (token_dict -> bool) that SanTok calls per candidate.
        Also returns derived tension_threshold from topology concentration.
    """
    # Build suppression and promotion sets from cluster labels
    suppressed_text = set()   # token TEXT values for trapped identities
    promoted_text   = set()   # token TEXT values for free identities
    if symbol_to_token is None:
        symbol_to_token = {}

    for cluster_label, members in clusters.items():
        for member in members:
            # ClusterMember is a dataclass with .symbol attribute (integer key)
            sym = getattr(member, "symbol", None)
            if sym is None and isinstance(member, dict):
                sym = member.get("symbol")
            if sym is None:
                continue
            # Resolve integer sym ID → token text via symbol_to_token
            token_text = symbol_to_token.get(sym) or symbol_to_token.get(str(sym), "")
            if not token_text:
                continue
            t = token_text.strip().lower()
            if "high_pressure" in cluster_label:
                suppressed_text.add(t)
            if "high_freedom" in cluster_label:
                promoted_text.add(t)

    def validator(token_dict):
        """Allows/blocks SanTok candidates based on structural pressure."""
        text_key = token_dict.get("text", "").strip().lower()
        if text_key in promoted_text:
            return True
        if text_key in suppressed_text:
            return False
        return True

    # Compute tension_threshold from mean escape_concentration across topology
    if topology:
        concentrations = []
        for sym, td in topology.items():
            conc = getattr(td, "escape_concentration", 0.0) if not isinstance(td, dict) else td.get("escape_concentration", 0.0)
            concentrations.append(conc)
        mean_concentration = sum(concentrations) / len(concentrations) if concentrations else 0.5
    else:
        mean_concentration = 0.5

    # High concentration (identity trapped ≈ 1.0) → Aggressive tight threshold
    # Low concentration (identity free ≈ 0.0) → Calm wide threshold
    if mean_concentration >= 0.75:
        tension_threshold = 1   # Aggressive
    elif mean_concentration <= 0.25:
        tension_threshold = 10  # Calm
    else:
        tension_threshold = 4   # Neutral

    return validator, tension_threshold, suppressed_text, promoted_text




# ── Identity Seed Extractor ───────────────────────────────────────────────────

def extract_seed_from_identity(engine, current_state_text):
    """
    Converts THRESHOLD_ONSET's current identity state text into two seed
    tokens that the SantokEngine can use as its starting trajectory vector.

    The current_state_text could be the most recent structural anchor phrase
    from THRESHOLD_ONSET (e.g. "Action before knowledge").

    Strategy:
      - Split the state text into words.
      - Match the first two words that exist in the engine's vocabulary.
      - If no match is found, fall back to engine's own random seed.

    Args:
        engine            : SantokEngine instance (already loaded with corpus).
        current_state_text: String from THRESHOLD_ONSET's identity state.

    Returns:
        List of 2 token dicts suitable for engine.generate(seed_tokens=).
    """
    if not current_state_text or not current_state_text.strip():
        return engine.get_random_seed()

    words = current_state_text.strip().split()

    # Reverse-lookup: text -> token dict from engine vocabulary
    text_to_token = {}
    for cid, v in engine.vocab.items():
        text_to_token[v.get("text", "").strip().lower()] = {
            "text":           v.get("text", ""),
            "content_id":     cid,
            "frontend":       v.get("fe", 1),
            "backend_scaled": 50000,   # neutral start position
        }

    matched = []
    for word in words:
        key = word.strip().lower()
        if key in text_to_token:
            matched.append(text_to_token[key])
            if len(matched) == 2:
                return matched

    # Partial match: only one word found
    if len(matched) == 1:
        fallback = engine.get_random_seed()
        if fallback:
            return [matched[0], fallback[1]]

    # No match at all — pure physics seed
    return engine.get_random_seed()


# ── Directional Escape Physics (SanTok Law 7) ────────────────────────────────

def find_escape_seed(engine, topology, symbol_to_token):
    """
    DIRECTIONAL ESCAPE PHYSICS — SanTok Law 7.

    This is why the engine used to produce echo loops:
      - Old: seed from INPUT words → engine walks SAME trajectory → repeats input
      - New: detect input's identity cluster → find its ESCAPE BOUNDARY →
             seed at the EXIT point → engine walks AWAY from input → RESPONSE

    Algorithm (100% Sovereign, zero borrowed logic):

      1. Scan the topology for its HIGHEST-TRAFFIC escape path.
         `topology[symbol].escape_paths` is a Counter mapping:
           source_symbol → {escape_target_symbol: count}
         The escape target with the highest total count is where the
         geometry MOST WANTS to go when the input identity is under pressure.

      2. Map that escape target symbol back to a real token via symbol_to_token.
         This is the first word at the STRUCTURAL EXIT of the input cluster.

      3. Find that word in the SanTok vocabulary.
         Build a seed token dict at a NEUTRAL backend_scaled position (mid-space).

      4. Find the SECOND seed by scanning the SanTok matrix for where the
         escape token naturally leads via its own lowest-friction transition.

      5. Return the two-token escape seed. The engine now starts at the
         geometric EXIT, not the entry. Output is structurally different
         from the input. This is RESPONSE, not ECHO.

    Args:
        engine          : SantokEngine (loaded with corpus matrix).
        topology        : Dict[str, TopologyData] from THRESHOLD_ONSET pipeline.
        symbol_to_token : Dict[str, str] from model_state["symbol_to_token"].

    Returns:
        List of 2 token dicts at the escape boundary, or random seed if
        no escape path can be mapped to the SanTok vocabulary.
    """
    if not topology or not symbol_to_token:
        return engine.get_random_seed()

    # Build a reverse vocabulary lookup: text_lower → (cid, v)
    text_to_vocab = {}
    for cid, v in engine.vocab.items():
        text_lower = v.get("text", "").strip().lower()
        if text_lower:
            text_to_vocab[text_lower] = (cid, v)

    if not text_to_vocab:
        return engine.get_random_seed()

    # Step 1: Find highest-traffic escape target across ALL topology symbols.
    # topology keys and escape_paths keys are INTEGER symbol IDs.
    # symbol_to_token maps INTEGER ID → token text.
    escape_traffic = {}  # escape_target_symbol (int) → cumulative count
    for symbol, td in topology.items():
        for target_sym, count in td.escape_paths.items():
            if target_sym == symbol:
                continue  # skip self-loops
            escape_traffic[target_sym] = escape_traffic.get(target_sym, 0) + count

    if not escape_traffic:
        return engine.get_random_seed()

    # Sort by traffic descending — pick the dominant exit
    ranked_exits = sorted(escape_traffic.items(), key=lambda x: x[1], reverse=True)

    # Step 2: Walk ranked exits until one maps to a real token in SanTok vocab.
    # symbol_to_token uses the same integer IDs as topology.
    for escape_sym, traffic_count in ranked_exits:
        # Look up with integer key directly, then try string key as fallback
        token_text = symbol_to_token.get(escape_sym) or symbol_to_token.get(str(escape_sym), "")
        if not token_text:
            continue

        token_key = token_text.strip().lower()
        if token_key not in text_to_vocab:
            continue

        # Found an escape symbol that exists in the SanTok vocabulary
        escape_cid, escape_v = text_to_vocab[token_key]

        # Step 3: Build first seed token at escape boundary.
        # backend_scaled = 50000 is the neutral midpoint in geometric space.
        first_seed = {
            "text":           escape_v.get("text", token_text),
            "content_id":     escape_cid,
            "frontend":       escape_v.get("fe", 1),
            "backend_scaled": 50000,
        }

        # Step 4: Find second seed from the escape token's own
        # lowest-friction outgoing transition in the matrix.
        matrix_entries = engine.matrix.get(str(escape_cid), [])
        if matrix_entries:
            sorted_entries = sorted(
                matrix_entries,
                key=lambda e: abs(e.get("transfer_d_bs", 99999))
            )
            transfer_bs = sorted_entries[0].get("transfer_d_bs", 0)
            target_bs = 50000 + transfer_bs

            best_second_cid = None
            best_second_dist = 99999
            for cid2, v2 in engine.vocab.items():
                if cid2 == escape_cid:
                    continue
                dist = abs(v2.get("fe", 0) - target_bs)
                if dist < best_second_dist:
                    best_second_dist = dist
                    best_second_cid = cid2

            if best_second_cid is not None:
                v2 = engine.vocab[best_second_cid]
                second_seed = {
                    "text":           v2.get("text", ""),
                    "content_id":     best_second_cid,
                    "frontend":       v2.get("fe", 1),
                    "backend_scaled": target_bs,
                }
                return [first_seed, second_seed]

        # Step 4 fallback: pair with a random seed
        fallback = engine.get_random_seed()
        if fallback and len(fallback) >= 2:
            return [first_seed, fallback[1]]

    # Nothing mapped — fall back to random
    return engine.get_random_seed()


# ── Integrated Generation Entry Point ────────────────────────────────────────

class ThresholdSantokBridge:
    """
    The single integration point between THRESHOLD_ONSET and the SantokEngine.

    Usage:
        bridge = ThresholdSantokBridge(corpus_json_path)
        text   = bridge.generate(
                     current_state_text="Action before knowledge",
                     permission_profile=profile,
                     length=30
                 )

    The bridge can also be called without a permission_profile for pure
    physics generation, or without current_state_text for a random seed.
    """

    def __init__(self, corpus_json_path, min_freq=2):
        if not os.path.exists(corpus_json_path):
            raise FileNotFoundError(f"[!] Corpus not found: {corpus_json_path}")
        print(f"[Bridge] Loading corpus: {os.path.basename(corpus_json_path)}")
        self.engine = SantokEngine(corpus_json_path, min_freq=min_freq)
        print(f"[Bridge] Matrix ready. {len(self.engine.matrix)} structural nodes mapped.")

    def generate(
        self,
        current_state_text=None,
        permission_profile=None,
        length=30,
        tolerance=5000,
        identity_state_id=0
    ):
        """
        Generate text with THRESHOLD_ONSET identity steering.

        Args:
            current_state_text : THRESHOLD_ONSET's current identity phrase (seed).
            permission_profile : Identity permission dict from identity_permissions.py.
            length             : Number of tokens to generate.
            tolerance          : BSS friction tolerance.
            identity_state_id  : Sovereign Numeric State (0=Neutral, 1=Calm, 2=Aggressive).

        Returns:
            Generated string.
        """
        # 1. Build the identity gate from THRESHOLD_ONSET's permission state
        validator = build_identity_validator(permission_profile)

        # 2. Translate identity state to engine seed trajectory
        seed = extract_seed_from_identity(self.engine, current_state_text)

        if seed and len(seed) >= 2:
            print(f"[Bridge] Seed: '{seed[0]['text']}' → '{seed[1]['text']}'")
        else:
            print("[Bridge] No identity seed matched. Randomizing trajectory.")

        # Resolve Tension State Constraints
        tension_threshold = 4 # Neutral Default
        if identity_state_id == 1:
            tension_threshold = 10 # Calm / Wide linguistic waves
        elif identity_state_id == 2:
            tension_threshold = 1  # Aggressive / Rapid erratic jumping bounds

        # 3. Fire the engine with kinetic tension and gating active
        return self.engine.generate(
            seed_tokens=seed,
            length=length,
            tolerance=tolerance,
            identity_validator=validator,
            tension_threshold=tension_threshold
        )


# ── Standalone Demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Standalone Integration Execution.
    Runs the Real Identity evaluation sequence.
    """
    # 1. Accept REAL input from the console
    if len(sys.argv) > 1:
        raw_corpus = sys.argv[1]
        text_input = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    else:
        raw_corpus = input("Enter Corpus Name or Path > ").strip()
        text_input = input("Enter Real Identity State Text > ").strip()

    raw_corpus = raw_corpus.strip().replace("&", "").replace("'", "").replace('"', "").strip()
    corpus_name = os.path.basename(raw_corpus).replace(".txt", "").replace(".jsonl", "").replace("_santok_unified.json", "")

    if not corpus_name:
        print("[!] No corpus provided. Aborting.")
        sys.exit(1)

    if raw_corpus.endswith("_santok_unified.jsonl") and os.path.exists(raw_corpus):
        _corpus = raw_corpus
    elif raw_corpus.endswith("_santok_unified.json") and os.path.exists(raw_corpus):
        _corpus = raw_corpus
    else:
        _corpus = os.path.join(_root, "output", f"{corpus_name}_santok_unified.jsonl")
        if not os.path.exists(_corpus):
            _corpus = os.path.join(_root, "output", f"{corpus_name}_santok_unified.json")

    if not os.path.exists(_corpus):
        print(f"[!] Corpus not found. Run santok_pipeline.py first:\n"
              f"    python santok_pipeline.py \"{raw_corpus}\"")
        sys.exit(1)

    if not text_input:
        print("[!] No text provided. Aborting.")
        sys.exit(1)

    print("\n" + "=" * 65)
    print("STEP 1: THRESHOLD_ONSET LIVE IDENTITY RESOLUTION")
    print("=" * 65)
    
    # 2. Fire the full identity compilation stack natively on the string
    from integration.unified_system import process_text_through_phases
    from integration.identity_permissions import compute_permission_profile
    
    results = process_text_through_phases(
        text=text_input,
        tokenization_method="word",
        num_runs=3
    )

    live_profile = None
    if results.get("phase4"):
        print("\n[*] Identity structural bounds acquired. Compiling unified Profile...")
        live_profile = compute_permission_profile(
            results["phase4"],
            results["phase3"],
            results["phase2"]
        )
    else:
        print("\n[!] Input text yielded no structural identity. Bypassing filter.")

    print("\n" + "=" * 65)
    print("STEP 2: SANTOK NATIVE ENGINE INTEGRATION")
    print("=" * 65)
    
    # 3. Pass the strictly computed profile and original state seed into the generator
    bridge = ThresholdSantokBridge(_corpus)
    output = bridge.generate(
        current_state_text=text_input,
        permission_profile=live_profile,
        length=30
    )
    
    print("\n" + "=" * 65)
    print("FINAL SANTOK COLLISION OUTPUT")
    print("=" * 65)
    print(output)

