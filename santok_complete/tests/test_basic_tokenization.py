#!/usr/bin/env python3
"""
Basic tokenization tests
"""

import pytest
from santok_complete import TextTokenizationEngine
from santok_complete import tokenize_space, tokenize_word, tokenize_char

class TestBasicTokenization:
    """Test basic tokenization functionality"""
    
    def test_text_tokenization_engine_initialization(self):
        """Test TextTokenizationEngine can be initialized"""
        engine = TextTokenizationEngine()
        assert engine is not None
        assert engine.random_seed == 12345
        assert engine.normalize_case == True
    
    def test_whitespace_tokenization(self):
        """Test whitespace tokenization"""
        engine = TextTokenizationEngine()
        result = engine.tokenize("Hello World", method="whitespace")
        
        assert "tokens" in result
        assert len(result["tokens"]) == 2
        assert result["tokens"][0] == "hello"
        assert result["tokens"][1] == "world"
    
    def test_word_tokenization(self):
        """Test word tokenization"""
        engine = TextTokenizationEngine()
        result = engine.tokenize("Hello, World!", method="word")
        
        assert "tokens" in result
        assert len(result["tokens"]) == 2
        assert "hello" in result["tokens"]
        assert "world" in result["tokens"]
    
    def test_character_tokenization(self):
        """Test character tokenization"""
        engine = TextTokenizationEngine()
        result = engine.tokenize("ABC", method="character")
        
        assert "tokens" in result
        assert len(result["tokens"]) == 3
        assert result["tokens"] == ["a", "b", "c"]
    
    def test_direct_tokenize_space(self):
        """Test direct tokenize_space function"""
        tokens = tokenize_space("Hello World")
        assert len(tokens) == 2
        assert tokens[0]["text"] == "Hello"
        assert tokens[1]["text"] == "World"
    
    def test_direct_tokenize_word(self):
        """Test direct tokenize_word function"""
        tokens = tokenize_word("Hello, World!")
        assert len(tokens) == 2
        assert tokens[0]["text"] == "Hello"
        assert tokens[1]["text"] == "World"
    
    def test_features_computation(self):
        """Test that features are computed correctly"""
        engine = TextTokenizationEngine()
        result = engine.tokenize("Hello World", method="whitespace", compute_features=True)
        
        assert "features" in result
        assert result["features"] is not None
        assert "length_factor" in result["features"]
        assert "balance_index" in result["features"]
        assert "entropy_index" in result["features"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
