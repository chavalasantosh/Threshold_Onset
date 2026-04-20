"""
SanTOK Extended — Vocabulary Builder
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Law 3 — IDENTITY LAW:
  content_id is fixed per text string. Always.
  content_id IS the vocabulary integer. No mapping table needed.
  Same word = same cid = same vocabulary entry. Forever.

Law 2 — TRANSITION LAW:
  Term importance = how often a cid participates in FULL_TRANSITION events.
  High-transition cids carry structural weight.
  Static/drift cids are background noise.

This replaces TF-IDF entirely.
Signal Saturation Score = frequency × transition_rate
No scipy. No numpy. No external anything.
"""


def build_vocab(tokens, min_freq=1):
    """
    Build vocabulary from a token stream.

    content_id IS the vocab integer — Law 3.
    No mapping needed. No encoding step.

    Returns dict:
      cid → {
        "text": str,          # canonical text form
        "freq": int,          # how many times this cid appears
        "fe": int,            # frontend (fixed by Law 3)
        "transitions": int,   # times this cid was in FULL_TRANSITION
        "saturation": float,  # freq × (transitions/freq) = signal weight
      }
    """
    vocab = {}
    content = [t for t in tokens if t.get("text", "").strip()]

    # Count frequencies and fe (Law 3: fe is fixed per cid)
    for tok in content:
        cid = int(tok.get("content_id", 0))
        if cid == 0:
            continue
        if cid not in vocab:
            vocab[cid] = {
                "text": tok["text"],
                "freq": 0,
                "fe": int(tok.get("frontend", 5)),
                "transitions": 0,
                "saturation": 0.0,
            }
        vocab[cid]["freq"] += 1

    # Count FULL_TRANSITION participation (Law 2)
    # FULL_TRANSITION = fe changes AND bs_shift >= 20000
    for i in range(len(content) - 1):
        a = content[i]
        b = content[i + 1]
        fe_changed = a.get("frontend") != b.get("frontend")
        bs_shift = abs(
            int(a.get("backend_scaled", 0)) - int(b.get("backend_scaled", 0))
        )
        if fe_changed and bs_shift >= 20000:
            for tok in (a, b):
                cid = int(tok.get("content_id", 0))
                if cid in vocab:
                    vocab[cid]["transitions"] += 1

    # Compute Signal Saturation Score
    for cid, v in vocab.items():
        freq = v["freq"]
        trans = v["transitions"]
        # saturation = how often this token drives structural change
        v["saturation"] = (trans / freq) if freq > 0 else 0.0

    # Apply min_freq filter
    vocab = {cid: v for cid, v in vocab.items() if v["freq"] >= min_freq}

    return vocab


def get_top_terms(vocab, n=20, by="saturation"):
    """
    Return top N terms by saturation or frequency.
    by = "saturation" or "freq"
    """
    return sorted(vocab.items(), key=lambda x: x[1][by], reverse=True)[:n]


def cid_to_index(vocab):
    """
    Build a compact integer index from cid → sequential index.
    Used for embedding layer input.
    Returns: {cid: index} dict, index starts at 1 (0 = padding)
    """
    sorted_cids = sorted(vocab.keys())
    return {cid: idx + 1 for idx, cid in enumerate(sorted_cids)}


def demo():
    sample = [
        {"text": "Action",    "frontend": 7, "backend_scaled": 13461,  "content_id": 10310},
        {"text": "before",    "frontend": 8, "backend_scaled": 10970,  "content_id": 24365},
        {"text": "knowledge", "frontend": 1, "backend_scaled": 20599,  "content_id": 102258},
        {"text": ".",         "frontend": 7, "backend_scaled": 61016,  "content_id": 1908},
        {"text": "The",       "frontend": 1, "backend_scaled": 42111,  "content_id": 128727},
        {"text": "quick",     "frontend": 2, "backend_scaled": 94056,  "content_id": 29583},
        {"text": "brown",     "frontend": 3, "backend_scaled": 3864,   "content_id": 56274},
        {"text": "fox",       "frontend": 4, "backend_scaled": 89586,  "content_id": 26790},
        {"text": "jumps",     "frontend": 1, "backend_scaled": 94188,  "content_id": 4205},
        {"text": "over",      "frontend": 5, "backend_scaled": 31123,  "content_id": 16460},
        {"text": "the",       "frontend": 2, "backend_scaled": 99016,  "content_id": 125905},
        {"text": "lazy",      "frontend": 9, "backend_scaled": 35365,  "content_id": 39107},
        {"text": "dog",       "frontend": 5, "backend_scaled": 87064,  "content_id": 134410},
        {"text": ".",         "frontend": 7, "backend_scaled": 49554,  "content_id": 1908},
        {"text": "knowledge", "frontend": 1, "backend_scaled": 33210,  "content_id": 102258},
        {"text": "jumps",     "frontend": 1, "backend_scaled": 77100,  "content_id": 4205},
    ]

    vocab = build_vocab(sample, min_freq=1)
    mapping = cid_to_index(vocab)

    print("=" * 60)
    print("SanTOK VOCABULARY BUILDER — DEMO")
    print("content_id IS the vocab integer (Law 3)")
    print("Saturation = structural transition weight (Law 2)")
    print("=" * 60)
    print(f"\nVocab size: {len(vocab)} unique tokens")
    print(f"\n{'CID':>8} {'IDX':>5} {'TEXT':<12} {'FE':>3} {'FREQ':>5} {'TRANS':>6} {'SAT':>6}")
    print(f"{'-'*8} {'-'*5} {'-'*12} {'-'*3} {'-'*5} {'-'*6} {'-'*6}")
    for cid, v in sorted(vocab.items(), key=lambda x: x[1]["freq"], reverse=True):
        idx = mapping[cid]
        print(
            f"{cid:>8} {idx:>5} {repr(v['text']):<12} {v['fe']:>3} "
            f"{v['freq']:>5} {v['transitions']:>6} {v['saturation']:>6.2f}"
        )
    print("=" * 60)


if __name__ == "__main__":
    demo()
