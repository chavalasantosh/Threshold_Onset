"""
SanTOK Native Base Engine — Law 5 Constraint Matcher
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Law 5: A token's role is defined by its invariant neighbor constraints.
Prediction = find the token whose entry constraints match the current exit state.

Fixes applied from real Mahabharata data analysis:
  - Punct cids excluded from matrix (they are boundaries, not content)
  - Tiebreaker = freq × saturation (weight × density)
  - bs_tolerance tightened to 5000
  - Stop words excluded from generation candidates
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from vocabulary.vocab_builder import build_vocab
except ImportError:
    def build_vocab(tokens, min_freq=1):
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
        for cid, v in vocab.items():
            v["saturation"] = 1.0
        return vocab


# ── Punct cids derived from real corpus — Law 3 (fixed identities) ──
# These are structural boundaries, never generation targets
_PUNCT_CIDS = {
    1908,    # .
    11443,   # [
    21202,   # )
    32445,   # "
    50637,   # -
    51843,   # '
    83208,   # "
    94988,   # ;
    99086,   # ]
    101310,  # ?
    103671,  # :
    109199,  # '
    126647,  # (
    138105,  # ,
    141521,  # !
}

# Stop word cids — structural glue, not generation targets
# These are the top function words that dominate every transition
_STOP_CIDS = {
    125905,  # the
    82271,   # of
    10221,   # and
    101268,  # to
    127366,  # in
    1579,    # that
    114982,  # with
    7740,    # And
    83890,   # a
    76256,   # by
    3261,    # his
    145119,  # is
    34226,   # I
    110965,  # all
    132794,  # as
    112486,  # this
    32621,   # for
    10684,   # it
    31513,   # no
    147891,  # he
}

# Combined exclusion set
_EXCLUDED_CIDS = _PUNCT_CIDS | _STOP_CIDS


def _is_excluded(cid):
    return int(cid) in _EXCLUDED_CIDS


def build_crystalline_matrix(tokens):
    """
    One-pass corpus scan. Records entry constraints for every content_id.
    Excludes punct and stop word cids from being matrix targets.
    """
    matrix = {}
    content = [
        t for t in tokens
        if t.get("text", "").strip()
        and not _is_excluded(int(t.get("content_id", 0)))
    ]

    print(f"[*] Building Law 5 matrix from {len(content):,} content tokens...")

    for i in range(2, len(content)):
        t2 = content[i - 2]
        t1 = content[i - 1]
        t0 = content[i]

        cid = int(t0.get("content_id", 0))
        if cid == 0 or _is_excluded(cid):
            continue

        # Entry constraints: momentum arriving at this token
        d_fe = int(t1.get("frontend", 0)) - int(t2.get("frontend", 0))
        d_bs = int(t1.get("backend_scaled", 0)) - int(t2.get("backend_scaled", 0))

        # Momentum transfer: pressure shift upon entry
        transfer_bs = int(t0.get("backend_scaled", 0)) - int(t1.get("backend_scaled", 0))

        if cid not in matrix:
            matrix[cid] = []

        matrix[cid].append({
            "lock_d_fe":    d_fe,
            "lock_d_bs":    d_bs,
            "transfer_d_bs": transfer_bs,
        })

    print(f"[*] Matrix: {len(matrix):,} structural nodes mapped.")
    return matrix


def predict_next(sequence, matrix, vocab, bs_tolerance=5000):
    """
    Calculate exit momentum from sequence tail.
    Find content_id whose entry constraints match.
    Tiebreaker: freq × saturation (weight × structural density).
    """
    if len(sequence) < 2:
        return None, 0

    t1 = sequence[-2]
    t2 = sequence[-1]

    exit_fe = int(t2.get("frontend", 0)) - int(t1.get("frontend", 0))
    exit_bs = int(t2.get("backend_scaled", 0)) - int(t1.get("backend_scaled", 0))

    candidates = []

    for cid, entries in matrix.items():
        cid = int(cid)
        for entry in entries:
            if entry["lock_d_fe"] == exit_fe:
                dist = abs(entry["lock_d_bs"] - exit_bs)
                if dist <= bs_tolerance:
                    v = vocab.get(cid)
                    if not v:
                        continue
                    freq = v.get("freq", 1)
                    sat  = v.get("saturation", 0.0)
                    weight = freq * sat   # structural mass
                    friction = abs(entry["lock_d_bs"] - exit_bs)
                    candidates.append((cid, friction, weight, entry["transfer_d_bs"]))
                    break

    if not candidates:
        return None, 0

    # PURE NATIVE PHYSICS: 
    # 1. Primary: Lowest Friction (The tightest physical lock to Law 5)
    # 2. Secondary: Highest Mass (The topological tiebreaker)
    candidates.sort(key=lambda x: (x[1], -x[2]))
    return candidates[0][0], candidates[0][3]


def generate_text(seed, matrix, vocab, max_words=30, bs_tolerance=5000):
    """
    Generate tokens from seed using Law 5 constraint matching.
    Tracks last 10 generated cids to avoid immediate repetition.
    """
    sequence = list(seed)
    generated = []
    recent = []

    print("[*] Firing Law 5 generator...")

    for step in range(max_words):
        # Filter already-recent tokens from matrix temporarily
        active_matrix = {
            cid: entries for cid, entries in matrix.items()
            if int(cid) not in recent
        }

        best_cid, transfer_bs = predict_next(sequence, active_matrix, vocab, bs_tolerance)

        if best_cid is None:
            # Widen tolerance once before giving up
            best_cid, transfer_bs = predict_next(sequence, matrix, vocab, bs_tolerance * 3)
            if best_cid is None:
                print(f"  [!] No match found at step {step}. Halting.")
                break

        generated.append(best_cid)

        # Track recent to prevent loops
        recent.append(int(best_cid))
        if len(recent) > 10:
            recent.pop(0)

        # Build next token state from vocab
        v = vocab.get(int(best_cid), {})
        native_fe = v.get("fe", 1)
        prev_bs = int(sequence[-1].get("backend_scaled", 0))

        new_token = {
            "content_id":    best_cid,
            "frontend":      native_fe,
            "backend_scaled": max(0, min(99999, prev_bs + transfer_bs)),
        }
        sequence.append(new_token)

    return generated


def run(unified_path=None):
    if unified_path is None:
        unified_path = os.path.join("output", "mahabharata_ganguli_1_santok_unified.json")

    if not os.path.exists(unified_path):
        print(f"[!] File not found: {unified_path}")
        return

    print(f"[*] Loading: {unified_path}")
    with open(unified_path, encoding="utf-8") as f:
        data = json.load(f)

    tokens = data.get("tokens", [])
    print(f"[*] Tokens: {len(tokens):,}")

    print("[*] Building vocabulary...")
    vocab = build_vocab(tokens, min_freq=2)

    matrix = build_crystalline_matrix(tokens)

    import random

    for run_idx in range(1, 6):
        start = random.randint(1000, len(tokens) - 100)
        seed = []
        for t in tokens[start:]:
            cid = int(t.get("content_id", 0))
            txt = t.get("text", "").strip()
            if txt and not _is_excluded(cid) and cid > 0:
                seed.append(t)
                if len(seed) == 2:
                    break

        if len(seed) < 2:
            print("[!] Could not find seed tokens.")
            continue

        print(f"\n" + "=" * 65)
        print(f"SanTOK GENERATED TEXT (RUN {run_idx}):")
        print(f"Seed 1: '{seed[0]['text']}' (FE={seed[0]['frontend']}, BS={seed[0]['backend_scaled']})")
        print(f"Seed 2: '{seed[1]['text']}' (FE={seed[1]['frontend']}, BS={seed[1]['backend_scaled']})")
        print("-" * 65)

        gen_cids = generate_text(seed, matrix, vocab, max_words=30, bs_tolerance=5000)

        words = [seed[0]["text"], seed[1]["text"]]
        for cid in gen_cids:
            v = vocab.get(int(cid), {})
            words.append(v.get("text", f"<{cid}>"))

        print(" ".join(words))
        print("=" * 65)


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else None
    run(path)
