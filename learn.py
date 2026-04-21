"""
Sovereign Language Brain — Layer 2 Training (Learning Phase)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trains the THRESHOLD_ONSET CorpusState (Identity graph) and generates the Layer 4 surface map.
The result is permanent structural memory of the English language.

This file MUST be run to build the Sovereign Language Brain.
"""

import os
import sys
import csv
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from integration.run_complete import (
    PipelineConfig, _run_structure_emergence, 
    PhaseTimings, TUIRenderer, build_surface_mapping, tokenize_text
)
from threshold_onset.corpus_state import CorpusState

BRAIN_DIR = os.path.join(ROOT, "output", "brain")
os.makedirs(BRAIN_DIR, exist_ok=True)

CORPUS_STATE_PATH = os.path.join(ROOT, "output", "corpus_state.json")
HASH_TO_TEXT_PATH = os.path.join(BRAIN_DIR, "layer4_hash_to_text.json")
SURFACE_PATH = os.path.join(BRAIN_DIR, "layer4_surface.json")
ESCAPE_MAP_PATH = os.path.join(BRAIN_DIR, "layer3_escape_map.json")
MANIFEST_PATH = os.path.join(BRAIN_DIR, "sovereign_brain.json")

def load_checkpoint():
    if os.path.exists(CORPUS_STATE_PATH):
        cs = CorpusState.load(CORPUS_STATE_PATH)
    else:
        cs = CorpusState()
    
    hash_to_text = {}
    if os.path.exists(HASH_TO_TEXT_PATH):
        try:
            with open(HASH_TO_TEXT_PATH, "r", encoding="utf-8") as f:
                hash_to_text = json.load(f)
        except Exception:
            pass
            
    return cs, hash_to_text


def build_escape_map(cs, hash_to_text):
    print("\n[*] Building Layer 3 Escape Map from structural edges...")
    escape_traffic = {}
    
    # Init escape_traffic for all words.
    for h in hash_to_text:
        escape_traffic[hash_to_text[h]] = {}

    for edge_str, weight in cs.edge_weights.items():
        # handle literal string evaluations if edge_weights is serialized as a string keys
        if isinstance(edge_str, str):
            try:
                import ast
                edge = ast.literal_eval(edge_str)
            except Exception:
                continue
        else:
            edge = edge_str
            
        h_a, h_b = edge
        if h_a in hash_to_text and h_b in hash_to_text:
            wa = hash_to_text[h_a]
            wb = hash_to_text[h_b]
            # Accumulate traffic bidirectionally.
            if wb not in escape_traffic.get(wa, {}):
                escape_traffic.setdefault(wa, {})[wb] = 0.0
            escape_traffic[wa][wb] += float(weight)
            
            if wa not in escape_traffic.get(wb, {}):
                escape_traffic.setdefault(wb, {})[wa] = 0.0
            escape_traffic[wb][wa] += float(weight)
            
    escape_map = {}
    for word, connections in escape_traffic.items():
        if not connections:
            continue
        
        sorted_targets = sorted(connections.items(), key=lambda x: x[1], reverse=True)
        top_targets = [k for k, _ in sorted_targets[:3]]
        
        total_w = sum(connections.values())
        top_w = sorted_targets[0][1] if sorted_targets else 0
        
        concentration = top_w / total_w if total_w > 0 else 1.0
        tension_class = "Aggressive" if concentration >= 0.75 else "Calm" if concentration <= 0.25 else "Neutral"
        
        escape_map[word] = {
            "top_escape": top_targets[0] if top_targets else word,
            "escape_targets": top_targets,
            "escape_concentration": concentration,
            "tension_class": tension_class
        }
    
    return escape_map


