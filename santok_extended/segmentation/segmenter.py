"""
SanTOK Extended — Text Segmentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO borrowed algorithms.

Three segmentation modes:

1. PARAGRAPH SEGMENTATION
   A paragraph boundary fires when the index gap between consecutive
   tokens exceeds mean_gap * 2. This detects newlines and blank lines
   without character inspection.
   Also fires when backend_scaled drops by > 70000 between tokens
   (structural topic shift signal).

2. SLIDING WINDOW CHUNKING
   Fixed-size UID windows. Overlap configurable.
   Window identity = XOR of all content_ids in the window.

3. TOPIC BOUNDARY SEGMENTATION
   Detects topic shifts using frontend variance within a sliding buffer.
   High variance in frontend over a window = topic shift.
   Threshold = 3.0 (frontend range is 1-9, variance > 3 = diverse).
"""


def _variance(values):
    if not values:
        return 0.0
    n   = len(values)
    avg = sum(values) / n
    return sum((x - avg) ** 2 for x in values) / n


# ── 1. Paragraph segmentation ─────────────────────────────────────────────────

def paragraph_segments(tokens):
    """
    Split token list into paragraphs.

    A new paragraph starts when:
      - index gap between tokens > mean_gap * 2, OR
      - backend_scaled drops by more than 70000 between tokens.

    Returns list of paragraph token-lists.
    """
    content = [t for t in tokens if t.get("text", "").strip()]
    if not content:
        return [[]]

    # Compute index gaps
    gaps = []
    for i in range(len(content) - 1):
        idx_a = int(content[i].get("index", i))
        idx_b = int(content[i + 1].get("index", i + 1))
        gaps.append(abs(idx_b - idx_a))

    mean_gap   = (sum(gaps) / len(gaps)) if gaps else 1
    threshold  = mean_gap * 2

    segments, current = [], []
    for i, tok in enumerate(content):
        current.append(tok)
        if i < len(content) - 1:
            gap   = gaps[i]
            bs_i  = int(tok.get("backend_scaled", 50000))
            bs_j  = int(content[i + 1].get("backend_scaled", 50000))
            bs_drop = abs(bs_i - bs_j) > 70000

            if gap > threshold or bs_drop:
                segments.append(current)
                current = []

    if current:
        segments.append(current)
    return segments


# ── 2. Sliding window chunker ─────────────────────────────────────────────────

def sliding_windows(tokens, window_size=5, step=1):
    """
    Generate overlapping fixed-size windows over content tokens.

    Each window:
      tokens    — list of token dicts in window
      texts     — list of text strings
      window_id — XOR of content_ids (structural identity)
      start     — start position in content list
    """
    content = [t for t in tokens if t.get("text", "").strip()]
    if window_size < 1:
        return []
    results = []
    for i in range(0, len(content) - window_size + 1, step):
        window = content[i : i + window_size]
        wid    = 0
        for t in window:
            wid ^= int(t.get("content_id", 0))
        results.append({
            "tokens"   : window,
            "texts"    : [t["text"] for t in window],
            "window_id": wid,
            "start"    : i,
            "size"     : window_size,
        })
    return results


# ── 3. Topic boundary segmentation ────────────────────────────────────────────

def topic_segments(tokens, buffer_size=5, variance_threshold=3.0):
    """
    Detect topic boundaries using frontend variance over a rolling buffer.

    High frontend variance in a window signals structural diversity = topic shift.
    Returns list of segment token-lists.
    """
    content = [t for t in tokens if t.get("text", "").strip()]
    if len(content) <= buffer_size:
        return [content]

    segments, current = [], []
    fe_buffer = []

    for i, tok in enumerate(content):
        current.append(tok)
        fe_buffer.append(int(tok.get("frontend", 5)))
        if len(fe_buffer) > buffer_size:
            fe_buffer.pop(0)

        if len(fe_buffer) == buffer_size:
            v = _variance(fe_buffer)
            if v > variance_threshold and len(current) > buffer_size:
                segments.append(current[:-1])
                current = [tok]
                fe_buffer = [int(tok.get("frontend", 5))]

    if current:
        segments.append(current)
    return segments


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    # Simulate two paragraphs with large index gap between them
    stream = [
        {"text": "Action",    "index": 0,  "backend_scaled": 34000, "content_id": 71000,  "frontend": 6},
        {"text": "before",    "index": 1,  "backend_scaled": 8000,  "content_id": 16000,  "frontend": 4},
        {"text": "knowledge", "index": 2,  "backend_scaled": 62000, "content_id": 55000,  "frontend": 3},
        # paragraph break (index jump from 2 to 20)
        {"text": "Tokens",    "index": 20, "backend_scaled": 26000, "content_id": 128000, "frontend": 1},
        {"text": "become",    "index": 21, "backend_scaled": 52000, "content_id": 38000,  "frontend": 4},
        {"text": "residues",  "index": 22, "backend_scaled": 87000, "content_id": 134000, "frontend": 5},
    ]

    print("=" * 60)
    print("SanTOK SEGMENTATION — DEMO")
    print("=" * 60)

    print("\n--- PARAGRAPH SEGMENTATION ---")
    for i, seg in enumerate(paragraph_segments(stream)):
        texts = " ".join(t["text"] for t in seg)
        print(f"  Para {i}: {repr(texts)}")

    print("\n--- SLIDING WINDOWS (size=3, step=1) ---")
    for w in sliding_windows(stream, 3, 1):
        print(f"  [{w['start']}] {w['texts']}  window_id={w['window_id']}")

    print("\n--- TOPIC SEGMENTS ---")
    for i, seg in enumerate(topic_segments(stream, buffer_size=3, variance_threshold=2.0)):
        texts = " ".join(t["text"] for t in seg)
        print(f"  Topic {i}: {repr(texts)}")

    print("=" * 60)


if __name__ == "__main__":
    demo()
