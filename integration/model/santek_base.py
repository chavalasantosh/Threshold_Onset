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
     v3 only used "word". The pipeline supports 9 methods.
     v4: _run_pipeline_all_methods() runs ALL 9 methods per text and merges
         all model_states. Every text contributes 9x more structural data.

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
  _run_pipeline_all_methods()   ← runs 9 tokenization methods per text
      │  merges model_states from all 9 runs
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
import hashlib
import importlib.util
import json
import logging
import os
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
        cfg.generation.num_sequences = 0         # skip generation
        cfg.generation.steps = 0                 # skip generation
        cfg.continuation_text = text[:300]       # use real domain text
        cfg.continuation_texts = None
        result = rc_mod.run(
            text_override=text,
            cfg=cfg,
            return_result=True,
            return_model_state=True,
        )
        if result is None:
            return None
        return getattr(result, "model_state", None)
    except Exception as exc:
        log.debug("Pipeline failed method=%s text=%r: %s", method, text[:40], exc)
        return None


def _run_pipeline_all_methods(
    rc_mod,
    text: str,
    methods: Optional[List[str]] = None,
) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Run pipeline for ALL 9 tokenization methods. Returns list of (method, model_state).
    Skips methods that fail. Always returns at least [] (never raises).

    This is the KEY upgrade: 9 different tokenization perspectives on the same text
    → 9 different residue sequences → richer identity/relation graph after merging.
    """
    if methods is None:
        methods = ALL_TOKENIZATION_METHODS
    results = []
    for method in methods:
        ms = _run_pipeline_single(rc_mod, text, method)
        if ms is not None:
            results.append((method, ms))
    return results


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
        f"Δ={ep.updates}  {ep.elapsed_ms:.0f}ms"
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
) -> SanTEKTrainingResult:
    """
    Train SanTEK model on corpus. Returns SanTEKTrainingResult.

    Key differences from v3:
    - Runs ALL 9 tokenization methods per text (not just "word")
    - Sequences merged from all methods (not just run 0)
    - Path scores accumulated additively (not max)
    - Vocab built from all methods
    - Global merge at end gives complete model
    - Auto-saves if model_path provided
    """
    if methods is None:
        methods = ALL_TOKENIZATION_METHODS

    if verbose:
        print()
        print("=" * 76)
        print("  SanTEK Structural Learning Engine  v4")
        print("  THRESHOLD_ONSET / SanTOK / SanVerse / Sanformers")
        print("  Author: Chavala Santosh")
        print("=" * 76)
        print(f"  Corpus   : {len(corpus)} texts")
        print(f"  Methods  : {len(methods)} tokenization methods")
        print(f"  Epochs   : {epochs}  Eta: {eta}  Decay: {decay}")
        print(f"  MaxStreak: {max_streak}  Patience: {patience}  Threshold: {tension_threshold}")
        print(f"  Methods  : {', '.join(methods)}")
        print()

    log.info("Loading pipeline...")
    rc = _load_run_complete()

    # ── INIT: run all methods per text ────────────────────────────────────────
    if verbose:
        print("─" * 76)
        print("  INIT — building per-text structural state (9 methods per text)")
        print("─" * 76)

    text_path_scores: List[PathScores] = []
    text_streaks: List[Dict[Tuple[int, int], int]] = []
    text_seqs: List[List[int]] = []
    global_vocab: Vocab = {}
    valid_indices: List[int] = []

    t_init_start = time.time()

    for i, text in enumerate(corpus):
        t_text = time.time()

        # Run all 9 methods
        method_states = _run_pipeline_all_methods(rc, text, methods)

        if not method_states:
            log.warning("corpus[%d] skipped — all methods failed", i)
            text_path_scores.append({})
            text_streaks.append({})
            text_seqs.append([])
            continue

        # Build additive path_scores from all methods
        ps = _build_path_scores_additive(method_states)

        # Build merged symbol sequence from all methods
        seq = _get_symbol_sequence_multi_state(method_states)

        # Build vocab from all methods
        vocab = _build_vocab_all_methods(method_states)
        _merge_vocab(global_vocab, vocab)

        text_path_scores.append(ps)
        text_streaks.append(defaultdict(int))
        text_seqs.append(seq)
        valid_indices.append(i)

        elapsed_text_ms = (time.time() - t_text) * 1000

        if verbose:
            n_methods = len(method_states)
            n_id = max(
                len(ms.get("phase4_metrics", {}).get("identity_to_symbol", {}))
                for _, ms in method_states
            )
            print(f"  [{i+1:>5}/{len(corpus)}] "
                  f"methods={n_methods}/9  "
                  f"edges={len(ps):>5}  "
                  f"identities={n_id:>4}  "
                  f"seq_len={len(seq):>4}  "
                  f"vocab={len(vocab):>4}  "
                  f"{elapsed_text_ms:.0f}ms")

    if not valid_indices:
        raise ValueError("No valid pipeline results from corpus. Check pipeline setup.")

    if verbose:
        total_edges_sum = sum(len(text_path_scores[i]) for i in valid_indices)
        t_init_elapsed = (time.time() - t_init_start)
        print()
        print(f"  Init complete: {len(valid_indices)}/{len(corpus)} texts valid  "
              f"total_edges_sum={total_edges_sum}  "
              f"vocab={len(global_vocab)}  "
              f"time={t_init_elapsed:.1f}s")
        print()

    # ── TRAINING LOOP ─────────────────────────────────────────────────────────
    if verbose:
        print("─" * 76)
        print("  TRAINING LOOP")
        print("─" * 76)

    out = SanTEKTrainingResult(
        converged=False,
        converged_at_epoch=None,
        total_epochs_run=0,
        global_vocab=global_vocab,
    )
    prev_tension = float("inf")
    plateau_count = 0

    for epoch in range(1, epochs + 1):
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

        if verbose:
            _print_epoch(ep, epochs)

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

    # ── GLOBAL MERGE: all text path_scores → single model ────────────────────
    global_ps: PathScores = {}
    for i in valid_indices:
        _merge_path_scores_additive(global_ps, text_path_scores[i])

    # Final normalise
    if global_ps:
        vals = list(global_ps.values())
        lo, hi = min(vals), max(vals)
        span = hi - lo
        if span > 0:
            global_ps = {k: (v - lo) / span for k, v in global_ps.items()}

    out.final_path_scores = global_ps

    if verbose:
        _print_summary(out)

    # Auto-save if path given
    if model_path is not None:
        _save_model(global_ps, global_vocab, out, model_path)
        if verbose:
            print(f"  Model saved → {model_path}")

    return out


# ─────────────────────────────────────────────────────────────────────────────
# Save / Load
# ─────────────────────────────────────────────────────────────────────────────

def _save_model(
    path_scores: PathScores,
    vocab: Vocab,
    result: SanTEKTrainingResult,
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 4,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "meta": {
            "converged": result.converged,
            "converged_at_epoch": result.converged_at_epoch,
            "total_epochs_run": result.total_epochs_run,
            "best_accuracy": result.best_accuracy,
            "best_9centric": result.best_9centric,
            "edge_count": len(path_scores),
            "vocab_size": len(vocab),
        },
        "path_scores": [[a, b, v] for (a, b), v in path_scores.items()],
        "vocab": {str(k): v for k, v in vocab.items()},
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def save_base_model(
    model: SantekModel,
    path: Path,
    *,
    training_config: Optional[Dict[str, Any]] = None,
) -> Path:
    """Public save API."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: Dict[str, Any] = {
        "version": 4,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "meta": model.meta,
        "path_scores": [[a, b, v] for (a, b), v in model.path_scores.items()],
        "vocab": {str(k): v for k, v in model.vocab.items()},
    }
    if training_config is not None:
        payload["training_config"] = training_config
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
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
    if "training_config" in payload:
        meta["training_config"] = payload["training_config"]
    return SantekModel(path_scores=ps, vocab=vocab, meta=meta)


# ─────────────────────────────────────────────────────────────────────────────
# Generation
# ─────────────────────────────────────────────────────────────────────────────

def _is_prompt_connected(last_symbol: int, path_scores: PathScores) -> bool:
    for (fr, to) in path_scores:
        if fr == last_symbol and to != last_symbol:
            return True
    return False


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
    length: int = 30,
    methods: Optional[List[str]] = None,
    refuse_if_disconnected: bool = True,
) -> Tuple[str, bool]:
    """
    Generate text from prompt. Returns (output_text, was_refused).

    Uses all 9 methods on prompt to find best anchor in learned graph.
    Refuses if prompt is structurally disconnected from model.
    """
    if methods is None:
        methods = ALL_TOKENIZATION_METHODS

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
        methods = ALL_TOKENIZATION_METHODS

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