#!/usr/bin/env python3
"""
MASTER ONSET DAEMON — Production Infinite Loop
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Boot once. Query forever.

SanTok Law 7 — Directional Escape Physics is now active.
The engine no longer echoes your input. It finds the ESCAPE BOUNDARY
of your input's identity cluster and generates from there — a RESPONSE.

Startup (~3-5 min for large corpus):
  [1] Load SanTok matrix into RAM permanently.
  [2] Load the Sovereign Language Brain (O(1) structural lookup).

Per query:
  If Brain loaded (Fast Path — <50ms):
    [3a] O(1) escape boundary resolution (Layer 3 & 4). 
    [4a] Law 8 Generation.
  If Brain missing (Slow Path — ~1200ms):
    [3b] Run THRESHOLD_ONSET Phase 0-10 to infer structural shape live.
    [4b] Law 8 Generation.


Usage:
  python master_daemon.py
"""

import sys
import os
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def resolve_corpus(raw_corpus):
    corpus_name = os.path.basename(raw_corpus)
    for ext in ["_santok_unified.jsonl", "_santok_unified.json", ".jsonl", ".json", ".txt", ".csv"]:
        corpus_name = corpus_name.replace(ext, "")

    if raw_corpus.endswith("_santok_unified.jsonl") and os.path.exists(raw_corpus):
        return raw_corpus
    if raw_corpus.endswith("_santok_unified.json") and os.path.exists(raw_corpus):
        return raw_corpus

    path = os.path.join(ROOT, "output", f"{corpus_name}_santok_unified.jsonl")
    if os.path.exists(path):
        return path
    path = os.path.join(ROOT, "output", f"{corpus_name}_santok_unified.json")
    if os.path.exists(path):
        return path
    return None


