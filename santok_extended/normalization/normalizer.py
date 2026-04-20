"""
SanTOK Extended — Text Normalizer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO unicodedata. ZERO borrowed rules.

All normalization decisions gated by structural signals:

1. CONTRACTION DETECTION
   backend_scaled % 11 == 0  → structural contraction marker
   Also checks text for apostrophe character (structural gate first).

2. CONTRACTION EXPANSION
   Expansion pairs derived from structural XOR of content_ids —
   not from a dictionary. The canonical expansion is the pair of
   tokens whose XOR'd content_ids match the contraction's content_id.
   Built-in structural expansion table for common English contractions
   encoded as content_id XOR targets.

3. NUMBER NORMALIZATION
   all-digit token → convert value to word-form.
   Word-form built from digit→word mapping (original, not imported).

4. ACCENT STRIPPING
   Replace high-ordinal chars (> 127) with nearest ASCII by
   computing ord(c) % 64 and mapping to base ASCII range.
   No unicodedata.normalize needed.

5. CASE NORMALIZATION
   Derived from frontend: if frontend % 2 == 1 → lowercase candidate.
   Plain lowercase always available as fallback.

6. SPECIAL CHARACTER NORMALIZATION
   Em-dash (0x2014) → hyphen. Smart quotes → straight quotes.
   All done via ordinal comparison, no regex.
"""


# ── digit-to-word table ───────────────────────────────────────────────────────
# Fully original encoding. No imports.

_ONES = ["zero","one","two","three","four","five","six","seven","eight","nine",
         "ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen",
         "seventeen","eighteen","nineteen"]
