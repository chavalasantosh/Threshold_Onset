"""
SanTOK Extended — Sequence Generator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Converts the santok_pipeline.py JSON output into integer sequences
ready for model training.

Pipeline:
  1. Load unified JSON (from santok_pipeline.py)
  2. Split into sentences (sentence_splitter.py)
  3. Filter stop words (stop_word_filter.py)
  4. Build vocabulary (vocab_builder.py)
  5. Convert each sentence → list of content_ids
  6. Save as sequences.json

content_id IS the token integer (Law 3).
No encoding step. No tokenization step. No mapping table.

Output format:
  {
    "vocab_size": int,
    "total_sequences": int,
    "sequences": [[cid, cid, cid, ...], ...]
  }
"""

import json
import os
import sys

# Add parent path so modules import cleanly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_tokenizer.sentence_splitter import split_sentences
from stopwords.stop_word_filter import filter_stops, detect_poles
from vocabulary.vocab_builder import build_vocab, cid_to_index


def generate_sequences(
    tokens,
    min_seq_len=3,
    max_seq_len=64,
    min_vocab_freq=2,
    filter_stop_words=True,
):
    """
    Full pipeline: tokens → training sequences.

    Input:  list of SanTOK token dicts
    Output: dict with vocab and sequences

    Steps:
      1. Detect poles from stream (Law 1)
      2. Split into sentences (Law 3 + Law 4)
      3. Optionally filter stop words (Law 1 + Law 3)
      4. Build vocabulary (Law 3 + Law 2)
      5. Convert sentences to cid sequences
      6. Filter by length
    """
    # Step 1: detect poles
    poles = detect_poles(tokens)

    # Step 2: split sentences
    sentences = split_sentences(tokens)

    # Step 3: optionally filter stops per sentence
    if filter_stop_words:
        sentences = [filter_stops(sent, poles) for sent in sentences]

    # Step 4: flatten all tokens for vocab building
    all_tokens = [t for sent in sentences for t in sent]
    vocab = build_vocab(all_tokens, min_freq=min_vocab_freq)
    mapping = cid_to_index(vocab)

    # Step 5: convert to integer sequences
    sequences = []
    for sent in sentences:
        seq = []
        for tok in sent:
            cid = int(tok.get("content_id", 0))
            if cid in mapping:
                seq.append(mapping[cid])
        if min_seq_len <= len(seq) <= max_seq_len:
            sequences.append(seq)

    return {
        "vocab_size": len(vocab) + 1,   # +1 for padding index 0
        "total_sequences": len(sequences),
        "poles_detected": sorted(poles),
        "vocab": {str(cid): v for cid, v in vocab.items()},
        "sequences": sequences,
    }


def generate_from_json(input_path, output_path, **kwargs):
    """
    Load santok_pipeline.py output JSON, generate sequences, save.

    input_path:  path to mahabharata_..._santok_unified.json
    output_path: path to write sequences.json
    """
    print(f"[*] Loading: {input_path}")
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    tokens = data.get("tokens", [])
    print(f"[*] Tokens loaded: {len(tokens):,}")

    result = generate_sequences(tokens, **kwargs)

    print(f"[*] Vocab size:      {result['vocab_size']:,}")
    print(f"[*] Sequences:       {result['total_sequences']:,}")
    print(f"[*] Poles detected:  fe={result['poles_detected']}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f)

    print(f"[✓] Saved: {output_path}")
    return result


def demo():
    """Run on embedded sample data."""
    sample = [
        {"text": "Action",    "frontend": 7, "backend_scaled": 13461,  "content_id": 10310},
        {"text": "before",    "frontend": 8, "backend_scaled": 10970,  "content_id": 24365},
        {"text": "knowledge", "frontend": 1, "backend_scaled": 20599,  "content_id": 102258},
        {"text": ".",         "frontend": 7, "backend_scaled": 61016,  "content_id": 1908},
        {"text": "The",       "frontend": 1, "backend_scaled": 42111,  "content_id": 128727},
        {"text": "quick",     "frontend": 2, "backend_scaled": 94056,  "content_id": 29583},
        {"text": "brown",     "frontend": 3, "backend_scaled": 3864,   "content_id": 56274},
        {"text": "fox",       "frontend": 4, "backend_scaled": 89586,  "content_id": 26790},
        {"text": "jumps",     "frontend": 1, "backend_scaled": 94188,  "content_id": 4205},
        {"text": "over",      "frontend": 5, "backend_scaled": 31123,  "content_id": 16460},
        {"text": "the",       "frontend": 2, "backend_scaled": 99016,  "content_id": 125905},
        {"text": "lazy",      "frontend": 9, "backend_scaled": 35365,  "content_id": 39107},
        {"text": "dog",       "frontend": 5, "backend_scaled": 87064,  "content_id": 134410},
        {"text": ".",         "frontend": 7, "backend_scaled": 49554,  "content_id": 1908},
        {"text": "Tokens",    "frontend": 9, "backend_scaled": 14680,  "content_id": 123596},
        {"text": "become",    "frontend": 1, "backend_scaled": 66130,  "content_id": 59217},
        {"text": "structural","frontend": 4, "backend_scaled": 89193,  "content_id": 145320},
        {"text": "residues",  "frontend": 9, "backend_scaled": 79019,  "content_id": 37242},
        {"text": "in",        "frontend": 6, "backend_scaled": 51551,  "content_id": 127366},
        {"text": "the",       "frontend": 2, "backend_scaled": 16084,  "content_id": 125905},
        {"text": "digital",   "frontend": 5, "backend_scaled": 88309,  "content_id": 128969},
        {"text": "root",      "frontend": 3, "backend_scaled": 63819,  "content_id": 143200},
        {"text": "space",     "frontend": 8, "backend_scaled": 44616,  "content_id": 92095},
        {"text": ".",         "frontend": 7, "backend_scaled": 19498,  "content_id": 1908},
    ]

    result = generate_sequences(sample, min_seq_len=2, min_vocab_freq=1)

    print("=" * 55)
    print("SanTOK SEQUENCE GENERATOR — DEMO")
    print("=" * 55)
    print(f"Vocab size:     {result['vocab_size']}")
    print(f"Sequences:      {result['total_sequences']}")
    print(f"Poles:          fe={result['poles_detected']}")
    print()
    print("SEQUENCES (cid index lists for model training):")
    for i, seq in enumerate(result["sequences"]):
        print(f"  [{i+1}] {seq}")
    print("=" * 55)
    print()
    print("TO GENERATE FROM REAL DATA:")
    print("  from sequence_generator import generate_from_json")
    print("  generate_from_json(")
    print("    'output/mahabharata_ganguli_1_santok_unified.json',")
    print("    'output/sequences.json'")
    print("  )")


if __name__ == "__main__":
    demo()
