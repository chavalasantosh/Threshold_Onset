# Identity-conditioned continuation (design)

**Status:** Design note — not a frozen phase contract.

## What this is not

- **Not** “halo effect” as a baked prior (“source A is good → trust everything from A”).
- **Not** Phase 0–4. Those phases stay structural / aliasing without social or reputational semantics.

## What this is

**Observed** continuation may depend on **both** “what” and “who” (source handle), e.g.:

- Same **content signature** (symbol run, template id, cluster id, hash of utterance structure).
- Different **source identity** (or role handle).
- Different **downstream** structural events (ignored vs engaged, reply vs silence).

Formal pattern:

```text
(source_id, content_id) → observed_next_event
```

Counts and graphs only — **no** moral labels, **no** global “worthiness” scalar unless it is itself an emergent summary you define and audit.

## Relation to existing code

| Layer | What it does today |
|--------|---------------------|
| **Phases 0–4** | Residues, identity hashes, relations, symbols — no “speaker reputation”. |
| **Phase 10** | Directed **identity → identity** statistics on **ordered identity streams** from the pipeline. Same *content* from two sources is **not** separated unless you add a **content** dimension to the stream or to the state space. |
| **Semantic 5–9** | Consequence / roles / constraints / fluency — richer context for “what” and interaction shape. |

## What you need to implement (when ready)

1. **Stable handles**  
   - `source_id`: structural id for the emitting process (identity hash, role id, or session-scoped id — project-defined).  
   - `content_id`: structural summary of “what” was emitted (not raw text if you want reproducibility — e.g. symbol sequence hash, template key).

2. **Event vocabulary**  
   Define observable **outcomes** as discrete or hashed events (e.g. `no_response`, `reply_within_k`, `branch_to_topic_q`). Must be measurable from logs or simulation, not inferred “respect”.

3. **Accumulation**  
   Same discipline as Phase 10: directed counts, optional gates, JSON-serializable summaries. Optional comparison: same `content_id`, different `source_id` → compare outgoing distributions **empirically**.

4. **Boundary**  
   If two sources never appear with the same `content_id` in data, you cannot claim “same sentence, different treatment” from structure alone — that is a **data coverage** limit, not a failure of the formalism.

## Naming

Prefer **identity-conditioned continuation** or **source-conditioned continuation** over “halo” in code and APIs to avoid importing psychological bias as a specification.

## Implementation in this repo

- **`threshold_onset.identity_conditioned.IdentityConditionedAccumulator`** — count `(source_id, content_id, outcome_key)` triples; `to_jsonable()` / `from_jsonable()` for persistence.
- **Semantic Phase 5** (`ConsequenceFieldEngine`) — optional `phase10_metrics=` stores a Phase 10 JSON snapshot inside **`save()` metadata only** (provenance; **does not** change rollouts or vectors). Entry points pass `phase10_jsonable_from_model_state(model_state)` when available.

## Reconciling this note with informal “Phase 5–6 territory” language

Some explanations place *interaction* / *who + what* “near Phase 5–6” **conceptually** (consequence field, meaning clusters). In **this repository’s numbering**:

| Idea in the narrative | Where it lives in code |
|------------------------|-------------------------|
| “Same content, different source → different outcome” (observed counts) | **`threshold_onset.identity_conditioned`** (+ your event logs), **not** a frozen numbered phase. |
| Directed **identity → identity** along time (no separate “content” key unless you add it) | **`threshold_onset.phase10`** |
| Consequence / futures / policies over structure | **`threshold_onset.semantic.phase5`** (semantic Phase 5 **only** — see `docs/CANONICAL_PHASE_MAP.md`) |
| Meaning clusters | **`threshold_onset.semantic.phase6`** |

So: the **psychology** word “halo” is still a bad **spec** name; the **structure** you want is **identity-conditioned observation**. Do **not** confuse that with **semantic Phase 5**’s package path — they are different layers.

## See also

- `threshold_onset/phase10/README.md` — directed continuation on identity streams.
- `docs/MODEL_CONTRACT.md` — `model_state` shape; optional `phase10_metrics`.
