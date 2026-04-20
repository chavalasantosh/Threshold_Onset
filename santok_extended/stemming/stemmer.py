"""
SanTOK Extended — Stemmer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO suffix tables. ZERO borrowed rules.

Logic: A token's stem is the shortest prefix whose structural
       frontend signature stays the same as the full token.

       We compute frontend for the full token, then for each
       progressively shorter prefix (right-to-left trim), and
       stop trimming the moment the frontend diverges.

       Only applied to NOUN and VERB tokens (POS-gated).
       Everything else is returned unchanged.

frontend formula (mirrors SanTOK core):
  weighted_sum = sum(ord(c) * (i+1) for i, c in enumerate(text))
  digital_root = ((weighted_sum - 1) % 9) + 1  if weighted_sum > 0 else 9
  hash_val     = polynomial rolling hash mod 10
  frontend     = (digital_root * 9 + hash_val) % 9 + 1
"""


# ── structural signal helpers ─────────────────────────────────────────────────

def _weighted_sum(text):
    total = 0
    for i, c in enumerate(text):
        total += ord(c) * (i + 1)
    return total


def _digital_root(n):
    if n <= 0:
        return 9
    return ((n - 1) % 9) + 1


def _poly_hash_digit(text):
    h = 0
    for c in text:
        h = h * 31 + ord(c)
    return h % 10


def _frontend(text):
    """Recompute frontend for any text string."""
    if not text:
        return 9
    ws  = _weighted_sum(text)
    dr  = _digital_root(ws)
    hd  = _poly_hash_digit(text)
    return (dr * 9 + hd) % 9 + 1


def _backend_scaled(text):
    """Recompute backend_scaled for any text string."""
    ws  = _weighted_sum(text)
    dr  = _digital_root(ws)
    # backend_huge approximation: ws * dr * (1 + len)
    # backend_scaled = backend_huge % 100000
    bh  = ws * dr * (1 + len(text))
    return bh % 100000


# ── stem logic ────────────────────────────────────────────────────────────────

_STEMABLE_POS = {"NOUN", "VERB"}          # only these get stemmed
_MIN_STEM     = 2                          # never shorten below 2 chars


def _structural_stem(text):
    """
    Derive stem by structural signal stability.

    Trim characters from the right one at a time.
    Stop when frontend changes from the full-token value.
    That prefix is the stem.

    If trimming never changes frontend, the stem is the shortest
    2-char prefix (absolute minimum).
    """
    if len(text) <= _MIN_STEM:
        return text

    full_fe = _frontend(text)
    stem    = text

    for cut in range(1, len(text) - _MIN_STEM + 1):
        candidate = text[: len(text) - cut]
        if _frontend(candidate) != full_fe:
            # The previous (longer) candidate was the last stable one
            break
        stem = candidate

    return stem


# ── public API ────────────────────────────────────────────────────────────────

def stem_token(token):
    """
    Stem one SanTOK TokenRecord dict.

    Input:  dict with keys: text, pos (from POS tagger),
            frontend, backend_scaled  (others preserved)

    Output: same dict + added keys:
              "stem"         — stemmed form (or original if not stemable)
              "stem_signals" — signals used
    """
    result = dict(token)
    text   = token.get("text", "")
    pos    = token.get("pos")

    if not text or pos not in _STEMABLE_POS:
        result["stem"]         = text
        result["stem_signals"] = {"gate": "SKIP", "reason": pos or "no_text"}
        return result

    stem = _structural_stem(text)
    full_fe  = _frontend(text)
    stem_fe  = _frontend(stem)
    full_bs  = _backend_scaled(text)
    stem_bs  = _backend_scaled(stem)

    result["stem"]         = stem
    result["stem_signals"] = {
        "original"      : text,
        "full_fe"       : full_fe,
        "stem_fe"       : stem_fe,
        "fe_stable"     : full_fe == stem_fe,
        "chars_removed" : len(text) - len(stem),
        "full_bs"       : full_bs,
        "stem_bs"       : stem_bs,
    }
    return result


def stem_stream(tokens):
    """Stem a list of SanTOK token dicts. Returns same-length list."""
    return [stem_token(t) for t in tokens]


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    # Use the same tokens from the POS demo, already tagged
    sample = [
        {"text": "The",   "pos": "DET",  "frontend": 1, "backend_scaled": 26151},
        {"text": "quick", "pos": "ADJ",  "frontend": 2, "backend_scaled": 20529},
        {"text": "brown", "pos": "ADJ",  "frontend": 3, "backend_scaled": 86990},
        {"text": "fox",   "pos": "NOUN", "frontend": 4, "backend_scaled": 52293},
        {"text": "jumps", "pos": "VERB", "frontend": 1, "backend_scaled": 50736},
        {"text": "over",  "pos": "PREP", "frontend": 5, "backend_scaled": 6801},
        {"text": "the",   "pos": "DET",  "frontend": 2, "backend_scaled": 94973},
        {"text": "lazy",  "pos": "ADJ",  "frontend": 9, "backend_scaled": 86254},
        {"text": "dog",   "pos": "NOUN", "frontend": 5, "backend_scaled": 87919},
        {"text": "running",  "pos": "VERB", "frontend": 1, "backend_scaled": 39546},
        {"text": "runs",     "pos": "VERB", "frontend": 3, "backend_scaled": 22000},
        {"text": "dogs",     "pos": "NOUN", "frontend": 2, "backend_scaled": 51000},
        {"text": "quickly",  "pos": "ADV",  "frontend": 6, "backend_scaled": 77000},
        {"text": "tokens",   "pos": "NOUN", "frontend": 4, "backend_scaled": 33000},
        {"text": "tokenize", "pos": "VERB", "frontend": 7, "backend_scaled": 44000},
    ]

    print("=" * 65)
    print("SanTOK STEMMER — DEMO")
    print("=" * 65)
    print(f"{'TEXT':<12} {'POS':<6} {'STEM':<12} {'FE_STABLE':<10} {'TRIMMED':>7}  {'NOTE'}")
    print("-" * 60)

    for t in stem_stream(sample):
        sig  = t["stem_signals"]
        gate = sig.get("gate")
        if gate == "SKIP":
            print(f"{t['text']:<12} {t['pos'] or ''::<6} {'—':<12} {'—':<10} {'—':>7}  skipped ({sig['reason']})")
        else:
            stable = "YES" if sig["fe_stable"] else "NO"
            print(f"{t['text']:<12} {t['pos']:<6} {t['stem']:<12} {stable:<10} {sig['chars_removed']:>7}  ")

    print("=" * 65)


if __name__ == "__main__":
    demo()
