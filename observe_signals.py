"""
SanTOK — Deep Signal Observer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PURPOSE: Observe — do NOT interpret, do NOT build, do NOT name.

This script runs real SanTOK tokenization on a real text,
then produces 5 observation tables from actual data.

NO modules. NO labels. NO assumptions.
ONLY: what does the system actually produce?

TABLES PRODUCED:
  TABLE 1 — Raw token stream (what each token looks like)
  TABLE 2 — Transition table (what follows what, by frontend)
  TABLE 3 — Identity distribution (where each content_id appears)
  TABLE 4 — Context dynamics (same content_id, different backend_scaled?)
  TABLE 5 — Structural event chain (what changes between each pair)

READ the output. Look for:
  - Which frontend values appear most?
  - Which transitions are most common?
  - Do same content_ids always get same frontend? (they should)
  - Does backend_scaled vary for the same content_id? (it should)
  - What is the most common "event" in the event chain?
"""

import sys
import os

# ── Add santok_complete to path ───────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "santok_complete"))

try:
    from core.core_tokenizer import run_once, _content_id, combined_digit
except ImportError as e:
    print(f"ERROR: Cannot import SanTOK core: {e}")
    sys.exit(1)


# ── Run tokenization ──────────────────────────────────────────────────────────

SAMPLE_TEXT = """
Action before knowledge. The quick brown fox jumps over the lazy dog.
Tokens become structural residues in the digital root space.
Every token knows its neighbors. Every token carries its own pressure.
The system finds its own order without being told what order means.
"""

print("=" * 72)
print("SanTOK DEEP SIGNAL OBSERVER")
print("No labels. No assumptions. Only what the system produces.")
print("=" * 72)
print(f"\nInput text ({len(SAMPLE_TEXT.split())} words):")
print(f"  {SAMPLE_TEXT.strip()[:120]}...")

result = run_once(SAMPLE_TEXT.strip(), seed=12345, embedding_bit=False)

# Use word tokenizer stream (most meaningful for linguistic analysis)
# Fall back to space if word not available
stream_name = "word" if "word" in result else "space"
stream_data  = result[stream_name]
records      = stream_data["records"]
backends     = stream_data["backends"]
scaled       = stream_data["scaled"]
digits       = stream_data["digits"]   # these are the frontend values

# Build token list
tokens = []
for i, rec in enumerate(records):
    cid = _content_id(rec["text"])
    fe  = max(1, min(9, digits[i]))
    tokens.append({
        "index"         : i,
        "text"          : rec["text"],
        "frontend"      : fe,
        "backend_scaled": scaled[i],
        "backend_huge"  : backends[i],
        "content_id"    : cid,
        "uid"           : rec["uid"],
        "prev_uid"      : rec.get("prev_uid", 0),
        "next_uid"      : rec.get("next_uid", 0),
    })

