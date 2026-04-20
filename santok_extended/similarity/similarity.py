"""
SanTOK Extended — Structural Interference Engine (Similarity)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO named algorithms. ZERO borrowed math.

CONCEPT: STRUCTURAL INTERFERENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A token stream is treated as a composite structural waveform.

Each token's frontend (1-9) is one "signal state."
The GRADIENT between consecutive tokens =
    gradient[i] = frontend[i+1] - frontend[i]   (range: -8 to +8)

This gradient encodes HOW the structure changes, not just what it is.

When two streams are compared:
  CONSTRUCTIVE RESONANCE: gradients move in the same direction
    (both rising, or both falling, or both flat)
  DESTRUCTIVE DISSONANCE: gradients move in opposite directions

INTERFERENCE QUOTIENT (IQ):
  iq_fe = count(resonant_positions) / count(total_positions)
  iq_bs = backend_scaled gradient alignment (same logic, different axis)
  IQ = (iq_fe × 7 + iq_bs × 2) / 9
       frontend weighted 7, backend weighted 2 — fe is the stronger signal

Range: [0.0, 1.0]
  1.0 = perfect constructive resonance (identical structure rhythm)
  0.0 = complete destructive dissonance (opposite structural directions)
  0.5 = incoherent (random mix — structurally unrelated streams)

CONTENT IDENTITY LOCK (CIL):
  Separate measure. If two streams share the same content_ids
  at the same relative positions, their content is locked.
  CIL = matched_positions / min_stream_length

These two measures together answer:
  IQ  → do the streams move through structure the same way?
  CIL → do the streams carry the same content in lockstep?
"""


def _fe_gradient(tokens):
    """
    Compute frontend gradient sequence.
    gradient[i] = fe[i+1] - fe[i]
    Returns list of length (n-1).
    """
    content = [t for t in tokens if t.get("text", "").strip()]
    fe_vals = [max(1, min(9, int(t.get("frontend", 5)))) for t in content]
    return [fe_vals[i + 1] - fe_vals[i] for i in range(len(fe_vals) - 1)]


def _bs_gradient(tokens):
    """
    Compute backend_scaled gradient sequence, normalised to [-1, 0, 1].
    gradient[i] = sign(bs[i+1] - bs[i])
    """
    content = [t for t in tokens if t.get("text", "").strip()]
    bs_vals = [int(t.get("backend_scaled", 50000)) for t in content]
    result  = []
    for i in range(len(bs_vals) - 1):
        diff = bs_vals[i + 1] - bs_vals[i]
        result.append(1 if diff > 0 else (-1 if diff < 0 else 0))
    return result


