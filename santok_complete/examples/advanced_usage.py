#!/usr/bin/env python3
"""
Advanced Usage Examples for SanTOK Tokenization System
"""

from santok_complete import tokenize_text, tokenize_space, tokenize_word
from santok_complete.core.parallel_tokenizer import tokenize_parallel_threaded
from santok_complete import TextTokenizer

def example_direct_functions():
    """Example using direct tokenization functions"""
    print("=" * 60)
    print("Example 1: Direct Tokenization Functions")
    print("=" * 60)
    
    text = "Hello World! This is a test."
    
    # Using direct functions
    tokens_space = tokenize_space(text)
    tokens_word = tokenize_word(text)
    
    print(f"Space tokenization: {[t['text'] for t in tokens_space[:5]]}")
    print(f"Word tokenization: {[t['text'] for t in tokens_word[:5]]}")
    print()

def example_text_tokenizer_class():
    """Example using TextTokenizer class"""
    print("=" * 60)
    print("Example 2: TextTokenizer Class")
    print("=" * 60)
    
    tokenizer = TextTokenizer(seed=42, embedding_bit=False)
    text = "Hello World!"
    
    tokens = tokenizer.tokenize(text, method="word")
    print(f"Tokens: {[t.text for t in tokens[:5]]}")
    print()

def example_parallel_tokenization():
    """Example of parallel tokenization for large texts"""
    print("=" * 60)
    print("Example 3: Parallel Tokenization")
    print("=" * 60)
    
    # Create a large text
    large_text = "Hello World! " * 10000
    
    # Sequential tokenization
    tokens_sequential = tokenize_word(large_text)
    
    # Parallel tokenization
    tokens_parallel = tokenize_parallel_threaded(
        large_text, 
        tokenizer_type='word', 
        max_workers=4,
        chunk_size=50000
    )
    
    print(f"Sequential tokens: {len(tokens_sequential)}")
    print(f"Parallel tokens: {len(tokens_parallel)}")
    print()

def example_multi_language():
    """Example of multi-language tokenization"""
    print("=" * 60)
    print("Example 4: Multi-language Tokenization")
    print("=" * 60)
    
    # English text
    english_text = "Hello World"
    tokens_en = tokenize_text(english_text, tokenizer_type="word")
    print(f"English: {[t['text'] for t in tokens_en[:5]]}")
    
    # CJK text (character-based)
    cjk_text = "你好世界"
    tokens_cjk = tokenize_text(cjk_text, tokenizer_type="word", language="cjk")
    print(f"CJK: {[t['text'] for t in tokens_cjk[:5]]}")
    print()

def example_all_tokenizers():
    """Example using all available tokenizers"""
    print("=" * 60)
    print("Example 5: All Available Tokenizers")
    print("=" * 60)
    
    from santok_complete import (
        tokenize_space,
        tokenize_word,
        tokenize_char,
        tokenize_grammar,
        tokenize_subword
    )
    
    text = "Hello, World! 123"
    
    print(f"Space: {[t['text'] for t in tokenize_space(text)]}")
    print(f"Word: {[t['text'] for t in tokenize_word(text)]}")
    print(f"Char: {[t['text'] for t in tokenize_char(text)][:10]}...")
    print(f"Grammar: {[t['text'] for t in tokenize_grammar(text)]}")
    print(f"Subword: {[t['text'] for t in tokenize_subword(text, chunk_len=3)]}")
    print()

if __name__ == "__main__":
    example_direct_functions()
    example_text_tokenizer_class()
    example_parallel_tokenization()
    example_multi_language()
    example_all_tokenizers()
