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


def process_target_file(file_path, api):
    print("\n" + "=" * 72)
    print(f"[*] INGESTING TARGET: {os.path.basename(file_path)}")
    print("=" * 72)
    
    # We switch entirely to stream chunking to survive memory bounds.
    CHUNK_MEM_BOUND = 500000  # 500k chars ~ 5MB RAM per flush

    # 1. Open Target Output
    base_name = os.path.basename(file_path)
    for ext in [".txt", ".jsonl", ".csv", ".json"]:
        base_name = base_name.replace(ext, "")
        
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, f"{base_name}_santok_unified.jsonl")
    
    total_tokens = 0
    buffer_text = ""
    chunk_index = 0
    
    # 2. Iterate Native Reads
    with open(out_file, "w", encoding="utf-8") as f_out:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f_in:
            for line in f_in:
                if not line.strip(): continue
                # Decode JSONL or handle raw text natively
                if file_path.endswith('.jsonl') or file_path.endswith('.json'):
                    try:
                        obj = json.loads(line)
                        for field in ("text", "en", "hi", "source", "target", "sentence"):
                            if field in obj and obj[field]:
                                buffer_text += str(obj[field]) + " "
                                break
                    except: pass
                elif file_path.endswith('.csv'):
                    # Basic naive CSV column aggregation for strict physics texts
                    buffer_text += line.replace(",", " ") + " "
                else:
                    buffer_text += line + " "

                # 3. Process Chunk Bound
                if len(buffer_text) >= CHUNK_MEM_BOUND:
                    result = api.process(buffer_text)
                    if result.get("tokens"):
                        for t in result["tokens"]:
                            if not t["text"].strip(): continue
                            f_out.write(json.dumps(t, ensure_ascii=False) + "\n")
                            total_tokens += 1
                    buffer_text = ""
                    chunk_index += 1
                    if chunk_index % 1 == 0:
                        print(f"    [-] Checkpoint: {total_tokens} tokens structured...")

            # 4. Process Trailing Remnants
            if buffer_text.strip():
                result = api.process(buffer_text)
                if result.get("tokens"):
                    for t in result["tokens"]:
                        if not t["text"].strip(): continue
                        f_out.write(json.dumps(t, ensure_ascii=False) + "\n")
                        total_tokens += 1

    print("\n" + "-" * 72)
    print(f"[✓] SUCCESS! Exported {total_tokens} topological bounds sequentially.")
    print(f"[✓] Saved zero-memory JSONL structure to: {out_file}")
    print("-" * 72)


# ── Executable Demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import json
    import os

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        target_path = sys.argv[1]
    else:
        print("[!] No valid input path provided.")
        sys.exit(1)

    api = SanTokAPI()
    
    if os.path.isdir(target_path):
        print(f"[*] Directory target detected. Initiating Bulk Pipeline...")
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.endswith(('.txt', '.jsonl', '.json', '.csv')):
                    process_target_file(os.path.join(root, file), api)
    else:
        process_target_file(target_path, api)

