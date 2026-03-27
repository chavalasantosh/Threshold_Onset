# SanTOK - Text Tokenization System

A comprehensive, pure-Python text tokenization system with multiple tokenization methods and statistical analysis features.

## Features

- **Multiple Tokenization Methods**: whitespace, word, character, grammar, subword, byte
- **Mathematical Analysis**: Frontend digits, statistical features, weighted sums
- **Parallel Processing**: Multi-threaded and multi-process support for large texts
- **Multi-language Support**: Automatic language detection for CJK, Arabic, Cyrillic, Hebrew, Thai, Devanagari
- **No External Dependencies**: Pure Python implementation (except for optional parallel processing)

## Installation

```bash
pip install -e .
```

Or use directly by adding the package to your Python path:

```python
import sys
sys.path.insert(0, '/path/to/santok_complete')
from santok_complete import TextTokenizationEngine
```

## Quick Start

```python
from santok_complete import TextTokenizationEngine

# Create tokenization engine
engine = TextTokenizationEngine(
    random_seed=12345,
    normalize_case=True,
    remove_punctuation=False
)

# Tokenize text
result = engine.tokenize("Hello World! This is a test.", method="whitespace")

print(f"Tokens: {result['tokens']}")
print(f"Frontend Digits: {result['frontend_digits']}")
print(f"Features: {result['features']}")
```

## Available Tokenization Methods

- `whitespace` - Split by whitespace delimiters
- `word` - Word boundary tokenization (alphabetic characters)
- `character` - Character-level tokenization
- `subword` - Subword tokenization with configurable chunk size
- `grammar` - Grammar-aware tokenization (words and punctuation separate)
- `byte` - Byte-level tokenization

## Core Tokenization Functions

```python
from santok_complete import (
    tokenize_space,
    tokenize_word,
    tokenize_char,
    tokenize_grammar,
    tokenize_subword,
    tokenize_text,
    TextTokenizer
)

# Direct function calls
tokens = tokenize_space("Hello World")
tokens = tokenize_word("Hello, World!")
tokens = tokenize_char("ABC")

# Using TextTokenizer class
tokenizer = TextTokenizer(seed=42, embedding_bit=False)
tokens = tokenizer.tokenize("Hello World", method="word")
```

## Advanced Usage

### Multiple Tokenization Methods

```python
engine = TextTokenizationEngine()
analysis = engine.analyze_text("Hello World", methods=["whitespace", "word", "character"])
```

### Parallel Processing

```python
from santok_complete.core.parallel_tokenizer import tokenize_parallel_threaded

# Tokenize large text with parallel processing
tokens = tokenize_parallel_threaded(large_text, tokenizer_type="word", max_workers=4)
```

### Multi-language Tokenization

```python
from santok_complete import tokenize_text

# Automatic language detection
tokens = tokenize_text("Hello 世界", tokenizer_type="word", language=None)

# Manual language specification
tokens = tokenize_text("你好世界", tokenizer_type="word", language="cjk")
```

## Project Structure

```
santok_complete/
├── __init__.py              # Package initialization
├── core/                    # Core tokenization engines
│   ├── base_tokenizer.py    # Base tokenization functions
│   ├── core_tokenizer.py    # Full tokenization system
│   ├── parallel_tokenizer.py # Parallel processing
│   └── santok_engine.py     # TextTokenizationEngine class
├── santok/                  # Alternative tokenization implementation
│   ├── santok.py            # TextTokenizationEngine implementation
│   ├── cli.py               # Command-line interface
│   └── utils/               # Utility modules
└── examples/                # Example scripts
```

## Requirements

- Python 3.7+
- Standard library only (no external dependencies required)

Optional for parallel processing:
- `concurrent.futures` (included in Python 3.2+)

## License

Copyright (c) 2024 Santosh Chavala

## Author

Santosh Chavala
