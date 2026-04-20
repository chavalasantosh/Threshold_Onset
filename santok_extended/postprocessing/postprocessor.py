"""
SanTOK Extended — Post-Processing Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO borrowed logic.

Four post-processing operations on SanTOK token streams:

1. TOKEN MERGER
   Merges adjacent tokens when next_uid of token[i] == uid of token[i+1].
   Confirmed adjacency via UID chain — not text heuristics.
   Merged token gets combined content_id (XOR), averaged frontend.

2. TOKEN FILTER
   Filter by: min/max text length, allowed POS set, min frontend,
   max backend_scaled, min/max content_id.
   All thresholds are structural — no text matching.

3. TOKEN MAPPER
   Maps each token to an integer ID using content_id directly.
   content_id IS the integer vocabulary index — no separate mapping needed.
   Inverse map: integer ID → representative text.

4. TOKEN SERIALIZER / DESERIALIZER
   Serialize token list to compact string format:
     "text|fe|bs|cid|uid|prev|next"
   Deserialize back to token dict list.
   No json import needed — pure string split/join.
"""


# ── 1. Token Merger ───────────────────────────────────────────────────────────

def _uid_str(v):
    return str(v) if (v and v != 0) else "0"


def merge_adjacent(tokens):
    """
    Merge tokens that are confirmed adjacent via UID chain.
    Two tokens are mergeable if:
      next_uid of token[i] == uid of token[i+1]
      AND both are content tokens (not pure space/punct).

    Returns a new token list with merged tokens.
    Merged token:
      text       = concat of both texts
      content_id = content_id_a XOR content_id_b
      frontend   = (fe_a + fe_b) // 2
      backend_scaled = (bs_a + bs_b) // 2
      uid        = uid_a  (keep first uid)
      next_uid   = next_uid_b
    """
    if not tokens:
        return []

    result = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if i + 1 < len(tokens):
            nxt = tokens[i + 1]
            t_uid   = _uid_str(tok.get("uid", "0"))
            n_uid   = _uid_str(nxt.get("uid", "0"))
            t_next  = _uid_str(tok.get("next_uid", "0"))

            chain_ok = (t_next == n_uid) and t_next != "0"
            both_content = tok.get("text", "").strip() and nxt.get("text", "").strip()

            if chain_ok and both_content:
                merged = {
                    "text"          : tok["text"] + nxt["text"],
                    "content_id"    : int(tok.get("content_id", 0)) ^ int(nxt.get("content_id", 0)),
                    "frontend"      : (int(tok.get("frontend", 5)) + int(nxt.get("frontend", 5))) // 2,
                    "backend_scaled": (int(tok.get("backend_scaled", 0)) + int(nxt.get("backend_scaled", 0))) // 2,
                    "uid"           : t_uid,
                    "prev_uid"      : tok.get("prev_uid", 0),
                    "next_uid"      : nxt.get("next_uid", 0),
                    "stream"        : tok.get("stream", "merged"),
                    "index"         : tok.get("index", 0),
                    "_merged"       : True,
                }
                result.append(merged)
                i += 2
                continue

        result.append(dict(tok))
        i += 1
    return result


# ── 2. Token Filter ───────────────────────────────────────────────────────────

def filter_tokens(tokens, min_len=1, max_len=9999,
                  allowed_pos=None, min_frontend=1,
                  max_backend=99999, min_cid=0, max_cid=150013):
    """
    Filter token list by structural thresholds.
    All parameters optional — defaults pass everything.
    """
    result = []
    for tok in tokens:
        text = tok.get("text", "")
        n    = len(text)
        fe   = int(tok.get("frontend", 5))
        bs   = int(tok.get("backend_scaled", 50000))
        cid  = int(tok.get("content_id", 0))
        pos  = tok.get("pos")

        if n < min_len or n > max_len:     continue
        if fe < min_frontend:              continue
        if bs > max_backend:               continue
        if cid < min_cid or cid > max_cid: continue
        if allowed_pos and pos and pos not in allowed_pos: continue

        result.append(tok)
    return result


# ── 3. Token Mapper ───────────────────────────────────────────────────────────

