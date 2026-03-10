"""
SanTOK - Text Tokenization System
A comprehensive text tokenization system with mathematical analysis and statistical features
"""

__version__ = "1.0.0"
__author__ = "Santosh Chavala"
__email__ = "chavalasantosh@example.com"

# Core Tokenization
try:
    from .core.core_tokenizer import (
        tokenize_space,
        tokenize_word,
        tokenize_char,
        tokenize_grammar,
        tokenize_subword,
        TextTokenizer,
        TokenRecord,
    )
except ImportError:
    pass

try:
    from .core.santok_engine import TextTokenizationEngine, tokenize_text, analyze_text_comprehensive
except ImportError:
    pass

try:
    from .santok.santok import (
        TextTokenizationEngine as SanTOKEngine,
        tokenize_text as santok_tokenize_text,
        analyze_text_comprehensive as santok_analyze_text,
        generate_text_summary
    )
except ImportError:
    pass

__all__ = [
    # Core Tokenization
    'TextTokenizationEngine',
    'SanTOKEngine',
    'TextTokenizer',
    'TokenRecord',
    'tokenize_text',
    'tokenize_space',
    'tokenize_word',
    'tokenize_char',
    'tokenize_grammar',
    'tokenize_subword',
    'analyze_text_comprehensive',
    'santok_tokenize_text',
    'santok_analyze_text',
    'generate_text_summary',
]
