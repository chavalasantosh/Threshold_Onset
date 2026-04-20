"""
SanTOK Extended — Stop Word Filter
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO hardcoded word lists. ZERO corpora.

Logic: A token is a stop word when it satisfies structural
       conditions derived from POS + frontend + backend_scaled
       + text length:

  Rule 1 (FUNCTIONAL POS gate):
    pos in {DET, PREP, CONJ, PRON} → candidate stop word

  Rule 2 (STRUCTURAL confirmation):
    frontend in {1, 2, 3, 7} AND text_length <= 4
    → short functional form confirmed by structural signature

  Rule 3 (BACKEND light zone):
    backend_scaled < 15000 OR backend_scaled > 85000
    → extreme bs values indicate structurally boundary tokens
      (common function words cluster at the extremes)

  A token is a STOP WORD if it passes Rule 1 AND (Rule 2 OR Rule 3).
  Space tokens are always stop words.

  Custom additions/removals are supported without hardcoded lists.
"""

_FUNCTIONAL_POS = {"DET", "PREP", "CONJ", "PRON"}
_FUNC_FRONTENDS = {1, 2, 3, 7}
_MAX_FUNC_LEN   = 4
_BS_LOW_BOUND   = 15000
_BS_HIGH_BOUND  = 85000


def _is_space(text):
    return bool(text) and all(c in ' \t\n\r' for c in text)


def _structural_stop(token):
    """Return True if token passes structural stop-word conditions."""
    fe  = int(token.get("frontend", 5))
    bs  = int(token.get("backend_scaled", 50000))
    txt = token.get("text", "")
    n   = len(txt)

    rule2 = (fe in _FUNC_FRONTENDS) and (n <= _MAX_FUNC_LEN)
    rule3 = (bs < _BS_LOW_BOUND) or (bs > _BS_HIGH_BOUND)
    return rule2 or rule3


class StopWordFilter:
    """
    Stateful stop-word filter.
    Supports custom add/remove without any hardcoded word list.
    """

    def __init__(self):
        self._forced_stop   = set()   # always stop regardless of signals
        self._forced_keep   = set()   # never stop regardless of signals

    def add(self, text):
        """Force a word to always be treated as a stop word."""
        t = text.strip()
        self._forced_keep.discard(t)
        self._forced_stop.add(t)
        return self

    def remove(self, text):
        """Force a word to never be treated as a stop word."""
        t = text.strip()
        self._forced_stop.discard(t)
        self._forced_keep.add(t)
        return self

    def is_stop(self, token):
        """
        Return True if token is a stop word.

        token: SanTOK TokenRecord dict with pos, frontend,
               backend_scaled, text fields.
        """
        text = token.get("text", "")

        if text in self._forced_keep:
            return False
        if text in self._forced_stop:
            return True
        if _is_space(text):
            return True

        pos = token.get("pos")
        functional_pos = pos in _FUNCTIONAL_POS
        structural_ok  = _structural_stop(token)

        return functional_pos and structural_ok

    def filter_stream(self, tokens):
        """Return only non-stop tokens from a list."""
        return [t for t in tokens if not self.is_stop(t)]

    def tag_stream(self, tokens):
        """Add 'is_stop' bool to every token. Returns same-length list."""
        result = []
        for tok in tokens:
            t2 = dict(tok)
            t2["is_stop"] = self.is_stop(tok)
            result.append(t2)
        return result


# Module-level default filter instance
_DEFAULT_FILTER = StopWordFilter()


def is_stop(token):
    """Convenience: check single token with default filter."""
    return _DEFAULT_FILTER.is_stop(token)


def filter_stream(tokens):
    """Convenience: filter list with default filter."""
    return _DEFAULT_FILTER.filter_stream(tokens)


def tag_stream(tokens):
    """Convenience: tag list with default filter."""
    return _DEFAULT_FILTER.tag_stream(tokens)


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
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
        {"text": "action",   "pos": "NOUN", "frontend": 6, "backend_scaled": 34000},
        {"text": "before",   "pos": "PREP", "frontend": 4, "backend_scaled": 8000},
        {"text": "knowledge","pos": "NOUN", "frontend": 3, "backend_scaled": 62000},
    ]

    f = StopWordFilter()

    print("=" * 55)
    print("SanTOK STOP WORD FILTER — DEMO")
    print("=" * 55)
    print(f"{'TEXT':<12} {'POS':<6} {'FE':>3} {'BS':>7}  {'STOP?'}")
    print("-" * 42)

    for t in f.tag_stream(sample):
        stop = "STOP ✓" if t["is_stop"] else "keep"
        print(f"{t['text']:<12} {t['pos']:<6} {t['frontend']:>3} {t['backend_scaled']:>7}  {stop}")

    kept = f.filter_stream(sample)
    print()
    print("After filtering: " + " ".join(t["text"] for t in kept))
    print("=" * 55)


if __name__ == "__main__":
    demo()
