"""
SanTOK Extended — Gravitational Bonding Engine (Structural Relations)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO external imports. ZERO grammar rules. ZERO linguistic labels.
ZERO Universal Dependencies. ZERO subject/object/predicate concepts.

CONCEPT: GRAVITATIONAL BONDING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
In a token stream, every token has STRUCTURAL MASS.

STRUCTURAL MASS:
  mass(t) = backend_scaled(t)
  (backend_scaled already encodes text content + position + neighbors)
  Range: 0 – 99999

The CORE of a stream = the token with maximum structural mass.
All other tokens are ORBITERS.

ORBITAL RADIUS:
  orbital_radius(t) = abs(index(t) - index(CORE))
  (how far from the core in the stream)

GRAVITATIONAL TENSION:
  tension(t) = mass(CORE) / (1 + orbital_radius(t))
  (decreases with distance — heavier cores pull farther)

ORBITAL CLASSIFICATION:
  CORE      → the heaviest token (max backend_scaled)
  INNER     → tension > mass(CORE) × 0.5   (strong pull, close orbit)
  MIDDLE    → tension > mass(CORE) × 0.2   (medium orbit)
  OUTER     → tension ≤ mass(CORE) × 0.2   (weak pull, far orbit)
  ESCAPE    → orbital_radius > escape_radius   (effectively free)

ESCAPE RADIUS:
  escape_radius = len(content_tokens) // 3
  Beyond this, the token is structurally independent.

MULTI-CORE SYSTEMS:
  If two tokens have mass within 10% of each other, they form a BINARY.
  Both are COREs. Orbiters bond to the nearest core.

STRUCTURAL BOND LABEL (our own invention):
  CORE → CORE:     "binary_bond"
  INNER orbit:     "tight_bond"
  MIDDLE orbit:    "field_bond"
  OUTER orbit:     "weak_bond"
  ESCAPE:          "free_orbit"
"""

CORE        = "CORE"
INNER       = "INNER"
MIDDLE      = "MIDDLE"
OUTER       = "OUTER"
ESCAPE      = "ESCAPE"

BINARY_BOND = "binary_bond"
TIGHT_BOND  = "tight_bond"
FIELD_BOND  = "field_bond"
WEAK_BOND   = "weak_bond"
FREE_ORBIT  = "free_orbit"


def _digital_root_9(n):
    if n <= 0:
        return 9
    return ((n - 1) % 9) + 1


def _mass(token):
    """Structural mass = backend_scaled."""
    return int(token.get("backend_scaled", 0))


def _classify_orbital(tension, core_mass, orbital_radius, escape_radius):
    if orbital_radius == 0:
        return CORE, BINARY_BOND
    if orbital_radius > escape_radius:
        return ESCAPE, FREE_ORBIT
    if tension > core_mass * 0.5:
        return INNER, TIGHT_BOND
    if tension > core_mass * 0.2:
        return MIDDLE, FIELD_BOND
    return OUTER, WEAK_BOND


