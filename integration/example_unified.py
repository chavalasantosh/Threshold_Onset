#!/usr/bin/env python3
"""
Example: Unified System Usage

Demonstrates how to use the unified threshold_onset <-> santok system.
"""

from integration.unified_system import process_text_through_phases

# Example 1: Simple English text
print("=" * 70)
print("EXAMPLE 1: Simple English Text")
print("=" * 70)
text1 = """
Action before knowledge.
Function stabilizes before meaning appears.
Structure emerges before language exists.
Tokens become actions.
Patterns become residues.
Structure emerges naturally.
"""
results1 = process_text_through_phases(
    text=text1,
    tokenization_method="word",
    num_runs=3
)
print("\nSummary:")
print(f"  Tokens: {len(results1['tokens'])}")
if results1['phase2']:
    print(f"  Persistent identities: {len(results1['phase2']['persistent_segment_hashes'])}")
if results1['phase3']:
    print(f"  Persistent relations: {len(results1['phase3']['persistent_relation_hashes'])}")
print()

# Example 2: Multilingual text with philosophy
print("=" * 70)
print("EXAMPLE 2: Multilingual Text (Philosophy)")
print("=" * 70)
text2 = """
कार्य (kārya) happens before ज्ञान (jñāna)
Action before knowledge.
Function before meaning.
Structure before language.
"""
results2 = process_text_through_phases(
    text=text2,
    tokenization_method="word",
    num_runs=3
)
print("\nSummary:")
print(f"  Tokens: {len(results2['tokens'])}")
if results2['phase2']:
    print(f"  Persistent identities: {len(results2['phase2']['persistent_segment_hashes'])}")
if results2['phase3']:
    print(f"  Persistent relations: {len(results2['phase3']['persistent_relation_hashes'])}")
print()

# Example 3: Character-level analysis
print("=" * 70)
print("EXAMPLE 3: Character-Level Analysis")
print("=" * 70)
text3 = "Structure emerges naturally from patterns."
results3 = process_text_through_phases(
    text=text3,
    tokenization_method="character",
    num_runs=3
)
print("\nSummary:")
print(f"  Tokens: {len(results3['tokens'])}")
if results3['phase2']:
    print(f"  Persistent identities: {len(results3['phase2']['persistent_segment_hashes'])}")
if results3['phase3']:
    print(f"  Persistent relations: {len(results3['phase3']['persistent_relation_hashes'])}")
print()

print("=" * 70)
print("All examples complete!")
print("=" * 70)
print()
print("Key insight: Structure emerges from token patterns.")
print("Semantics emerge automatically from the structure.")
print("No embeddings. No neural networks. Just structure emergence.")
