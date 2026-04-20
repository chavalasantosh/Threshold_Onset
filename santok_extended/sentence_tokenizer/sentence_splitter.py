"""
SanTOK Extended — Sentence Tokenizer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO period/punctuation rules. ZERO regex.

Logic: A sentence boundary exists between token[i] and token[i+1]
       when a structural discontinuity signal fires:

  Signal 1 — FRONTEND DROP:
    abs(fe[i] - fe[i+1]) >= 4
    A large jump in the structural signature = new clause.

  Signal 2 — BACKEND SPIKE:
    abs(bs[i] - bs[i+1]) > 60000
    A large jump in the numerical fingerprint = structural break.

  Signal 3 — UID CHAIN GAP:
    next_uid of token[i] != uid of token[i+1]
    A broken link in the uid chain = explicit boundary.

  Signal 4 — CONTENT_ID RESET:
    abs(cid[i] - cid[i+1]) > 100000
    A large jump in content_id = semantically distant tokens.

A boundary fires if ANY two signals agree simultaneously,
or Signal 3 fires alone (explicit link break).
"""


def _safe_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _uid_str(v):
    return str(v) if (v and v != 0) else "0"


def _boundary_signals(t1, t2):
    """
    Compute boundary signals between adjacent tokens.
    Returns dict of signal: bool.
    """
    fe1  = _safe_int(t1.get("frontend", 5))
    fe2  = _safe_int(t2.get("frontend", 5))
    bs1  = _safe_int(t1.get("backend_scaled", 50000))
    bs2  = _safe_int(t2.get("backend_scaled", 50000))
    cid1 = _safe_int(t1.get("content_id", 0))
    cid2 = _safe_int(t2.get("content_id", 0))

    # UID chain continuity
    t1_next = _uid_str(t1.get("next_uid", 0))
    t2_uid  = _uid_str(t2.get("uid", 0))
    chain_broken = (t1_next != t2_uid) and (t1_next != "0") and (t2_uid != "0")

    return {
        "fe_drop"    : abs(fe1 - fe2) >= 4,
        "bs_spike"   : abs(bs1 - bs2) > 60000,
        "chain_break": chain_broken,
        "cid_reset"  : abs(cid1 - cid2) > 100000,
    }


def _is_boundary(signals):
    """True if boundary should be placed between these two tokens."""
    # chain break alone is sufficient
    if signals["chain_break"]:
        return True
    # any two signals together
    active = [v for v in signals.values() if v]
    return len(active) >= 2


def tokenize_sentences(tokens):
    """
    Split a flat list of SanTOK tokens into sentences.

    Returns: list of sentences, where each sentence is a list of token dicts.
    Each token dict gets added keys:
      "sentence_id" — 0-based sentence index
      "boundary_signals" — signals that fired at the boundary after this token
    """
    if not tokens:
        return []

    sentences   = []
    current     = []
    sentence_id = 0

    for i, tok in enumerate(tokens):
        t2 = dict(tok)
        t2["sentence_id"] = sentence_id

        if i < len(tokens) - 1:
            signals  = _boundary_signals(tokens[i], tokens[i + 1])
            boundary = _is_boundary(signals)
            t2["boundary_signals"] = signals
        else:
            boundary = False
            t2["boundary_signals"] = {}

        current.append(t2)

        if boundary:
            sentences.append(current)
            current     = []
            sentence_id += 1

    if current:
        sentences.append(current)

    return sentences


def sentence_texts(sentences):
    """Extract plain text string for each sentence."""
    return ["".join(t.get("text", "") for t in sent) for sent in sentences]


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    # Simulate two sentences with a structural break in between
    sample = [
        # Sentence 1: "Action before knowledge."
        {"text": "Action",    "frontend": 6, "backend_scaled": 34000, "content_id": 71000, "uid": "1001", "next_uid": "1002", "prev_uid": "0"},
        {"text": " ",         "frontend": 3, "backend_scaled": 91000, "content_id": 127598,"uid": "1002", "next_uid": "1003", "prev_uid": "1001"},
        {"text": "before",    "frontend": 4, "backend_scaled": 8000,  "content_id": 16000, "uid": "1003", "next_uid": "1004", "prev_uid": "1002"},
        {"text": " ",         "frontend": 3, "backend_scaled": 61000, "content_id": 127598,"uid": "1004", "next_uid": "1005", "prev_uid": "1003"},
        {"text": "knowledge", "frontend": 3, "backend_scaled": 62000, "content_id": 55000, "uid": "1005", "next_uid": "1006", "prev_uid": "1004"},
        {"text": ".",         "frontend": 7, "backend_scaled": 5000,  "content_id": 2000,  "uid": "1006", "next_uid": "0",    "prev_uid": "1005"},
        # Sentence 2: "Tokens become residues."
        {"text": "Tokens",    "frontend": 1, "backend_scaled": 26000, "content_id": 128000,"uid": "2001", "next_uid": "2002", "prev_uid": "0"},
        {"text": " ",         "frontend": 3, "backend_scaled": 91000, "content_id": 127598,"uid": "2002", "next_uid": "2003", "prev_uid": "2001"},
        {"text": "become",    "frontend": 4, "backend_scaled": 52000, "content_id": 38000, "uid": "2003", "next_uid": "2004", "prev_uid": "2002"},
        {"text": " ",         "frontend": 3, "backend_scaled": 40000, "content_id": 127598,"uid": "2004", "next_uid": "2005", "prev_uid": "2003"},
        {"text": "residues",  "frontend": 5, "backend_scaled": 87000, "content_id": 134000,"uid": "2005", "next_uid": "0",    "prev_uid": "2004"},
        {"text": ".",         "frontend": 9, "backend_scaled": 3000,  "content_id": 1500,  "uid": "2006", "next_uid": "0",    "prev_uid": "2005"},
    ]

    sents  = tokenize_sentences(sample)
    texts  = sentence_texts(sents)

    print("=" * 60)
    print("SanTOK SENTENCE TOKENIZER — DEMO")
    print("=" * 60)
    print(f"Total tokens: {len(sample)} → {len(sents)} sentence(s)")
    print()
    for i, (sent, text) in enumerate(zip(sents, texts)):
        print(f"  Sentence {i}: {repr(text.strip())}  ({len(sent)} tokens)")

    print("=" * 60)


if __name__ == "__main__":
    demo()
