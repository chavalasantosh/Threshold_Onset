"""
Parallel Processing Module for SanTOK
Supports multi-threading and multi-processing for large text tokenization
"""

import os
import multiprocessing
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any, Optional

from .core_tokenizer import (
    tokenize_space,
    tokenize_word,
    tokenize_char,
    tokenize_grammar,
    tokenize_subword,
    tokenize_bytes,
)

try:
    from .core_tokenizer import detect_language
except ImportError:
    detect_language = None


def _fallback_detect_language(text: str) -> str:
    """
    Lightweight script-based language fallback when core detect_language
    is unavailable.
    Returns one of: cjk, devanagari, arabic, cyrillic, latin.
    """
    if not text:
        return "latin"

    cjk = 0
    devanagari = 0
    arabic = 0
    cyrillic = 0
    latin = 0

    for ch in text:
        code = ord(ch)
        if (
            0x4E00 <= code <= 0x9FFF  # CJK Unified Ideographs
            or 0x3400 <= code <= 0x4DBF  # CJK Extension A
            or 0x3040 <= code <= 0x30FF  # Hiragana + Katakana
            or 0xAC00 <= code <= 0xD7AF  # Hangul Syllables
        ):
            cjk += 1
        elif 0x0900 <= code <= 0x097F:
            devanagari += 1
        elif 0x0600 <= code <= 0x06FF:
            arabic += 1
        elif 0x0400 <= code <= 0x04FF:
            cyrillic += 1
        elif ("A" <= ch <= "Z") or ("a" <= ch <= "z"):
            latin += 1

    counts = {
        "cjk": cjk,
        "devanagari": devanagari,
        "arabic": arabic,
        "cyrillic": cyrillic,
        "latin": latin,
    }
    return max(counts, key=counts.get)

def _safe_int_env(name: str, default: int, minimum: int = 1) -> int:
    """Read integer env var safely with sane bounds."""
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return max(minimum, int(raw))
    except ValueError:
        return default


def _resolve_chunk_size(chunk_size: Optional[int]) -> int:
    if chunk_size is not None and chunk_size > 0:
        return int(chunk_size)
    return _safe_int_env("SANTOK_PARALLEL_CHUNK_SIZE", 50000, minimum=1024)


def _resolve_workers(max_workers: Optional[int], chunk_count: int) -> int:
    if max_workers is not None:
        requested = max(1, int(max_workers))
    else:
        requested = _safe_int_env("SANTOK_PARALLEL_WORKERS", multiprocessing.cpu_count(), minimum=1)
    return max(1, min(chunk_count, requested))


def chunk_text(text: str, chunk_size: int = 50000) -> List[str]:
    """Split text into chunks for parallel processing"""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

def process_chunk_sequential(chunk_data: tuple) -> List[Dict[str, Any]]:
    """Process a single chunk sequentially"""
    chunk_text, _tokenizer_func, tokenizer_type, _chunk_index = chunk_data
    # _tokenizer_func is unused — tokenizer_map lookup is done instead
    tokenizer_map = {
        'space': tokenize_space,
        'word': tokenize_word,
        'char': tokenize_char,
        'grammar': tokenize_grammar,
        'subword': lambda x: tokenize_subword(x, 3, 'fixed'),
        'bpe': lambda x: tokenize_subword(x, 3, 'bpe'),
        'syllable': lambda x: tokenize_subword(x, 3, 'syllable'),
        'frequency': lambda x: tokenize_subword(x, 3, 'frequency'),
        'byte': tokenize_bytes
    }
    
    tokenizer_func = tokenizer_map.get(tokenizer_type, tokenize_word)
    tokens = tokenizer_func(chunk_text)
    
    return tokens

def tokenize_parallel_threaded(text: str, tokenizer_type: str = 'word', 
                              max_workers: Optional[int] = None, chunk_size: Optional[int] = 50000) -> List[Dict[str, Any]]:
    """Tokenize text using multiple threads"""
    chunk_size = _resolve_chunk_size(chunk_size)
    if len(text) <= chunk_size:
        # Use sequential processing for small texts
        return process_chunk_sequential((text, None, tokenizer_type, 0))
    
    chunks = chunk_text(text, chunk_size)
    chunk_data = [(chunk, None, tokenizer_type, i) for i, chunk in enumerate(chunks)]

    workers = _resolve_workers(max_workers, len(chunks))
    all_tokens: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # executor.map preserves chunk order; deterministic token stream.
        chunk_results = list(executor.map(process_chunk_sequential, chunk_data))

    token_id = 0
    for chunk_tokens in chunk_results:
        for token in chunk_tokens:
            token['id'] = token_id
            all_tokens.append(token)
            token_id += 1

    return all_tokens

