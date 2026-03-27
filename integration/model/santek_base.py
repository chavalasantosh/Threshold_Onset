# """
# Canonical SanTEK base model surface: train, generate, eval.

# - Train on train split only; optional val/test for evaluation.
# - Generate refuses disconnected prompts instead of falling back to learned cycles.
# - Eval reports held-out accuracy and frequency baseline.

# Contract: docs/MODEL_CONTRACT.md, docs/GAP_TO_MODEL_ROADMAP.md.
# """

# from __future__ import annotations

# import hashlib
# import importlib.util
# import json
# import os
# import sys
# import time
# from collections import defaultdict
# from dataclasses import dataclass, field
# from datetime import datetime, timezone
# from pathlib import Path
# from typing import Any, Dict, List, Optional, Tuple

# # ─────────────────────────────────────────────────────────────────────────────
# # Types
# # ─────────────────────────────────────────────────────────────────────────────

# PathScores = Dict[Tuple[int, int], float]
# Vocab = Dict[int, str]


# @dataclass
# class SantekModel:
#     """Loaded SanTEK base model: path_scores + vocab + meta."""
#     path_scores: PathScores
#     vocab: Vocab
#     meta: Dict[str, Any] = field(default_factory=dict)


# @dataclass
# class EvalResult:
#     """Held-out eval: model accuracy, baseline accuracy, counts."""
#     model_accuracy: float
#     baseline_accuracy: float
#     total_predictions: int
#     model_correct: int
#     baseline_correct: int
#     error: Optional[str] = None


# # ─────────────────────────────────────────────────────────────────────────────
# # Repo / pipeline
# # ─────────────────────────────────────────────────────────────────────────────

# def _find_repo_root() -> Path:
#     """Locate repo root (containing integration/run_complete.py)."""
#     here = Path(os.path.abspath(__file__)).resolve().parent.parent.parent
#     for candidate in [here, here.parent, Path.cwd()]:
#         if (candidate / "integration" / "run_complete.py").exists():
#             return candidate
#     raise FileNotFoundError("Cannot find repo root (integration/run_complete.py).")


# def _load_pipeline(repo_root: Path):
#     """Load integration.run_complete module."""
#     rc_path = repo_root / "integration" / "run_complete.py"
#     if not rc_path.exists():
#         raise FileNotFoundError(f"Missing: {rc_path}")
#     spec = importlib.util.spec_from_file_location("run_complete", str(rc_path))
#     module = importlib.util.module_from_spec(spec)
#     sys.modules["run_complete"] = module
#     spec.loader.exec_module(module)
#     return module


# def _run_pipeline(rc_mod, text: str, show_tui: bool = False) -> Optional[Dict[str, Any]]:
#     """Run text through Phases 0–4; return model_state or None."""
#     try:
#         cfg = rc_mod.PipelineConfig.from_project()
#         cfg.show_tui = show_tui
#         cfg.tokenization_methods = [
#         "word", "character", "whitespace", "grammar",
#         "subword", "subword_bpe", "subword_syllable",
#         "subword_frequency", "byte"
#     ]
#         cfg.generation.num_sequences = 0   # ← ADD THIS
#         cfg.generation.steps = 0           # ← ADD THIS
#         cfg.continuation_text = text[:200]
#         result = rc_mod.run(
#             text_override=text,
#             cfg=cfg,
#             return_result=True,
#             return_model_state=True,
#         )
#         if result is None:
#             return None
#         return getattr(result, "model_state", None)
#     except Exception:
#         return None


# # ─────────────────────────────────────────────────────────────────────────────
# # Symbol sequence / vocab / path_scores from model state
# # ─────────────────────────────────────────────────────────────────────────────

# def _segment_hash(r_a: float, r_b: float) -> str:
#     return hashlib.md5(str((r_a, r_b)).encode("utf-8")).hexdigest()


# def extract_symbol_sequence(ms: Dict[str, Any]) -> List[int]:
#     """Ordered symbol sequence from Phase 0–4 model state."""
#     p2 = ms.get("phase2_metrics", {})
#     p4 = ms.get("phase4_metrics", {})
#     identity_mappings = p2.get("identity_mappings", {})
#     identity_to_symbol = p4.get("identity_to_symbol", {})
#     residue_sequences = ms.get("residue_sequences", [])

#     if not identity_mappings or not identity_to_symbol or not residue_sequences:
#         return []
#     run0 = residue_sequences[0]
#     if len(run0) < 2:
#         return []

#     seq: List[int] = []
#     for i in range(len(run0) - 1):
#         h = _segment_hash(float(run0[i]), float(run0[i + 1]))
#         identity = identity_mappings.get(h)
#         if identity is not None:
#             sym = identity_to_symbol.get(identity)
#             if sym is not None:
#                 seq.append(int(sym))
#     return seq


# def build_vocab(ms: Dict[str, Any]) -> Vocab:
#     """Symbol → token mapping from model state (first-seen wins)."""
#     p2 = ms.get("phase2_metrics", {})
#     p4 = ms.get("phase4_metrics", {})
#     tokens = ms.get("tokens", [])
#     residue_sequences = ms.get("residue_sequences", [])
#     identity_mappings = p2.get("identity_mappings", {})
#     identity_to_symbol = p4.get("identity_to_symbol", {})

#     if not tokens or not residue_sequences or not identity_mappings or not identity_to_symbol:
#         return {}

#     run0 = residue_sequences[0]
#     n_tok = min(len(tokens), len(run0))
#     vocab: Vocab = {}
#     for i in range(min(n_tok - 1, len(run0) - 1)):
#         h = _segment_hash(float(run0[i]), float(run0[i + 1]))
#         identity = identity_mappings.get(h)
#         if identity is None:
#             continue
#         sym = identity_to_symbol.get(identity)
#         if sym is None:
#             continue
#         sym = int(sym)
#         if sym not in vocab and i < len(tokens):
#             tok = str(tokens[i]).strip()
#             if tok:
#                 vocab[sym] = tok
#     return vocab


# def extract_path_scores(raw: Dict[Any, Any]) -> PathScores:
#     """Normalize path_scores to (int,int) -> float."""
#     ps: PathScores = {}
#     for edge, score in raw.items():
#         if not isinstance(edge, (list, tuple)) or len(edge) != 2:
#             continue
#         if not isinstance(score, (int, float)):
#             continue
#         key = (int(edge[0]), int(edge[1]))
#         ps[key] = max(ps.get(key, 0.0), float(score))
#     return ps


# def merge_path_scores(base: PathScores, new: PathScores) -> None:
#     for k, v in new.items():
#         base[k] = max(base.get(k, 0.0), v)


# def merge_vocab(base: Vocab, new: Vocab) -> None:
#     for sym, tok in new.items():
#         if sym not in base:
#             base[sym] = tok


# # ─────────────────────────────────────────────────────────────────────────────
# # Learning (ASD + decay)
# # ─────────────────────────────────────────────────────────────────────────────

# def _apply_decay(ps: PathScores, decay: float) -> None:
#     factor = 1.0 - decay
#     for k in ps:
#         ps[k] *= factor


# def _normalise(ps: PathScores) -> PathScores:
#     if not ps:
#         return {}
#     vals = list(ps.values())
#     lo, hi = min(vals), max(vals)
#     span = hi - lo
#     if span == 0.0:
#         return {k: 0.5 for k in ps}
#     return {k: (v - lo) / span for k, v in ps.items()}


# def _predict(current: int, ps: PathScores) -> Optional[int]:
#     """Argmax next symbol; no self-transition."""
#     best_sym, best_score = None, -1.0
#     for (fr, to), score in ps.items():
#         if fr == current and to != current and score > best_score:
#             best_sym, best_score = to, score
#     return best_sym


# def _tension(current: int, actual: int, norm: PathScores) -> float:
#     return 1.0 - norm.get((current, actual), 0.0)


# def _asd_update(
#     ps: PathScores,
#     streaks: Dict[Tuple[int, int], int],
#     current: int,
#     predicted: Optional[int],
#     actual: int,
#     tension_val: float,
#     eta: float,
#     max_streak: int,
# ) -> None:
#     correct_edge = (current, actual)
#     if predicted == actual:
#         ps[correct_edge] = ps.get(correct_edge, 0.0) + eta * (1.0 + tension_val)
#         if predicted is not None:
#             streaks[(current, predicted)] = 0
#     else:
#         ps[correct_edge] = ps.get(correct_edge, 0.0) + eta * (1.0 + tension_val)
#         if predicted is not None:
#             wrong_edge = (current, predicted)
#             streaks[wrong_edge] = min(streaks.get(wrong_edge, 0) + 1, max_streak)
#             mult = 1 + streaks[wrong_edge]
#             ps[wrong_edge] = max(0.0, ps.get(wrong_edge, 0.0) - eta * mult * (1.0 + tension_val))


# # ─────────────────────────────────────────────────────────────────────────────
# # Disconnected prompt
# # ─────────────────────────────────────────────────────────────────────────────

# def is_prompt_connected(last_symbol: int, path_scores: PathScores) -> bool:
#     """True if there is at least one outgoing edge from last_symbol (excluding self)."""
#     for (fr, to) in path_scores:
#         if fr == last_symbol and to != last_symbol:
#             return True
#     return False


# # ─────────────────────────────────────────────────────────────────────────────
# # Generation (anchor + cycle control + refusal) — uses integration.model.generator
# # ─────────────────────────────────────────────────────────────────────────────

# def generate_symbols(
#     start_seq: List[int],
#     path_scores: PathScores,
#     length: int,
#     recency_window: int = 6,
#     recency_penalty: float = 0.30,
#     bigram_penalty: float = 0.20,
#     trigram_penalty: float = 0.35,
# ) -> List[int]:
#     """Extend sequence with cycle control (2-gram and 3-gram penalties). Delegates to generator."""
#     from integration.model.generator import generate_symbols_with_cycle_control
#     return generate_symbols_with_cycle_control(
#         start_seq, path_scores, length,
#         recency_window=recency_window,
#         recency_penalty=recency_penalty,
#         bigram_penalty=bigram_penalty,
#         trigram_penalty=trigram_penalty,
#     )


# def symbols_to_text(symbols: List[int], vocab: Vocab) -> str:
#     """Decode symbol sequence to text. Delegates to generator."""
#     from integration.model.generator import symbols_to_text as _st
#     return _st(symbols, vocab)


# def generate(
#     prompt: str,
#     model: SantekModel,
#     repo_root: Path,
#     length: int = 20,
#     refuse_if_disconnected: bool = True,
# ) -> Tuple[str, bool]:
#     """
#     Generate text from prompt. Returns (output_text, was_refused).

#     Anchor = last prompt symbol that exists in the learned graph. Only that suffix
#     is used; if none, refuse. No fallback to global-best-edge. Extension uses
#     cycle control (2-gram and 3-gram penalties).
#     """
#     from integration.model.generator import last_connected_anchor, generate_symbols_with_cycle_control, symbols_to_text as _symbols_to_text

#     rc = _load_pipeline(repo_root)
#     ms = _run_pipeline(rc, prompt, show_tui=False)
#     vocab = dict(model.vocab)
#     if ms is not None:
#         prompt_symbols = extract_symbol_sequence(ms)
#         merge_vocab(vocab, build_vocab(ms))
#     else:
#         if refuse_if_disconnected:
#             return (
#                 "[Refused: prompt could not be parsed by the pipeline.]",
#                 True,
#             )
#         if not model.path_scores:
#             return ("[Refused: no model edges.]", True)
#         return (
#             "[Refused: prompt could not be parsed; no fallback to canned output.]",
#             True,
#         )

#     if not prompt_symbols:
#         if refuse_if_disconnected:
#             return ("[Refused: prompt produced no symbol sequence.]", True)
#         return ("[Refused: no symbol sequence.]", True)