def _sign(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def _gradient_resonance(grad_a, grad_b):
    """
    Count resonant positions where both gradients move in the same direction.
    Returns float in [0, 1].
    """
    n = min(len(grad_a), len(grad_b))
    if n == 0:
        return 0.5   # undefined → neutral

    resonant = sum(
        1 for i in range(n)
        if _sign(grad_a[i]) == _sign(grad_b[i])
    )
    return resonant / n


def interference_quotient(tokens_a, tokens_b):
    """
    IQ: Structural Interference Quotient between two token streams.

    Measures how similarly the two streams move through structural space.
    Returns float in [0, 1].
    """
    fe_grad_a = _fe_gradient(tokens_a)
    fe_grad_b = _fe_gradient(tokens_b)
    bs_grad_a = _bs_gradient(tokens_a)
    bs_grad_b = _bs_gradient(tokens_b)

    iq_fe = _gradient_resonance(fe_grad_a, fe_grad_b)
    iq_bs = _gradient_resonance(bs_grad_a, bs_grad_b)

    # Frontend weighted 7, backend weighted 2
    iq = (iq_fe * 7 + iq_bs * 2) / 9
    return round(iq, 6)


def content_identity_lock(tokens_a, tokens_b):
    """
    CIL: Content Identity Lock.

    Measures how many content_ids match at the same relative position.
    Both streams normalized to their content tokens only.
    Returns float in [0, 1].
    """
    ca = [t for t in tokens_a if t.get("text", "").strip()]
    cb = [t for t in tokens_b if t.get("text", "").strip()]
    n  = min(len(ca), len(cb))
    if n == 0:
        return 0.0

    matched = sum(
        1 for i in range(n)
        if int(ca[i].get("content_id", 0)) == int(cb[i].get("content_id", 0))
    )
    return round(matched / n, 6)


def interference_profile(tokens_a, tokens_b):
    """
    Full structural comparison between two streams.
    Returns dict with IQ, CIL, and per-position resonance breakdown.
    """
    fe_grad_a = _fe_gradient(tokens_a)
    fe_grad_b = _fe_gradient(tokens_b)
    bs_grad_a = _bs_gradient(tokens_a)
    bs_grad_b = _bs_gradient(tokens_b)

    n_fe = min(len(fe_grad_a), len(fe_grad_b))
    n_bs = min(len(bs_grad_a), len(bs_grad_b))

    fe_positions = []
    for i in range(n_fe):
        sa = _sign(fe_grad_a[i])
        sb = _sign(fe_grad_b[i])
        fe_positions.append({
            "position": i,
            "gradient_a": fe_grad_a[i],
            "gradient_b": fe_grad_b[i],
            "resonance": sa == sb,
        })

    iq_fe = sum(1 for p in fe_positions if p["resonance"]) / n_fe if n_fe else 0.5
    iq_bs_val = _gradient_resonance(bs_grad_a, bs_grad_b)
    iq        = (iq_fe * 7 + iq_bs_val * 2) / 9

    return {
        "iq"              : round(iq, 6),
        "iq_fe"           : round(iq_fe, 6),
        "iq_bs"           : round(iq_bs_val, 6),
        "cil"             : content_identity_lock(tokens_a, tokens_b),
        "fe_positions"    : fe_positions,
        "len_a"           : len([t for t in tokens_a if t.get("text", "").strip()]),
        "len_b"           : len([t for t in tokens_b if t.get("text", "").strip()]),
    }


def token_proximity(token_a, token_b):
    """
    Direct structural proximity between two individual tokens.
    Based on how close their frontend and backend_scaled values are.
    Returns float in [0, 1].
    """
    fe_a = max(1, min(9, int(token_a.get("frontend", 5))))
    fe_b = max(1, min(9, int(token_b.get("frontend", 5))))
    bs_a = int(token_a.get("backend_scaled", 0))
    bs_b = int(token_b.get("backend_scaled", 0))

    fe_prox = 1.0 - abs(fe_a - fe_b) / 8.0
    bs_prox = 1.0 - abs(bs_a - bs_b) / 99999.0
    overall = (fe_prox * 7 + bs_prox * 2) / 9
    return round(overall, 6)


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    # Stream A: "The quick brown fox"
    stream_a = [
        {"text": "The",   "frontend": 1, "backend_scaled": 26151, "content_id": 128727},
        {"text": "quick", "frontend": 2, "backend_scaled": 20529, "content_id": 29583},
        {"text": "brown", "frontend": 3, "backend_scaled": 86990, "content_id": 56274},
        {"text": "fox",   "frontend": 4, "backend_scaled": 52293, "content_id": 26790},
    ]
    # Stream B: "The lazy brown dog" — same rising fe pattern as A, different content
    stream_b = [
        {"text": "The",   "frontend": 1, "backend_scaled": 26151, "content_id": 128727},
        {"text": "lazy",  "frontend": 9, "backend_scaled": 86254, "content_id": 39107},
        {"text": "brown", "frontend": 3, "backend_scaled": 86990, "content_id": 56274},
        {"text": "dog",   "frontend": 5, "backend_scaled": 87919, "content_id": 134410},
    ]
    # Stream C: "action before knowledge" — completely different
    stream_c = [
        {"text": "action",    "frontend": 6, "backend_scaled": 34000, "content_id": 71000},
        {"text": "before",    "frontend": 4, "backend_scaled": 8000,  "content_id": 16000},
        {"text": "knowledge", "frontend": 3, "backend_scaled": 62000, "content_id": 55000},
    ]

    print("=" * 65)
    print("SanTOK INTERFERENCE ENGINE — DEMO")
    print("Measuring structural waveform resonance between streams.")
    print("=" * 65)

    def show(name_a, name_b, ta, tb):
        p = interference_profile(ta, tb)
        print(f"\n  {name_a}  vs  {name_b}")
        print(f"    IQ  (Interference Quotient):   {p['iq']:.4f}  "
              f"[fe={p['iq_fe']:.4f} bs={p['iq_bs']:.4f}]")
        print(f"    CIL (Content Identity Lock):   {p['cil']:.4f}")
        print(f"    Fe gradients A: {[g['gradient_a'] for g in p['fe_positions']]}")
        print(f"    Fe gradients B: {[g['gradient_b'] for g in p['fe_positions']]}")
        resonance_map = ["✓" if pos["resonance"] else "✗" for pos in p["fe_positions"]]
        print(f"    Resonance map:  {resonance_map}")

    show("stream_A (fox)", "stream_B (dog)", stream_a, stream_b)
    show("stream_A (fox)", "stream_C (knowledge)", stream_a, stream_c)
    show("stream_A (fox)", "stream_A (identical)", stream_a, stream_a)

    print()
    tok_fox = {"text": "fox", "frontend": 4, "backend_scaled": 52293}
    tok_dog = {"text": "dog", "frontend": 5, "backend_scaled": 87919}
    tok_fox2= {"text": "fox", "frontend": 4, "backend_scaled": 52293}
    print(f"  Token proximity - fox vs dog:   {token_proximity(tok_fox, tok_dog):.4f}")
    print(f"  Token proximity - fox vs fox:   {token_proximity(tok_fox, tok_fox2):.4f}")
    print("=" * 65)


if __name__ == "__main__":
    demo()
