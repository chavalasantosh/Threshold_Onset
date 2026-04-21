#!/usr/bin/env python3
"""
MASTER ONSET — Production Unified Controller
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Single command entry point for the complete sovereign architecture.

Modes:
  compile  : Bulk-build corpus directories into geometric JSONL matrices.
  identity : Run Phase 0-10 on input text and print structural identity map.
  invoke   : Full end-to-end: Phase 0-10 identity → SanTok physics → output.

Usage:
  python master_onset.py compile "data/clean"
  python master_onset.py identity "Which language is best?"
  python master_onset.py invoke  "shard_00000" "Which language is best?"
"""

import sys
import os
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# ── MODE 1: Compile ───────────────────────────────────────────────────────────

def execute_compile(target_path):
    """
    Bulk-compile raw text data into SanTok topological JSONL matrices.
    Accepts a single file or an entire directory of files.
    """
    print("\n" + "=" * 70)
    print("  MASTER ONSET — COMPILE MODE")
    print("=" * 70)

    from santok_pipeline import SanTokAPI, process_target_file

    if not os.path.exists(target_path):
        print(f"[!] Target path not found: {target_path}")
        return

    api = SanTokAPI()

    if os.path.isdir(target_path):
        print(f"[*] Directory detected. Walking recursively: {target_path}")
        compiled = 0
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.endswith(('.txt', '.jsonl', '.json', '.csv')):
                    process_target_file(os.path.join(root, file), api)
                    compiled += 1
        print(f"\n[✓] Bulk compile complete. {compiled} files processed.")
    else:
        process_target_file(target_path, api)
        print(f"\n[✓] Compile complete.")


# ── MODE 2: Identity ──────────────────────────────────────────────────────────

def execute_identity(seed_text):
    """
    Run the complete THRESHOLD_ONSET Phase 0-10 pipeline on a text string.
    Prints the full structural identity report without generating SanTok output.
    """
    print("\n" + "=" * 70)
    print("  MASTER ONSET — IDENTITY MODE")
    print("=" * 70)
    print(f"[*] Input: \"{seed_text}\"")

    from integration.run_complete import run, PipelineConfig

    cfg = PipelineConfig.from_project()
    cfg.show_tui = True  # Show full pipeline output

    result = run(
        text_override=seed_text,
        cfg=cfg,
        return_result=True,
        return_model_state=True
    )

    if not result:
        print("[!] Pipeline returned no result.")
        return

    print("\n" + "=" * 70)
    print("  STRUCTURAL IDENTITY REPORT")
    print("=" * 70)
    print(f"  Tokens          : {result.token_count}")
    print(f"  Identities      : {result.identity_count}")
    print(f"  Relations       : {result.relation_count}")
    print(f"  Refusals        : {result.refusal_count}")
    print(f"  Topology Nodes  : {len(result.topology)}")
    print(f"  Clusters        : {list(result.clusters.keys())}")
    print(f"  Scored Paths    : {result.scored_path_count}")
    print(f"  Pipeline Time   : {result.timings.total_ms:.1f}ms")

    print("\n  [ Topology Detail ]")
    for sym, td in result.topology.items():
        conc = getattr(td, "escape_concentration", 0.0)
        paths = getattr(td, "distinct_escape_paths", 0)
        pressure = getattr(td, "self_transition_attempts", 0)
        print(f"    Symbol: {sym[:20]:20s}  Concentration: {conc:.3f}  Escape Paths: {paths}  Pressure: {pressure}")

    print("\n  [ THRESHOLD_ONSET Generated Outputs ]")
    for i, out in enumerate(result.generated_outputs[:3], 1):
        print(f"    [{i}] {out[:80]}")


# ── MODE 3: Invoke ────────────────────────────────────────────────────────────