#     connected_prefix, anchor = last_connected_anchor(prompt_symbols, model.path_scores)
#     if anchor is None:
#         return (
#             "[Refused: prompt is disconnected from the learned graph; continuing would ignore your words.]",
#             True,
#         )

#     extended = generate_symbols_with_cycle_control(
#         [anchor], model.path_scores, length,
#     )
#     full_seq = connected_prefix + extended[1:]
#     return _symbols_to_text(full_seq, vocab), False


# santek_generate = generate  # public alias


# # ─────────────────────────────────────────────────────────────────────────────
# # Train
# # ─────────────────────────────────────────────────────────────────────────────

# def train(
#     corpus: List[str],
#     repo_root: Path,
#     epochs: int = 100,
#     eta: float = 0.10,
#     decay: float = 0.05,
#     max_streak: int = 3,
#     tension_threshold: float = 0.10,
#     patience: int = 5,
# ) -> SantekModel:
#     """
#     Train on corpus only (no val/test used). Returns SantekModel with path_scores, vocab, meta.
#     """
#     rc = _load_pipeline(repo_root)
#     text_ps: List[PathScores] = []
#     text_streaks: List[Dict[Tuple[int, int], int]] = []
#     text_seqs: List[List[int]] = []
#     global_vocab: Vocab = {}
#     valid_idx: List[int] = []

#     for i, text in enumerate(corpus):
#         ms = _run_pipeline(rc, text, show_tui=False)
#         if ms is None:
#             text_ps.append({})
#             text_streaks.append(defaultdict(int))
#             text_seqs.append([])
#             continue
#         ps = extract_path_scores(ms.get("path_scores", {}))
#         seq = extract_symbol_sequence(ms)
#         vocab = build_vocab(ms)
#         text_ps.append(ps)
#         text_streaks.append(defaultdict(int))
#         text_seqs.append(seq)
#         merge_vocab(global_vocab, vocab)
#         valid_idx.append(i)

#     if not valid_idx:
#         raise ValueError("No valid pipeline results from corpus.")

#     best_accuracy = 0.0
#     best_tension = float("inf")
#     prev_tension = float("inf")
#     plateau_count = 0
#     epoch = 0

#     for epoch in range(1, epochs + 1):
#         correct = total = 0
#         all_tensions: List[float] = []
#         for i in valid_idx:
#             ps = text_ps[i]
#             stk = text_streaks[i]
#             seq = text_seqs[i]
#             _apply_decay(ps, decay)
#             snapshot = dict(ps)
#             norm = _normalise(snapshot)
#             for step in range(len(seq) - 1):
#                 cur, actual = seq[step], seq[step + 1]
#                 if cur == actual:
#                     continue
#                 pred = _predict(cur, snapshot)
#                 t_val = _tension(cur, actual, norm)
#                 all_tensions.append(t_val)
#                 if pred == actual:
#                     correct += 1
#                 total += 1
#                 _asd_update(ps, stk, cur, pred, actual, t_val, eta, max_streak)

#         if total > 0:
#             raw_acc = correct / total
#             if raw_acc > best_accuracy:
#                 best_accuracy = raw_acc
#             mean_t = sum(all_tensions) / len(all_tensions) if all_tensions else 1.0
#             if mean_t < best_tension:
#                 best_tension = mean_t
#             if mean_t < tension_threshold:
#                 break
#             if abs(mean_t - prev_tension) < 1e-7:
#                 plateau_count += 1
#             else:
#                 plateau_count = 0
#             prev_tension = mean_t
#             if plateau_count >= patience:
#                 break

#     global_ps: PathScores = {}
#     for i in valid_idx:
#         merge_path_scores(global_ps, text_ps[i])

#     meta = {
#         "corpus_size": len(corpus),
#         "valid_texts": len(valid_idx),
#         "epochs_run": epoch,
#         "best_accuracy": best_accuracy,
#         "best_tension": best_tension,
#         "eta": eta,
#         "decay": decay,
#         "max_streak": max_streak,
#         "vocab_size": len(global_vocab),
#         "edge_count": len(global_ps),
#     }
#     return SantekModel(path_scores=global_ps, vocab=global_vocab, meta=meta)


# # Public alias for "train" to avoid shadowing in callers
# santek_train = train


# # ─────────────────────────────────────────────────────────────────────────────
# # Save / load
# # ─────────────────────────────────────────────────────────────────────────────

# def save_santek_model(
#     model: SantekModel,
#     path: Path,
#     *,
#     training_config: Optional[Dict[str, Any]] = None,
#     split_manifest: Optional[Any] = None,
# ) -> Path:
#     """Save model artifact. Optional training_config and split_manifest for reproducibility."""
#     path.parent.mkdir(parents=True, exist_ok=True)
#     payload: Dict[str, Any] = {
#         "version": 1,
#         "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
#         "meta": model.meta,
#         "path_scores": [[a, b, v] for (a, b), v in model.path_scores.items()],
#         "vocab": {str(k): v for k, v in model.vocab.items()},
#     }
#     if training_config is not None:
#         payload["training_config"] = training_config
#     if split_manifest is not None:
#         payload["split_manifest"] = getattr(split_manifest, "to_dict", lambda: split_manifest)()
#     with open(path, "w", encoding="utf-8") as f:
#         json.dump(payload, f, indent=2)
#     return path


# def load_santek_model(path: Path) -> SantekModel:
#     if not path.exists():
#         raise FileNotFoundError(f"Model not found: {path}")
#     with open(path, encoding="utf-8") as f:
#         payload = json.load(f)
#     ps_list = payload.get("path_scores", [])
#     ps: PathScores = {}
#     for row in ps_list:
#         if len(row) >= 3:
#             ps[(int(row[0]), int(row[1]))] = float(row[2])
#     vocab = {int(k): v for k, v in payload.get("vocab", {}).items()}
#     meta = dict(payload.get("meta", {}))
#     if "training_config" in payload:
#         meta["training_config"] = payload["training_config"]
#     if "split_manifest" in payload:
#         meta["split_manifest"] = payload["split_manifest"]
#     return SantekModel(path_scores=ps, vocab=vocab, meta=meta)


# # ─────────────────────────────────────────────────────────────────────────────
# # Eval: held-out + frequency baseline
# # ─────────────────────────────────────────────────────────────────────────────

# def _transition_counts_from_sequences(sequences: List[List[int]]) -> Dict[Tuple[int, int], int]:
#     """(cur, next) -> count over all sequences (no self-transitions)."""
#     counts: Dict[Tuple[int, int], int] = defaultdict(int)
#     for seq in sequences:
#         for i in range(len(seq) - 1):
#             a, b = seq[i], seq[i + 1]
#             if a != b:
#                 counts[(a, b)] += 1
#     return dict(counts)


# def _baseline_predict(current: int, train_counts: Dict[Tuple[int, int], int]) -> Optional[int]:
#     """Predict next = most frequent (current, *) in train."""
#     best_next, best_count = None, -1
#     for (fr, to), c in train_counts.items():
#         if fr == current and c > best_count:
#             best_next, best_count = to, c
#     return best_next


# def eval_held_out(
#     model_path: Path,
#     repo_root: Path,
#     train_docs: List[str],
#     val_docs: List[str],
# ) -> EvalResult:
#     """
#     Run pipeline on train_docs and val_docs to get symbol sequences.
#     Model: load path_scores from model_path; predict next = argmax path_scores from current.
#     Baseline: predict next = most frequent (current, next) in train sequences.
#     Report model accuracy and baseline accuracy on val.
#     """
#     if not val_docs:
#         return EvalResult(
#             model_accuracy=0.0,
#             baseline_accuracy=0.0,
#             total_predictions=0,
#             model_correct=0,
#             baseline_correct=0,
#             error="No validation documents.",
#         )

#     try:
#         model = load_santek_model(model_path)
#     except FileNotFoundError as e:
#         return EvalResult(
#             model_accuracy=0.0,
#             baseline_accuracy=0.0,
#             total_predictions=0,
#             model_correct=0,
#             baseline_correct=0,
#             error=str(e),
#         )

#     rc = _load_pipeline(repo_root)
#     train_seqs: List[List[int]] = []
#     for text in train_docs:
#         ms = _run_pipeline(rc, text, show_tui=False)
#         if ms is not None:
#             seq = extract_symbol_sequence(ms)
#             if len(seq) >= 2:
#                 train_seqs.append(seq)

#     val_seqs: List[List[int]] = []
#     for text in val_docs:
#         ms = _run_pipeline(rc, text, show_tui=False)
#         if ms is not None:
#             seq = extract_symbol_sequence(ms)
#             if len(seq) >= 2:
#                 val_seqs.append(seq)

#     if not val_seqs:
#         return EvalResult(
#             model_accuracy=0.0,
#             baseline_accuracy=0.0,
#             total_predictions=0,
#             model_correct=0,
#             baseline_correct=0,
#             error="No validation sequences (pipeline produced no valid sequences).",
#         )

#     train_counts = _transition_counts_from_sequences(train_seqs)
#     ps = model.path_scores

#     model_correct = baseline_correct = total = 0
#     for seq in val_seqs:
#         for i in range(len(seq) - 1):
#             cur, actual = seq[i], seq[i + 1]
#             if cur == actual:
#                 continue
#             total += 1
#             pred_model = _predict(cur, ps)
#             pred_baseline = _baseline_predict(cur, train_counts)
#             if pred_model == actual:
#                 model_correct += 1
#             if pred_baseline == actual:
#                 baseline_correct += 1

#     if total == 0:
#         return EvalResult(
#             model_accuracy=0.0,
#             baseline_accuracy=0.0,
#             total_predictions=0,
#             model_correct=0,
#             baseline_correct=0,
#             error="No valid prediction steps in validation sequences.",
#         )

#     return EvalResult(
#         model_accuracy=model_correct / total,
#         baseline_accuracy=baseline_correct / total,
#         total_predictions=total,
#         model_correct=model_correct,
#         baseline_correct=baseline_correct,
#     )




