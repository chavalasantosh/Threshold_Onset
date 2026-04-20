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
    Converts THRESHOLD_ONSET's identity permission profile into a native
    validator callable for the SantokEngine.

    The permission profile is a dict mapping symbol -> {allowed, refused, ...}
    as produced by integration/identity_permissions.py.

    Logic:
      - If a token's text (lowercased) maps to a symbol that has been
        structurally REFUSED more than it is ALLOWED, it is an unstable
        identity node. The engine must skip it.
      - If the profile is missing or empty, the validator approves all tokens
        (pure physics mode).

    Args:
        permission_profile : dict or None, from compute_permission_profile().

    Returns:
        A callable (token_dict -> bool) that the engine calls per candidate.
    """
    if not permission_profile:
        # No identity state. Pure physics mode.
        return None

    # Build a lookup: text_lower -> True (allowed) / False (refused)
    identity_gate = {}
    for symbol, data in permission_profile.items():
        allowed  = data.get("allowed", 0)
        refused  = data.get("refused", 0)
        # A symbol is structurally stable if it has been allowed at least once
        # and has not been refused more than it has been allowed.
        stable = (allowed > 0) and (allowed >= refused)
        identity_gate[str(symbol).lower()] = stable

    def validator(token_dict):
        """
        Returns True if the candidate token passes THRESHOLD_ONSET's
        structural identity gate.
        Returns True by default if the token is not in the profile
        (unlisted tokens are not refused by default).
        """
        text_key = token_dict.get("text", "").strip().lower()
        # If we have a profile entry, obey it. Otherwise, allow.
        return identity_gate.get(text_key, True)

    return validator


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
    ):
        """
        Generate text with THRESHOLD_ONSET identity steering.

        Args:
            current_state_text : THRESHOLD_ONSET's current identity phrase (seed).
            permission_profile : Identity permission dict from identity_permissions.py.
            length             : Number of tokens to generate.
            tolerance          : BSS friction tolerance.

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

        # 3. Fire the engine with identity gating active
        return self.engine.generate(
            seed_tokens=seed,
            length=length,
            tolerance=tolerance,
            identity_validator=validator,
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

    if raw_corpus.endswith("_santok_unified.json") and os.path.exists(raw_corpus):
        _corpus = raw_corpus
    else:
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

