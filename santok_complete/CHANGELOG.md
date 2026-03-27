# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added
- Initial release of SanTOK tokenization system
- Multiple tokenization methods: whitespace, word, character, grammar, subword, byte
- TextTokenizationEngine class with mathematical analysis
- TextTokenizer class for core tokenization
- Parallel processing support for large texts
- Multi-language support (CJK, Arabic, Cyrillic, Hebrew, Thai, Devanagari)
- Statistical features computation (length factor, balance index, entropy index)
- Frontend digit generation for tokens
- Command-line interface (CLI)
- Comprehensive examples and tests
- Pure Python implementation with no external dependencies

### Features
- Space-based tokenization
- Word boundary tokenization
- Character-level tokenization
- Grammar-aware tokenization
- Subword tokenization with configurable chunk sizes
- Byte-level tokenization
- Parallel tokenization (threaded and multiprocess)
- Text preprocessing options (case normalization, punctuation removal)
- Token reconstruction capabilities
- Source tagging support (optional)