"""
santek_base.py  ·  SanTEK Structural Learning Engine  v4
══════════════════════════════════════════════════════════════════════════════

THRESHOLD_ONSET / SanTOK / SanVerse / Sanformers
Author: Chavala Santosh

─────────────────────────────────────────────────────────────────────────────
WHAT IS NEW IN v4  (10x upgrade over v3)
─────────────────────────────────────────────────────────────────────────────

  v3 problems fixed:
  ──────────────────
  1. SINGLE TOKENIZATION METHOD
     v3 only used "word". The pipeline can run up to 9 tokenizers (incl. byte).
     v4: _run_pipeline_all_methods() runs the configured method list per text
         (default: all except ``byte`` — use env SANTEK_INCLUDE_BYTE=1 for byte)
         and merges all model_states. More tokenizers ⇒ more structural evidence.

  2. IDENTICAL RUNS (num_runs=3 → same output 3 times)
     v3 ran the same method 3 times → identical residues every run.
     v4: each run uses a DIFFERENT tokenization method. Runs are structurally
         distinct. Phase 2/3 persistence requires CROSS-METHOD agreement →
         only truly stable structures survive.

  3. SYMBOL SEQUENCE FROM RUN 0 ONLY
     v3 _get_symbol_sequence() read residue_sequences[0] and discarded all
     other runs. v4 extracts sequences from ALL runs, deduplicates, and
     merges into one richer sequence per text.

  4. MERGE BY MAX (loses evidence)
     v3 merge_path_scores used max(). v4 uses ADDITIVE merge then normalises.
     More observations of an edge → stronger signal, not just the loudest.

  5. GENERIC CONTINUATION TEXTS
     v3 continuation used pipeline meta-sentences unrelated to the corpus.
     Topology measured 5 irrelevant nodes.
     v4: continuation_text = actual input text (first 300 chars).
     Topology now measures the real domain structure.

  6. VOCAB BUILT FROM RUN 0 ONLY
     v4 build_vocab_all_runs() builds vocab from all residue_sequences runs,
     giving richer symbol→token coverage.

  7. ASD ASYMMETRY BUG
     v3 wrong-edge penalised incorrectly. v4 uses correct ASD formula:
       correct: += eta * (1 - tension)
       wrong:   -= eta * tension * multiplier  (floor 0)

  8. final_path_scores = first valid text only
     v3 only returned path_scores from corpus[0]. v4 merges ALL text
     path_scores into a single global model.

  9. NO PROGRESS DISPLAY DURING INIT
     v4 shows per-text progress with edges, identities, sequence length,
     and which methods contributed data.

  10. NO SAVE / LOAD / GENERATE / EVAL in train loop
      v4 has full cmd_train(), cmd_generate(), cmd_chat(), cmd_eval(),
      cmd_info() with the canonical santek_base_model.json format.

─────────────────────────────────────────────────────────────────────────────
ARCHITECTURE
─────────────────────────────────────────────────────────────────────────────

  Input text
      │
      ▼
  _run_pipeline_all_methods()   ← runs each tokenizer in ``methods`` (default 8; +byte if opted in)
      │  merges model_states from all tokenizer runs
      ▼
  _extract_all_sequences()      ← symbol sequences from ALL runs
  _build_path_scores_additive() ← additive merge, not max
  _build_vocab_all_runs()       ← vocab from all runs
      │
      ▼
  santek_train()                ← ASD learning loop
      │  per-text path_scores + streaks
      │  global merge at end
      ▼
  save_base_model()             ← output/santek_base_model.json

─────────────────────────────────────────────────────────────────────────────
USAGE
─────────────────────────────────────────────────────────────────────────────
  python santek_base_model.py train --corpus data/hindu_corpus_real.jsonl
  python santek_base_model.py generate "Om Namah Shivaya"
  python santek_base_model.py chat
  python santek_base_model.py eval
  python santek_base_model.py info
─────────────────────────────────────────────────────────────────────────────
Zero third-party libraries. Pure Python stdlib only.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import hashlib
import importlib.util
import json
import logging
import os
import queue
import sys
import tempfile
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from integration.runtime import JobSpec, run_tasks
    _HAS_RUNTIME_EXECUTOR = True
except Exception:  # pragma: no cover - optional hardening
    JobSpec = None  # type: ignore[assignment]
    run_tasks = None  # type: ignore[assignment]
    _HAS_RUNTIME_EXECUTOR = False

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("santek_base")

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

ALL_TOKENIZATION_METHODS = [
    "word",
    "whitespace",
    "character",
    "grammar",
    "subword",
    "subword_bpe",
    "subword_syllable",
    "subword_frequency",
    "byte",
]

DEFAULT_MODEL_PATH = Path("output/santek_base_model.json")


def _default_training_methods() -> List[str]:
    """
    Default corpus-training tokenizers: the 8 pipeline methods other than ``byte``.

    (``ALL_TOKENIZATION_METHODS`` lists 9 names; ``byte`` is omitted here unless
    you set ``SANTEK_INCLUDE_BYTE=1``. Worker env vars like ``SANTEK_METHOD_WORKERS``
    only change parallelism, not this list.)

    Rationale: byte-level training duplicates coverage when a dedicated byte
    model already exists; it also amplifies numeric-looking vocab tokens.
    """
    if _env_flag("SANTEK_INCLUDE_BYTE", default=False):
        return list(ALL_TOKENIZATION_METHODS)
    return [m for m in ALL_TOKENIZATION_METHODS if m != "byte"]


# Concurrent pipeline runs may trip ``redirect_stdout`` / shared stdio paths.
# Serialize pipeline execution that wraps sys.stdout/sys.stderr in each process.
_PIPELINE_STDIO_LOCK = threading.Lock()

DEFAULT_CORPUS = [
    "Action before knowledge. Function stabilizes before meaning appears.",
    "Structure emerges before language exists.",
    "Hash to residue. Residue to identity. Identity to symbol.",
    "Tokens become residues. Residues form segments. Segments earn identity.",
    "Constraint bounds generation. No self-transition allowed.",
    "Boundary detection clusters the opaque trace.",
    "Repetition earns persistence. Persistence earns identity.",
    "chinni gunde lo anni asala.",
    "inka yenni dhachi navoo dhanni lona.",
    "oohaa lo illa telave ala telave illa telave.",
]

# ─────────────────────────────────────────────────────────────────────────────
# Types
# ─────────────────────────────────────────────────────────────────────────────

PathScores = Dict[Tuple[int, int], float]
Vocab = Dict[int, str]


@dataclass
class SantekModel:
    """Loaded SanTEK base model: path_scores + vocab + meta."""
    path_scores: PathScores
    vocab: Vocab
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SanTEKEpochResult:
    epoch: int
    correct: int
    total: int
    raw_accuracy: float
    accuracy_9centric: int
    mean_tension: float
    updates: int
    elapsed_ms: float


@dataclass
class SanTEKTrainingResult:
    converged: bool
    converged_at_epoch: Optional[int]
    total_epochs_run: int
    best_accuracy: float = 0.0
    best_9centric: int = 1
    best_tension: float = 1.0  # lowest mean epoch tension seen (easier structure)
    epochs: List[SanTEKEpochResult] = field(default_factory=list)
    final_path_scores: PathScores = field(default_factory=dict)
    global_vocab: Vocab = field(default_factory=dict)


@dataclass
class EvalResult:
    model_accuracy: float
    baseline_accuracy: float
    total_predictions: int
    model_correct: int
    baseline_correct: int
    error: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline loader
# ─────────────────────────────────────────────────────────────────────────────

def _load_run_complete():
    """Load integration/run_complete.py from repo root."""
    here = Path(os.path.abspath(__file__)).parent
    for candidate in [here, here.parent, Path.cwd()]:
        rc_path = candidate / "integration" / "run_complete.py"
        if rc_path.exists():
            spec = importlib.util.spec_from_file_location("run_complete", str(rc_path))
            mod = importlib.util.module_from_spec(spec)
            sys.modules["run_complete"] = mod
            spec.loader.exec_module(mod)
            return mod
    raise FileNotFoundError(
        "Cannot find integration/run_complete.py. Run from THRESHOLD_ONSET repo root."
    )


_PIPELINE_FAILURE_LOG_COUNT: List[int] = [0]  # mutable ref for rate-limiting


def _run_pipeline_single(rc_mod, text: str, method: str) -> Optional[Dict[str, Any]]:
    """
    Run pipeline for ONE tokenization method. Returns model_state or None.
    Generation is skipped (num_sequences=0, steps=0) for speed.
    Continuation text = actual input text (not generic meta-sentences).
    """
    try:
        cfg = rc_mod.PipelineConfig.from_project()
        cfg.show_tui = False
        cfg.tokenization_method = method
        cfg.tokenization_methods = None          # single method run
        cfg.corpus.enabled = False               # avoid expensive corpus state I/O
        cfg.generation.num_sequences = 0         # skip generation
        cfg.generation.steps = 0                 # skip generation
        cfg.continuation_text = text[:300]       # use real domain text
        cfg.continuation_texts = None
        verbose_pipeline = _env_flag("SANTEK_PIPELINE_VERBOSE", default=False)
        if verbose_pipeline:
            result = rc_mod.run(
                text_override=text,
                cfg=cfg,
                return_result=True,
                return_model_state=True,
            )
        else:
            # Suppress per-method pipeline console output during corpus training init.
            # Serialize stdio redirection: concurrent threads + redirect_stdout can
            # trigger "I/O operation on closed file" inside the pipeline stack.
            with _PIPELINE_STDIO_LOCK:
                with open(os.devnull, "w", encoding="utf-8") as sink:
                    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                        result = rc_mod.run(
                            text_override=text,
                            cfg=cfg,
                            return_result=True,
                            return_model_state=True,
                        )
        if result is None:
            return None
        ms = getattr(result, "model_state", None)
        if ms is None and _PIPELINE_FAILURE_LOG_COUNT[0] < 3:
            _PIPELINE_FAILURE_LOG_COUNT[0] += 1
            log.warning(
                "Pipeline returned no model_state method=%s text=%r",
                method, (text[:60] + "…") if len(text) > 60 else text,
            )
        return ms
    except Exception as exc:
        if _PIPELINE_FAILURE_LOG_COUNT[0] < 3:
            _PIPELINE_FAILURE_LOG_COUNT[0] += 1
            log.warning(
                "Pipeline failed method=%s text=%r: %s",
                method, (text[:60] + "…") if len(text) > 60 else text, exc,
            )
        return None


def _run_pipeline_all_methods(
    rc_mod,
    text: str,
    methods: Optional[List[str]] = None,
    max_method_workers: int = 1,
) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Run pipeline for each requested tokenization method. Returns list of (method, model_state).
    Skips methods that fail. Always returns at least [] (never raises).

    Multiple tokenization perspectives on the same text → richer identity/relation
    graph after merging. Default training set excludes ``byte`` unless
    ``SANTEK_INCLUDE_BYTE=1``.
    """
    if methods is None:
        methods = _default_training_methods()

    results: List[Tuple[str, Dict[str, Any]]] = []
    workers = max(1, int(max_method_workers))
    if workers == 1 or len(methods) <= 1:
        for method in methods:
            ms = _run_pipeline_single(rc_mod, text, method)
            if ms is not None:
                results.append((method, ms))
        return results

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(workers, len(methods)),
        thread_name_prefix="santek-method",
    ) as executor:
        fut_to_method = {
            executor.submit(_run_pipeline_single, rc_mod, text, method): method
            for method in methods
        }
        for fut in concurrent.futures.as_completed(fut_to_method):
            method = fut_to_method[fut]
            try:
                ms = fut.result()
            except Exception as exc:  # pylint: disable=broad-exception-caught
                log.debug("Method worker failed method=%s text=%r: %s", method, text[:40], exc)
                continue
            if ms is not None:
                results.append((method, ms))
    return results


@contextlib.contextmanager
def _temporary_env(overrides: Dict[str, str]):
    """Temporarily set environment variables, then restore previous values."""
    if not overrides:
        yield
        return

    previous: Dict[str, Optional[str]] = {}
    for key, value in overrides.items():
        previous[key] = os.environ.get(key)
        os.environ[key] = value
    try:
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def _env_flag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


def _training_fast_env_overrides() -> Dict[str, str]:
    """
    Opt-in training fast preset:
      - skips Phase 1 pairwise distances
      - skips Phase 3 path-length BFS
    Only applies when SANTEK_TRAIN_FAST is enabled.
    """
    if not _env_flag("SANTEK_TRAIN_FAST", default=True):
        return {}
    overrides: Dict[str, str] = {}
    if "PHASE1_SKIP_DISTANCES" not in os.environ:
        overrides["PHASE1_SKIP_DISTANCES"] = "1"
    if "PHASE3_SKIP_PATH_LENGTHS" not in os.environ:
        overrides["PHASE3_SKIP_PATH_LENGTHS"] = "1"
    return overrides


def _env_int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return max(minimum, int(raw))
    except ValueError:
        return default


# Aggregates merged Phase 10 across corpus texts (optional; see SANTEK_PHASE10_TRAINING_SUMMARY).
_P10_TRAIN_SUM_LOCK = threading.Lock()
_P10_TRAIN_SUM: Dict[str, int] = {
    "texts_observed": 0,
    "total_transitions": 0,
    "gate_passed_texts": 0,
    "universe_size_sum": 0,
}


def _phase10_training_summary_reset() -> None:
    """Clear training-wide Phase 10 counters (no-op if env flag off)."""
    if not _env_flag("SANTEK_PHASE10_TRAINING_SUMMARY", default=False):
        return
    with _P10_TRAIN_SUM_LOCK:
        _P10_TRAIN_SUM["texts_observed"] = 0
        _P10_TRAIN_SUM["total_transitions"] = 0
        _P10_TRAIN_SUM["gate_passed_texts"] = 0
        _P10_TRAIN_SUM["universe_size_sum"] = 0


