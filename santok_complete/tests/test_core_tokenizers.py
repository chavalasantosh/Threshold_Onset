#!/usr/bin/env python3
"""
Tests for core tokenization functions
"""

import pytest
from santok_complete import (
    tokenize_space,
    tokenize_word,
    tokenize_char,
    tokenize_grammar,
    tokenize_subword,
    tokenize_text,
    TextTokenizer
)

class TestCoreTokenizers:
    """Test core tokenization functions"""
    
    def test_tokenize_space(self):
        """Test space tokenization"""
        text = "Hello   World"
        tokens = tokenize_space(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) >= 2
        assert tokens[0]["text"] == "Hello"
        assert "index" in tokens[0]
    
    def test_tokenize_word(self):
        """Test word tokenization"""
        text = "Hello, World!"
        tokens = tokenize_word(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) == 2
        assert tokens[0]["text"] == "Hello"
        assert tokens[1]["text"] == "World"
    
    def test_tokenize_char(self):
        """Test character tokenization"""
        text = "ABC"
        tokens = tokenize_char(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) == 3
        assert tokens[0]["text"] == "A"
    
    def test_tokenize_grammar(self):
        """Test grammar tokenization"""
        text = "Hello, World!"
        tokens = tokenize_grammar(text)
        
        assert isinstance(tokens, list)
        # Should separate words and punctuation
        assert any(t["text"] == "Hello" for t in tokens)
        assert any(t["text"] == "World" for t in tokens)
    
    def test_tokenize_subword(self):
        """Test subword tokenization"""
        text = "Hello"
        tokens = tokenize_subword(text, chunk_len=3)
        
        assert isinstance(tokens, list)
        # "Hello" (5 chars) with chunk_len=3 should give ["Hel", "lo"]
        assert len(tokens) >= 1
    
    def test_tokenize_text_function(self):
        """Test tokenize_text convenience function"""
        text = "Hello World"
        tokens = tokenize_text(text, tokenizer_type="word")
        
        assert isinstance(tokens, list)
        assert len(tokens) >= 2
    
    def test_text_tokenizer_class(self):
        """Test TextTokenizer class"""
        tokenizer = TextTokenizer(seed=42, embedding_bit=False)
        tokens = tokenizer.tokenize("Hello World", method="word")
        
        assert isinstance(tokens, list)
        assert len(tokens) >= 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
