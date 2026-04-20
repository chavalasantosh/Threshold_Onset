"""
SanTOK Architecture: Physics Predictor API Wrapper
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Cleanly decoupled from the Extraction Pipeline.
Ingests `_unified.json` and exposes a pure `.generate()` method.

Identity Hook:
  `generate()` accepts an optional `identity_validator` callable.
  The engine hands each candidate {cid, text, fe, bs} to the validator.
  If the validator refuses (returns False), the engine tests the next
  lowest-friction candidate, until identity and physics align.
  If no validator is passed, the engine runs in pure physics mode.
"""

import json
import os
import random

def _build_vocab(tokens, min_freq=2):
    vocab = {}
    for t in tokens:
        cid = int(t.get("content_id", 0))
        if cid == 0: continue
        if cid not in vocab:
            vocab[cid] = {
                "text": t.get("text", ""),
                "freq": 0, "transitions": 0,
                "fe": int(t.get("frontend", 0)),
                "saturation": 0.0
            }
        vocab[cid]["freq"] += 1
    
    # Prune obscure occurrences
    vocab = {cid: v for cid, v in vocab.items() if v["freq"] >= min_freq}
        
    for cid, v in vocab.items():
        v["saturation"] = 1.0
    return vocab


class SantokEngine:
    """
    Native Law 5 Text Generator.
    Operates strictly via Topological Subtraction and Friction bounds. 
    """
    def __init__(self, json_path=None, json_data=None, min_freq=2):
        # ── Punct & Stop exclusions mapped natively from Law 3 ──
        self._excluded_cids = {
            1908, 11443, 21202, 32445, 50637, 51843, 83208, 94988, 
            99086, 101310, 103671, 109199, 126647, 138105, 141521, # punct
            125905, 82271, 10221, 101268, 127366, 1579, 114982, 
            7740, 83890, 76256, 3261, 145119, 34226, 110965, 
            132794, 112486, 32621, 10684, 31513, 147891 # stops
        }
        self.tokens = []
        self.vocab = {}
        self.matrix = {}
        
        if json_path:
            self.load_from_path(json_path, min_freq)
        elif json_data:
            self._load(json_data, min_freq)

    def _is_excluded(self, cid):
        return int(cid) in self._excluded_cids

    def load_from_path(self, json_path, min_freq=2):
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"[!] Corpus missing: {json_path}")
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        self._load(data, min_freq)

    def _load(self, data, min_freq=2):
        self.tokens = data.get("tokens", [])
        self.vocab = _build_vocab(self.tokens, min_freq)
        
        # Build Matrix natively
        self.matrix = {}
        content = [
            t for t in self.tokens
            if t.get("text", "").strip() 
            and not self._is_excluded(int(t.get("content_id", 0)))
        ]
        
        for i in range(2, len(content)):
            t2 = content[i - 2]
            t1 = content[i - 1]
            t0 = content[i]

            cid = int(t0.get("content_id", 0))
            if cid == 0 or self._is_excluded(cid):
                continue

            # Momentum constraints
            d_fe = int(t1.get("frontend", 0)) - int(t2.get("frontend", 0))
            d_bs = int(t1.get("backend_scaled", 0)) - int(t2.get("backend_scaled", 0))
            transfer_bs = int(t0.get("backend_scaled", 0)) - int(t1.get("backend_scaled", 0))

            if cid not in self.matrix:
                self.matrix[cid] = []

            self.matrix[cid].append({
                "lock_d_fe": d_fe,
                "lock_d_bs": d_bs,
                "transfer_d_bs": transfer_bs,
            })

    def get_random_seed(self):
        """Pulls a random valid 2-word tuple natively from the corpus."""
        if not self.tokens:
            return []
        
        for attempt in range(100):
            start = random.randint(1000, max(2000, len(self.tokens) - 100))
            seed = []
            for t in self.tokens[start:]:
                cid = int(t.get("content_id", 0))
                txt = t.get("text", "").strip()
                if txt and not self._is_excluded(cid) and cid > 0:
                    seed.append(t)
                    if len(seed) == 2:
                        return seed
        return []

    def _predict_next(self, sequence, active_matrix, bs_tolerance=5000, identity_validator=None):
        if len(sequence) < 2:
            return None, 0

        t1 = sequence[-2]
        t2 = sequence[-1]

        exit_fe = int(t2.get("frontend", 0)) - int(t1.get("frontend", 0))
        exit_bs = int(t2.get("backend_scaled", 0)) - int(t1.get("backend_scaled", 0))

        candidates = []
        for cid, entries in active_matrix.items():
            cid = int(cid)
            v = self.vocab.get(cid)
            if not v:
                continue

            for entry in entries:
                if entry["lock_d_fe"] == exit_fe:
                    dist = abs(entry["lock_d_bs"] - exit_bs)
                    if dist <= bs_tolerance:
                        freq = v.get("freq", 1)
                        sat  = v.get("saturation", 0.0)
                        weight = freq * sat
                        friction = dist
                        candidates.append((cid, friction, weight, entry["transfer_d_bs"]))
                        break

        if not candidates:
            return None, 0

        # Primary: Lowest Friction. Secondary: Highest Mass.
        candidates.sort(key=lambda x: (x[1], -x[2]))

        # Walk through friction-sorted candidates.
        # If THRESHOLD_ONSET provides an identity_validator, every candidate
        # is submitted for structural approval before it locks into the trajectory.
        # The validator receives the full token dict so it can make a
        # structural decision without a reverse lookup.
        for cid, friction, weight, transfer_d_bs in candidates:
            if identity_validator is not None:
                v = self.vocab.get(cid, {})
                token_dict = {
                    "cid":  cid,
                    "text": v.get("text", ""),
                    "fe":   v.get("fe", 0),
                    "freq": v.get("freq", 0),
                    "weight": weight,
                }
                if not identity_validator(token_dict):
                    continue  # Identity refused — test next lowest-friction candidate
            return cid, transfer_d_bs

        return None, 0

    def generate(self, seed_tokens=None, length=30, tolerance=5000, identity_validator=None):
        """
        Executes Generation via Native Law 5 Friction Matching.

        Args:
            seed_tokens   : List of 2 token dicts from the corpus. Auto-selected if None.
            length        : Number of tokens to generate beyond the seed.
            tolerance     : BS friction tolerance window for constraint matching.
            identity_validator : Optional callable from THRESHOLD_ONSET identity layer.
                                 Receives full token dict {cid, text, fe, freq, weight}.
                                 Returns True to allow, False to refuse the candidate.
        """
        if not self.matrix:
            raise ValueError("[!] Matrix is uninitialized. Pass JSON on __init__")

        seed_tokens = seed_tokens or self.get_random_seed()
        if len(seed_tokens) < 2:
            raise ValueError("[!] Need exactly 2 seed tokens.")

        sequence = list(seed_tokens)
        gen_cids = []
        recent = []

        for step in range(length):
            active_matrix = {
                cid: entries for cid, entries in self.matrix.items()
                if int(cid) not in recent
            }

            best_cid, transfer_bs = self._predict_next(
                sequence, active_matrix, tolerance, identity_validator
            )

            if best_cid is None:
                # Widen tolerance, pass identity filter through again
                best_cid, transfer_bs = self._predict_next(
                    sequence, self.matrix, tolerance * 3, identity_validator
                )
                if best_cid is None:
                    break

            gen_cids.append(best_cid)

            recent.append(int(best_cid))
            if len(recent) > 10:
                recent.pop(0)

            v = self.vocab.get(int(best_cid), {})
            native_fe = v.get("fe", 1)
            prev_bs = int(sequence[-1].get("backend_scaled", 0))

            sequence.append({
                "content_id": best_cid,
                "frontend": native_fe,
                "backend_scaled": max(0, min(99999, prev_bs + transfer_bs)),
            })

        # Assemble string output
        words = [seed_tokens[0]["text"], seed_tokens[1]["text"]]
        for cid in gen_cids:
            v = self.vocab.get(int(cid), {})
            words.append(v.get("text", f"<{cid}>"))

        return " ".join(words)