def analyze(tokens):
    """
    Gravitational bonding analysis of a token stream.

    Each non-space token gets:
      "mass"             — structural mass (backend_scaled)
      "orbital_class"    — CORE / INNER / MIDDLE / OUTER / ESCAPE
      "bond_type"        — binary_bond / tight_bond / field_bond / weak_bond / free_orbit
      "core_index"       — stream index of the token's gravitational core
      "core_text"        — text of the gravitational core
      "orbital_radius"   — distance from core (in stream positions)
      "tension"          — gravitational tension value
      "is_core"          — True if this token is a core
    """
    content = [(i, t) for i, t in enumerate(tokens) if t.get("text", "").strip()]
    if not content:
        return list(tokens)

    n = len(content)
    masses = [(k, idx, t, _mass(t)) for k, (idx, t) in enumerate(content)]

    # Find core(s)
    max_mass = max(m for _, _, _, m in masses)
    binary_threshold = max_mass * 0.9   # within 10% = binary candidate

    core_ks = [k for k, idx, t, m in masses if m >= binary_threshold]
    is_binary = len(core_ks) > 1

    escape_radius = max(1, n // 3)

    result = [dict(t) for t in tokens]

    for k, (idx, tok) in enumerate(content):
        mass = _mass(tok)

        if k in core_ks:
            orbital_radius = 0
            nearest_core_k = k
            tension        = float(max_mass)
            orbital_class  = CORE
            bond           = BINARY_BOND if is_binary and len(core_ks) > 1 else TIGHT_BOND
        else:
            # Bond to nearest core
            nearest_core_k = min(core_ks, key=lambda ck: abs(k - ck))
            orbital_radius = abs(k - nearest_core_k)
            core_mass_val  = masses[nearest_core_k][3]
            tension        = core_mass_val / (1 + orbital_radius)
            orbital_class, bond = _classify_orbital(
                tension, core_mass_val, orbital_radius, escape_radius
            )

        core_stream_idx = content[nearest_core_k][0]
        core_text       = content[nearest_core_k][1].get("text", "")

        # Also compute local digital_root of mass for extra signal
        mass_root = _digital_root_9(mass)

        result[idx].update({
            "mass"           : mass,
            "mass_root"      : mass_root,
            "orbital_class"  : orbital_class,
            "bond_type"      : bond,
            "core_index"     : core_stream_idx,
            "core_text"      : core_text,
            "orbital_radius" : orbital_radius,
            "tension"        : round(tension, 2),
            "is_core"        : k in core_ks,
            "escape_radius"  : escape_radius,
        })

    return result


def bond_map(tokens):
    """
    Return a compact bond summary: list of (text, orbital_class, tension, core).
    Only content tokens.
    """
    parsed = analyze(tokens)
    return [
        {
            "text"    : t["text"],
            "class"   : t.get("orbital_class"),
            "bond"    : t.get("bond_type"),
            "tension" : t.get("tension"),
            "core"    : t.get("core_text"),
            "radius"  : t.get("orbital_radius"),
        }
        for t in parsed
        if t.get("text", "").strip()
    ]


# ── demo ─────────────────────────────────────────────────────────────────────

def demo():
    sample = [
        {"text": "The",   "frontend": 1, "backend_scaled": 26151},
        {"text": "quick", "frontend": 2, "backend_scaled": 20529},
        {"text": "brown", "frontend": 3, "backend_scaled": 86990},
        {"text": "fox",   "frontend": 4, "backend_scaled": 52293},
        {"text": "jumps", "frontend": 1, "backend_scaled": 50736},
        {"text": "over",  "frontend": 5, "backend_scaled": 6801},
        {"text": "the",   "frontend": 2, "backend_scaled": 94973},
        {"text": "lazy",  "frontend": 9, "backend_scaled": 86254},
        {"text": "dog",   "frontend": 5, "backend_scaled": 87919},
    ]

    bonds = bond_map(sample)

    print("=" * 72)
    print("SanTOK GRAVITATIONAL BONDING ENGINE — DEMO")
    print("Structural mass and orbital relationships. Zero grammar rules.")
    print("=" * 72)
    print(f"{'TOKEN':<8} {'MASS':>6} {'CLASS':<8} {'BOND':<14} {'TENSION':>8} {'RADIUS':>7}  CORE")
    print("-" * 65)
    for b in bonds:
        core_mark = "← CORE" if b["class"] == CORE else f"→ {b['core']}"
        print(
            f"{b['text']:<8} {b['tension'] if b['class']==CORE else '':>6} "
            f"{b['class']:<8} {b['bond']:<14} {b['tension']:>8.1f} "
            f"{b['radius']:>7}  {core_mark}"
        )

    # Show max mass
    max_tok = max(bonds, key=lambda b: sample[[t["text"] for t in sample].index(b["text"])]["backend_scaled"])
    print()
    print(f"  CORE: '{max_tok['text']}'  (highest mass = backend_scaled)")
    print("=" * 72)


if __name__ == "__main__":
    demo()