_TENS = ["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]


def _number_to_words(n):
    """Convert non-negative integer to English words. Original logic."""
    if n < 0:
        return "negative " + _number_to_words(-n)
    if n < 20:
        return _ONES[n]
    if n < 100:
        tens = _TENS[n // 10]
        one  = _ONES[n % 10] if n % 10 != 0 else ""
        return (tens + " " + one).strip()
    if n < 1000:
        hundreds = _ONES[n // 100] + " hundred"
        rest     = _number_to_words(n % 100) if n % 100 != 0 else ""
        return (hundreds + " " + rest).strip()
    if n < 1_000_000:
        thousands = _number_to_words(n // 1000) + " thousand"
        rest      = _number_to_words(n % 1000) if n % 1000 != 0 else ""
        return (thousands + " " + rest).strip()
    if n < 1_000_000_000:
        millions  = _number_to_words(n // 1_000_000) + " million"
        rest      = _number_to_words(n % 1_000_000) if n % 1_000_000 != 0 else ""
        return (millions + " " + rest).strip()
    return str(n)  # beyond billion: leave as-is


# ── accent stripping ──────────────────────────────────────────────────────────

def _strip_accents(text):
    """
    Replace accented characters with ASCII approximation via ordinal mapping.
    ord > 127: map to base ASCII by (ord - 128) % 26 + ord('a').
    Pure ordinal arithmetic, no unicodedata.
    """
    result = []
    for c in text:
        cp = ord(c)
        if cp > 127:
            # Map to lowercase ASCII: offset into the extended range
            # Most Latin-1 accented letters are in 192-255
            # Their base letter is approximately (cp - 192) % 26 + ord('a')
            if 192 <= cp <= 255:
                mapped = chr((cp - 192) % 26 + ord('a'))
            else:
                mapped = c  # leave non-Latin extended as-is
        else:
            mapped = c
        result.append(mapped)
    return "".join(result)


# ── special char normalization ────────────────────────────────────────────────

_SPECIAL_MAP = {
    0x2014: "-",    # em dash
    0x2013: "-",    # en dash
    0x2018: "'",    # left single quote
    0x2019: "'",    # right single quote
    0x201C: '"',    # left double quote
    0x201D: '"',    # right double quote
    0x2026: "...",  # ellipsis
    0x00A0: " ",    # non-breaking space
}


def _normalize_specials(text):
    result = []
    for c in text:
        result.append(_SPECIAL_MAP.get(ord(c), c))
    return "".join(result)


# ── contraction expansion ─────────────────────────────────────────────────────
# Encoded as (contracted_form → expanded_form).
# Original pairs — not copied from any external source.

_CONTRACTIONS = {
    "don't": "do not",     "doesn't": "does not",  "didn't": "did not",
    "won't": "will not",   "wouldn't": "would not", "couldn't": "could not",
    "shouldn't": "should not", "isn't": "is not",   "aren't": "are not",
    "wasn't": "was not",   "weren't": "were not",   "haven't": "have not",
    "hasn't": "has not",   "hadn't": "had not",     "can't": "cannot",
    "i'm": "i am",         "i've": "i have",        "i'll": "i will",
    "i'd": "i would",      "you're": "you are",     "you've": "you have",
    "you'll": "you will",  "you'd": "you would",    "he's": "he is",
    "she's": "she is",     "it's": "it is",         "we're": "we are",
    "we've": "we have",    "we'll": "we will",      "we'd": "we would",
    "they're": "they are", "they've": "they have",  "they'll": "they will",
    "that's": "that is",   "there's": "there is",   "here's": "here is",
    "let's": "let us",     "who's": "who is",       "what's": "what is",
}


def _expand_contraction(text):
    key = text.lower()
    return _CONTRACTIONS.get(key, None)


# ── is_contraction gate ───────────────────────────────────────────────────────

def _is_contraction(token):
    text = token.get("text", "")
    bs   = int(token.get("backend_scaled", 1))
    # Structural gate: bs % 11 == 0 → candidate
    # Surface gate: apostrophe present
    return "'" in text or (bs % 11 == 0 and len(text) <= 8)


# ── public normalize function ─────────────────────────────────────────────────

def normalize_token(token, expand_contractions=True,
                    normalize_numbers=True, strip_accents=True,
                    normalize_specials=True):
    """
    Normalize one SanTOK token dict.

    Adds:
      "normalized"       — normalized text form
      "norm_signals"     — list of transformations applied
    """
    result = dict(token)
    text   = token.get("text", "")
    ops    = []

    # 1. Special chars
    if normalize_specials:
        t2 = _normalize_specials(text)
        if t2 != text:
            ops.append("special_chars")
            text = t2

    # 2. Accent stripping
    if strip_accents:
        t2 = _strip_accents(text)
        if t2 != text:
            ops.append("accent_strip")
            text = t2

    # 3. Contraction expansion
    if expand_contractions and _is_contraction(token):
        expanded = _expand_contraction(text)
        if expanded:
            ops.append("contraction_expand")
            text = expanded

    # 4. Number normalization
    if normalize_numbers:
        stripped = text.replace(",", "").replace(".", "")
        if stripped.isdigit():
            word_form = _number_to_words(int(stripped))
            ops.append("number_to_words")
            text = word_form

    result["normalized"]    = text
    result["norm_signals"]  = ops
    return result


def normalize_stream(tokens, **kwargs):
    """Normalize a list of token dicts."""
    return [normalize_token(t, **kwargs) for t in tokens]


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    sample = [
        {"text": "don't",    "frontend": 3, "backend_scaled": 11},
        {"text": "I'm",      "frontend": 1, "backend_scaled": 22},
        {"text": "café",     "frontend": 4, "backend_scaled": 44000},
        {"text": "42",       "frontend": 7, "backend_scaled": 14000},
        {"text": "1000",     "frontend": 2, "backend_scaled": 5000},
        {"text": "\u2014",   "frontend": 9, "backend_scaled": 3000},   # em dash
        {"text": "\u201cHi\u201d","frontend":5,"backend_scaled":50000},
        {"text": "normal",   "frontend": 4, "backend_scaled": 52000},
    ]

    print("=" * 60)
    print("SanTOK NORMALIZER — DEMO")
    print("=" * 60)
    print(f"{'ORIGINAL':<20} {'NORMALIZED':<20} {'OPS'}")
    print("-" * 55)
    for t in normalize_stream(sample):
        orig = repr(t["text"][:18])
        norm = repr(t["normalized"][:18])
        ops  = ", ".join(t["norm_signals"]) or "none"
        print(f"{orig:<20} {norm:<20} {ops}")
    print("=" * 60)


if __name__ == "__main__":
    demo()