def main():
    print("=" * 70)
    print("  SOVEREIGN LANGUAGE BRAIN — Layer 2 Training")
    print("  Mode: Hybrid Context (Word + First 14 Definition Tokens)")
    print("=" * 70)
    
    cfg = PipelineConfig.from_project()
    cfg.show_tui = False
    
    dictionary_path = os.path.join(ROOT, "data", "english_sample_dictionary.csv")
    if not os.path.exists(dictionary_path):
        print(f"[!] Dictionary not found at {dictionary_path}")
        return
        
    cs, hash_to_text = load_checkpoint()
    
    skip_lines = cs.doc_count
    
    lines_total = 124090 # General expectation based on WC of english_sample_dictionary.csv
    print(f"[*] Total entries to process: ~{lines_total}")
    if skip_lines > 0:
        print(f"[*] Resuming from checkpoint: Line {skip_lines}...")
    
    timings = PhaseTimings()
    tui = TUIRenderer(show_tui=False)
    
    csv.field_size_limit(sys.maxsize)
    
    with open(dictionary_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader, None)
        except StopIteration:
            pass
        
        for i, row in enumerate(reader):
            if i < skip_lines:
                continue
                
            if len(row) < 2:
                cs.doc_count += 1
                continue
                
            word, definition = row[0], row[1]
            # Learn WORD + Context
            raw_text = f"{word} {definition}"
            tokens = tokenize_text(raw_text, cfg.tokenization_method)
            
            chunk = tokens[:15] # Target 15-word structural chunk
            if len(chunk) < 3:
                cs.doc_count += 1
                continue
                
            try:
                (residue_seqs, p1, p2, p3, p4, tok_res, p0_runs) = _run_structure_emergence(
                    chunk, cfg, timings, tui
                )
                
                # Surface map extraction
                sym_to_tok = build_surface_mapping(
                    chunk, residue_seqs, p2, p4, tok_res
                )
                
                # Accumulate
                identity_hashes = p2.get("persistent_segment_hashes", set())
                edge_pairs = p3.get("graph_edges", set())
                
                sym_to_id = p4.get("symbol_to_identity", {})
                
                for sym, token in sym_to_tok.items():
                    # Handle symbol keys which may be int or str in python dict depending on JSON
                    h = sym_to_id.get(int(sym)) if str(sym).isdigit() else sym_to_id.get(sym)
                    if h:
                        cleaned = ''.join(c for c in token if c.isalnum() or c in "-'")
                        if cleaned:
                            hash_to_text[h] = cleaned.lower()
                
                cs.update(identity_hashes, edge_pairs)
                
            except Exception as e:
                # Safe skip in case of structure limits on rare phrases
                cs.doc_count += 1
            
            if cs.doc_count % 100 == 0:
                perc = (cs.doc_count / lines_total) * 100
                print(f"    [-] Learned {cs.doc_count} / {lines_total} chunks  ({perc:.1f}%) | Identities: {len(cs.identity_stability)} | Edges: {len(cs.edge_weights)}")
                
            if cs.doc_count % 500 == 0:
                # Checkpoint
                cs.save(CORPUS_STATE_PATH)
                with open(HASH_TO_TEXT_PATH, "w", encoding="utf-8") as out:
                    json.dump(hash_to_text, out, indent=2)
                
    # Final save
    cs.save(CORPUS_STATE_PATH)
    with open(HASH_TO_TEXT_PATH, "w", encoding="utf-8") as out:
        json.dump(hash_to_text, out, indent=2)
        
    print("\n[✓] Layer 2 Training Complete!")
    
    # ── Brain Post-Processing ─────────────────────────────────────────────────
    escape_map = build_escape_map(cs, hash_to_text)
    
    with open(ESCAPE_MAP_PATH, "w", encoding="utf-8") as out:
        json.dump(escape_map, out, indent=2)
    print(f"[✓] Layer 3 Escape Map generated: {len(escape_map)} entries.")
    
    # Build surface words (for fast lookup)
    word_to_hash = {}
    for h, w in hash_to_text.items():
        if w not in word_to_hash:
            word_to_hash[w] = h
            
    surface = {
        "hash_to_text": hash_to_text,
        "word_to_hash": word_to_hash
    }
    with open(SURFACE_PATH, "w", encoding="utf-8") as out:
        json.dump(surface, out, indent=2)
        
    # Manifest
    manifest = {
        "version": 2,
        "language": "english",
        "doc_count": cs.doc_count,
        "core_identities": len(cs.core_identities),
        "total_identities": len(cs.identity_stability),
        "total_edges": len(cs.edge_weights)
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as out:
        json.dump(manifest, out, indent=2)
        
    print("[✓] BRAIN MANIFEST SECURED.")
    print("Run `master_daemon.py` to use the Sovereign Language Brain.")

if __name__ == "__main__":
    main()
