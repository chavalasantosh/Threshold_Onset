# Architecture workflow & process

This page is the **“how it works”** view — similar in spirit to **transformer / NN block diagrams** (boxes and arrows), but matched to **this** codebase: structural phases + SanTEK learning, **not** a generic PyTorch transformer tutorial.

---

## 1. Analogy: classic ML diagram vs this project

| Typical deep-learning diagram | In THRESHOLD_ONSET (what actually exists) |
|------------------------------|-------------------------------------------|
| Input tensor | **Text** (string or file) |
| Embedding layer | **Tokenization** (SanTOK / strategies in `run_complete`) |
| Stack of layers | **Phases 0–4** (structural) then **semantic 5–9** (when used in a flow) |
| Forward pass | **Pipeline run** — residues, boundaries, identity, relations, symbols |
| Loss + backprop | **Not** standard gradient descent on neural weights. **SanTEK-SLE** updates **path scores / structural state** (see `santek_base_model.py`, `integration/model/santek_base.py`) |
| Checkpoint | **`output/`** JSON / `santek_base_model.json` style artifacts |
| Inference | **GEN / CHAT / API** — prompt → pipeline → symbol sequence → extend via path scores → decode to text |

So: think **structural pipeline + learned transition statistics**, not “one big differentiable transformer.”

---

## 2. Big picture: repo vs runtime

```mermaid
flowchart TB
  subgraph dev [Developer workflow]
    clone[Clone repo]
    install[pip install -e . dev]
    smoke[python scripts/dev_check.py]
    edit[Edit code]
    test[pytest]
    push[git push]
    clone --> install --> smoke --> edit --> test --> push
  end

  subgraph runtime [Runtime — what runs the idea]
    entry[Entry: main.py / run_complete / API / health_server]
    int[integration layer]
    core[threshold_onset phases + semantic]
    tok[santok_complete optional]
    out[Artifacts: output/ logs metrics]
    entry --> int --> core
    int --> tok
    core --> out
  end
```

---

## 3. Core processing pipeline (conceptual)

**Orchestrator:** `integration/run_complete.py` ties tokenization, phases, topology/scoring, optional generation.

```mermaid
flowchart LR
  T[Text in]
  Tok[Tokenize]
  P0[Phase 0 Action / residue]
  P1[Phase 1 Boundaries]
  P2[Phase 2 Identity]
  P3[Phase 3 Relations]
  P4[Phase 4 Symbols]
  S5[Semantic 5–9 optional]
  Topo[Topology / scoring / surface]
  R[PipelineResult state + metrics]
  T --> Tok --> P0 --> P1 --> P2 --> P3 --> P4 --> S5 --> Topo --> R
```

**Package home for phases:** `threshold_onset/phase0` … `phase4`, `threshold_onset/semantic/`.

---

## 4. SanTEK base model: train → save → generate

High-level flow as described in `santek_base_model.py`:

```mermaid
flowchart TB
  subgraph train [Training]
    C[Corpus lines / files]
    P[Phase 0–4 on each text]
    Sym[Symbol sequences + transitions]
    SLE[SanTEK-SLE / ASD / path reinforcement]
    J[(santek_base_model.json)]
    C --> P --> Sym --> SLE --> J
  end

  subgraph infer [Generation / chat]
    Pr[Prompt text]
    P2[Phase 0–4 → symbol sequence]
    Ext[Greedy / beam over path_scores]
    Dec[Decode symbols → text]
    Out[Text out]
    Pr --> P2 --> Ext --> Dec --> Out
    J -. provides .-> Ext
  end
```

**Note:** This is **structural + learned scores on transitions**, not “attention softmax × V” in the Transformer sense.

---

## 5. How requests reach code (API / HTTP)

```mermaid
sequenceDiagram
  participant Client
  participant HS as scripts/health_server.py
  participant API as threshold_onset.api.process
  participant Pipe as integration / phases

  Client->>HS: POST /process JSON body
  HS->>API: process(text, options)
  API->>Pipe: pipeline work as configured
  Pipe-->>API: result object
  API-->>HS: ProcessResult
  HS-->>Client: text/plain or JSON compact line codec
```

**Compact encoding:** `threshold_onset/line_codec.py` used for logs / health payloads.

---

## 6. Clean development process (recommended)

```mermaid
flowchart TD
  A[Clone + branch] --> B[pip install -e . dev]
  B --> C[python scripts/dev_check.py]
  C --> D{Pass?}
  D -->|No| E[Fix imports / tests]
  E --> C
  D -->|Yes| F[Run one target only]
  F --> G[integration/run_complete.py sample]
  F --> H[pytest tests/ scoped]
  F --> I[API / health_server if needed]
  G --> J[Commit small logical changes]
  H --> J
  I --> J
  J --> K[Push]
```

**Rule of thumb:** one entry point per debugging session (`run_complete` *or* `main.py` *or* API), so you do not mix five stories at once.

---

## 7. Where to read more

| Topic | Doc |
|-------|-----|
| Repo vs `threshold_onset/` package | [FULL_ARCHITECTURE.md](FULL_ARCHITECTURE.md) |
| Deep codebase map, `run_complete`, SanTEK files | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Install + smoke commands | [GOLDEN_PATH.md](GOLDEN_PATH.md) |
| Semantic layers 5–9 | [../../threshold_onset/semantic/ARCHITECTURE.md](../../threshold_onset/semantic/ARCHITECTURE.md) |

---

## Rendering

GitHub renders **Mermaid** in Markdown automatically. In VS Code, use a Mermaid preview extension if you want the same diagrams locally.
