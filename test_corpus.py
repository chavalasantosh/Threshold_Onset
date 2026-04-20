import os
import sys
import subprocess
from model.santok_engine import SantokEngine

def analyze_corpus(corpus_name):
    print("=" * 70)
    print(f"SanTOK NATIVE GENERALIZATION TEST: {corpus_name}")
    print("=" * 70)

    raw_path = os.path.join("data", "raw", "en", f"{corpus_name}.txt")
    json_path = os.path.join("output", f"{corpus_name}_santok_unified.json")

    if not os.path.exists(json_path):
        if not os.path.exists(raw_path):
            print(f"[!] Target text not found: {raw_path}")
            return
        
        print(f"[*] Native JSON mapping not found. Routing {corpus_name} through the structural pipeline...")
        # Force Unbuffered output to prevent hang
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        subprocess.run(["python", "santok_pipeline.py", raw_path], env=env)

    print(f"[*] Engine initializing topological matrix for {corpus_name}...")
    engine = SantokEngine(json_path)

    print(f"[*] Extracting 5 distinct structural sequences blindly:\n")
    for i in range(1, 6):
        print(f"--- RUN {i} ---")
        output = engine.generate(length=25)
        print(output)
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1].replace(".txt", "")
        analyze_corpus(target)
    else:
        print("[!] Pass a corpus filename (e.g. 'python test_corpus.py manusmriti_en')")
