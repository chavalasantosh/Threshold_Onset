"""
SanTOK Extended — Topographical Basin Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO fixed window sizes. ZERO n-gram concept.

CONCEPT: TOPOGRAPHICAL BASINS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The token stream forms a topography based on backend_scaled values.

backend_scaled is the contextual pressure fingerprint of each token.
Plotted across the stream:  some tokens are PEAKS (local maxima),
some are VALLEYS (local minima), most are SLOPES in between.

A BASIN is the sequence of tokens between two consecutive peaks.
Basin boundaries are naturally determined by the data — not a fixed N.

WHY THIS IS BETTER THAN FIXED WINDOWS:
  Fixed windows (n-grams) cut text at arbitrary positions.
  Topographical Basins cut at natural structural boundaries.
  A 3-word sentence and a 15-word sentence form different-sized basins
  because they have different structural topographies.

BASIN PROPERTIES:
  basin_id     — XOR cascade of content_ids, folded through digital_root
  depth        — sum of backend_scaled values in basin (structural pressure)
  altitude     — digital_root_9(depth) → 1-9, the basin's structural class
  peak_mass    — the max backend_scaled at the basin's boundary peak
  valley_floor — min backend_scaled inside the basin

PEAK DETECTION:
  A token at index i is a PEAK if:
    backend_scaled[i] > backend_scaled[i-1]  AND
    backend_scaled[i] > backend_scaled[i+1]

  Edge tokens (first/last) and isolated tokens use one-sided comparison.

FRONTIER PEAK (basin start/end sentinel):
  We treat index 0 and index n-1 as implicit boundary peaks.
  This ensures every stream has at least one basin.
"""


def _dr9(n):
    if n <= 0:
        return 9
    return ((n - 1) % 9) + 1


def _basin_id(tokens):
    """XOR cascade of content_ids, folded through digital_root at each step."""
    val = 0
    for t in tokens:
        cid = int(t.get("content_id", 0))
        val = _dr9(val ^ cid)
    return val


def _find_peaks(bs_values):
    """
    Find indices of local maxima in backend_scaled sequence.
    Returns sorted list of peak indices.
    Always includes index 0 and index n-1 as boundary sentinels.
    """
    n = len(bs_values)
    if n == 0:
        return []
    if n == 1:
        return [0]

    peaks = [0]   # left sentinel always a boundary

    for i in range(1, n - 1):
        if bs_values[i] >= bs_values[i - 1] and bs_values[i] >= bs_values[i + 1]:
            # Only add if it's genuinely higher than both neighbors
            if bs_values[i] > bs_values[i - 1] or bs_values[i] > bs_values[i + 1]:
                peaks.append(i)

    if (n - 1) not in peaks:
        peaks.append(n - 1)   # right sentinel

    return sorted(peaks)


def extract_basins(tokens):
    """
    Extract topographical basins from a token stream.

    Each basin is a dict:
      tokens       — list of token dicts in this basin
      texts        — list of text strings
      basin_id     — structural identity (XOR cascade of content_ids)
      depth        — sum of backend_scaled values
      altitude     — digital_root_9(depth) → 1-9
      peak_mass    — backend_scaled of the bounding peak
      valley_floor — min backend_scaled inside basin
      start        — start index in content token list
      end          — end index in content token list
    """
    content = [t for t in tokens if t.get("text", "").strip()]
    if not content:
        return []

    bs_values = [int(t.get("backend_scaled", 0)) for t in content]
    peaks     = _find_peaks(bs_values)

    basins = []
    for p in range(len(peaks) - 1):
        start_idx = peaks[p]
        end_idx   = peaks[p + 1]

        # Basin = tokens from start_idx to end_idx (inclusive of end peak)
        basin_tokens = content[start_idx : end_idx + 1]

        if not basin_tokens:
            continue

        depth        = sum(int(t.get("backend_scaled", 0)) for t in basin_tokens)
        altitude     = _dr9(depth)
        peak_mass    = bs_values[peaks[p]]   # left peak's mass
        valley_floor = min(bs_values[i] for i in range(start_idx, end_idx + 1))

        basins.append({
            "tokens"      : basin_tokens,
            "texts"       : [t["text"] for t in basin_tokens],
            "basin_id"    : _basin_id(basin_tokens),
            "depth"       : depth,
            "altitude"    : altitude,
            "peak_mass"   : peak_mass,
            "valley_floor": valley_floor,
            "start"       : start_idx,
            "end"         : end_idx,
            "size"        : len(basin_tokens),
        })

    return basins