class TokenMapper:
    """
    Maps tokens to integer IDs using content_id as the vocabulary index.
    No separate vocabulary needed — content_id IS the integer ID.
    """

    def __init__(self):
        self._id_to_text = {}   # content_id → text

    def register(self, tokens):
        """Register content_ids from a token list."""
        for tok in tokens:
            cid  = int(tok.get("content_id", 0))
            text = tok.get("text", "")
            if cid and text.strip():
                self._id_to_text[cid] = text

    def to_ids(self, tokens):
        """Map token list to list of content_id integers."""
        result = []
        for tok in tokens:
            cid = int(tok.get("content_id", 0))
            result.append(cid)
        return result

    def from_ids(self, ids):
        """Map list of content_ids back to text strings."""
        return [self._id_to_text.get(i, f"<{i}>") for i in ids]

    def tag_stream(self, tokens):
        """Add 'token_id' field (= content_id) to each token dict."""
        result = []
        for tok in tokens:
            t2 = dict(tok)
            t2["token_id"] = int(tok.get("content_id", 0))
            result.append(t2)
        return result


# ── 4. Serializer / Deserializer ─────────────────────────────────────────────

_SEP = "|"
_ROW_SEP = "\n"


def serialize(tokens):
    """
    Serialize token list to compact string.
    Format per token: text|fe|bs|cid|uid|prev_uid|next_uid
    Rows separated by newline.
    """
    rows = []
    for tok in tokens:
        parts = [
            tok.get("text", "").replace(_SEP, "\\|"),   # escape pipes in text
            str(tok.get("frontend", 5)),
            str(tok.get("backend_scaled", 0)),
            str(tok.get("content_id", 0)),
            str(tok.get("uid", 0)),
            str(tok.get("prev_uid", 0)),
            str(tok.get("next_uid", 0)),
        ]
        rows.append(_SEP.join(parts))
    return _ROW_SEP.join(rows)


def deserialize(s):
    """
    Deserialize string produced by serialize() back to token dict list.
    """
    tokens = []
    for row in s.split(_ROW_SEP):
        row = row.strip()
        if not row:
            continue
        parts = row.split(_SEP)
        if len(parts) < 7:
            continue
        text = parts[0].replace("\\|", _SEP)
        tokens.append({
            "text"          : text,
            "frontend"      : int(parts[1]),
            "backend_scaled": int(parts[2]),
            "content_id"    : int(parts[3]),
            "uid"           : parts[4],
            "prev_uid"      : parts[5],
            "next_uid"      : parts[6],
        })
    return tokens


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    sample = [
        {"text": "The",   "uid": "1001", "next_uid": "1002", "prev_uid": "0",    "frontend": 1, "backend_scaled": 26151, "content_id": 128727, "pos": "DET"},
        {"text": "quick", "uid": "1002", "next_uid": "1003", "prev_uid": "1001", "frontend": 2, "backend_scaled": 20529, "content_id": 29583,  "pos": "ADJ"},
        {"text": "fox",   "uid": "1003", "next_uid": "0",    "prev_uid": "1002", "frontend": 4, "backend_scaled": 52293, "content_id": 26790,  "pos": "NOUN"},
        {"text": "jumps", "uid": "2001", "next_uid": "0",    "prev_uid": "0",    "frontend": 1, "backend_scaled": 50736, "content_id": 4205,   "pos": "VERB"},
    ]

    print("=" * 60)
    print("SanTOK POST-PROCESSING — DEMO")
    print("=" * 60)

    print("\n--- MERGE ADJACENT (The+quick: chain 1001→1002) ---")
    merged = merge_adjacent(sample[:3])
    for t in merged:
        print(f"  {t['text']!r:<12} cid={t['content_id']} merged={t.get('_merged', False)}")

    print("\n--- FILTER (min_len=4, allowed_pos=NOUN/VERB) ---")
    filtered = filter_tokens(sample, min_len=4, allowed_pos={"NOUN", "VERB"})
    for t in filtered:
        print(f"  {t['text']!r} pos={t['pos']}")

    print("\n--- TOKEN MAPPER ---")
    mapper = TokenMapper()
    mapper.register(sample)
    ids  = mapper.to_ids(sample)
    back = mapper.from_ids(ids)
    print(f"  IDs:  {ids}")
    print(f"  Back: {back}")

    print("\n--- SERIALIZE / DESERIALIZE ---")
    s     = serialize(sample[:2])
    print(f"  Serialized:\n{s}")
    recon = deserialize(s)
    print(f"  Reconstructed: {[t['text'] for t in recon]}")

    print("=" * 60)


if __name__ == "__main__":
    demo()
