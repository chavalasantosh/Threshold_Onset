"""
SanTOK Extended — Role Engine Stress Test
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Test across different sentence structures
2. Test same token across different contexts
3. Edge cases

Prove that poles and constraints hold empirically.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "santok_complete"))
from core.core_tokenizer import run_once, _content_id

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "santok_extended", "mechanics"))
from role_engine import assign_roles, extract_role_summary

def get_tokens(text):
    result = run_once(text.strip(), seed=12345, embedding_bit=False)
    sd = result.get("word", result.get("space"))
    records = sd["records"]
    scaled = sd["scaled"]
    digits = sd["digits"]

    tokens = []
    for i, rec in enumerate(records):
        tokens.append({
            "index": i, "text": rec["text"],
            "frontend": max(1, min(9, digits[i])), 
            "backend_scaled": scaled[i],
            "content_id": _content_id(rec["text"]),
            "uid": rec["uid"],
        })
    return tokens


def test_different_contexts():
    print("=" * 72)
    print("TEST 1 & 2: CONTEXT STABILITY (SAME TOKEN, DIFFERENT CONTEXTS)")
    print("=" * 72)
    
    text_corpus = """
    Every man runs.
    Every system breaks.
    Every single time they try.
    I watch every move.
    """
    
    tokens = get_tokens(text_corpus)
    tagged = assign_roles(tokens)
    
    content_tagged = [t for t in tagged if t["text"].strip()]
    
    print(f"Target: 'Every' / 'every'")
    for t in content_tagged:
        if t["text"].lower() == "every":
            print(f"Token: {t['text']:<6} | fe: {t['frontend']} | constraints: {t.get('structural_constraints')}")


def test_edge_cases():
    print("\n" + "=" * 72)
    print("TEST 3: EDGE CASES (NUMBERS, COMMAS, REPETITIONS)")
    print("=" * 72)

    text_corpus = """
    Wait, wait, wait. 
    1 2 3 4 5 1 2 3.
    System crash... system failure... system reboot.
    """

    tokens = get_tokens(text_corpus)
    summary = extract_role_summary(tokens)
    tagged = assign_roles(tokens)

    print(f"Poles for Edge Case corpus: {summary['poles']}")
    
    content_tagged = [t for t in tagged if t["text"].strip()]
    for t in content_tagged:
        if t["text"].lower() in {"wait", "1", "system"}:
            print(f"Token: {t['text']:<6} | fe: {t['frontend']} | constraints: {t.get('structural_constraints')}")


if __name__ == "__main__":
    test_different_contexts()
    test_edge_cases()
