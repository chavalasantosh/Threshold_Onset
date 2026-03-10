#!/usr/bin/env python3
"""
Basic Usage Examples for SanTOK Tokenization System
"""

from santok_complete import TextTokenizationEngine

def example_basic_tokenization():
    """Basic tokenization example"""
    print("=" * 60)
    print("Example 1: Basic Tokenization")
    print("=" * 60)
    
    engine = TextTokenizationEngine()
    text = "Hello World! This is a test."
    
    result = engine.tokenize(text, method="whitespace")
    
    print(f"Original Text: {result['original_text']}")
    print(f"Preprocessed: {result['preprocessed_text']}")
    print(f"Tokens: {result['tokens']}")
    print(f"Frontend Digits: {result['frontend_digits']}")
    print(f"Features: {result['features']}")
    print()

def example_all_methods():
    """Example using all tokenization methods"""
    print("=" * 60)
    print("Example 2: All Tokenization Methods")
    print("=" * 60)
    
    engine = TextTokenizationEngine()
    text = "Hello, World!"
    
    methods = ["whitespace", "word", "character", "subword"]
    
    for method in methods:
        result = engine.tokenize(text, method=method)
        print(f"{method.upper()}: {result['tokens']}")
    print()

def example_analyze_text():
    """Example of comprehensive text analysis"""
    print("=" * 60)
    print("Example 3: Comprehensive Analysis")
    print("=" * 60)
    
    engine = TextTokenizationEngine()
    text = "The quick brown fox jumps over the lazy dog."
    
    analysis = engine.analyze_text(text)
    
    for method, result in analysis.items():
        print(f"{method}: {len(result['tokens'])} tokens")
    print()

def example_custom_config():
    """Example with custom configuration"""
    print("=" * 60)
    print("Example 4: Custom Configuration")
    print("=" * 60)
    
    engine = TextTokenizationEngine(
        random_seed=99999,
        normalize_case=True,
        remove_punctuation=True,
        collapse_repetitions=0
    )
    
    text = "Hello!!! World!!!"
    result = engine.tokenize(text, method="whitespace")
    
    print(f"Original: {text}")
    print(f"Preprocessed: {result['preprocessed_text']}")
    print(f"Tokens: {result['tokens']}")
    print()

def example_generate_summary():
    """Example of generating text summary"""
    print("=" * 60)
    print("Example 5: Text Summary")
    print("=" * 60)
    
    engine = TextTokenizationEngine()
    text = "Natural language processing is a field of artificial intelligence."
    
    summary = engine.generate_summary(text)
    
    print(f"Text Length: {summary['text_length']}")
    print(f"Token Count: {summary['token_count']}")
    print(f"Unique Tokens: {summary['unique_tokens']}")
    print(f"Frontend Digits: {summary['frontend_digits']}")
    print()

if __name__ == "__main__":
    example_basic_tokenization()
    example_all_methods()
    example_analyze_text()
    example_custom_config()
    example_generate_summary()