def _phase10_training_merge_row(row: Optional[Dict[str, Any]]) -> None:
    """Merge one text's Phase 10 row into global training summary (thread-safe)."""
    if not row or not _env_flag("SANTEK_PHASE10_TRAINING_SUMMARY", default=False):
        return
    with _P10_TRAIN_SUM_LOCK:
        _P10_TRAIN_SUM["texts_observed"] += 1
        _P10_TRAIN_SUM["total_transitions"] += int(row.get("transitions") or 0)
        if row.get("gate_passed"):
            _P10_TRAIN_SUM["gate_passed_texts"] += 1
        _P10_TRAIN_SUM["universe_size_sum"] += int(row.get("universe_size") or 0)


def _phase10_training_accumulate(method_states: List[Tuple[str, Dict[str, Any]]]) -> None:
    """Main process: merged Phase 10 per text for end-of-training meta (compact sums only)."""
    if not _env_flag("SANTEK_PHASE10_TRAINING_SUMMARY", default=False):
        return
    if not method_states:
        return
    try:
        from threshold_onset.phase10 import run_phase10_from_method_states

        r = run_phase10_from_method_states(method_states)
        _phase10_training_merge_row(
            {
                "transitions": int(r.total_transitions),
                "gate_passed": bool(r.gate_passed),
                "universe_size": len(r.universe_ids),
            }
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        log.debug("phase10 training summary accumulate skip: %s", exc)


def _phase10_training_summary_snapshot() -> Optional[Dict[str, Any]]:
    """JSON-safe dict for model meta, or None if feature disabled / no data."""
    if not _env_flag("SANTEK_PHASE10_TRAINING_SUMMARY", default=False):
        return None
    with _P10_TRAIN_SUM_LOCK:
        n = int(_P10_TRAIN_SUM["texts_observed"])
        if n <= 0:
            return {
                "texts_observed": 0,
                "note": "no texts accumulated (check pipeline / corpus)",
            }
        u_sum = int(_P10_TRAIN_SUM["universe_size_sum"])
        return {
            "texts_observed": n,
            "total_directed_transitions": int(_P10_TRAIN_SUM["total_transitions"]),
            "texts_phase10_gate_passed": int(_P10_TRAIN_SUM["gate_passed_texts"]),
            "mean_universe_size_per_text": round(u_sum / n, 4),
        }


def _resolve_worker_plan(corpus_size: int, method_count: int) -> Tuple[int, int, str]:
    """
    Resolve text/method worker plan.

    ``SANTEK_TEXT_WORKERS`` / ``SANTEK_METHOD_WORKERS`` set **parallelism only**
    (how many texts or method-tasks run at once). They do **not** change which
    tokenizers run; that list is ``methods`` / ``_default_training_methods()``
    (byte is excluded unless ``SANTEK_INCLUDE_BYTE=1``).

    - Manual env overrides always win.
    - Default profile is "max": use full CPU for text-level workers.
    """
    cpu_count = os.cpu_count() or 4
    profile = os.environ.get("SANTEK_THROUGHPUT_PROFILE", "max").strip().lower() or "max"

    has_text_override = "SANTEK_TEXT_WORKERS" in os.environ
    has_method_override = "SANTEK_METHOD_WORKERS" in os.environ
    if has_text_override or has_method_override:
        default_text = min(corpus_size, max(1, cpu_count))
        text_workers = _env_int("SANTEK_TEXT_WORKERS", default_text, minimum=1)
        default_method = 1 if text_workers > 1 else min(4, max(1, method_count))
        method_workers = _env_int("SANTEK_METHOD_WORKERS", default_method, minimum=1)
        return text_workers, method_workers, "manual"

    if profile == "legacy":
        text_workers = min(corpus_size, max(1, cpu_count - 1))
    else:
        # "max" (default): consume full available CPU at text level.
        text_workers = min(corpus_size, max(1, cpu_count))
    method_workers = 1 if text_workers > 1 else min(4, max(1, method_count))
    return max(1, text_workers), max(1, method_workers), profile


def _process_text_worker(
    payload: Tuple[int, str, List[str], int]
) -> Tuple[
    int,
    Optional[PathScores],
    Optional[List[int]],
    Optional[Vocab],
    int,
    int,
    float,
    Optional[str],
    Optional[Dict[str, Any]],
]:
    """
    Worker entrypoint for per-text parallel init.
    Returns (idx, path_scores, seq, vocab, method_count, identity_count, elapsed_ms, error, phase10_row).

    ``phase10_row`` is set when ``SANTEK_PHASE10_TRAINING_SUMMARY=1`` (merged Phase 10 for this text);
    parent merges rows into ``meta.phase10_training_summary`` on final save.
    """
    idx, text, methods, method_workers = payload
    t_text = time.time()
    try:
        rc = _load_run_complete()
        method_states = _run_pipeline_all_methods(
            rc, text, methods, max_method_workers=max(1, int(method_workers))
        )
        if not method_states:
            return idx, None, None, None, 0, 0, (time.time() - t_text) * 1000.0, "all methods failed", None

        ps = _build_path_scores_additive(method_states)
        seq = _get_symbol_sequence_multi_state(method_states)
        vocab = _build_vocab_all_methods(method_states)
        n_id = max(
            len(ms.get("phase4_metrics", {}).get("identity_to_symbol", {}))
            for _, ms in method_states
        )
        p10_row: Optional[Dict[str, Any]] = None
        if _env_flag("SANTEK_PHASE10_TRAINING_SUMMARY", default=False):
            try:
                from threshold_onset.phase10 import run_phase10_from_method_states

                r = run_phase10_from_method_states(method_states)
                p10_row = {
                    "transitions": int(r.total_transitions),
                    "gate_passed": bool(r.gate_passed),
                    "universe_size": len(r.universe_ids),
                }
            except Exception:
                p10_row = None
        if _env_flag("SANTEK_PHASE10_MERGED_DEBUG", default=False):
            try:
                from threshold_onset.phase10 import run_phase10_from_method_states

                m10 = run_phase10_from_method_states(method_states)
                log.debug(
                    "phase10_merged worker idx=%s methods=%s gate=%s transitions=%s universe=%s",
                    idx,
                    len(method_states),
                    m10.gate_passed,
                    m10.total_transitions,
                    len(m10.universe_ids),
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                log.debug("phase10_merged worker skip: %s", exc)
        return idx, ps, seq, vocab, len(method_states), n_id, (time.time() - t_text) * 1000.0, None, p10_row
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return idx, None, None, None, 0, 0, (time.time() - t_text) * 1000.0, str(exc), None


# ─────────────────────────────────────────────────────────────────────────────
# Segment hash — must match Phase 2 exactly
# ─────────────────────────────────────────────────────────────────────────────

def _segment_hash(r_a: float, r_b: float) -> str:
    return hashlib.md5(str((r_a, r_b)).encode("utf-8")).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Symbol sequence extraction
# ─────────────────────────────────────────────────────────────────────────────

def _get_symbol_sequence_from_run(
    run_residues: List[float],
    identity_mappings: Dict[str, str],
    identity_to_symbol: Dict[str, str],
) -> List[int]:
    """Extract symbol sequence from one residue run."""
    if len(run_residues) < 2:
        return []
    seq = []
    for i in range(len(run_residues) - 1):
        h = _segment_hash(float(run_residues[i]), float(run_residues[i + 1]))
        identity = identity_mappings.get(h)
        if identity is not None:
            sym = identity_to_symbol.get(identity)
            if sym is not None:
                seq.append(int(sym))
    return seq


def _get_symbol_sequence(model_state: Dict[str, Any]) -> List[int]:
    """
    Extract symbol sequence from ALL runs and merge.
    v3 only read run 0. v4 reads all runs and concatenates unique transitions.
    """
    p2 = model_state.get("phase2_metrics", {})
    p4 = model_state.get("phase4_metrics", {})
    identity_mappings = p2.get("identity_mappings", {})
    identity_to_symbol = p4.get("identity_to_symbol", {})
    residue_sequences = model_state.get("residue_sequences", [])

    if not identity_mappings or not identity_to_symbol or not residue_sequences:
        return []

    # Collect sequences from all runs
    all_seqs: List[List[int]] = []
    for run_residues in residue_sequences:
        seq = _get_symbol_sequence_from_run(
            run_residues, identity_mappings, identity_to_symbol
        )
        if seq:
            all_seqs.append(seq)

    if not all_seqs:
        return []

    # Use first run as primary, append transitions from other runs not in primary
    # This preserves order while adding coverage
    primary = all_seqs[0]
    seen_transitions = set(
        (primary[i], primary[i + 1])
        for i in range(len(primary) - 1)
    )
    extended = list(primary)
    for seq in all_seqs[1:]:
        for i in range(len(seq) - 1):
            t = (seq[i], seq[i + 1])
            if t not in seen_transitions:
                seen_transitions.add(t)
                extended.append(seq[i])
                extended.append(seq[i + 1])

    return extended


def _get_symbol_sequence_multi_state(
    method_states: List[Tuple[str, Dict[str, Any]]]
) -> List[int]:
    """
    Extract and merge symbol sequences from ALL method model_states.
    Each method tokenizes differently → different symbols → different transitions.
    Merged result covers the full structural space of the text.
    """
    all_seqs: List[List[int]] = []
    for _method, ms in method_states:
        seq = _get_symbol_sequence(ms)
        if seq:
            all_seqs.append(seq)

    if not all_seqs:
        return []

    # Additive merge: concatenate all, dedup adjacent duplicates
    merged: List[int] = []
    seen_transitions = set()
    for seq in all_seqs:
        for i in range(len(seq) - 1):
            t = (seq[i], seq[i + 1])
            if t not in seen_transitions:
                seen_transitions.add(t)
                if not merged or merged[-1] != seq[i]:
                    merged.append(seq[i])
                merged.append(seq[i + 1])

    return merged


# ─────────────────────────────────────────────────────────────────────────────
# Path scores
# ─────────────────────────────────────────────────────────────────────────────

def _build_path_scores(raw_ps: Dict[Any, Any]) -> PathScores:
    """Normalize path_scores to (int,int) -> float."""
    ps: PathScores = {}
    for edge, score in raw_ps.items():
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            continue
        if not isinstance(score, (int, float)):
            continue
        key = (int(edge[0]), int(edge[1]))
        ps[key] = max(ps.get(key, 0.0), float(score))
    return ps


def _build_path_scores_additive(
    method_states: List[Tuple[str, Dict[str, Any]]]
) -> PathScores:
    """
    Additive merge of path_scores from ALL method states.
    v3 used max() which loses evidence. v4 accumulates: more observations
    of an edge = stronger signal.
    """
    accumulated: PathScores = {}
    for _method, ms in method_states:
        ps = _build_path_scores(ms.get("path_scores", {}))
        for k, v in ps.items():
            accumulated[k] = accumulated.get(k, 0.0) + v

    # Normalise to [0, 1] after accumulation
    if not accumulated:
        return {}
    vals = list(accumulated.values())
    lo, hi = min(vals), max(vals)
    span = hi - lo
    if span == 0.0:
        return {k: 0.5 for k in accumulated}
    return {k: (v - lo) / span for k, v in accumulated.items()}


def _merge_path_scores_additive(base: PathScores, new: PathScores) -> None:
    """Add new scores into base (additive, not max)."""
    for k, v in new.items():
        base[k] = base.get(k, 0.0) + v


def _merge_vocab(base: Vocab, new: Vocab) -> None:
    """Merge vocab (first-seen wins per symbol)."""
    for sym, tok in new.items():
        if sym not in base:
            base[sym] = tok


def _merge_global_path_scores_normalized(
    valid_indices: List[int],
    text_path_scores: List[PathScores],
) -> PathScores:
    """Same merge + min–max normalisation as end-of-training export."""
    global_ps: PathScores = {}
    for i in valid_indices:
        _merge_path_scores_additive(global_ps, text_path_scores[i])
    if not global_ps:
        return {}
    vals = list(global_ps.values())
    lo, hi = min(vals), max(vals)
    span = hi - lo
    if span > 0:
        return {k: (v - lo) / span for k, v in global_ps.items()}
    return {k: 0.5 for k in global_ps}


def _atomic_write_json_payload(path: Path, payload: Dict[str, Any], *, indent: Optional[int] = None) -> None:
    """Write JSON atomically (temp file + os.replace). Keeps a single canonical path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        suffix=".json.tmp",
        prefix="santek_ckpt_",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=indent, ensure_ascii=False)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


class _AsyncCheckpointWriter:
    """
    Background JSON writer so checkpoint serialisation does not block training.

    Coalesces pending jobs: only the most recently submitted write runs if the
    worker is still busy (prevents unbounded queue growth on huge models).
    """

    def __init__(self) -> None:
        self._q: "queue.SimpleQueue[Optional[Tuple[Path, Callable[[], Dict[str, Any]]]]]" = (
            queue.SimpleQueue()
        )
        self._thread: Optional[threading.Thread] = None
        self.used = False

    def _loop(self) -> None:
        while True:
            item = self._q.get()
            if item is None:
                break
            path, factory = item
            try:
                payload = factory()
                compact = _env_flag("SANTEK_CHECKPOINT_PRETTY", default=False)
                ind = 2 if compact else None
                _atomic_write_json_payload(path, payload, indent=ind)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                log.warning("Checkpoint write failed (%s): %s", path, exc)

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._loop, name="santek-ckpt", daemon=False)
        self._thread.start()

    def submit(self, path: Path, factory: Callable[[], Dict[str, Any]]) -> None:
        self.used = True
        self.start()
        drained = True
        while drained:
            drained = False
            try:
                while True:
                    self._q.get_nowait()
                    drained = True
            except queue.Empty:
                break
        self._q.put((path, factory))

    def close(self, *, wait: bool = True, timeout: float = 7200.0) -> None:
        if self._thread is None or not self._thread.is_alive():
            return
        self._q.put(None)
        if wait:
            self._thread.join(timeout=timeout)


_CHECKPOINT_WRITER = _AsyncCheckpointWriter()


def _build_model_json_payload(
    path_scores: PathScores,
    vocab: Vocab,
    result: SanTEKTrainingResult,
    *,
    created_iso: Optional[str] = None,
    training_config: Optional[Dict[str, Any]] = None,
    split_manifest: Optional[Dict[str, Any]] = None,
    checkpoint_block: Optional[Dict[str, Any]] = None,
    phase10_training_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Single-file schema: loadable model + optional training / checkpoint metadata."""
    created = created_iso or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    meta: Dict[str, Any] = {
        "version": 4,
        "created_at": created,
        "author": "Chavala Santosh",
        "family": "THRESHOLD_ONSET / SanTOK / SanVerse / Sanformers",
        "converged": result.converged,
        "converged_at_epoch": result.converged_at_epoch,
        "epochs_run": result.total_epochs_run,
        "total_epochs_run": result.total_epochs_run,
        "best_accuracy": result.best_accuracy,
        "best_tension": getattr(result, "best_tension", None),
        "best_9centric": result.best_9centric,
        "edge_count": len(path_scores),
        "vocab_size": len(vocab),
    }
    if training_config:
        meta["training_config"] = dict(training_config)
    if split_manifest is not None:
        meta["split_manifest"] = dict(split_manifest)
    if checkpoint_block:
        meta["checkpoint"] = dict(checkpoint_block)
    # Epoch-wise trace (compact) for analysis / dashboards
    if result.epochs:
        meta["epoch_trace"] = [
            {
                "epoch": e.epoch,
                "accuracy": e.raw_accuracy,
                "mean_tension": e.mean_tension,
                "correct": e.correct,
                "total": e.total,
                "updates": e.updates,
                "elapsed_ms": e.elapsed_ms,
            }
            for e in result.epochs
        ]
    return {
        "version": 4,
        "created_at": created,
        "meta": meta,
        "path_scores": [[a, b, v] for (a, b), v in path_scores.items()],
        "vocab": {str(k): v for k, v in vocab.items()},
    }


def _schedule_training_checkpoint(
    model_path: Path,
    merged_ps: PathScores,
    vocab_snapshot: Vocab,
    out: SanTEKTrainingResult,
    *,
    training_config: Optional[Dict[str, Any]],
    split_manifest: Optional[Dict[str, Any]],
    checkpoint_block: Dict[str, Any],
) -> None:
    """Persist single-file checkpoint (async by default)."""
    if _env_flag("SANTEK_DISABLE_CHECKPOINT", default=False):
        return

    def factory() -> Dict[str, Any]:
        return _build_model_json_payload(
            merged_ps,
            vocab_snapshot,
            out,
            training_config=training_config,
            split_manifest=split_manifest,
            checkpoint_block=checkpoint_block,
        )

    if _env_flag("SANTEK_CHECKPOINT_SYNC", default=False):
        try:
            payload = factory()
            pretty = _env_flag("SANTEK_CHECKPOINT_PRETTY", default=False)
            _atomic_write_json_payload(model_path, payload, indent=2 if pretty else None)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            log.warning("Synchronous checkpoint failed: %s", exc)
        return

    _CHECKPOINT_WRITER.submit(model_path, factory)


# ─────────────────────────────────────────────────────────────────────────────
# Vocab
# ─────────────────────────────────────────────────────────────────────────────

def _build_vocab_from_state(model_state: Dict[str, Any]) -> Vocab:
    """Build symbol→token vocab from one model_state using all runs."""
    p2 = model_state.get("phase2_metrics", {})
    p4 = model_state.get("phase4_metrics", {})
    tokens = model_state.get("tokens", [])
    residue_sequences = model_state.get("residue_sequences", [])
    identity_mappings = p2.get("identity_mappings", {})
    identity_to_symbol = p4.get("identity_to_symbol", {})

    if not tokens or not residue_sequences or not identity_mappings or not identity_to_symbol:
        return {}

    vocab: Vocab = {}
    for run_residues in residue_sequences:
        n_tok = min(len(tokens), len(run_residues))
        for i in range(min(n_tok - 1, len(run_residues) - 1)):
            h = _segment_hash(float(run_residues[i]), float(run_residues[i + 1]))
            identity = identity_mappings.get(h)
            if identity is None:
                continue
            sym = identity_to_symbol.get(identity)
            if sym is None:
                continue
            sym = int(sym)
            if sym not in vocab and i < len(tokens):
                tok = str(tokens[i]).strip()
                if tok:
                    vocab[sym] = tok
    return vocab


def _build_vocab_all_methods(
    method_states: List[Tuple[str, Dict[str, Any]]]
) -> Vocab:
    """Build vocab from all method states merged."""
    vocab: Vocab = {}
    for _method, ms in method_states:
        v = _build_vocab_from_state(ms)
        _merge_vocab(vocab, v)
    return vocab


# ─────────────────────────────────────────────────────────────────────────────
# Learning helpers
# ─────────────────────────────────────────────────────────────────────────────

def _apply_decay(ps: PathScores, decay: float) -> None:
    factor = 1.0 - decay
    for k in ps:
        ps[k] *= factor


def _normalise(ps: PathScores) -> PathScores:
    if not ps:
        return {}
    vals = list(ps.values())
    lo, hi = min(vals), max(vals)
    span = hi - lo
    if span == 0.0:
        return {k: 0.5 for k in ps}
    return {k: (v - lo) / span for k, v in ps.items()}


def _predict(current: int, ps: PathScores) -> Optional[int]:
    """Argmax next symbol; no self-transition."""
    best_sym, best_score = None, -1.0
    for (fr, to), score in ps.items():
        if fr == current and to != current and score > best_score:
            best_sym, best_score = to, score
    return best_sym


def _tension(current: int, actual: int, norm: PathScores) -> float:
    return 1.0 - norm.get((current, actual), 0.0)


def _digital_root(n: int) -> int:
    if n == 0:
        return 9
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n if n != 0 else 9


def _accuracy_9c(correct: int, total: int) -> Tuple[float, int]:
    if total == 0:
        return 0.0, 9
    raw = correct / total
    return raw, _digital_root(round(raw * 100))


def _accumulated_structural_delta(
    live_ps: PathScores,
    streaks: Dict[Tuple[int, int], int],
    current: int,
    predicted: Optional[int],
    actual: int,
    tension: float,
    eta: float,
    max_streak: int,
) -> None:
    """
    ASD v4 — correct formula.

    Correct prediction:
      correct_edge += eta * (1 - tension)   [reward proportional to ease]
      streak reset to 0

    Wrong prediction:
      correct_edge += eta * tension * multiplier   [reward hard cases more]
      wrong_edge   -= eta * tension * multiplier   [penalise proportional to hardness]
      floor at 0

    Streak tracks consecutive wrong predictions for same edge.
    Capped at max_streak before computing multiplier (prevents explosion).
    """
    correct_edge = (current, actual)

    if predicted == actual:
        live_ps[correct_edge] = live_ps.get(correct_edge, 0.0) + eta * (1.0 - tension)
        if predicted is not None:
            streaks[(current, predicted)] = 0
    else:
        if predicted is not None:
            wrong_edge = (current, predicted)
            raw_streak = streaks.get(wrong_edge, 0) + 1
            capped = min(raw_streak, max_streak)
            streaks[wrong_edge] = capped
            multiplier = 1 + capped
            live_ps[correct_edge] = (
                live_ps.get(correct_edge, 0.0) + eta * tension * multiplier
            )
            live_ps[wrong_edge] = max(
                0.0,
                live_ps.get(wrong_edge, 0.0) - eta * tension * multiplier,
            )
        else:
            # No prediction possible — reward correct edge with tension signal
            live_ps[correct_edge] = live_ps.get(correct_edge, 0.0) + eta * tension


# ─────────────────────────────────────────────────────────────────────────────
# Display
# ─────────────────────────────────────────────────────────────────────────────

def _bar(v: float, w: int = 20, full: str = "█", empty: str = "░") -> str:
    n = max(0, min(w, round(v * w)))
    return full * n + empty * (w - n)


def _print_epoch(ep: SanTEKEpochResult, total_epochs: int) -> None:
    print(
        f"  Epoch {ep.epoch:>4}/{total_epochs}  "
        f"acc={ep.raw_accuracy:.4f} {_bar(ep.raw_accuracy, 15)}  "
        f"9c={ep.accuracy_9centric}  "
        f"tension={ep.mean_tension:.4f} {_bar(1.0-ep.mean_tension, 10, '▓', '░')}  "
        f"{ep.correct}/{ep.total}  "
        f"Δ={ep.updates}  {ep.elapsed_ms:.0f}ms",
        flush=True,
    )


def _print_summary(r: SanTEKTrainingResult) -> None:
    print()
    print("=" * 76)
    print("  SanTEK-SLE  v4  TRAINING COMPLETE")
    print("=" * 76)
    print(f"  Epochs run    : {r.total_epochs_run}")
    conv = f"YES at epoch {r.converged_at_epoch}" if r.converged else "NO (limit or plateau)"
    print(f"  Converged     : {conv}")
    print(f"  Best accuracy : {r.best_accuracy:.4f}  ({r.best_accuracy * 100:.1f}%)")
    print(f"  Best tension  : {r.best_tension:.4f}  (lowest mean epoch tension; lower = easier)")
    print(f"  Best 9-centric: {r.best_9centric}  (SanVerse scale 1-9)")
    print(f"  Final edges   : {len(r.final_path_scores)}")
    print(f"  Vocab size    : {len(r.global_vocab)}")
    if r.epochs:
        first, last = r.epochs[0], r.epochs[-1]
        t_delta = last.mean_tension - first.mean_tension
        a_delta = last.raw_accuracy - first.raw_accuracy
        t_dir = "▼" if t_delta < 0 else ("▲" if t_delta > 0 else "=")
        a_dir = "▲" if a_delta > 0 else ("▼" if a_delta < 0 else "=")
        print(f"  Tension  {t_dir}    : {first.mean_tension:.4f} → {last.mean_tension:.4f}  (Δ={t_delta:+.4f})")
        print(f"  Accuracy {a_dir}    : {first.raw_accuracy:.4f} → {last.raw_accuracy:.4f}  (Δ={a_delta:+.4f})")
    print()
    print(f"  {'Ep':>4}  {'Accuracy':>10}  {'9c':>3}  {'Tension':>9}  "
          f"{'Right/Total':>12}  {'Δ':>6}  {'ms':>7}")
    print("  " + "─" * 64)
    for ep in r.epochs:
        mark = " ← best" if ep.raw_accuracy == r.best_accuracy else ""
        print(f"  {ep.epoch:>4}  {ep.raw_accuracy:>10.4f}  {ep.accuracy_9centric:>3}  "
              f"{ep.mean_tension:>9.4f}  {ep.correct:>6}/{ep.total:<5}  "
              f"{ep.updates:>6}  {ep.elapsed_ms:>7.0f}{mark}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Main training function
# ─────────────────────────────────────────────────────────────────────────────

def santek_train(
    corpus: List[str],
    epochs: int = 100,
    eta: float = 0.10,
    decay: float = 0.05,
    max_streak: int = 3,
    tension_threshold: float = 0.10,
    patience: int = 5,
    verbose: bool = True,
    methods: Optional[List[str]] = None,
    model_path: Optional[Path] = None,
    training_config: Optional[Dict[str, Any]] = None,
    split_manifest: Optional[Dict[str, Any]] = None,
) -> SanTEKTrainingResult:
    """
    Train SanTEK model on corpus. Returns SanTEKTrainingResult.

    Key differences from v3:
    - Runs multiple tokenization methods per text (default: all except ``byte``)
    - Sequences merged from all methods (not just run 0)
    - Path scores accumulated additively (not max)
    - Vocab built from all methods
    - Global merge at end gives complete model
    - Single-file checkpoints: after INIT and after every epoch (``model_path``)
    - Final atomic save always written when ``model_path`` is set

    Env:
    - ``SANTEK_INCLUDE_BYTE=1`` — include byte tokenizer in default method list
    - ``SANTEK_DISABLE_CHECKPOINT=1`` — only final save (no mid-run snapshots)
    - ``SANTEK_CHECKPOINT_SYNC=1`` — write checkpoints on main thread (debug)
    - ``SANTEK_CHECKPOINT_PRETTY=1`` — indented JSON for sync checkpoints
    - ``PIPELINE_PHASE10_METRICS=1`` — each per-method ``run_complete`` call attaches
      ``phase10_metrics`` to that method's ``model_state`` (via ``PipelineConfig``).
    - ``SANTEK_PHASE10_MERGED_DEBUG=1`` — log DEBUG lines with merged Phase 10 stats
      across all tokenizers for each corpus text (serial + worker init paths).
    - ``SANTEK_PHASE10_TRAINING_SUMMARY=1`` — accumulate compact merged Phase 10 stats
      per corpus text (works with parallel text workers; rows merged in parent) and
      write ``meta.phase10_training_summary`` on the final model JSON.
    """
    methods = list(methods) if methods is not None else _default_training_methods()
    _phase10_training_summary_reset()

    text_workers, method_workers, worker_profile = _resolve_worker_plan(
        corpus_size=len(corpus), method_count=len(methods)
    )
    fast_env = _training_fast_env_overrides()
    fast_mode_active = (
        bool(fast_env)
        or _env_flag("SANTEK_TRAIN_FAST", default=True)
        and (
            _env_flag("PHASE1_SKIP_DISTANCES", default=False)
            or _env_flag("PHASE3_SKIP_PATH_LENGTHS", default=False)
        )
    )

    if verbose:
        print()
        print("=" * 76)
        print("  SanTEK Structural Learning Engine  v4")
        print("  THRESHOLD_ONSET / SanTOK / SanVerse / Sanformers")
        print("  Author: Chavala Santosh")
        print("=" * 76)
        print(f"  Corpus   : {len(corpus)} texts")
        print(f"  Methods  : {len(methods)} tokenization methods")
        print(f"  Parallel : text_workers={text_workers}  method_workers={method_workers}")
        print(f"  Profile  : {worker_profile}")
        print(f"  Fast mode: {'on' if fast_mode_active else 'off'}")
        print(f"  Epochs   : {epochs}  Eta: {eta}  Decay: {decay}")
        print(f"  MaxStreak: {max_streak}  Patience: {patience}  Threshold: {tension_threshold}")
        print(f"  Methods  : {', '.join(methods)}")
        print()

    log.info("Loading pipeline...")
    rc = None
    if text_workers <= 1:
        rc = _load_run_complete()

    # ── INIT: run each tokenizer in ``methods`` per text ─────────────────────
    if verbose:
        print("─" * 76)
        print(f"  INIT — building per-text structural state ({len(methods)} tokenizers per text)")
        print("─" * 76)

    text_path_scores: List[PathScores] = []
    text_streaks: List[Dict[Tuple[int, int], int]] = []
    text_seqs: List[List[int]] = []
    global_vocab: Vocab = {}
    valid_indices: List[int] = []

    t_init_start = time.time()

    with _temporary_env(fast_env):
        if text_workers > 1 and len(corpus) > 1 and _HAS_RUNTIME_EXECUTOR:
            # Process short texts first so first output appears quickly (avoids 1+ hour wait)
            corpus_with_idx: List[Tuple[int, str]] = [
                (i, text) for i, text in enumerate(corpus)
            ]
            corpus_with_idx.sort(key=lambda x: len(x[1].split()))
            payloads: List[Tuple[int, str, List[str], int]] = [
                (orig_i, text, list(methods), method_workers)
                for orig_i, text in corpus_with_idx
            ]
            jobs = [
                JobSpec(
                    job_id=f"text-{idx}",
                    fn=_process_text_worker,
                    args=(payload,),
                    retries=0,
                )
                for idx, payload in enumerate(payloads)
            ]

            done_count: List[int] = [0]

            def _on_job_done(_metrics: Any, result: Any) -> None:
                if verbose and result.ok and result.value is not None:
                    done_count[0] += 1
                    val = result.value
                    # Worker returns (idx, ps, seq, vocab, n_methods, n_id, elapsed_ms, err, phase10_row)
                    ps = val[1]
                    seq = val[2]
                    vocab = val[3]
                    n_methods = val[4]
                    n_id = val[5]
                    elapsed_ms = val[6]
                    n_edges = len(ps) if ps else 0
                    vocab_size = len(vocab) if isinstance(vocab, (dict, list, set)) else (vocab if isinstance(vocab, int) else 0)
                    print(
                        f"  [{done_count[0]:>6}/{len(corpus)}] "
                        f"methods={n_methods}/{len(methods)}  edges={n_edges:>5}  "
                        f"identities={n_id:>4}  seq_len={len(seq) if seq else 0:>4}  "
                        f"vocab={vocab_size:>4}  {elapsed_ms:.0f}ms",
                        flush=True,
                    )

            if verbose:
                print("  (short texts first — first output in ~1–2 min)", flush=True)
            job_results, _metrics = run_tasks(
                jobs,
                backend="process",
                max_workers=min(text_workers, len(corpus)),
                progress_callback=_on_job_done if verbose else None,
            )
            results_by_idx: Dict[
                int,
                Tuple[
                    int,
                    Optional[PathScores],
                    Optional[List[int]],
                    Optional[Vocab],
                    int,
                    int,
                    float,
                    Optional[str],
                    Optional[Dict[str, Any]],
                ],
            ] = {}
            for jr in job_results:
                if not jr.ok or jr.value is None:
                    continue
                value = jr.value
                results_by_idx[value[0]] = value

            for i in range(len(corpus)):
                if i not in results_by_idx:
                    log.warning("corpus[%d] skipped — worker did not return result", i)
                    text_path_scores.append({})
                    text_streaks.append({})
                    text_seqs.append([])
                    continue
                result = results_by_idx[i]
                _, ps, seq, vocab, n_methods, n_id, elapsed_text_ms, err, p10_row = result
                if ps is None or seq is None or vocab is None:
                    log.warning("corpus[%d] skipped — %s", i, err or "worker failed")
                    text_path_scores.append({})
                    text_streaks.append({})
                    text_seqs.append([])
                    continue
                _phase10_training_merge_row(p10_row)
                _merge_vocab(global_vocab, vocab)
                text_path_scores.append(ps)
                text_streaks.append(defaultdict(int))
                text_seqs.append(seq)
                valid_indices.append(i)
                # Progress already printed by _on_job_done callback
        else:
            if text_workers > 1 and len(corpus) > 1 and not _HAS_RUNTIME_EXECUTOR:
                log.warning("integration.runtime unavailable; falling back to single-process text loop")
            for i, text in enumerate(corpus):
                t_text = time.time()
                method_states = _run_pipeline_all_methods(
                    rc, text, methods, max_method_workers=method_workers
                )
                if not method_states:
                    log.warning("corpus[%d] skipped — all methods failed", i)
                    text_path_scores.append({})
                    text_streaks.append({})
                    text_seqs.append([])
                    continue

                _phase10_training_accumulate(method_states)
                ps = _build_path_scores_additive(method_states)
                seq = _get_symbol_sequence_multi_state(method_states)
                vocab = _build_vocab_all_methods(method_states)
                _merge_vocab(global_vocab, vocab)

                text_path_scores.append(ps)
                text_streaks.append(defaultdict(int))
                text_seqs.append(seq)
                valid_indices.append(i)

                elapsed_text_ms = (time.time() - t_text) * 1000
                if _env_flag("SANTEK_PHASE10_MERGED_DEBUG", default=False):
                    try:
                        from threshold_onset.phase10 import run_phase10_from_method_states

                        m10 = run_phase10_from_method_states(method_states)
                        log.debug(
                            "phase10_merged text=%s/%s methods=%s gate=%s transitions=%s universe=%s",
                            i + 1,
                            len(corpus),
                            len(method_states),
                            m10.gate_passed,
                            m10.total_transitions,
                            len(m10.universe_ids),
                        )
                    except Exception as exc:  # pylint: disable=broad-exception-caught
                        log.debug("phase10_merged skip: %s", exc)
                if verbose:
                    n_methods = len(method_states)
                    n_id = max(
                        len(ms.get("phase4_metrics", {}).get("identity_to_symbol", {}))
                        for _, ms in method_states
                    )
                    print(f"  [{i+1:>5}/{len(corpus)}] "
                          f"methods={n_methods}/{len(methods)}  "
                          f"edges={len(ps):>5}  "
                          f"identities={n_id:>4}  "
                          f"seq_len={len(seq):>4}  "
                          f"vocab={len(vocab):>4}  "
                          f"{elapsed_text_ms:.0f}ms")

    if not valid_indices:
        raise ValueError("No valid pipeline results from corpus. Check pipeline setup.")

    t_init_elapsed = time.time() - t_init_start
    total_edges_sum = sum(len(text_path_scores[i]) for i in valid_indices)
    skipped_indices = [i for i in range(len(corpus)) if i not in set(valid_indices)]

    if verbose:
        print()
        print(f"  Init complete: {len(valid_indices)}/{len(corpus)} texts valid  "
              f"total_edges_sum={total_edges_sum}  "
              f"vocab={len(global_vocab)}  "
              f"time={t_init_elapsed:.1f}s")
        if skipped_indices:
            preview = skipped_indices[:12]
            more = " …" if len(skipped_indices) > 12 else ""
            print(f"  Skipped corpus indices ({len(skipped_indices)}): {preview}{more}")
        print()

    out = SanTEKTrainingResult(
        converged=False,
        converged_at_epoch=None,
        total_epochs_run=0,
        global_vocab=global_vocab,
    )

    if model_path is not None:
        merged_post_init = _merge_global_path_scores_normalized(valid_indices, text_path_scores)
        _schedule_training_checkpoint(
            Path(model_path),
            merged_post_init,
            dict(global_vocab),
            out,
            training_config=training_config,
            split_manifest=split_manifest,
            checkpoint_block={
                "phase": "post_init",
                "corpus_size": len(corpus),
                "valid_texts": len(valid_indices),
                "skipped_indices": skipped_indices,
                "init_wall_seconds": round(t_init_elapsed, 3),
                "tokenizers": list(methods),
                "total_edges_sum": total_edges_sum,
            },
        )
        if verbose:
            print(f"  Checkpoint (single file) → {model_path}  phase=post_init", flush=True)
            print()

    # ── TRAINING LOOP ─────────────────────────────────────────────────────────
    if verbose:
        print("─" * 76)
        print("  TRAINING LOOP")
        print("─" * 76)
    prev_tension = float("inf")
    plateau_count = 0

    try:
        for epoch in range(1, epochs + 1):
            if verbose:
                print(f"  Epoch {epoch:>4}/{epochs}  … running", flush=True)
            t0 = time.time()
            correct = total = updates = 0
            all_tensions: List[float] = []

            for i in valid_indices:
                ps = text_path_scores[i]
                stk = text_streaks[i]
                seq = text_seqs[i]

                # Decay and snapshot per-text at epoch start
                _apply_decay(ps, decay)
                snapshot = dict(ps)
                norm = _normalise(snapshot)

                for step in range(len(seq) - 1):
                    cur, actual = seq[step], seq[step + 1]
                    if cur == actual:
                        continue

                    pred = _predict(cur, snapshot)
                    t_val = _tension(cur, actual, norm)
                    all_tensions.append(t_val)

                    if pred == actual:
                        correct += 1
                    total += 1

                    _accumulated_structural_delta(
                        ps, stk, cur, pred, actual, t_val, eta, max_streak
                    )
                    updates += 1

            elapsed_ms = (time.time() - t0) * 1000
            mean_t = sum(all_tensions) / len(all_tensions) if all_tensions else 1.0
            raw_acc, acc9 = _accuracy_9c(correct, total)

            ep = SanTEKEpochResult(
                epoch=epoch, correct=correct, total=total,
                raw_accuracy=raw_acc, accuracy_9centric=acc9,
                mean_tension=mean_t, updates=updates, elapsed_ms=elapsed_ms,
            )
            out.epochs.append(ep)
            out.total_epochs_run = epoch

            if raw_acc > out.best_accuracy:
                out.best_accuracy = raw_acc
                out.best_9centric = acc9

            out.best_tension = min(out.best_tension, mean_t)

            if verbose:
                _print_epoch(ep, epochs)

            if model_path is not None:
                merged_epoch = _merge_global_path_scores_normalized(valid_indices, text_path_scores)
                _schedule_training_checkpoint(
                    Path(model_path),
                    merged_epoch,
                    dict(global_vocab),
                    out,
                    training_config=training_config,
                    split_manifest=split_manifest,
                    checkpoint_block={
                        "phase": "epoch_end",
                        "epoch": epoch,
                        "mean_tension": mean_t,
                        "accuracy": raw_acc,
                    },
                )

            if total == 0:
                continue

            # Convergence check
            if mean_t < tension_threshold:
                out.converged = True
                out.converged_at_epoch = epoch
                if verbose:
                    print(f"\n  CONVERGED  epoch={epoch}  tension={mean_t:.4f} < {tension_threshold}")
                break

            # Plateau check
            if abs(mean_t - prev_tension) < 1e-6:
                plateau_count += 1
            else:
                plateau_count = 0
            prev_tension = mean_t

            if plateau_count >= patience:
                if verbose:
                    print(f"\n  PLATEAU  {patience} epochs unchanged — stopping at epoch {epoch}")
                break

    except KeyboardInterrupt:
        if verbose:
            print(
                f"\n  INTERRUPTED  (Ctrl+C)  last fully completed epoch: "
                f"{out.total_epochs_run}/{epochs}",
                flush=True,
            )
        raise
    except MemoryError:
        if verbose:
            print(
                "\n  MEMORY ERROR  try fewer texts/tokenizers or free RAM; "
                "checkpoint on disk may reflect last completed epoch.",
                flush=True,
            )
        raise

    # ── GLOBAL MERGE: all text path_scores → single model ────────────────────
    global_ps = _merge_global_path_scores_normalized(valid_indices, text_path_scores)
    out.final_path_scores = global_ps

    if verbose:
        _print_summary(out)

    if model_path is not None:
        if _CHECKPOINT_WRITER.used:
            _CHECKPOINT_WRITER.close(wait=True, timeout=7200.0)
        final_payload = _build_model_json_payload(
            global_ps,
            dict(global_vocab),
            out,
            training_config=training_config,
            split_manifest=split_manifest,
            checkpoint_block={
                "phase": "training_complete",
                "corpus_size": len(corpus),
                "valid_texts": len(valid_indices),
                "skipped_indices": skipped_indices,
            },
            phase10_training_summary=_phase10_training_summary_snapshot(),
        )
        _atomic_write_json_payload(Path(model_path), final_payload, indent=2)
        if verbose:
            print(f"  Final model (atomic, single file) → {model_path}")

    return out


def train(
    corpus: List[str],
    epochs: int = 100,
    eta: float = 0.10,
    decay: float = 0.05,
    max_streak: int = 3,
    tension_threshold: float = 0.10,
    patience: int = 5,
    verbose: bool = True,
    methods: Optional[List[str]] = None,
    model_path: Optional[Path] = None,
    training_config: Optional[Dict[str, Any]] = None,
    split_manifest: Optional[Dict[str, Any]] = None,
) -> SanTEKTrainingResult:
    """Compatibility alias for canonical import surface."""
    return santek_train(
        corpus=corpus,
        epochs=epochs,
        eta=eta,
        decay=decay,
        max_streak=max_streak,
        tension_threshold=tension_threshold,
        patience=patience,
        verbose=verbose,
        methods=methods,
        model_path=model_path,
        training_config=training_config,
        split_manifest=split_manifest,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Save / Load
# ─────────────────────────────────────────────────────────────────────────────

def _save_model(
    path_scores: PathScores,
    vocab: Vocab,
    result: SanTEKTrainingResult,
    path: Path,
) -> None:
    """Legacy helper — prefer _build_model_json_payload + _atomic_write_json_payload."""
    payload = _build_model_json_payload(path_scores, vocab, result, checkpoint_block=None)
    _atomic_write_json_payload(path, payload, indent=2)


def save_base_model(
    model: SantekModel,
    path: Path,
    *,
    training_config: Optional[Dict[str, Any]] = None,
) -> Path:
    """Public save API (atomic replace)."""
    meta = dict(model.meta)
    if training_config is not None:
        meta["training_config"] = dict(training_config)
    created = meta.get("created_at") or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload: Dict[str, Any] = {
        "version": 4,
        "created_at": created,
        "meta": meta,
        "path_scores": [[a, b, v] for (a, b), v in model.path_scores.items()],
        "vocab": {str(k): v for k, v in model.vocab.items()},
    }
    if training_config is not None:
        payload["training_config"] = training_config
    _atomic_write_json_payload(path, payload, indent=2)
    return path


def load_base_model(path: Path) -> SantekModel:
    """Load model from JSON. Raises FileNotFoundError if missing."""
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}")
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    ps_list = payload.get("path_scores", [])
    ps: PathScores = {}
    for row in ps_list:
        if len(row) >= 3:
            ps[(int(row[0]), int(row[1]))] = float(row[2])
    vocab = {int(k): v for k, v in payload.get("vocab", {}).items()}
    meta = dict(payload.get("meta", {}))
    # Promote top-level fields into meta so model info always has them.
    for field in ("version", "created_at"):
        if field not in meta and field in payload:
            meta[field] = payload[field]
    meta.setdefault("author", "Chavala Santosh")
    meta.setdefault("family", "THRESHOLD_ONSET / SanTOK / SanVerse / Sanformers")
    # Alias: epochs_run <-> total_epochs_run for cross-version compat.
    if "epochs_run" not in meta and "total_epochs_run" in meta:
        meta["epochs_run"] = meta["total_epochs_run"]
    if "training_config" in payload:
        meta["training_config"] = payload["training_config"]
    return SantekModel(path_scores=ps, vocab=vocab, meta=meta)


def save_santek_model(
    model: SantekModel,
    path: Path,
    *,
    training_config: Optional[Dict[str, Any]] = None,
    split_manifest: Optional[Dict[str, Any]] = None,
) -> Path:
    """Compatibility wrapper; preserves optional split manifest metadata."""
    merged_cfg: Dict[str, Any] = {}
    if training_config:
        merged_cfg.update(training_config)
    if split_manifest is not None:
        merged_cfg["split_manifest"] = split_manifest
    return save_base_model(
        model,
        path,
        training_config=(merged_cfg if merged_cfg else None),
    )


def load_santek_model(path: Path) -> SantekModel:
    """Compatibility alias for canonical import surface."""
    return load_base_model(path)


# ─────────────────────────────────────────────────────────────────────────────
# Generation
# ─────────────────────────────────────────────────────────────────────────────

def _is_prompt_connected(last_symbol: int, path_scores: PathScores) -> bool:
    for (fr, to) in path_scores:
        if fr == last_symbol and to != last_symbol:
            return True
    return False


def is_prompt_connected(last_symbol: int, path_scores: PathScores) -> bool:
    """Public compatibility alias."""
    return _is_prompt_connected(last_symbol, path_scores)


def _generate_symbols_with_cycle_control(
    start_seq: List[int],
    path_scores: PathScores,
    length: int,
    recency_window: int = 6,
    recency_penalty: float = 0.30,
    bigram_penalty: float = 0.20,
    trigram_penalty: float = 0.35,
) -> List[int]:
    """
    Extend symbol sequence with cycle control.
    Penalties applied to recently seen symbols, bigrams, trigrams.
    A_ii = 0 enforced (no self-transition).
    """
    seq = list(start_seq)
    if not seq:
        return seq

    # Build bigram/trigram history
    bigrams = set()
    trigrams = set()
    for i in range(len(seq) - 1):
        bigrams.add((seq[i], seq[i + 1]))
    for i in range(len(seq) - 2):
        trigrams.add((seq[i], seq[i + 1], seq[i + 2]))

    for _ in range(length):
        current = seq[-1]

        # Get all candidates from path_scores
        candidates: Dict[int, float] = {}
        for (fr, to), score in path_scores.items():
            if fr == current and to != current:  # A_ii = 0
                candidates[to] = candidates.get(to, 0.0) + score

        if not candidates:
            break

        # Apply penalties
        recent = seq[-recency_window:] if len(seq) >= recency_window else seq
        penalised: Dict[int, float] = {}
        for sym, score in candidates.items():
            s = score
            # Recency penalty
            occurrences = recent.count(sym)
            s -= recency_penalty * occurrences
            # Bigram penalty
            if len(seq) >= 1 and (seq[-1], sym) in bigrams:
                s -= bigram_penalty
            # Trigram penalty
            if len(seq) >= 2 and (seq[-2], seq[-1], sym) in trigrams:
                s -= trigram_penalty
            penalised[sym] = max(0.0, s)

        # If all penalised to 0, use original scores
        if sum(penalised.values()) == 0.0:
            penalised = dict(candidates)

        # Argmax
        best = max(penalised, key=penalised.get)
        seq.append(best)

        # Update history
        if len(seq) >= 2:
            bigrams.add((seq[-2], seq[-1]))
        if len(seq) >= 3:
            trigrams.add((seq[-3], seq[-2], seq[-1]))

    return seq


def _symbols_to_text(symbols: List[int], vocab: Vocab) -> str:
    """Decode symbol sequence to text."""
    words = []
    prev = None
    for sym in symbols:
        if sym == prev:
            continue
        tok = vocab.get(sym)
        if tok:
            words.append(tok)
        prev = sym
    text = " ".join(words)
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    if text and not text.endswith((".", "!", "?", "...")):
        text = text.rstrip() + "."
    return text


def generate(
    prompt: str,
    model: SantekModel,
    repo_root: Optional[Path] = None,
    length: int = 30,
    methods: Optional[List[str]] = None,
    refuse_if_disconnected: bool = True,
) -> Tuple[str, bool]:
    """
    Generate text from prompt. Returns (output_text, was_refused).

    Runs the same default tokenizer set as training (all except ``byte`` unless
    ``SANTEK_INCLUDE_BYTE=1``) on the prompt to anchor in the learned graph.
    Refuses if prompt is structurally disconnected from model.
    """
    if methods is None:
        methods = _default_training_methods()

    # repo_root kept for compatibility with older wrappers; resolution is internal.
    _ = repo_root
    rc = _load_run_complete()
    method_states = _run_pipeline_all_methods(rc, prompt, methods)

    if not method_states:
        if refuse_if_disconnected:
            return ("[Refused: prompt could not be parsed by the pipeline.]", True)
        return ("[Refused: pipeline failed on prompt.]", True)

    prompt_seq = _get_symbol_sequence_multi_state(method_states)
    prompt_vocab = _build_vocab_all_methods(method_states)

    # Merge prompt vocab into model vocab for decoding
    merged_vocab = dict(model.vocab)
    _merge_vocab(merged_vocab, prompt_vocab)

    if not prompt_seq:
        if refuse_if_disconnected:
            return ("[Refused: prompt produced no symbol sequence.]", True)
        return ("[Refused: no symbol sequence from prompt.]", True)

    # Find last connected anchor in prompt sequence
    anchor = None
    connected_prefix: List[int] = []
    for sym in reversed(prompt_seq):
        if _is_prompt_connected(sym, model.path_scores):
            anchor = sym
            break

    if anchor is None:
        return (
            "[Refused: prompt is disconnected from the learned graph. "
            "The model has not seen this domain yet.]",
            True,
        )

    # Build connected prefix up to anchor
    for sym in prompt_seq:
        connected_prefix.append(sym)
        if sym == anchor:
            break

    # Generate extension
    extended = _generate_symbols_with_cycle_control(
        [anchor], model.path_scores, length
    )
    full_seq = connected_prefix + extended[1:]

    return _symbols_to_text(full_seq, merged_vocab), False


# ─────────────────────────────────────────────────────────────────────────────
# Eval: held-out + frequency baseline
# ─────────────────────────────────────────────────────────────────────────────

def _transition_counts(sequences: List[List[int]]) -> Dict[Tuple[int, int], int]:
    counts: Dict[Tuple[int, int], int] = defaultdict(int)
    for seq in sequences:
        for i in range(len(seq) - 1):
            a, b = seq[i], seq[i + 1]
            if a != b:
                counts[(a, b)] += 1
    return dict(counts)


def _baseline_predict(current: int, train_counts: Dict[Tuple[int, int], int]) -> Optional[int]:
    best_next, best_count = None, -1
    for (fr, to), c in train_counts.items():
        if fr == current and c > best_count:
            best_next, best_count = to, c
    return best_next


def eval_held_out(
    model_path: Path,
    train_docs: List[str],
    val_docs: List[str],
    methods: Optional[List[str]] = None,
) -> EvalResult:
    """
    Held-out evaluation. Compares model accuracy vs frequency baseline.
    Uses all methods for sequence extraction.
    """
    if methods is None:
        methods = _default_training_methods()

    if not val_docs:
        return EvalResult(0.0, 0.0, 0, 0, 0, error="No validation documents.")

    try:
        model = load_base_model(model_path)
    except FileNotFoundError as e:
        return EvalResult(0.0, 0.0, 0, 0, 0, error=str(e))

    rc = _load_run_complete()

    def _get_seqs(docs: List[str]) -> List[List[int]]:
        seqs = []
        for text in docs:
            ms_list = _run_pipeline_all_methods(rc, text, methods)
            if ms_list:
                seq = _get_symbol_sequence_multi_state(ms_list)
                if len(seq) >= 2:
                    seqs.append(seq)
        return seqs

    print("  Running pipeline on train docs for baseline...")
    train_seqs = _get_seqs(train_docs)
    print("  Running pipeline on val docs...")
    val_seqs = _get_seqs(val_docs)

    if not val_seqs:
        return EvalResult(0.0, 0.0, 0, 0, 0,
                          error="No validation sequences produced.")

    train_counts = _transition_counts(train_seqs)
    ps = model.path_scores
    model_correct = baseline_correct = total = 0

    for seq in val_seqs:
        for i in range(len(seq) - 1):
            cur, actual = seq[i], seq[i + 1]
            if cur == actual:
                continue
            total += 1
            if _predict(cur, ps) == actual:
                model_correct += 1
            if _baseline_predict(cur, train_counts) == actual:
                baseline_correct += 1

    if total == 0:
        return EvalResult(0.0, 0.0, 0, 0, 0,
                          error="No valid prediction steps in val sequences.")

    return EvalResult(
        model_accuracy=model_correct / total,
        baseline_accuracy=baseline_correct / total,
        total_predictions=total,
        model_correct=model_correct,
        baseline_correct=baseline_correct,
    )


# ─────────────────────────────────────────────────────────────────────────────
# CLI commands
# ─────────────────────────────────────────────────────────────────────────────

def cmd_train(
    corpus: List[str],
    epochs: int = 200,
    eta: float = 0.10,
    decay: float = 0.05,
    max_streak: int = 3,
    tension_threshold: float = 0.10,
    patience: int = 5,
    model_path: Optional[Path] = None,
    verbose: bool = True,
) -> None:
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH
    result = santek_train(
        corpus=corpus,
        epochs=epochs,
        eta=eta,
        decay=decay,
        max_streak=max_streak,
        tension_threshold=tension_threshold,
        patience=patience,
        verbose=verbose,
        model_path=model_path,
    )
    print(f"\n  Best accuracy : {result.best_accuracy:.4f}  ({result.best_accuracy * 100:.1f}%)")
    print(f"  Best 9-centric: {result.best_9centric}")
    print(f"  Model saved → {model_path}")


def cmd_generate(
    prompt: str,
    model_path: Optional[Path] = None,
    length: int = 30,
) -> None:
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH
    model = load_base_model(model_path)
    print(f"\n  Prompt : {prompt}")
    print(f"  Model  : {model_path}  edges={len(model.path_scores)}  vocab={len(model.vocab)}")
    print()
    text, refused = generate(prompt, model, length=length)
    if refused:
        print(f"  {text}")
    else:
        print(f"  Output : {text}")


def cmd_chat(model_path: Optional[Path] = None) -> None:
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH
    model = load_base_model(model_path)
    print(f"\n  SanTEK Chat  |  model={model_path}  edges={len(model.path_scores)}")
    print("  Type your prompt. Ctrl+C to exit.\n")
    try:
        while True:
            try:
                prompt = input("  > ").strip()
            except EOFError:
                break
            if not prompt:
                continue
            text, refused = generate(prompt, model, length=30)
            if refused:
                print(f"  {text}\n")
            else:
                print(f"  {text}\n")
    except KeyboardInterrupt:
        print("\n  Goodbye.")


def cmd_eval(
    model_path: Optional[Path] = None,
    corpus_path: Optional[Path] = None,
    train_ratio: float = 0.8,
) -> None:
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH
    if corpus_path is None:
        corpus_path = Path("data/hindu_corpus_real.jsonl")

    if not corpus_path.exists():
        print(f"  [ERROR] Corpus not found: {corpus_path}")
        return

    texts = []
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    texts.append(json.loads(line)["text"])
                except Exception:
                    pass

    split = int(len(texts) * train_ratio)
    train_docs, val_docs = texts[:split], texts[split:]
    print(f"\n  Eval: train={len(train_docs)}  val={len(val_docs)}")

    result = eval_held_out(model_path, train_docs, val_docs)
    if result.error:
        print(f"  [ERROR] {result.error}")
        return

    print(f"\n  Model accuracy   : {result.model_accuracy:.4f}  ({result.model_correct}/{result.total_predictions})")
    print(f"  Baseline accuracy: {result.baseline_accuracy:.4f}  ({result.baseline_correct}/{result.total_predictions})")
    delta = result.model_accuracy - result.baseline_accuracy
    print(f"  Delta            : {delta:+.4f}  ({'better' if delta > 0 else 'worse'} than baseline)")
    _, acc9 = _accuracy_9c(result.model_correct, result.total_predictions)
    print(f"  9-centric        : {acc9}")


def cmd_info(model_path: Optional[Path] = None) -> None:
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH
    if not model_path.exists():
        print(f"  No model at {model_path}")
        return
    model = load_base_model(model_path)
    print(f"\n  Model    : {model_path}")
    print(f"  Version  : {model.meta.get('version', 'unknown')}")
    print(f"  Created  : {model.meta.get('created_at', 'unknown')}")
    print(f"  Edges    : {len(model.path_scores)}")
    print(f"  Vocab    : {len(model.vocab)}")
    for k, v in model.meta.items():
        if k not in ("version", "created_at"):
            print(f"  {k:20s}: {v}")
    if model.vocab:
        sample = list(model.vocab.items())[:10]
        print(f"\n  Vocab sample:")
        for sym, tok in sample:
            print(f"    {sym:>6} → {tok}")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(
        description="SanTEK-SLE v4  |  THRESHOLD_ONSET / SanTOK / SanVerse",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  train    --corpus <jsonl>  [--epochs N] [--eta F] [--decay F]
  generate "<prompt>"        [--length N]
  chat
  eval     [--corpus <jsonl>]
  info
        """
    )
    ap.add_argument("command", choices=["train", "generate", "chat", "eval", "info"])
    ap.add_argument("prompt", nargs="?", default=None, help="Prompt for generate command")
    ap.add_argument("--corpus", type=Path, default=None)
    ap.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--eta", type=float, default=0.10)
    ap.add_argument("--decay", type=float, default=0.05)
    ap.add_argument("--max-streak", type=int, default=3, dest="max_streak")
    ap.add_argument("--tension-threshold", type=float, default=0.10, dest="tension_threshold")
    ap.add_argument("--patience", type=int, default=5)
    ap.add_argument("--length", type=int, default=30)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    if args.command == "train":
        corpus_path = args.corpus or Path("data/hindu_corpus_real.jsonl")
        if not corpus_path.exists():
            print(f"[ERROR] Corpus not found: {corpus_path}")
            sys.exit(1)
        texts = []
        with open(corpus_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        texts.append(json.loads(line)["text"])
                    except Exception:
                        pass
        if not texts:
            print("[ERROR] No texts in corpus.")
            sys.exit(1)
        cmd_train(
            corpus=texts,
            epochs=args.epochs,
            eta=args.eta,
            decay=args.decay,
            max_streak=args.max_streak,
            tension_threshold=args.tension_threshold,
            patience=args.patience,
            model_path=args.model,
            verbose=not args.quiet,
        )

    elif args.command == "generate":
        prompt = args.prompt or "Om Namah Shivaya"
        cmd_generate(prompt, model_path=args.model, length=args.length)

    elif args.command == "chat":
        cmd_chat(model_path=args.model)

    elif args.command == "eval":
        cmd_eval(model_path=args.model, corpus_path=args.corpus)

    elif args.command == "info":
        cmd_info(model_path=args.model)


if __name__ == "__main__":
    main()