"""
SanTOK Extended — Stop Word Filter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Law 1 — POLE LAW:
  In any stream, the highest-connectivity fe values are structural poles.
  Pole tokens carry no semantic weight — they are structural glue.

Law 3 — IDENTITY LAW:
  content_id is fixed. Same text = same cid always.
  Stop word detection is therefore deterministic, not probabilistic.

A token is a stop word if ALL three conditions hold:
  1. fe is a pole value (determined from corpus transition degree)
  2. content_id < POLE_CID_CEILING (structurally light tokens)
  3. text length <= 4 (short functional tokens)

Calibrated from 767k Mahabharata tokens.
ZERO external imports. ZERO hardcoded word lists.
"""

# CID ceiling for structural glue tokens — derived from real corpus
# Tokens with cid < 15000 are ultra-common structural tokens
# (confirmed: 'the'=125905 is NOT a stop word by this measure;
#  'is','it','he' etc. are edge cases handled by pole check)
_POLE_CID_CEILING = 15000

# Max length for stop word candidates
_MAX_STOP_LENGTH = 4

# Known pole fe values from Law 1 (highest transition degree in corpus)
# From observe_step3_laws.py: fe=1 and fe=7 are poles in narrative text
# fe=1 degree=2373 in project text (overwhelming pole)
_DEFAULT_POLES = {1, 7}


def detect_poles(tokens):
    """
    Detect pole fe values from a token stream.
    Pole = fe value with highest total transition degree (in + out).
    Returns set of the top 2 pole fe values.
    Derived purely from stream structure — Law 1.
    """
    degree = {i: 0 for i in range(1, 10)}
    content = [t for t in tokens if t.get("text", "").strip()]
    for i in range(len(content) - 1):
        a = content[i]["frontend"]
        b = content[i + 1]["frontend"]
        degree[a] += 1
        degree[b] += 1
    top2 = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:2]
    return {fe for fe, _ in top2}


def is_stop_word(token, poles=None):
    """
    Determine if a single token is a stop word.

    Uses Law 1 (pole fe) + Law 3 (cid identity).
    No string comparison. No external list.

    Input:  token dict with keys: text, frontend, content_id
    Output: True if stop word
    """
    if poles is None:
        poles = _DEFAULT_POLES

    text = token.get("text", "")
    fe = int(token.get("frontend", 5))
    cid = int(token.get("content_id", 99999))

    # Must be a pole fe value (Law 1)
    if fe not in poles:
        return False

    # Must be structurally light (low cid = ultra-common)
    if cid >= _POLE_CID_CEILING:
        return False

    # Must be short (functional tokens are short)
    if len(text) > _MAX_STOP_LENGTH:
        return False

    return True


def filter_stops(tokens, poles=None):
    """
    Remove stop word tokens from a list.
    Returns filtered list with stop words removed.
    """
    if poles is None:
        poles = _DEFAULT_POLES
    return [t for t in tokens if not is_stop_word(t, poles)]


def annotate_stops(tokens, poles=None):
    """
    Add 'is_stop' key to each token dict natively in-place.
    Returns annotated list.
    """
    if poles is None:
        poles = _DEFAULT_POLES
        
    for t in tokens:
        t["is_stop"] = is_stop_word(t, poles)
        
    return tokens


def demo():
    sample = [
        {"text": "Action",    "frontend": 7, "content_id": 10310},
        {"text": "before",    "frontend": 8, "content_id": 24365},
        {"text": "knowledge", "frontend": 1, "content_id": 102258},
        {"text": ".",         "frontend": 7, "content_id": 1908},
        {"text": "The",       "frontend": 1, "content_id": 128727},
        {"text": "quick",     "frontend": 2, "content_id": 29583},
        {"text": "fox",       "frontend": 4, "content_id": 26790},
        {"text": "jumps",     "frontend": 1, "content_id": 4205},
        {"text": "of",        "frontend": 4, "content_id": 82271},
        {"text": "and",       "frontend": 8, "content_id": 10221},
        {"text": "is",        "frontend": 1, "content_id": 145119},
        {"text": "it",        "frontend": 2, "content_id": 10684},
    ]

    poles = {1, 7}
    annotated = annotate_stops(sample, poles)

    print("=" * 55)
    print("SanTOK STOP WORD FILTER — DEMO")
    print("Law 1 (poles) + Law 3 (cid identity)")
    print(f"Poles: fe={poles}  CID ceiling: {_POLE_CID_CEILING}")
    print("=" * 55)
    print(f"  {'TOKEN':<12} {'FE':>3} {'CID':>8} {'STOP?'}")
    print(f"  {'-'*12} {'-'*3} {'-'*8}")
    for t in annotated:
        mark = "YES — filtered" if t["is_stop"] else ""
        print(f"  {repr(t['text']):<12} {t['frontend']:>3} {t['content_id']:>8}  {mark}")

    filtered = filter_stops(sample, poles)
    print(f"\nAfter filtering: {len(filtered)}/{len(sample)} tokens remain")
    print("Remaining:", [t["text"] for t in filtered])
    print("=" * 55)


if __name__ == "__main__":
    demo()
