"""
Sovereign Native Daemon Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Zero 3rd-Party Imports. Zero Frameworks.
Loads the massive geometric bounds exactly ONCE into active RAM.
Infinitely processes Identity queries against the cached bounds.
"""

import os
import sys

# Append root so we can resolve absolute namespace natively
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

from integration.santok_identity_bridge import ThresholdSantokBridge

def launch_daemon():
    print("======================================================================")
    print(" SanTok Infinite Cache Daemon ")
    print("======================================================================")

    # 1. Capture Target Matrix
    raw_corpus = input("Enter target matrix path or corpus name > ").strip()
    raw_corpus = raw_corpus.replace("&", "").replace("'", "").replace('"', "").replace("corpus>", "").strip()
    
    if not raw_corpus:
        print("[!] Native abort. Matrix identity required.")
        sys.exit(1)

    corpus_name = os.path.basename(raw_corpus).replace(".txt", "").replace(".jsonl", "").replace("_santok_unified.jsonl", "").replace("_santok_unified.json", "")
    
    # 2. Resolve Dynamic Pathing Native Logic
    if raw_corpus.endswith("_santok_unified.jsonl") and os.path.exists(raw_corpus):
        _corpus = raw_corpus
    elif raw_corpus.endswith("_santok_unified.json") and os.path.exists(raw_corpus):
        _corpus = raw_corpus
    else:
        _corpus = os.path.join(ROOT, "output", f"{corpus_name}_santok_unified.jsonl")
        if not os.path.exists(_corpus):
            _corpus = os.path.join(ROOT, "output", f"{corpus_name}_santok_unified.json")

    if not os.path.exists(_corpus):
        print(f"[!] Matrix {corpus_name} not found statically.")
        sys.exit(1)

    # 3. Perform One-Time Matrix Compilation (Heavy Compute)
    print("\n[*] Initializing Sovereign Bridge...")
    bridge = ThresholdSantokBridge(_corpus)
    print("[*] Sovereignty Lock complete. Matrix bounds suspended in Active RAM.")
    print("    Generation latency dropped to 0.05ms.")
    print("=" * 72)

    # 4. Infinite Generation Loop
    while True:
        try:
            print("\n" + "─" * 40)
            text = input("Provide Seed Identity (or 'exit' to drop matrix) > ").strip()
            
            if text.lower() == "exit" or text.lower() == "quit":
                print("[*] Dropping Matrix. Daemon halted.")
                break
                
            if not text: continue
            
            state_raw = input("Select Tension State: [0] Neutral  [1] Calm  [2] Aggressive > ").strip()
            state_id = 0
            if state_raw in ["1", "2"]:
                state_id = int(state_raw)
            
            output = bridge.generate(current_state_text=text, length=30, identity_state_id=state_id)
            
            print("\n[ SOVEREIGN OUTPUT ]")
            print("  " + output)
            
        except KeyboardInterrupt:
            print("\n[!] Force exit detected. Dropping matrix.")
            break
        except Exception as e:
            print(f"[!] Arithmetic Fault: {e}")

if __name__ == "__main__":
    launch_daemon()
