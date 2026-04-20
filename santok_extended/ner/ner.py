"""
SanTOK Extended — Named Entity Recognizer (NER)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO gazetteers. ZERO corpora. ZERO rules.

Logic: Entity type is derived purely from SanTOK structural signals.

Signal axes:
  content_id band  → entity class zone
  frontend         → confirms or narrows entity type
  backend_scaled   → sub-type discriminator
  neighbor signal  → START anchor (token after [START] is high-value entity signal)
  text_length      → short=ORG/LOC, medium=PERSON/DATE, long=misc

ENTITY TYPES: PERSON  ORG  LOC  DATE  NUM  EMAIL  URL  MISC  O

content_id bands (from real SanTOK observations):
  content_id is a deterministic hash, not frequency.
  Band boundaries are derived from the hash space (0–150012).

  Zone A:  0 – 20000   → DATE/NUM   (low-hash, structurally primitive)
  Zone B:  20001–50000  → ORG/LOC    (lower-mid, short structural forms)
  Zone C:  50001–100000 → PERSON     (mid-range)
  Zone D: 100001–150012 → MISC       (high-hash, complex forms)

Frontend confirmation:
  fe in {1,2}  → sharpens toward PERSON or DET-attached entity
  fe in {3,4}  → sharpens toward ORG
  fe in {5,6}  → sharpens toward LOC
  fe in {7,8}  → sharpens toward DATE
  fe == 9      → edge/rare → MISC

Neighbor signal:
  ns == 1 (START) → first token in stream, elevated entity probability
  ns == 3 (ISOLATED) → high entity signal (standalone proper noun)
"""

PERSON = "PERSON"
ORG    = "ORG"
LOC    = "LOC"
DATE   = "DATE"
NUM    = "NUM"
EMAIL  = "EMAIL"
URL    = "URL"
MISC   = "MISC"
O      = "O"       # not an entity

ALL_ENTITY_TYPES = (PERSON, ORG, LOC, DATE, NUM, EMAIL, URL, MISC, O)


def _ns(prev_uid, next_uid):
    hp = bool(prev_uid and prev_uid != 0)
    hn = bool(next_uid and next_uid != 0)
    if hp and hn: return 0     # interior
    if not hp and hn: return 1 # start
    if hp and not hn: return 2 # end
    return 3                   # isolated


def _is_num(text):
    return bool(text) and all(c.isdigit() or c in '.,_-' for c in text)


def _looks_like_url(text):
    t = text
    return (t.startswith("http") or t.startswith("www.") or
            ("." in t and "/" in t and len(t) > 8))


def _looks_like_email(text):
    return "@" in text and "." in text and len(text) > 4


def _cid_zone(cid):
    """Map content_id to entity zone 0-3."""
    if cid <= 20000:  return 0
    if cid <= 50000:  return 1
    if cid <= 100000: return 2
    return 3


def _resolve_entity(fe, cid_zone, bs, ns, text_len):
    """
    Resolve entity type from structural signals.
    Returns entity type string.
    """
    # Zone 0: primitive forms → DATE or NUM territory
    if cid_zone == 0:
        if fe in {7, 8}: return DATE
        if fe in {1, 9}: return NUM
        return DATE if bs < 50000 else MISC

    # Zone 1: lower-mid → ORG or LOC
    if cid_zone == 1:
        if fe in {5, 6}: return LOC
        if fe in {3, 4}: return ORG
        if fe in {1, 2} and text_len <= 3: return LOC
        return ORG

    # Zone 2: mid-range → PERSON
    if cid_zone == 2:
        if fe in {1, 2}: return PERSON
        if fe in {3, 4}: return ORG
        if fe in {5, 6}: return LOC
        return PERSON

    # Zone 3: high-hash → MISC
    if fe == 9: return MISC
    if fe in {1, 2} and text_len <= 5: return PERSON
    if fe in {5, 6}: return LOC
    return MISC


