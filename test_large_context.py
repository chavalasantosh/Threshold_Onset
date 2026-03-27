#!/usr/bin/env python3
"""
Test and Benchmark Large Context Capabilities

Tests GPT-5.2-like features:
- 1M token context windows
- 512K token output capacity
- Chunked processing
- Streaming generation
- Memory optimizations
"""

import sys
import time
import gc
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from threshold_onset.semantic.large_context import (
    LargeContextProcessor,
    StreamingGenerator,
    MAX_CONTEXT_TOKENS,
    MAX_OUTPUT_TOKENS
)


def generate_large_text(size_mb: float = 1.0) -> str:
    """Generate a large text for testing."""
    base_text = (
        "The cat sat on the mat. The cat was happy. The dog ran fast. "
        "The dog chased the cat. The cat jumped high. The dog barked loud. "
        "The mat was soft. The cat liked the mat. The dog wanted the mat. "
        "The cat and dog played together. They ran around the house. "
        "The house was big. The house had many rooms. Each room was different. "
        "The cat found a toy. The dog found a ball. They played with their toys. "
        "The toys were fun. The cat and dog were friends. They enjoyed playing. "
        "Action happens before knowledge. Learning comes from doing. "
        "Practice makes perfect. Repetition builds understanding. "
        "The more you do, the more you know. Experience teaches wisdom. "
    )
    
    # Calculate how many repetitions needed
    target_size = int(size_mb * 1024 * 1024)  # Convert MB to bytes
    repetitions = target_size // len(base_text) + 1
    
    return base_text * repetitions


def test_context_processing():
    """Test large context processing."""
    print("=" * 70)
    print("TEST 1: Large Context Processing")
    print("=" * 70)
    
    processor = LargeContextProcessor()
    
    # Test with different text sizes
    test_sizes = [0.1, 1.0, 5.0, 10.0]  # MB
    
    for size_mb in test_sizes:
        print(f"\nTesting with {size_mb} MB text...")
        text = generate_large_text(size_mb)
        
        estimated_tokens = processor.estimate_tokens(text)
        can_process = processor.can_process(text)
        
        print(f"  Text size: {len(text):,} characters")
        print(f"  Estimated tokens: {estimated_tokens:,}")
        print(f"  Can process in one go: {can_process}")
        print(f"  Max context: {processor.max_context_tokens:,} tokens")
        
        if not can_process:
            start_time = time.time()
            chunks = processor.chunk_text(text, overlap=1000, preserve_sentences=True)
            chunk_time = time.time() - start_time
            
            print(f"  Chunks created: {len(chunks)}")
            print(f"  Chunking time: {chunk_time:.3f} seconds")
            print(f"  Avg chunk size: {len(text) // len(chunks):,} chars")
        
        # Memory check
        gc.collect()
        print()


def test_streaming_generation():
    """Test streaming generation."""
    print("=" * 70)
    print("TEST 2: Streaming Generation")
    print("=" * 70)
    
    generator = StreamingGenerator()
    
    # Simple generator function for testing
    counter = [0]
    def test_generator(current):
        counter[0] += 1
        return counter[0]
    
    print(f"\nGenerating up to {generator.max_output_tokens:,} items...")
    start_time = time.time()
    
    total_generated = 0
    chunk_count = 0
    max_test_items = 50_000  # Limit for testing
    
    for chunk in generator.generate_streaming(
        generator_func=test_generator,
        start_input=0,
        max_length=max_test_items
    ):
        total_generated += len(chunk)
        chunk_count += 1
        if chunk_count % 10 == 0:
            print(f"  Generated {total_generated:,} items in {chunk_count} chunks...")
    
    gen_time = time.time() - start_time
    
    print(f"\n  Total generated: {total_generated:,} items")
    print(f"  Chunks yielded: {chunk_count}")
    print(f"  Generation time: {gen_time:.3f} seconds")
    print(f"  Rate: {total_generated / gen_time:,.0f} items/second")
    print()


def test_memory_efficiency():
    """Test memory efficiency."""
    print("=" * 70)
    print("TEST 3: Memory Efficiency")
    print("=" * 70)
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    # Baseline memory
    gc.collect()
    baseline_mem = process.memory_info().rss / 1024 / 1024  # MB
    print(f"Baseline memory: {baseline_mem:.2f} MB")
    
    # Test with large text
    processor = LargeContextProcessor()
    text = generate_large_text(5.0)  # 5 MB
    
    print(f"\nProcessing 5 MB text...")
    chunks = processor.chunk_text(text)
    
    after_chunk_mem = process.memory_info().rss / 1024 / 1024  # MB
    print(f"After chunking: {after_chunk_mem:.2f} MB")
    print(f"Memory increase: {after_chunk_mem - baseline_mem:.2f} MB")
    print(f"Chunks: {len(chunks)}")
    
    # Process chunks and monitor memory
    for i, chunk in enumerate(chunks[:5]):  # Process first 5 chunks
        # Simulate processing
        _ = len(chunk.split())
        
        if i % 2 == 0:
            gc.collect()
            current_mem = process.memory_info().rss / 1024 / 1024
            print(f"  After chunk {i+1}: {current_mem:.2f} MB")
    
    final_mem = process.memory_info().rss / 1024 / 1024
    print(f"\nFinal memory: {final_mem:.2f} MB")
    print(f"Total increase: {final_mem - baseline_mem:.2f} MB")
    print()


def benchmark_performance():
    """Benchmark performance metrics."""
    print("=" * 70)
    print("BENCHMARK: Performance Metrics")
    print("=" * 70)
    
    processor = LargeContextProcessor()
    
    # Test different text sizes
    sizes = [0.5, 1.0, 2.0, 5.0, 10.0]  # MB
    
    print("\nChunking Performance:")
    print(f"{'Size (MB)':<12} {'Tokens (est)':<15} {'Chunks':<10} {'Time (s)':<12} {'Rate (MB/s)':<12}")
    print("-" * 70)
    
    for size_mb in sizes:
        text = generate_large_text(size_mb)
        estimated_tokens = processor.estimate_tokens(text)
        
        start = time.time()
        chunks = processor.chunk_text(text)
        elapsed = time.time() - start
        
        rate = size_mb / elapsed if elapsed > 0 else 0
        
        print(f"{size_mb:<12.1f} {estimated_tokens:<15,} {len(chunks):<10} {elapsed:<12.3f} {rate:<12.2f}")
    
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("LARGE CONTEXT CAPABILITIES - TEST SUITE")
    print("=" * 70)
    print()
    print(f"Max Context Tokens: {MAX_CONTEXT_TOKENS:,}")
    print(f"Max Output Tokens: {MAX_OUTPUT_TOKENS:,}")
    print()
    
    try:
        test_context_processing()
        test_streaming_generation()
        test_memory_efficiency()
        benchmark_performance()
        
        print("=" * 70)
        print("[OK] ALL TESTS COMPLETE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