def basin_stream(tokens):
    """
    Tag each content token with its basin membership.
    Returns list of (token_dict, basin_index) tuples.
    """
    content   = [t for t in tokens if t.get("text", "").strip()]
    basins    = extract_basins(tokens)
    token_basin = {}   # content_index → basin_index

    for bi, basin in enumerate(basins):
        for tok in basin["tokens"]:
            # Match by text + uid for uniqueness
            key = (tok.get("text"), tok.get("uid", -1), tok.get("index", -1))
            token_basin[key] = bi

    result = []
    for tok in content:
        key = (tok.get("text"), tok.get("uid", -1), tok.get("index", -1))
        bi  = token_basin.get(key, -1)
        t2  = dict(tok)
        t2["basin_index"] = bi
        t2["basin_id"]    = basins[bi]["basin_id"] if bi >= 0 else 0
        result.append(t2)

    return result


def ridge_walk(tokens):
    """
    Walk the peaks of the topography only.
    Returns the sequence of peak tokens — the "ridge line" of the stream.
    """
    content   = [t for t in tokens if t.get("text", "").strip()]
    bs_values = [int(t.get("backend_scaled", 0)) for t in content]
    peaks     = _find_peaks(bs_values)
    return [content[i] for i in peaks]


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    sample = [
        {"text": "The",   "frontend": 1, "backend_scaled": 26151, "content_id": 128727},
        {"text": "quick", "frontend": 2, "backend_scaled": 20529, "content_id": 29583},
        {"text": "brown", "frontend": 3, "backend_scaled": 86990, "content_id": 56274},  # PEAK
        {"text": "fox",   "frontend": 4, "backend_scaled": 52293, "content_id": 26790},
        {"text": "jumps", "frontend": 1, "backend_scaled": 50736, "content_id": 4205},
        {"text": "over",  "frontend": 5, "backend_scaled": 6801,  "content_id": 16460},
        {"text": "the",   "frontend": 2, "backend_scaled": 94973, "content_id": 125905},  # PEAK
        {"text": "lazy",  "frontend": 9, "backend_scaled": 86254, "content_id": 39107},
        {"text": "dog",   "frontend": 5, "backend_scaled": 87919, "content_id": 134410},
    ]

    basins = extract_basins(sample)
    ridge  = ridge_walk(sample)

    print("=" * 72)
    print("SanTOK TOPOGRAPHICAL BASIN ENGINE — DEMO")
    print("Natural structural chunking at backend_scaled peaks. Zero fixed N.")
    print("=" * 72)

    bs_vals = [t["backend_scaled"] for t in sample]
    print(f"\nBackend_scaled topography: {bs_vals}")
    print()

    for i, basin in enumerate(basins):
        print(f"  BASIN {i}  [{basin['start']}–{basin['end']}]  "
              f"size={basin['size']}  depth={basin['depth']}  "
              f"altitude={basin['altitude']}  id={basin['basin_id']}")
        print(f"    tokens: {basin['texts']}")
        print(f"    peak_mass={basin['peak_mass']}  valley_floor={basin['valley_floor']}")

    print()
    ridge_texts = [t["text"] for t in ridge]
    print(f"RIDGE LINE (peaks): {ridge_texts}")
    print("=" * 72)


if __name__ == "__main__":
    demo()