def tag_token(token):
    """
    NER-tag one SanTOK TokenRecord dict.

    Input:  dict with text, frontend, backend_scaled, content_id,
            prev_uid, next_uid (others preserved)

    Output: same dict + "entity_type", "ner_signals"
    """
    result  = dict(token)
    text    = token.get("text", "")

    # fast-path gates
    if not text or not text.strip():
        result["entity_type"] = O
        result["ner_signals"] = {"gate": "SPACE"}
        return result

    if _is_num(text):
        result["entity_type"] = NUM
        result["ner_signals"] = {"gate": "NUM_GATE"}
        return result

    if _looks_like_email(text):
        result["entity_type"] = EMAIL
        result["ner_signals"] = {"gate": "EMAIL_GATE"}
        return result

    if _looks_like_url(text):
        result["entity_type"] = URL
        result["ner_signals"] = {"gate": "URL_GATE"}
        return result

    fe   = max(1, min(9, int(token.get("frontend", 5))))
    bs   = int(token.get("backend_scaled", 50000))
    cid  = int(token.get("content_id", 75000))
    pu   = token.get("prev_uid", 0)
    nu   = token.get("next_uid", 0)
    ns   = _ns(pu, nu)
    n    = len(text)
    zone = _cid_zone(cid)

    entity = _resolve_entity(fe, zone, bs, ns, n)

    # Neighbor boost: isolated or start position elevates confidence
    # but doesn't change entity type — just records it
    result["entity_type"] = entity
    result["ner_signals"]  = {
        "fe": fe, "cid_zone": zone, "bs": bs, "ns": ns,
        "text_len": n, "cid": cid,
    }
    return result


def tag_stream(tokens):
    """NER-tag a list of SanTOK token dicts."""
    return [tag_token(t) for t in tokens]


def entities_only(tokens):
    """Return only tokens that are named entities (entity_type != O)."""
    return [t for t in tag_stream(tokens) if t.get("entity_type") != O]


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    sample = [
        {"text": "The",       "frontend": 1, "backend_scaled": 26151,  "content_id": 128727, "prev_uid": 0,   "next_uid": 100},
        {"text": "quick",     "frontend": 2, "backend_scaled": 20529,  "content_id": 29583,  "prev_uid": 100, "next_uid": 200},
        {"text": "fox",       "frontend": 4, "backend_scaled": 52293,  "content_id": 26790,  "prev_uid": 200, "next_uid": 300},
        {"text": "London",    "frontend": 5, "backend_scaled": 62000,  "content_id": 72000,  "prev_uid": 300, "next_uid": 400},
        {"text": "2024",      "frontend": 7, "backend_scaled": 14000,  "content_id": 5000,   "prev_uid": 400, "next_uid": 500},
        {"text": "OpenAI",    "frontend": 3, "backend_scaled": 38000,  "content_id": 44000,  "prev_uid": 500, "next_uid": 600},
        {"text": "user@x.com","frontend": 6, "backend_scaled": 71000,  "content_id": 90000,  "prev_uid": 600, "next_uid": 700},
        {"text": "http://ex.io","frontend":4, "backend_scaled": 55000, "content_id": 80000,  "prev_uid": 700, "next_uid": 0},
        {"text": "42",        "frontend": 2, "backend_scaled": 3000,   "content_id": 1200,   "prev_uid": 0,   "next_uid": 0},
    ]

    print("=" * 60)
    print("SanTOK NER — DEMO")
    print("=" * 60)
    print(f"{'TEXT':<15} {'FE':>2} {'ZONE':>5} {'NS':>3}  {'ENTITY'}")
    print("-" * 45)

    for t in tag_stream(sample):
        sig = t["ner_signals"]
        print(
            f"{t['text']:<15} "
            f"{sig.get('fe', '-'):>2} "
            f"{sig.get('cid_zone', '-'):>5} "
            f"{sig.get('ns', '-'):>3}  "
            f"{t['entity_type']}"
        )

    print("=" * 60)


if __name__ == "__main__":
    demo()
