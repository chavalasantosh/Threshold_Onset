# Internal Module Mapping

## Your System Architecture

```
Traditional LLM:
Input → Embed → Attention → Logits → Sample → Output
              ↑ (learned, black box)

Your System:
Input → Structure → Constraints → Scores → Select → Output
                    ↑ (mechanical, auditable)
```

## Internal Modules

Your project uses **internal modules** owned by the project:

- **santok**: Primary tokenization module
- **santek**: Alternative/additional tokenization module  
- **somaya**: Additional processing module

## Current Implementation

The system currently uses `santok_complete` as the tokenization module, which contains:
- `santok_complete/core/core_tokenizer.py` - Core tokenization functions
- `santok_complete/santok/santok.py` - Alternative tokenization engine

## Module Paths

All imports should use the internal module structure:
- `santok` → `santok_complete` (current mapping)
- `santek` → (to be mapped)
- `somaya` → (to be mapped)

## Integration Points

The unified system (`run_complete.py`) uses:
- `tokenize_text()` function that imports from `santok_complete`
- This can be updated to use `santok`, `santek`, or `somaya` directly

## Next Steps

1. Map `santok_complete` → `santok` (internal name)
2. Identify `santek` module location
3. Identify `somaya` module location
4. Update all imports to use internal module names
