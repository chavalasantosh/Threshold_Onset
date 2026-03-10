# SanTOK Core

Core tokenization logic.

| File | Purpose |
|------|---------|
| `base_tokenizer.py` | tokenize_space, tokenize_char, tokenize_word, tokenize_grammar, tokenize_subword, tokenize_bytes |
| `core_tokenizer.py` | tokenize_text(text, tokenizer_type, ...); multilang helpers |
| `parallel_tokenizer.py` | tokenize_parallel_threaded, tokenize_parallel_multiprocess, tokenize_multilang_parallel |
| `santok_engine.py` | tokenize_text(text, tokenization_method) — API entry |