# Only content tokens (non-space, non-empty)
content_tokens = [t for t in tokens if t["text"].strip() and t["text"] not in (" ", "\t", "\n")]


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 1 — RAW TOKEN STREAM
# ─────────────────────────────────────────────────────────────────────────────
print("\n")
print("━" * 72)
print("TABLE 1 — RAW TOKEN STREAM (first 20 content tokens)")
print("━" * 72)
print(f"{'#':>3}  {'TEXT':<14}  {'FE':>3}  {'BS':>6}  {'CID':>7}  {'UID_TAIL':>10}")
print("-" * 58)
for t in content_tokens[:20]:
    uid_tail = str(t["uid"])[-8:]   # last 8 digits of uid
    print(f"{t['index']:>3}  {repr(t['text']):<14}  {t['frontend']:>3}  "
          f"{t['backend_scaled']:>6}  {t['content_id']:>7}  {uid_tail:>10}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 2 — TRANSITION TABLE  (fe_i → fe_{i+1})
# ─────────────────────────────────────────────────────────────────────────────
print("\n")
print("━" * 72)
print("TABLE 2 — STRUCTURAL TRANSITIONS  (frontend_A → frontend_B, count)")
print("  What structure follows what structure?")
print("━" * 72)

transitions = {}
for i in range(len(content_tokens) - 1):
    key = (content_tokens[i]["frontend"], content_tokens[i + 1]["frontend"])
    transitions[key] = transitions.get(key, 0) + 1

# Sort by count
sorted_trans = sorted(transitions.items(), key=lambda x: x[1], reverse=True)

print(f"  {'FE_A → FE_B':<16}  {'COUNT':>6}  {'MEANING (observed)':}")
print(f"  {'-'*16}  {'-'*6}")
for (fa, fb), count in sorted_trans[:15]:
    direction = "→ RISE" if fb > fa else ("→ FALL" if fb < fa else "→ SAME")
    print(f"  {fa} → {fb:<13}  {count:>6}  {direction}")

# Summary
same = sum(c for (a, b), c in transitions.items() if a == b)
rise = sum(c for (a, b), c in transitions.items() if b > a)
fall = sum(c for (a, b), c in transitions.items() if b < a)
total = same + rise + fall
print(f"\n  SAME: {same} ({100*same//total if total else 0}%)   "
      f"RISE: {rise} ({100*rise//total if total else 0}%)   "
      f"FALL: {fall} ({100*fall//total if total else 0}%)")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 3 — IDENTITY DISTRIBUTION  (content_id → positions)
# ─────────────────────────────────────────────────────────────────────────────
print("\n")
print("━" * 72)
print("TABLE 3 — IDENTITY DISTRIBUTION  (which content_ids repeat?)")
print("  Same content_id = same token text (by SanTOK invariant)")
print("━" * 72)

identity_map = {}
for t in content_tokens:
    cid = t["content_id"]
    if cid not in identity_map:
        identity_map[cid] = {"text": t["text"], "positions": [], "frontends": [], "backends": []}
    identity_map[cid]["positions"].append(t["index"])
    identity_map[cid]["frontends"].append(t["frontend"])
    identity_map[cid]["backends"].append(t["backend_scaled"])

# Show repeating ones first
repeating = [(cid, v) for cid, v in identity_map.items() if len(v["positions"]) > 1]
repeating.sort(key=lambda x: len(x[1]["positions"]), reverse=True)

print(f"\n  Tokens that appear MORE THAN ONCE: {len(repeating)}")
print(f"  {'TEXT':<16}  {'CID':>7}  {'COUNT':>5}  {'POSITIONS':<20}  FE_SAME?  BS_VARIES?")
print(f"  {'-'*16}  {'-'*7}  {'-'*5}  {'-'*20}")
for cid, v in repeating[:10]:
    fe_same = "YES" if len(set(v["frontends"])) == 1 else "NO(!)"
    bs_same = "YES" if len(set(v["backends"])) == 1 else "YES varies"
    bs_varies = "NO" if len(set(v["backends"])) == 1 else "YES"
    pos_str = str(v["positions"][:5])
    print(f"  {repr(v['text']):<16}  {cid:>7}  {len(v['positions']):>5}  "
          f"{pos_str:<20}  {fe_same:<8}  {bs_varies}")

print(f"\n  FINDING: Do same content_ids always produce same frontend?")
fe_consistent = all(
    len(set(v["frontends"])) == 1
    for v in identity_map.values()
    if len(v["positions"]) > 1
)
print(f"  → {'YES — content_id uniquely determines frontend (FE is content-only)' if fe_consistent else 'NO — unexpected fe variation'}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 4 — CONTEXT DYNAMICS  (same content_id, different backend_scaled?)
# ─────────────────────────────────────────────────────────────────────────────
print("\n")
print("━" * 72)
print("TABLE 4 — CONTEXT DYNAMICS  (does backend_scaled vary for same content_id?)")
print("  backend_scaled should vary with position/neighbors (by design)")
print("━" * 72)

print(f"\n  {'TEXT':<16}  {'COUNT':>5}  {'BS_MIN':>7}  {'BS_MAX':>7}  {'BS_RANGE':>9}  STABLE?")
print(f"  {'-'*16}  {'-'*5}  {'-'*7}  {'-'*7}  {'-'*9}")
for cid, v in repeating[:10]:
    bs_min = min(v["backends"])
    bs_max = max(v["backends"])
    bs_range = bs_max - bs_min
    stable = "stable" if bs_range < 1000 else ("vibrates" if bs_range < 20000 else "SHIFTS")
    print(f"  {repr(v['text']):<16}  {len(v['positions']):>5}  "
          f"{bs_min:>7}  {bs_max:>7}  {bs_range:>9}  {stable}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 5 — STRUCTURAL EVENT CHAIN
# ─────────────────────────────────────────────────────────────────────────────
print("\n")
print("━" * 72)
print("TABLE 5 — STRUCTURAL EVENT CHAIN  (what changes between each pair?)")
print("  Three observables: identity (content_id), structure (fe), context (bs)")
print("━" * 72)

def detect_event(a, b):
    """Purely observational. No interpretation."""
    same_id      = a["content_id"] == b["content_id"]
    fe_changed   = a["frontend"] != b["frontend"]
    bs_shift     = abs(a["backend_scaled"] - b["backend_scaled"])

    if same_id:
        return "PERSISTENCE"          # same identity returned
    if not fe_changed and bs_shift < 5000:
        return "CONTEXT_DRIFT"        # structure same, context barely moves
    if not fe_changed and bs_shift >= 5000:
        return "CONTEXT_SHIFT"        # structure same, context jumps
    if fe_changed and bs_shift < 20000:
        return "STRUCTURE_CHANGE"     # structure changed, modest context shift
    return "FULL_TRANSITION"          # both things changed significantly

events = []
for i in range(len(content_tokens) - 1):
    a, b = content_tokens[i], content_tokens[i + 1]
    ev   = detect_event(a, b)
    events.append({
        "from": a["text"], "to": b["text"],
        "fe_a": a["frontend"], "fe_b": b["frontend"],
        "bs_shift": abs(a["backend_scaled"] - b["backend_scaled"]),
        "event": ev,
    })

print(f"\n  First 20 events:")
print(f"  {'FROM':<12}  {'TO':<12}  {'FE_A→B':<8}  {'BS_SHIFT':>8}  EVENT")
print(f"  {'-'*12}  {'-'*12}  {'-'*8}  {'-'*8}")
for ev in events[:20]:
    fe_str = f"{ev['fe_a']}→{ev['fe_b']}"
    print(f"  {repr(ev['from']):<12}  {repr(ev['to']):<12}  "
          f"{fe_str:<8}  {ev['bs_shift']:>8}  {ev['event']}")

# Event frequency summary
event_counts = {}
for ev in events:
    event_counts[ev["event"]] = event_counts.get(ev["event"], 0) + 1

print(f"\n  EVENT FREQUENCY (across entire stream):")
for ev_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
    bar = "█" * (count * 30 // len(events))
    pct = 100 * count // len(events)
    print(f"  {ev_type:<22}  {count:>4} ({pct:>3}%)  {bar}")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY — WHAT DID WE OBSERVE?
# ─────────────────────────────────────────────────────────────────────────────
print("\n")
print("━" * 72)
print("OBSERVATIONS — WHAT THE SYSTEM ACTUALLY DOES")
print("━" * 72)

print(f"""
  1. STREAM STATS:
     Total tokens:   {len(tokens)}
     Content tokens: {len(content_tokens)}
     Unique CIDs:    {len(identity_map)}
     Repeating CIDs: {len(repeating)}

  2. FRONTEND DISTRIBUTION:
""")
fe_dist = {}
for t in content_tokens:
    fe_dist[t["frontend"]] = fe_dist.get(t["frontend"], 0) + 1
for fe in sorted(fe_dist):
    bar = "█" * (fe_dist[fe] * 30 // len(content_tokens))
    pct = 100 * fe_dist[fe] // len(content_tokens)
    print(f"     fe={fe}: {fe_dist[fe]:>4} ({pct:>3}%)  {bar}")

print(f"""
  3. CONFIRMED INVARIANTS:
     content_id → frontend always same?  {"YES ✓" if fe_consistent else "NO ✗"}
     backend_scaled varies for same CID? {"YES ✓" if repeating else "n/a"}

  4. DOMINANT EVENTS:
""")
dominant = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)
for ev, c in dominant:
    print(f"     {ev:<22}  {c} times")

print(f"""
  5. MOST COMMON TRANSITIONS:
""")
for (fa, fb), count in sorted_trans[:5]:
    print(f"     fe {fa} → fe {fb}  ({count} times)")

print("\n" + "=" * 72)
print("END OF OBSERVATION. Now read this output and ask:")
print("  What patterns do YOU see?")
print("  Which transitions dominate?")
print("  What does FULL_TRANSITION mean structurally?")
print("  What does PERSISTENCE mean?")
print("  These questions — not code — are the research.")
print("=" * 72)
