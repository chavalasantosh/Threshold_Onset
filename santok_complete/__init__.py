"""
SanTOK - Text Tokenization System
A comprehensive text tokenization system with mathematical analysis and statistical features
"""

from typing import Any, Dict, List

__version__ = "1.0.0"
__author__ = "Santosh Chavala"
__email__ = "chavalasantosh@example.com"

from .core.core_tokenizer import (
    tokenize_space as _core_tokenize_space,
    tokenize_word as _core_tokenize_word,
    tokenize_char,
    tokenize_grammar,
    tokenize_subword,
    tokenize_text as _core_tokenize_text,
    TextTokenizer,
    TokenRecord,
)
from .core.santok_engine import (
    TextTokenizationEngine,
    analyze_text_comprehensive,
    generate_text_summary,
)
from .santok.santok import (
    TextTokenizationEngine as SanTOKEngine,
    tokenize_text as santok_tokenize_text,
    analyze_text_comprehensive as santok_analyze_text,
)


def _strip_non_word_tokens(tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compatibility view: keep lexical tokens, drop separators/punctuation."""
    return [
        token for token in tokens
        if token.get("type") not in {"space", "punctuation", "separator"}
    ]


def tokenize_space(text: str) -> List[Dict[str, Any]]:
    return _strip_non_word_tokens(_core_tokenize_space(text))


def tokenize_word(text: str) -> List[Dict[str, Any]]:
    return [token for token in _core_tokenize_word(text) if token.get("type") == "word"]


def tokenize_text(text: str, tokenizer_type: str = "word") -> List[Dict[str, Any]]:
    return _core_tokenize_text(text, tokenizer_type=tokenizer_type)

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
