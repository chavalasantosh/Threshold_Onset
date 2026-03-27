# Unified System: threshold_onset <-> santok

**कार्य (kārya) happens before ज्ञान (jñāna)**

## What This Is

A revolutionary unified system that combines:
- **santok**: Text tokenization (action/kārya)
- **threshold_onset**: Structure emergence (knowledge/jñāna)

**The Breakthrough:**
- Text tokens become **actions**
- Token patterns become **residues**
- Structure emerges **naturally** from token sequences
- Semantics emerge **automatically** from the structure

**NO embeddings. NO transformers. NO neural networks. NO BERT. NO sentence piece. NO backpropagation.**

Just: **Tokenization → Structure → Semantics (emergent)**

---

## Philosophy

### कार्य (kārya) happens before ज्ञान (jñāna)

**Action before Knowledge. Function before Meaning.**

In this unified system:
1. **Tokenization** (santok) = Action (कार्य)
2. **Structure Emergence** (threshold_onset) = Knowledge (ज्ञान)

The semantics don't need to be embedded or learned. They **emerge automatically** when you combine tokenization with structure emergence.

### Why This Works

Traditional AI approaches:
- Text → Embeddings → Neural Networks → Semantics

Our approach:
- Text → Tokens → Residues → Structure → Semantics (emergent)

The key insight: **Structure IS semantics**. When structure emerges from token patterns, semantics emerge with it. No need for embeddings or neural networks.

---

## How It Works

### Step 1: Tokenization (santok)
Text is tokenized using santok's tokenization methods:
- `whitespace`: Split by whitespace
- `word`: Word boundary tokenization
- `character`: Character-level tokenization
- `grammar`: Grammar-aware tokenization
- `subword`: Subword tokenization
- `byte`: Byte-level tokenization

### Step 2: Token-to-Residue Conversion
Tokens are converted to numeric residues (hash-based, opaque, no meaning):
- Each token → SHA256 hash → normalized float [0, 1)
- Phase 0 compliant: numeric, opaque, no labels, no interpretation

### Step 3: Structure Emergence (threshold_onset)
Residues flow through threshold_onset phases:

**Phase 0: THRESHOLD_ONSET**
- Tokens become actions
- Actions produce residues
- Repetition reveals survival

**Phase 1: SEGMENTATION**
- Boundaries detected in residue sequences
- Clusters form
- Patterns emerge

**Phase 2: IDENTITY**
- Persistent segments identified
- Repeatable units detected
- Identity hashes assigned (internal only)

**Phase 3: RELATION**
- Relations between identities mapped
- Graph structures form
- Relations persist and stabilize

**Phase 4: SYMBOL**
- Integer aliases assigned to identities and relations
- Pure aliasing layer (reversible, no new structure)

### Step 4: Semantics Emerge
Structure = Semantics. When structure emerges from token patterns, semantics emerge automatically.

---

## Usage

### Basic Usage

```python
from unified_system import process_text_through_phases

text = """
कार्य (kārya) happens before ज्ञान (jñāna)
Action before knowledge.
Structure emerges before language exists.
"""

results = process_text_through_phases(
    text=text,
    tokenization_method="word",  # or "whitespace", "character", "grammar", "subword"
    num_runs=5  # Number of runs for multi-run persistence testing
)

# Results contain:
# - tokens: List of tokens from tokenization
# - residues: Residue sequences from Phase 0
# - phase1: Segmentation metrics
# - phase2: Identity metrics
# - phase3: Relation metrics
# - phase4: Symbol aliases
```

### Advanced Usage

```python
from unified_system import tokenize_text_to_actions, TokenAction

# Custom tokenization
action, tokens = tokenize_text_to_actions(
    text="Your text here",
    tokenization_method="grammar"
)

# Use action in threshold_onset phases directly
from threshold_onset.phase0.phase0 import phase0

steps = len(tokens) * 2
residues = []
for residue, count, step_count in phase0([action], steps=steps):
    residues.append(residue)
```

---

## What Makes This Different

### Traditional AI Approach
```
Text → Embeddings (BERT/Word2Vec) → Neural Network → Semantics
```
- Requires pre-trained embeddings
- Requires neural network training
- Requires backpropagation
- Requires large datasets
- Semantics are "learned"

### Our Unified Approach
```
Text → Tokens → Residues → Structure → Semantics (emergent)
```
- No embeddings needed
- No neural networks needed
- No training needed
- No backpropagation needed
- Works with any text
- Semantics **emerge** from structure

---

## Key Principles

1. **Action Before Knowledge**: Tokenization (action) happens before structure (knowledge)
2. **Structure = Semantics**: When structure emerges, semantics emerge with it
3. **No Embeddings**: Tokens are converted to residues (hash-based), not embeddings
4. **No Neural Networks**: Structure emerges through repetition and persistence, not learning
5. **Pure Python**: Standard library only (except optional dependencies)

---

## Examples

### Example 1: Simple Text

```python
text = "Hello world. Hello again."
results = process_text_through_phases(text, tokenization_method="word")
# Structure emerges from repeated "Hello"
# Relations form between "Hello" and "world", "Hello" and "again"
# Semantics emerge: "Hello" is related to both "world" and "again"
```

### Example 2: Multilingual Text

```python
text = "कार्य (kārya) happens before ज्ञान (jñāna)"
results = process_text_through_phases(text, tokenization_method="word")
# Structure emerges from token patterns
# Multilingual tokens are treated equally (hash-based residues)
# Semantics emerge from the structure
```

### Example 3: Character-Level Analysis

```python
text = "Structure emerges naturally"
results = process_text_through_phases(text, tokenization_method="character")
# Character-level tokens reveal fine-grained patterns
# Structure emerges at character level
# Semantics emerge from character patterns
```

---

## Technical Details

### Token-to-Residue Conversion

Tokens are converted to residues using SHA256 hashing:
1. Token string → UTF-8 bytes
2. Bytes → SHA256 hash
3. First 8 hex characters → 32-bit integer
4. Integer modulo 10000 → normalized float [0, 1)

This ensures:
- Phase 0 compliance (numeric, opaque, no meaning)
- Deterministic (same token → same residue)
- Uniform distribution (hash-based)
- No external dependencies (standard library only)

### Multi-Run Persistence

The system runs multiple times to detect persistence:
- Same tokens → same residues (deterministic)
- Repeated patterns → persistent segments
- Persistent segments → identities
- Persistent identities → relations
- Relations → semantics (emergent)

---

## Why This Is Revolutionary

1. **No Embeddings**: Semantics emerge from structure, not embeddings
2. **No Training**: Structure emerges through repetition, not learning
3. **No Neural Networks**: Pure algorithmic structure emergence
4. **Works with Any Text**: No pre-training or fine-tuning needed
5. **Multilingual**: Works with any language (tokenization handles it)
6. **Interpretable**: Structure is explicit, not hidden in weights

---

## Future Directions

This unified system opens new possibilities:

1. **Text Understanding**: Structure reveals meaning without embeddings
2. **Pattern Discovery**: Repeated patterns reveal semantics
3. **Relation Mapping**: Relations between tokens reveal structure
4. **Semantic Emergence**: Semantics emerge from structure automatically
5. **Language-Agnostic**: Works with any language (tokenization handles it)

---

## Credits

- **threshold_onset**: Structure emergence system (Phases 0-4)
- **santok**: Text tokenization system
- **Unified System**: Integration of both systems

**Philosophy**: कार्य (kārya) happens before ज्ञान (jñāna)

---

## License

Same as threshold_onset and santok projects.
