"""
SanTOK Extended — Signal Saturation Engine (Vocabulary Weight)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO frequency math. ZERO TF-IDF or variants.

CONCEPT: SIGNAL SATURATION & DECAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
In a token stream, every token emits a STRUCTURAL SIGNAL.

The signal strength = its frontend value (1-9).

Every time the same content_id appears again:
  saturation += frontend_value
  (cumulative signal pressure from repeated appearances)

As the uid chain advances (token positions spread out):
  The residual signal decays.
  Tokens scattered across the stream decay faster than clustered ones.

SATURATION:
  saturation(cid) = sum of frontend values each time cid appears
  = first_fe + second_fe + third_fe + ...
  NOT just a count — each occurrence contributes its structural weight.

DECAY:
  uid_span = max_index - min_index  (how spread across the stream)
  decay    = digital_root_9(uid_span)   → 1-9

  A small uid_span (clustered appearances) → small decay (signal persists)
  A large uid_span (scattered appearances) → large decay (signal fades)

SIGNAL STRENGTH:
  strength(cid) = saturation / decay
  (how much structural pressure this token exerts, adjusted for persistence)

INTERPRETATION:
  HIGH strength = dominant token (frequent, high fe, clustered)
  LOW strength  = peripheral token (rare, low fe, or scattered)
  OOV           = strength < 1.0 (below minimum structural footprint)

STRUCTURAL DENSITY:
  density(cid) = content_id XOR backend_scaled   (mod 9999)
  High XOR divergence = the content identity conflicts with context pressure
  = structurally unusual token = high density signal
"""


def _dr9(n):
    if n <= 0:
        return 9
    return ((n - 1) % 9) + 1


class SignalSaturationEngine:
    """
    Tracks signal saturation and decay for vocabulary analysis.
    Key = content_id. Weight = original SanTOK-native formulas.
    """

    def __init__(self):
        self._saturation  = {}   # cid → cumulative frontend sum
        self._min_idx     = {}   # cid → minimum position seen
        self._max_idx     = {}   # cid → maximum position seen
        self._occurrences = {}   # cid → count of appearances
        self._fe_first    = {}   # cid → frontend of first appearance
        self._bs_first    = {}   # cid → backend_scaled of first appearance
        self._text_map    = {}   # cid → representative text
        self._doc_ids     = {}   # cid → set of doc_ids seen in
        self._doc_count   = 0

    # ── ingest ───────────────────────────────────────────────────────────────

    def ingest(self, tokens, doc_id=None):
        """
        Ingest a list of SanTOK token dicts.
        Each call is ONE document. doc_id auto-assigned if None.
        """
        if doc_id is None:
            doc_id = self._doc_count
        self._doc_count += 1

        for pos, tok in enumerate(tokens):
            text = tok.get("text", "")
            if not text or not text.strip():
                continue

            cid  = int(tok.get("content_id", 0))
            fe   = max(1, min(9, int(tok.get("frontend", 5))))
            bs   = int(tok.get("backend_scaled", 0))
            idx  = int(tok.get("index", pos))

            # Accumulate saturation
            self._saturation[cid]  = self._saturation.get(cid, 0) + fe
            self._occurrences[cid] = self._occurrences.get(cid, 0) + 1

            # Track position range for decay
            if cid not in self._min_idx:
                self._min_idx[cid] = idx
                self._max_idx[cid] = idx
            else:
                if idx < self._min_idx[cid]: self._min_idx[cid] = idx
                if idx > self._max_idx[cid]: self._max_idx[cid] = idx

            # Track first-seen values
            if cid not in self._fe_first:
                self._fe_first[cid]  = fe
                self._bs_first[cid]  = bs
                self._text_map[cid]  = text

            # Track documents
            if cid not in self._doc_ids:
                self._doc_ids[cid] = set()
            self._doc_ids[cid].add(doc_id)

    # ── core formulas ─────────────────────────────────────────────────────────

    def saturation(self, cid):
        """Cumulative frontend signal from all appearances."""
        return self._saturation.get(cid, 0)

    def decay(self, cid):
        """
        Signal decay = digital_root_9(uid_span).
        uid_span = max_index - min_index.
        Result: 1-9. Low = signal persists. High = signal fades.
        """
        span = self._max_idx.get(cid, 0) - self._min_idx.get(cid, 0)
        return _dr9(span)

    def signal_strength(self, cid):
        """
        strength = saturation / decay
        Higher = more dominant structurally.
        """
        sat   = self.saturation(cid)
        dec   = self.decay(cid)
        return round(sat / dec, 4)

    def structural_density(self, cid):
        """
        density = (content_id XOR backend_scaled_first) % 9999
        High XOR = content conflicts with context = structurally unusual.
        """
        bs = self._bs_first.get(cid, 0)
        return (cid ^ bs) % 9999

    def is_oov(self, cid):
        """
        OOV = signal_strength < 1.0.
        Below minimum structural footprint threshold.
        """
        return self.signal_strength(cid) < 1.0

    def occurrences(self, cid):
        return self._occurrences.get(cid, 0)

    def doc_spread(self, cid):
        return len(self._doc_ids.get(cid, set()))

    # ── vocabulary access ─────────────────────────────────────────────────────

    def vocabulary(self):
        """
        Return sorted list of (cid, text, occurrences, saturation, decay,
        strength, density, is_oov) sorted by strength descending.
        """
        rows = []
        for cid, text in self._text_map.items():
            rows.append((
                cid, text,
                self.occurrences(cid),
                self.saturation(cid),
                self.decay(cid),
                self.signal_strength(cid),
                self.structural_density(cid),
                self.is_oov(cid),
            ))
        rows.sort(key=lambda r: r[5], reverse=True)
        return rows

    def top_n(self, n=10):
        return self.vocabulary()[:n]

    def tag_token(self, token):
        """Add saturation stats to a single token dict."""
        cid = int(token.get("content_id", 0))
        t2  = dict(token)
        t2["saturation"] = self.saturation(cid)
        t2["decay"]      = self.decay(cid)
        t2["strength"]   = self.signal_strength(cid)
        t2["density"]    = self.structural_density(cid)
        t2["is_oov"]     = self.is_oov(cid)
        return t2

    def tag_stream(self, tokens):
        return [self.tag_token(t) for t in tokens]

    @property
    def size(self):
        return len(self._saturation)

    @property
    def doc_count(self):
        return self._doc_count


