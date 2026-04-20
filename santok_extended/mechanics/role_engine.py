"""
SanTOK Extended — Core Mechanics: Role Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Derived strictly from:
  LAW 1 (Pole Law): The stream organizes around specific high-connectivity frontend values.
  LAW 5 (Role Law): A token's role is its repeating neighbor-transition constraints.

This engine outputs pure constraints as data. No string labels like "NOUN" or "CARRIER".
"""

def _build_transition_matrix(content_tokens):
    out_deg = {i: 0 for i in range(1, 10)}
    in_deg = {i: 0 for i in range(1, 10)}
    for i in range(len(content_tokens) - 1):
        a = content_tokens[i]["frontend"]
        b = content_tokens[i+1]["frontend"]
        out_deg[a] += 1
        in_deg[b] += 1
    total_deg = {i: out_deg[i] + in_deg[i] for i in range(1, 10)}
    return in_deg, out_deg, total_deg

def _find_poles(total_degree, n=2):
    sorted_fe = sorted(total_degree.items(), key=lambda x: x[1], reverse=True)
    return [fe for fe, _ in sorted_fe[:n] if _ > 0]

def _find_invariants(content_tokens):
    cid_ctx = {}
    for i, tok in enumerate(content_tokens):
        cid = tok["content_id"]
        prev_fe = content_tokens[i-1]["frontend"] if i > 0 else None
        next_fe = content_tokens[i+1]["frontend"] if i < len(content_tokens)-1 else None
        if cid not in cid_ctx:
            cid_ctx[cid] = []
        cid_ctx[cid].append((prev_fe, next_fe))
        
    invariants = {}
    for cid, contexts in cid_ctx.items():
        if len(contexts) < 2:
            continue
        prev_set = set(c[0] for c in contexts if c[0] is not None)
        next_set = set(c[1] for c in contexts if c[1] is not None)
        
        is_prev_locked = len(prev_set) == 1
        is_next_locked = len(next_set) == 1
        
        if is_prev_locked or is_next_locked:
            invariants[cid] = {
                "strict_prev_fe": list(prev_set)[0] if is_prev_locked and prev_set else None,
                "strict_next_fe": list(next_set)[0] if is_next_locked and next_set else None,
            }
    return invariants

def assign_roles(tokens):
    content = [t for t in tokens if str(t.get("text", "")).strip()]
    if not content:
        return list(tokens)

    in_deg, out_deg, total_deg = _build_transition_matrix(content)
    poles = _find_poles(total_deg)
    invariants = _find_invariants(content)

    result = [dict(t) for t in tokens]
    
    for i, tok in enumerate(content):
        orig_idx = int(tok.get("index", i))
        fe = tok.get("frontend", 5)
        cid = int(tok.get("content_id", 0))

        # Core physical metrics, zero labels
        role_data = {
            "is_pole": fe in poles,
            "in_connectivity": in_deg[fe],
            "out_connectivity": out_deg[fe],
            "attract_ratio": round(in_deg[fe] / (out_deg[fe] + 1e-5), 2),
            "strict_prev_fe": None,
            "strict_next_fe": None
        }

        if cid in invariants:
            role_data["strict_prev_fe"] = invariants[cid]["strict_prev_fe"]
            role_data["strict_next_fe"] = invariants[cid]["strict_next_fe"]

        for res_tok in result:
            if res_tok.get("index") == orig_idx and res_tok.get("uid") == tok.get("uid"):
                res_tok["structural_constraints"] = role_data
                break

    return result

def extract_role_summary(tokens):
    content = [t for t in tokens if str(t.get("text", "")).strip()]
    in_deg, out_deg, total_deg = _build_transition_matrix(content)
    return {
        "poles": _find_poles(total_deg),
        "invariant_count": len(_find_invariants(content)),
        "total_transitions": sum(total_deg.values()) // 2
    }
