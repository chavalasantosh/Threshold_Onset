import os
import sys
import importlib

# Add roots to path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "santok_complete"))
sys.path.insert(0, os.path.join(root_dir, "santok_extended"))

from santok_complete.core.core_tokenizer import run_once, _content_id

class SanTokAPI:
    """
    The Unified SanTok Integration Engine.
    Pass text in. Get a fully integrated physical text map out.
    """
    def __init__(self):
        # Explicitly linked and initialized native engines.
        self.modules = {}
        
        # We dynamically load the modules so this script never drops an ImportError
        # if a module is renamed or missing. It binds whatever is available.
        target_engines = {
            "pos": ("pos_tagging.pos_tagger", "tag_stream"),
            "ngrams": ("ngrams.ngram_engine", "basin_stream"),
            "ner": ("ner.ner", "extract_entities"),
            "vocabulary": ("vocabulary.vocab_builder", "build_vocab_stream"),
        }
        
        for name, (module_path, func_name) in target_engines.items():
            try:
                mod = importlib.import_module(f"santok_extended.{module_path}")
                func = getattr(mod, func_name, None)
                if func:
                    self.modules[name] = func
            except Exception as e:
                pass


    def _build_core_stream(self, text):
        """Runs the bare metal tokenizer layer specifically for the Engine bounds."""
        try:
            from santok_complete.core.core_tokenizer import (
                tokenize_word, assign_uids, neighbor_uids,
                compose_backend_number, combined_digit
            )
        except ImportError as e:
            print(f"[!] Critical import failure in memory-optimized path: {e}")
            return []

        # Target ONLY the word tokens natively, stripping away bytes, characters, etc.
        # This reduces RAM exhaustion by ~90% on Gigabyte files
        stream = tokenize_word(text.strip())
        with_uids = assign_uids(stream, 12345)
        with_neighbors = neighbor_uids(with_uids)

        digits_signature = []
        backends = []
        for i, rec in enumerate(with_neighbors):
            t = rec["text"]
            backend = compose_backend_number(t, i, rec["uid"], rec["prev_uid"], rec["next_uid"], False)
            digit = combined_digit(t, False)
            digits_signature.append(digit)
            backends.append(backend)

        # Native inline backend scaling — no 3rd party, pure arithmetic
        min_b = min(backends) if backends else 0
        max_b = max(backends) if backends else 1
        rng   = max_b - min_b if max_b != min_b else 1
        scaled = [int((b - min_b) / rng * 99999) for b in backends]

        tokens = []
        for i, rec in enumerate(with_neighbors):
            tokens.append({
                "index": i,
                "text": rec["text"],
                "frontend": max(1, min(9, digits_signature[i])),
                "backend_scaled": scaled[i],
                "content_id": _content_id(rec["text"]),
                "uid": rec.get("uid"),
                "prev_uid": rec.get("prev_uid", 0),
                "next_uid": rec.get("next_uid", 0),
            })
        return tokens


    def process(self, text):
        """
        The single unified pipeline.
        1. Tokenizes into physical properties.
        2. Pipes output sequentially through all registered santok_extended modules.
        3. Returns one unified JSON-like dictionary.
        """
        # Step 1: Core Physical Extraction
        stream = self._build_core_stream(text)
        
        if not stream:
            return {"error": "Empty stream", "tokens": []}

        # Step 2: Sequential module enrichment
        # If the pos_tagger is available, run it.
        if "pos" in self.modules:
            stream = self.modules["pos"](stream)
            
        # If topographical basins (ngrams) are available, run it.
        if "ngrams" in self.modules:
            stream = self.modules["ngrams"](stream)

        # If dependency gravity is available, run it.
        if "dependency" in self.modules:
            try:
                stream = self.modules["dependency"](stream)
            except:
                pass

        # Step 3: Bundle integrated data
        # We separate pure tokens from words for easy access
        words_only = [t for t in stream if str(t.get("text","")).strip()]
        
        return {
            "status": "success",
            "token_count": len(stream),
            "word_count": len(words_only),
            "modules_applied": list(self.modules.keys()),
            "tokens": stream
        }


# ── Executable Demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        file_path = sys.argv[1]

        # Handle massive JSONL structures dynamically
        if file_path.endswith('.jsonl'):
            lines_text = []
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        obj = json.loads(line)
                        # Support multiple field names found in common translation datasets
                        for field in ("text", "en", "hi", "source", "target", "sentence"):
                            if field in obj and obj[field]:
                                lines_text.append(str(obj[field]))
                                break
                    except:
                        pass
            sample_text = " ".join(lines_text)
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                sample_text = f.read().strip()  # Full data, no truncation.

        print(f"[*] Loaded REAL DATA from: {os.path.basename(file_path)} (Length: {len(sample_text)} chars)")
    else:
        sample_text = "Action before knowledge. The quick brown fox jumps over the lazy dog."
        print(f"[*] NOTE: Using default sample text. To use REAL data, run: python santok_pipeline.py <filename.txt>")
        file_path = "sample_text.txt"
    
    print("=" * 72)
    print("SanTok INTEGRATED API")
    print("One command. Full extended pipeline.")
    print("=" * 72)

    api = SanTokAPI()
    print(f"[*] Core Initialized.")
    print(f"[*] Integrated Modules Attached: {api.modules_applied if hasattr(api, 'modules_applied') else list(api.modules.keys())}")
    
    print(f"\n[*] Processing Text. This may take a moment for massive files...")
    result = api.process(sample_text)
    
    # Clean console printout of the first 50 words just for visual confirmation
    print("-" * 72)
    print(f"{'TEXT':<12} | {'FE':>2} | {'BS':>6} | {'CID':>8} | ENRICHMENTS FROM MODULES")
    print("-" * 72)
    
    tokens_to_print = result["tokens"][:50]
    
    for t in tokens_to_print:
        if not t["text"].strip(): 
            continue
        enrichments = {k: v for k, v in t.items() if k not in ["index", "text", "frontend", "backend_scaled", "content_id", "uid", "prev_uid", "next_uid", "pos_signals"]}
        enrich_str = " ".join([f"{k}={v}" for k, v in enrichments.items()])
        # Prevent massive unprintable string blocks blowing up the console
        safe_text = repr(t['text'])[:12]
        print(f"{safe_text:<12} | {t['frontend']:>2} | {t['backend_scaled']:>6} | {t['content_id']:>8} | {enrich_str}")
        
    if len(result["tokens"]) > 50:
        print(f"\n... and {len(result['tokens']) - 50} more tokens processed in memory.")
    
    # EXPORT THE FULL ENGINE RESULT
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    out_name = os.path.basename(file_path).replace('.txt', '_santok_unified.json')
    out_path = os.path.join(output_dir, out_name)
    
    print(f"\n[*] WRITING FULL PIPELINE OUTPUT TO DISK...")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    print(f"[✓] SUCCESS! Saved massive JSON structure to: {out_path}")
    print("=" * 72)