def main():
    print("=" * 70)
    print("  MASTER ONSET DAEMON")
    print("  SanTok Law 7 — Directional Escape Physics ACTIVE")
    print("=" * 70)

    # ── BOOT: Load corpus matrix ──────────────────────────────────────────────
    use_corpus = input(
        "\nEnter corpus name (e.g. 'shard_00000'), or press Enter to skip > "
    ).strip().replace("&", "").replace("'", "").replace('"', "").strip()

    engine = None

    if use_corpus:
        corpus_path = resolve_corpus(use_corpus)
        if not corpus_path:
            print(f"[!] Corpus '{use_corpus}' not found in output/.")
            print(f"    Run: python master_onset.py compile <data path>")
            print(f"    Continuing in THRESHOLD_ONSET-only mode.\n")
        else:
            print(f"\n[*] Booting SanTok Matrix: {os.path.basename(corpus_path)}")
            print(f"    Loading once. All queries will be near-instant after this.")
            from integration.santok_identity_bridge import ThresholdSantokBridge
            bridge = ThresholdSantokBridge(corpus_path)
            engine = bridge.engine
            print(f"[✓] Matrix locked in RAM. {len(engine.matrix):,} structural nodes ready.")

    # ── Import pipeline and escape physics ───────────────────────────────────
    print(f"\n[*] Initializing THRESHOLD_ONSET pipeline...")
    from integration.run_complete import run, PipelineConfig, tokenize_text
    from integration.santok_identity_bridge import (
        build_production_validator,
        find_escape_seed,
        extract_seed_from_identity,
    )
    cfg_template = PipelineConfig.from_project()
    cfg_template.show_tui = False
    print(f"[✓] Pipeline ready.")
    
    # ── BOOT: Load Sovereign Brain ──────────────────────────────────────────
    from integration.brain_loader import SovereignBrain
    brain = SovereignBrain()
    brain_active = brain.load()
    if brain_active:
        print(f"\n[✓] Sovereign Language Brain loaded: {brain.manifest.get('total_identities', 0):,} identities.")
        print(f"    Fast O(1) structural lookup enabled.")
    else:
        print(f"\n[!] Sovereign Brain not found. Run learn.py to build it.")
        print(f"    Falling back to slow Phase 0-10 structural inference per query.")



    print("\n" + "=" * 70)
    print("  DAEMON ACTIVE")
    print("  Type your seed text. Type 'exit' to stop.")
    print("=" * 70)

    # ── INFINITE QUERY LOOP ───────────────────────────────────────────────────
    while True:
        try:
            print()
            seed_text = input("Seed > ").strip()

            if not seed_text:
                continue
            if seed_text.lower() in ("exit", "quit", "q"):
                print("[*] Daemon halted.")
                break

            t0 = time.perf_counter()
            
            # ── FAST PATH: Layer 4 Lookup ──────────────────────────────
            if brain_active and engine:
                tokens = tokenize_text(seed_text, cfg_template.tokenization_method)
                b_word, esc_word, tension_class = brain.get_escape_seed(tokens)
                
                if b_word and esc_word:
                    # Find real Corpus CIDs corresponding to the words
                    cid1, cid2 = None, None
                    v1, v2 = None, None
                    
                    for cid, v in engine.vocab.items():
                        text_lower = v.get("text", "").lower()
                        if text_lower == b_word.lower() and cid1 is None:
                            cid1 = cid
                            v1 = v
                        elif text_lower == esc_word.lower() and cid2 is None:
                            cid2 = cid
                            v2 = v
                            
                        if cid1 and cid2:
                            break
                            
                    if cid1 and cid2:
                        escape_seed = [
                            {"text": v1["text"], "content_id": cid1, "frontend": v1["fe"], "backend_scaled": 0},
                            {"text": v2["text"], "content_id": cid2, "frontend": v2["fe"], "backend_scaled": 0}
                        ]
                        t_map = {"Aggressive": 1, "Neutral": 4, "Calm": 10}
                        tension_val = t_map.get(tension_class, 4)
                        
                        santok_output = engine.generate(
                            seed_tokens=escape_seed,
                            length=0, # Law 8 ignores length if until_sentence=True
                            until_sentence=True,
                            max_length=80,
                            tolerance=5000,
                            tension_threshold=tension_val
                        )
                        t_end = time.perf_counter()
                        print(f"\n  ┌─ SANTOK LAW 8 OUTPUT (O(1) Brain Lookup) {'─' * 20}┐")
                        print(f"  │  Seed: '{b_word}' → '{esc_word}' (Tension: {tension_class})")
                        print(f"  │  Time: {(t_end - t0)*1000:.0f}ms (Bypassed Phase 0-10)")
                        print(f"  │")
                        print(f"  │  {santok_output}")
                        print(f"  └{'─' * 55}┘")
                        continue # Done!

            # ── SLOW PATH: THRESHOLD_ONSET Phase 0-10 ───────────────────────────
            pipeline_result = run(
                text_override=seed_text,
                cfg=cfg_template,
                return_result=True,
                return_model_state=True
            )

            if not pipeline_result:
                print("[!] Pipeline failed. Try again.")
                continue

            t_identity = time.perf_counter()
            model_state = pipeline_result.model_state or {}

            # ── STEP B: Build production identity gate from topology ────────
            validator, tension_threshold, suppressed, promoted = build_production_validator(
                topology=pipeline_result.topology,
                path_scores=model_state.get("path_scores", {}),
                clusters=pipeline_result.clusters,
                symbol_to_token=model_state.get("symbol_to_token", {})
            )
            tension_map = {1: "Aggressive", 4: "Neutral", 10: "Calm"}

            # ── STEP C: Print THRESHOLD_ONSET's own structural outputs ──────
            print(f"\n  ┌─ THRESHOLD_ONSET STRUCTURAL OUTPUT ({'─' * 35}┐")
            print(f"  │  Identity: {pipeline_result.identity_count} ids │ "
                  f"Relations: {pipeline_result.relation_count} │ "
                  f"Tension: {tension_map.get(tension_threshold)} │ "
                  f"Time: {(t_identity-t0)*1000:.0f}ms")
            for i, out in enumerate(pipeline_result.generated_outputs[:2], 1):
                print(f"  │  [{i}] {out[:90]}")
            print(f"  └{'─' * 55}┘")

            # ── STEP D: SanTok Escape Physics Generation ───────────────────
            if engine:
                symbol_to_token = model_state.get("symbol_to_token", {})

                # LAW 7: Seed from ESCAPE BOUNDARY, not from input echo
                escape_seed = find_escape_seed(
                    engine=engine,
                    topology=pipeline_result.topology,
                    symbol_to_token=symbol_to_token
                )

                t_escape = time.perf_counter()

                if escape_seed and len(escape_seed) >= 2:
                    escape_mode = "Escape Boundary"
                    seed_display = f"'{escape_seed[0].get('text','')}' → '{escape_seed[1].get('text','')}'"
                else:
                    # Fallback: use identity seed (input-seeded)
                    escape_seed = extract_seed_from_identity(engine, seed_text)
                    escape_mode = "Identity Seed (fallback)"
                    seed_display = (
                        f"'{escape_seed[0].get('text','')}' → '{escape_seed[1].get('text','')}'"
                        if escape_seed and len(escape_seed) >= 2 else "random"
                    )

                santok_output = engine.generate(
                    seed_tokens=escape_seed,
                    length=40,
                    until_sentence=True,
                    max_length=80,
                    tolerance=5000,
                    identity_validator=validator,
                    tension_threshold=tension_threshold
                )

                t_end = time.perf_counter()
                print(f"\n  ┌─ SANTOK LAW 7 & 8 OUTPUT {escape_mode.ljust(26, ' ')} {'─' * 4}┐")
                print(f"  │  Seed: {seed_display}")
                print(f"  │  Time: {(t_end - t0)*1000:.0f}ms total")
                print(f"  │")
                print(f"  │  {santok_output}")
                print(f"  └{'─' * 55}┘")
            else:
                t_end = time.perf_counter()

        except KeyboardInterrupt:
            print("\n[!] Ctrl+C — Daemon halted.")
            break
        except Exception as e:
            print(f"[!] Fault in generation cycle: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