def tokenize_parallel_multiprocess(text: str, tokenizer_type: str = 'word', 
                                  max_workers: Optional[int] = None, chunk_size: Optional[int] = 50000) -> List[Dict[str, Any]]:
    """Tokenize text using multiple processes"""
    chunk_size = _resolve_chunk_size(chunk_size)
    if len(text) <= chunk_size:
        # Use sequential processing for small texts
        return process_chunk_sequential((text, None, tokenizer_type, 0))
    
    chunks = chunk_text(text, chunk_size)
    chunk_data = [(chunk, None, tokenizer_type, i) for i, chunk in enumerate(chunks)]

    workers = _resolve_workers(max_workers, len(chunks))
    all_tokens: List[Dict[str, Any]] = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        chunk_results = list(executor.map(process_chunk_sequential, chunk_data))

    token_id = 0
    for chunk_tokens in chunk_results:
        for token in chunk_tokens:
            token['id'] = token_id
            all_tokens.append(token)
            token_id += 1

    return all_tokens

def benchmark_parallel_performance(text: str, tokenizer_type: str = 'word', 
                                 chunk_size: int = 50000) -> Dict[str, Any]:
    """Benchmark parallel vs sequential performance"""
    results = {}
    
    # Sequential processing
    start_time = time.perf_counter()
    sequential_tokens = process_chunk_sequential((text, None, tokenizer_type, 0))
    sequential_time = time.perf_counter() - start_time
    
    # Threaded processing
    start_time = time.perf_counter()
    threaded_tokens = tokenize_parallel_threaded(text, tokenizer_type, chunk_size=chunk_size)
    threaded_time = time.perf_counter() - start_time
    
    # Multi-process processing
    start_time = time.perf_counter()
    multiprocess_tokens = tokenize_parallel_multiprocess(text, tokenizer_type, chunk_size=chunk_size)
    multiprocess_time = time.perf_counter() - start_time
    
    results = {
        'text_length': len(text),
        'chunk_size': chunk_size,
        'sequential_time': sequential_time,
        'threaded_time': threaded_time,
        'multiprocess_time': multiprocess_time,
        'sequential_speed': len(text) / sequential_time if sequential_time > 0 else 0,
        'threaded_speed': len(text) / threaded_time if threaded_time > 0 else 0,
        'multiprocess_speed': len(text) / multiprocess_time if multiprocess_time > 0 else 0,
        'threaded_speedup': sequential_time / threaded_time if threaded_time > 0 else 0,
        'multiprocess_speedup': sequential_time / multiprocess_time if multiprocess_time > 0 else 0,
        'token_count': len(sequential_tokens)
    }
    
    return results

def auto_parallel_tokenize(
    text: str,
    tokenizer_type: str = 'word',
    threshold: int = 100000,
    *,
    backend: str = "thread",
    max_workers: Optional[int] = None,
    chunk_size: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Automatically choose between sequential and parallel processing based on text size"""
    if len(text) <= threshold:
        # Use sequential processing for small texts
        return process_chunk_sequential((text, None, tokenizer_type, 0))

    resolved_backend = (backend or "thread").lower()
    if resolved_backend == "process":
        return tokenize_parallel_multiprocess(
            text, tokenizer_type, max_workers=max_workers, chunk_size=chunk_size
        )
    return tokenize_parallel_threaded(
        text, tokenizer_type, max_workers=max_workers, chunk_size=chunk_size
    )

# Language-specific parallel processing
def tokenize_multilang_parallel(text: str, tokenizer_type: str = 'word', 
                               language: str = None, max_workers: int = None) -> List[Dict[str, Any]]:
    """Tokenize multilingual text with parallel processing"""
    # Use module-level detect_language (imported at top); fall back to script detector
    _detector = detect_language if detect_language is not None else _fallback_detect_language
    if language is None:
        language = _detector(text)
    
    # For CJK languages, use character-based tokenization for better parallelization
    if language == "cjk" and tokenizer_type == "word":
        tokenizer_type = "char"
    
    return auto_parallel_tokenize(text, tokenizer_type)