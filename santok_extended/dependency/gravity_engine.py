"""
SanTOK Extended — Structural Dependency (Gravity Mapper)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ZERO traditional NLP dependency parsing. ZERO treebanks.
Operates purely on SanTOK physical signals:
  1. Topographical Basins (bounding contexts)
  2. frontend (fe=1 and fe=7 are massive structural poles/anchors)
  3. backend_scaled (mass/pressure of individual tokens)

LOGIC:
Inside a basin, the highest `bs` token is the Physical Peak (Core subject/action).
All other tokens naturally orbit (depend on) either:
  a. The nearest Pole (fe=1 or fe=7) if they are adjacent or trapped.
  b. The Physical Peak of the basin.
"""

def map_gravity(tokens):
    """
    Adds "gravity_role" and "orbits_index" to each token, representing
    the deterministic physical dependency tree.
    (Requires 'basin_id' to be set by ngram_engine beforehand).
    """
    if not tokens:
        return tokens

    # Ensure basins exist (fallback to 0 if ngram engine not run)
    has_basins = "basin_id" in tokens[0]

    basins = {}
    for i, t in enumerate(tokens):
        bid = t.get("basin_id", 0) if has_basins else 0
        if bid not in basins:
            basins[bid] = []
        basins[bid].append((i, t))

    for bid, b_tokens in basins.items():
        if not b_tokens: continue

        # 1. Identify Peak Mass and Poles
        peak_local = -1
        max_bs = -1
        poles_local = []

        for local_idx, (global_idx, t) in enumerate(b_tokens):
            bs = t.get("backend_scaled", 0)
            fe = t.get("frontend", 0)
            
            if bs > max_bs:
                max_bs = bs
                peak_local = local_idx
                
            if fe in (1, 7):
                poles_local.append(local_idx)

        # 2. Assign Gravity Vectors
        for local_idx, (global_idx, t) in enumerate(b_tokens):
            # If this is the absolute peak of the chunk
            if local_idx == peak_local:
                t["gravity_role"] = "PEAK_CENTER"
                t["orbits_index"] = "ROOT"
                continue
                
            # If this is a structural pole
            if local_idx in poles_local:
                t["gravity_role"] = "ANCHOR_POLE"
                # Poles orbit the giant mass peak
                t["orbits_index"] = b_tokens[peak_local][1].get("index", "?")
                continue

            # Standard tokens fall to nearest pole or to peak
            nearest_dist = 999
            nearest_pole = -1
            for p in poles_local:
                d = abs(local_idx - p)
                if d < nearest_dist:
                    nearest_dist = d
                    nearest_pole = p
            
            # If a pole is close (distance 1 or 2), it gets trapped in pole orbit
            if nearest_pole != -1 and nearest_dist <= 2:
                t["gravity_role"] = "ORBITS_POLE"
                t["orbits_index"] = b_tokens[nearest_pole][1].get("index", "?")
            else:
                # Otherwise it falls radially to the peak mass
                t["gravity_role"] = "ORBITS_PEAK"
                t["orbits_index"] = b_tokens[peak_local][1].get("index", "?")

    return tokens

def demo():
    print("SanTOK Gravity Engine loaded. Use through pipeline.")

if __name__ == "__main__":
    demo()
