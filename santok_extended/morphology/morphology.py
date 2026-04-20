"""
SanTOK Extended — Morphological Analyzer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO suffix tables. ZERO borrowed logic.

Logic: Compare backend_scaled of the full token vs its
       character-level sub-tokens (prefix and suffix windows).

       Structural divergence at the LEFT  → prefix boundary
       Structural divergence at the RIGHT → suffix boundary
       What remains in the middle          → root

Divergence = abs(backend_scaled(slice) - backend_scaled(full)) > threshold
Threshold  = backend_scaled(full) // 10  (10% tolerance zone)
"""


def _weighted_sum(text):
    total = 0
    for i, c in enumerate(text):
        total += ord(c) * (i + 1)
    return total


def _digital_root(n):
    return 9 if n <= 0 else ((n - 1) % 9) + 1


def _backend_scaled(text):
    if not text:
        return 0
    ws = _weighted_sum(text)
    dr = _digital_root(ws)
    return (ws * dr * (1 + len(text))) % 100000


def _frontend(text):
    if not text:
        return 9
    ws = _weighted_sum(text)
    dr = _digital_root(ws)
    h  = 0
    for c in text:
        h = h * 31 + ord(c)
    hd = h % 10
    return (dr * 9 + hd) % 9 + 1


# ── prefix detector ───────────────────────────────────────────────────────────

def _find_prefix(text, full_bs, tolerance):
    """
    Walk left-to-right, find longest prefix where backend diverges from full.
    A prefix exists if the FIRST chars create a different structural signature.
    Returns '' if no prefix detected.
    """
    if len(text) < 3:
        return ""
    for end in range(1, len(text) - 1):
        slice_bs = _backend_scaled(text[:end])
        if abs(slice_bs - full_bs) > tolerance:
            # Divergence at position `end` — prefix is text[:end]
            return text[:end]
    return ""


def _find_suffix(text, full_bs, tolerance):
    """
    Walk right-to-left, find longest suffix where backend diverges from full.
    Returns '' if no suffix detected.
    """
    if len(text) < 3:
        return ""
    for start in range(len(text) - 1, 0, -1):
        slice_bs = _backend_scaled(text[start:])
        if abs(slice_bs - full_bs) > tolerance:
            return text[start:]
    return ""


# ── public API ────────────────────────────────────────────────────────────────

def analyze_token(token):
    """
    Morphological analysis of one SanTOK TokenRecord dict.

    Adds:
      "morph_prefix"  — detected prefix string ('' if none)
      "morph_root"    — structural root
      "morph_suffix"  — detected suffix string ('' if none)
      "morph_class"   — backend_scaled % 7  (0-6 morphological class)
      "morph_signals" — raw signals
    """
    result = dict(token)
    text   = token.get("text", "")

    if not text or len(text) < 2:
        result.update({
            "morph_prefix": "", "morph_root": text,
            "morph_suffix": "", "morph_class": 0,
            "morph_signals": {"gate": "TOO_SHORT"},
        })
        return result

    full_bs   = _backend_scaled(text)
    tolerance = max(1000, full_bs // 10)   # 10% of full bs, minimum 1000

    prefix = _find_prefix(text, full_bs, tolerance)
    suffix = _find_suffix(text, full_bs, tolerance)

    # root = what's left after removing prefix and suffix
    inner = text[len(prefix):]
    if suffix and inner.endswith(suffix):
        root = inner[: len(inner) - len(suffix)]
    else:
        root   = inner
        suffix = ""

    # ensure root is non-empty
    if not root:
        root   = text
        prefix = ""
        suffix = ""

    morph_class = full_bs % 7

    result.update({
        "morph_prefix"  : prefix,
        "morph_root"    : root,
        "morph_suffix"  : suffix,
        "morph_class"   : morph_class,
        "morph_signals" : {
            "full_bs"   : full_bs,
            "tolerance" : tolerance,
            "full_fe"   : _frontend(text),
            "root_fe"   : _frontend(root) if root else 9,
            "root_bs"   : _backend_scaled(root),
        },
    })
    return result


def analyze_stream(tokens):
    """Analyze morphology of a list of SanTOK token dicts."""
    return [analyze_token(t) for t in tokens]


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    sample = [
        {"text": "running"},
        {"text": "quickly"},
        {"text": "tokenize"},
        {"text": "unhappy"},
        {"text": "rewrite"},
        {"text": "dogs"},
        {"text": "jumps"},
        {"text": "the"},
        {"text": "structural"},
        {"text": "emergence"},
        {"text": "knowledge"},
        {"text": "action"},
        {"text": "residues"},
    ]

    print("=" * 70)
    print("SanTOK MORPHOLOGICAL ANALYZER — DEMO")
    print("=" * 70)
    print(f"{'TEXT':<14} {'PREFIX':<8} {'ROOT':<12} {'SUFFIX':<8} {'CLASS':>5}")
    print("-" * 55)

    for t in analyze_stream(sample):
        print(
            f"{t['text']:<14} "
            f"{(t['morph_prefix'] or '—'):<8} "
            f"{t['morph_root']:<12} "
            f"{(t['morph_suffix'] or '—'):<8} "
            f"{t['morph_class']:>5}"
        )

    print("=" * 70)


if __name__ == "__main__":
    demo()