# Convenience alias for import compatibility
VocabularyBuilder = SignalSaturationEngine


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    doc1 = [
        {"text": "The",   "frontend": 1, "backend_scaled": 26151, "content_id": 128727, "index": 0},
        {"text": "quick", "frontend": 2, "backend_scaled": 20529, "content_id": 29583,  "index": 2},
        {"text": "brown", "frontend": 3, "backend_scaled": 86990, "content_id": 56274,  "index": 4},
        {"text": "fox",   "frontend": 4, "backend_scaled": 52293, "content_id": 26790,  "index": 6},
        {"text": "jumps", "frontend": 1, "backend_scaled": 50736, "content_id": 4205,   "index": 8},
        {"text": "over",  "frontend": 5, "backend_scaled": 6801,  "content_id": 16460,  "index": 10},
        {"text": "the",   "frontend": 2, "backend_scaled": 94973, "content_id": 125905, "index": 12},
        {"text": "lazy",  "frontend": 9, "backend_scaled": 86254, "content_id": 39107,  "index": 14},
        {"text": "dog",   "frontend": 5, "backend_scaled": 87919, "content_id": 134410, "index": 16},
    ]
    doc2 = [
        {"text": "action",    "frontend": 6, "backend_scaled": 34000, "content_id": 71000, "index": 0},
        {"text": "over",      "frontend": 5, "backend_scaled": 6801,  "content_id": 16460, "index": 4},
        {"text": "knowledge", "frontend": 3, "backend_scaled": 62000, "content_id": 55000, "index": 8},
        {"text": "the",       "frontend": 2, "backend_scaled": 94973, "content_id": 125905,"index": 12},
    ]

    eng = SignalSaturationEngine()
    eng.ingest(doc1, "doc1")
    eng.ingest(doc2, "doc2")

    print("=" * 78)
    print(f"SanTOK SIGNAL SATURATION ENGINE — {eng.size} terms, {eng.doc_count} docs")
    print("Vocabulary weight from structural signal physics. Zero TF-IDF.")
    print("=" * 78)
    print(f"{'TERM':<12} {'CID':>8} {'OCC':>4} {'SAT':>5} {'DECAY':>6} {'STRENGTH':>9} {'DENSITY':>8} {'OOV':>5}")
    print("-" * 70)
    for row in eng.vocabulary():
        cid, text, occ, sat, dec, strength, density, oov = row
        oov_mark = "OOV" if oov else ""
        print(f"{text:<12} {cid:>8} {occ:>4} {sat:>5} {dec:>6} {strength:>9.4f} {density:>8} {oov_mark:>5}")

    print()
    print("  HOW SATURATION WORKS:")
    print("  'the' appears twice (fe=2 each) → SAT=4 → spread across docs → DECAY=dr9(span)")
    print("  'lazy' appears once  (fe=9)     → SAT=9 → single position   → DECAY=1 → STRENGTH=9")
    print("=" * 78)


if __name__ == "__main__":
    demo()
