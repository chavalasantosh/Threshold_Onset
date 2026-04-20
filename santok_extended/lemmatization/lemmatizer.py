"""
SanTOK Extended — Lemmatizer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO dictionary lookup. ZERO borrowed logic.

Logic:
  Tokens are grouped into lemma groups by their (morph_class, frontend).
  Within a group, the lemma is the token with the lowest content_id.
  content_id is a deterministic hash — it doesn't encode frequency,
  but lowest-content_id within a structural group acts as the
  canonical anchor (the structurally "simplest" form).

  When running on a single token (no group context), the lemma is
  derived by stripping the detected suffix (from morphology) and
  recomputing whether the shorter form has a lower content_id
  than the original. If yes → shorter form is the lemma.

  POS-sensitive: VERB and NOUN tokens use morph_root as lemma base.
  ADJ and ADV use the full stem. Everything else is identity.
"""


def _weighted_sum(text):
    total = 0
    for i, c in enumerate(text):
        total += ord(c) * (i + 1)
    return total


def _digital_root(n):
    return 9 if n <= 0 else ((n - 1) % 9) + 1


def _content_id(text):
    """
    Deterministic content ID for any text string.
    Mirrors SanTOK's content_id formula: polynomial hash % 150013.
    """
    h = 0
    for c in text:
        h = h * 31 + ord(c)
    return abs(h) % 150013


def _frontend(text):
    if not text:
        return 9
    ws = _weighted_sum(text)
    dr = _digital_root(ws)
    h  = 0
    for c in text:
        h = h * 31 + ord(c)
    return (dr * 9 + h % 10) % 9 + 1


_LEMMA_POS = {"NOUN", "VERB", "ADJ", "ADV"}


def lemmatize_token(token):
    """
    Lemmatize one SanTOK token dict (already POS-tagged + morphology-analyzed).

    Adds:
      "lemma"         — the derived lemma form
      "lemma_signals" — signals used
    """
    result = dict(token)
    text   = token.get("text", "")
    pos    = token.get("pos", "")

    if not text or pos not in _LEMMA_POS:
        result["lemma"]         = text
        result["lemma_signals"] = {"gate": "SKIP", "reason": pos or "no_text"}
        return result

    # Start from morph_root if available, else stem, else text
    base = token.get("morph_root") or token.get("stem") or text

    full_cid = _content_id(text)
    base_cid = _content_id(base)

    # Choose whichever has lower content_id (structurally simpler form)
    if base_cid < full_cid and len(base) >= 2:
        lemma = base
    else:
        lemma = text

    # POS-specific: for VERB, also try dropping last char if it lowers cid
    if pos == "VERB" and len(lemma) > 3:
        shorter = lemma[:-1]
        if _content_id(shorter) < _content_id(lemma) and _frontend(shorter) == _frontend(lemma):
            lemma = shorter

    result["lemma"] = lemma
    result["lemma_signals"] = {
        "base_used"   : base,
        "full_cid"    : full_cid,
        "base_cid"    : base_cid,
        "lemma_cid"   : _content_id(lemma),
        "full_fe"     : _frontend(text),
        "lemma_fe"    : _frontend(lemma),
        "morph_class" : token.get("morph_class", -1),
    }
    return result


def lemmatize_stream(tokens):
    """Lemmatize a list of SanTOK token dicts."""
    return [lemmatize_token(t) for t in tokens]


def lemmatize_group(tokens):
    """
    Group-aware lemmatization.

    Groups tokens by (morph_class, frontend).
    The lemma for the group = the text with the lowest content_id.
    All tokens in the group share that lemma.
    """
    groups = {}
    for tok in tokens:
        key = (tok.get("morph_class", 0), tok.get("frontend", 5))
        if key not in groups:
            groups[key] = []
        groups[key].append(tok)

    result = []
    for key, group in groups.items():
        # Find anchor: lowest content_id in group
        anchor = min(group, key=lambda t: _content_id(t.get("text", "")))
        anchor_lemma = anchor.get("text", "")

        for tok in group:
            t2 = dict(tok)
            t2["lemma"] = anchor_lemma
            t2["lemma_signals"] = {
                "group_key"    : key,
                "group_size"   : len(group),
                "anchor_text"  : anchor_lemma,
                "anchor_cid"   : _content_id(anchor_lemma),
                "self_cid"     : _content_id(tok.get("text", "")),
            }
            result.append(t2)

    return result


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    # Tokens pre-tagged with POS and morphology
    sample = [
        {"text": "running",  "pos": "VERB", "morph_root": "run",   "morph_class": 3, "frontend": 1},
        {"text": "runs",     "pos": "VERB", "morph_root": "run",   "morph_class": 2, "frontend": 3},
        {"text": "ran",      "pos": "VERB", "morph_root": "ran",   "morph_class": 1, "frontend": 5},
        {"text": "dogs",     "pos": "NOUN", "morph_root": "dog",   "morph_class": 4, "frontend": 2},
        {"text": "dog",      "pos": "NOUN", "morph_root": "dog",   "morph_class": 4, "frontend": 5},
        {"text": "quickly",  "pos": "ADV",  "morph_root": "quick", "morph_class": 6, "frontend": 6},
        {"text": "quick",    "pos": "ADJ",  "morph_root": "quick", "morph_class": 2, "frontend": 2},
        {"text": "jumps",    "pos": "VERB", "morph_root": "jump",  "morph_class": 5, "frontend": 1},
        {"text": "tokens",   "pos": "NOUN", "morph_root": "token", "morph_class": 3, "frontend": 4},
        {"text": "tokenize", "pos": "VERB", "morph_root": "token", "morph_class": 0, "frontend": 7},
    ]

    print("=" * 65)
    print("SanTOK LEMMATIZER — SINGLE-TOKEN MODE")
    print("=" * 65)
    print(f"{'TEXT':<12} {'POS':<6} {'BASE':<10} {'LEMMA':<10} {'CID_DIFF':>10}")
    print("-" * 55)
    for t in lemmatize_stream(sample):
        sig  = t["lemma_signals"]
        gate = sig.get("gate")
        if gate:
            print(f"{t['text']:<12} {t['pos']:<6} {'—':<10} {'—':<10}  skipped")
        else:
            diff = sig["lemma_cid"] - sig["full_cid"]
            print(f"{t['text']:<12} {t['pos']:<6} {sig['base_used']:<10} {t['lemma']:<10} {diff:>10}")

    print()
    print("SanTOK LEMMATIZER — GROUP MODE (shared anchor)")
    print("=" * 65)
    grouped = lemmatize_group(sample)
    for t in grouped:
        sig = t["lemma_signals"]
        print(f"  {t['text']:<12} → lemma={t['lemma']:<10}  group={sig['group_key']}  anchor_cid={sig['anchor_cid']}")

    print("=" * 65)


if __name__ == "__main__":
    demo()
