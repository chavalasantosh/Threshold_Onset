# Internal Modules: santok, santek, somaya

## Overview

This project uses **internal pip-installable modules** that are part of our project ecosystem:

- **santok**: Primary tokenization module
- **santek**: Additional tokenization/processing module
- **somaya**: Additional processing module

## Installation

```bash
pip install santok
pip install santok
pip install somaya
```

## Architecture

```
Traditional LLM:
Input → Embed → Attention → Logits → Sample → Output
              ↑ (learned, black box)

Your System:
Input → Structure → Constraints → Scores → Select → Output
                    ↑ (mechanical, auditable)
```

## Module Usage

### santok (Primary Tokenization)

The system uses `santok` for all tokenization operations:

```python
from santok import (
    tokenize_space,
    tokenize_word,
    tokenize_char,
    tokenize_grammar,
    tokenize_subword,
    tokenize_bytes
)
```

Or alternative import paths:

```python
from santok.core import (
    tokenize_space,
    tokenize_word,
    # ...
)

from santok import tokenize_text
```

### santek

(To be documented based on module structure)

### somaya

(To be documented based on module structure)

## Migration from santok_complete

All code has been updated to use pip-installed `santok` instead of local `santok_complete` directory.

## Files Updated

- `integration/run_complete.py` - Main integration file
- `integration/unified_system.py` - Unified system module
- `integration/main_complete.py` - Alternative main entry
- `integration/main_end_to_end.py` - End-to-end main
- `integration/continuation_observer.py` - Continuation observer

## Benefits

1. **Clean Dependencies**: Uses pip-installed packages
2. **Version Control**: Can pin versions in requirements
3. **Modularity**: Each module is independently installable
4. **Internal Ownership**: All modules are part of our project ecosystem
