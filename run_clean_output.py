import sys
import os

# Add the original complete engine to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "santok_complete"))
from core.core_tokenizer import run_once, _content_id

def export_clean_signals(text: str):
    """
    No theories. No mechanics. No NLP.
    Just runs SanTok and outputs the clean 4 structural signals.
    """
    # 1. Run the core tokenizer
    result = run_once(text.strip(), seed=12345, embedding_bit=False)
    
    # 2. Extract stream data
    stream_data = result.get("word", result.get("space", {}))
    records = stream_data.get("records", [])
    scaled = stream_data.get("scaled", [])
    digits = stream_data.get("digits", [])
    
    if not records:
        print("No tokens processed.")
        return

    # 3. Print the absolute clean output
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"{'TOKEN_TEXT':<15} | {'FRONTEND':<8} | {'BACKEND_SCALED':<15} | {'CONTENT_ID':<15} | {'UID'}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for i, rec in enumerate(records):
        # Skip pure whitespace tokens to keep output totally clean
        if not str(rec.get("text", "")).strip():
            continue
            
        token_text = repr(rec["text"])
        frontend = max(1, min(9, digits[i]))
        backend_scaled = scaled[i]
        content_id = _content_id(rec["text"])
        uid = rec["uid"]
        
        print(f"{token_text:<15} | {frontend:<8} | {backend_scaled:<15} | {content_id:<15} | {uid}")
        
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if __name__ == "__main__":
    sample = "Action before knowledge. The quick brown fox jumps."
    
    # Check if a file was provided as an argument
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        with open(sys.argv[1], 'r', encoding='utf-8', errors='ignore') as f:
            sample = f.read()[:2000] # Limiting to 2000 chars for clean console output
            
    export_clean_signals(sample)