def execute_invoke(seed_text, raw_corpus):
    """
    Full sovereign unification:
    1. Run THRESHOLD_ONSET Phase 0-10 on seed_text.
    2. Extract topology, clusters, path_scores from PipelineResult.
    3. Build production identity_validator from real structural analysis.
    4. Derive tension_threshold from escape_concentration.
    5. Boot SanTok physics engine with corpus matrix.
    6. Generate output with full identity gating active.
    """
    print("\n" + "=" * 70)
    print("  MASTER ONSET — INVOKE MODE (Full Unification)")
    print("=" * 70)

    # ── Step 1: Resolve SanTok corpus matrix path ─────────────────────────────
    corpus_name = os.path.basename(raw_corpus)
    for ext in ["_santok_unified.jsonl", "_santok_unified.json", ".jsonl", ".json", ".txt", ".csv"]:
        corpus_name = corpus_name.replace(ext, "")

    _corpus = ""
    if raw_corpus.endswith("_santok_unified.jsonl") and os.path.exists(raw_corpus):
        _corpus = raw_corpus
    elif raw_corpus.endswith("_santok_unified.json") and os.path.exists(raw_corpus):
        _corpus = raw_corpus
    else:
        _corpus = os.path.join(ROOT, "output", f"{corpus_name}_santok_unified.jsonl")
        if not os.path.exists(_corpus):
            _corpus = os.path.join(ROOT, "output", f"{corpus_name}_santok_unified.json")

    if not os.path.exists(_corpus):
        print(f"[!] Corpus matrix not found: {corpus_name}")
        print(f"    Run first: python master_onset.py compile <your data path>")
        return

    print(f"[✓] Corpus matrix located: {os.path.basename(_corpus)}")

    # ── Step 2: Run THRESHOLD_ONSET Phase 0-10 ───────────────────────────────
    print(f"\n[*] STEP 1 — Running THRESHOLD_ONSET structural identity extraction...")
    print(f"    Input: \"{seed_text}\"")

    from integration.run_complete import run, PipelineConfig

    cfg = PipelineConfig.from_project()
    cfg.show_tui = False  # Silent for clean invoke output

    pipeline_result = run(
        text_override=seed_text,
        cfg=cfg,
        return_result=True,
        return_model_state=True
    )

    if not pipeline_result:
        print("[!] THRESHOLD_ONSET pipeline failed. Aborting.")
        return

    print(f"[✓] Identity extracted: {pipeline_result.identity_count} identities, "
          f"{pipeline_result.relation_count} relations, "
          f"{len(pipeline_result.topology)} topology nodes")

    # ── Step 3: Build production validator from real topology ─────────────────
    print(f"\n[*] STEP 2 — Building structural identity gate from topology...")

    from integration.santok_identity_bridge import (
        build_production_validator,
        extract_seed_from_identity,
        ThresholdSantokBridge
    )

    validator, tension_threshold, suppressed, promoted = build_production_validator(
        topology=pipeline_result.topology,
        path_scores=pipeline_result.model_state.get("path_scores", {}) if pipeline_result.model_state else {},
        clusters=pipeline_result.clusters
    )

    tension_labels = {1: "Aggressive (high concentration)", 4: "Neutral", 10: "Calm (low concentration)"}
    print(f"[✓] Validator built.")
    print(f"    Tension Threshold : {tension_threshold} → {tension_labels.get(tension_threshold, '')}")
    print(f"    Suppressed symbols: {len(suppressed)}")
    print(f"    Promoted symbols  : {len(promoted)}")

    # ── Step 4: Boot SanTok engine and generate ───────────────────────────────
    print(f"\n[*] STEP 3 — Booting SanTok Physics Engine...")

    bridge = ThresholdSantokBridge(_corpus)

    print(f"\n[*] STEP 4 — Generating sovereign output...")
    output = bridge.generate(
        current_state_text=seed_text,
        permission_profile=None,        # Using production validator instead
        length=30,
        identity_state_id=0             # Tension resolved dynamically from topology
    )

    # Re-generate using the production validator directly on the engine
    seed = extract_seed_from_identity(bridge.engine, seed_text)
    if seed and len(seed) >= 2:
        print(f"[Bridge] Seed: '{seed[0]['text']}' → '{seed[1]['text']}'")
    output = bridge.engine.generate(
        seed_tokens=seed,
        length=40,
        tolerance=5000,
        identity_validator=validator,
        tension_threshold=tension_threshold
    )

    print("\n" + "=" * 70)
    print("  SOVEREIGN UNIFIED OUTPUT")
    print("=" * 70)
    print(f"  {output}")

    print("\n" + "=" * 70)
    print("  THRESHOLD_ONSET STRUCTURAL BASELINE OUTPUTS")
    print("=" * 70)
    for i, o in enumerate(pipeline_result.generated_outputs[:3], 1):
        print(f"  [{i}] {o[:80]}")
    print("=" * 70)


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="THRESHOLD_ONSET + SanTok — Production Master Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python master_onset.py compile "data/clean"
  python master_onset.py identity "Which language is best?"
  python master_onset.py invoke  "shard_00000" "Which language is best?"
        """
    )

    subparsers = parser.add_subparsers(dest="mode", help="Execution mode")

    # compile
    p_compile = subparsers.add_parser("compile", help="Compile corpus directory into matrices.")
    p_compile.add_argument("target", help="Path to file or directory of raw text data.")

    # identity
    p_id = subparsers.add_parser("identity", help="Run Phase 0-10 structural identity extraction.")
    p_id.add_argument("text", help="Seed text for identity extraction.")

    # invoke
    p_invoke = subparsers.add_parser("invoke", help="Full unification: identity → matrix → generation.")
    p_invoke.add_argument("corpus", help="Corpus name or path (e.g. shard_00000)")
    p_invoke.add_argument("text", help="Seed text for identity extraction and generation.")

    args = parser.parse_args()

    if args.mode == "compile":
        execute_compile(args.target)
    elif args.mode == "identity":
        execute_identity(args.text)
    elif args.mode == "invoke":
        execute_invoke(args.text, args.corpus)
    else:
        parser.print_help()
