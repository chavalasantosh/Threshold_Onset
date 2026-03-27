# THRESHOLD_ONSET Paper

Professional LaTeX paper in NeurIPS/Google/DeepMind style.

## Formatting (NeurIPS-style)

- **Layout**: 5.5" × 9" text block, US Letter, 1.5" left margin
- **Font**: 10pt Times (mathptmx)
- **Title**: 17pt bold, centered between two horizontal rules
- **Abstract**: Centered bold "Abstract", indented single paragraph
- **Sections**: 12pt bold, flush left (NeurIPS heading style)

## Structure

- **Abstract** – Identity as induced; phase boundary; graph-theoretic invariant
- **§1 Introduction** – Motivation, contributions
- **§2 Preliminaries** – Formal notation
- **§3 Axioms** – Action before knowledge; identity is induced; constraint; structural inversion
- **§4 Background** – Related work
- **§5 Model Architecture** – Phases 0–4, decoder, generation
- **§6 Formal Propositions** – Reproducibility; no self-transition (A_ii=0); phase boundary p*; monotonicity
- **§7 Experiments** – Validation, benchmark, baselines, external, stability (frac vs theory)
- **§8 Results & Analysis** – Invariant; topology; identity collapse
- **§9 Conclusion** – Limitations, future work
- **Appendix** – Phase boundaries; stability mode & phase transition (binomial, p*); full sweep; ablations

## Figures

- **Figure 1** – Pipeline (Phase 0–4 + generation + decoder)
- **Figure 2** – Decoder forward/reverse flow
- **Figure 3** – Relation graph schematic

## Tables

- Hyperparameters, Validation (7/7), Stress test, Symbol mapping, Comparison, Summary

## Files

- `main.tex` – Main paper
- `appendix.tex` – Appendix sections
- `main_paperbanana_style.tex` – Alternate (longer) version
- `THRESHOLD_ONSET_PAPER.md` – Markdown summary
- `../docs/PHASE_TRANSITION_THEORY.md` – Formal phase boundary theory

## Compile

```bash
cd paper
pdflatex main.tex
pdflatex main.tex
```

Or upload `main.tex` and `appendix.tex` to Overleaf.

## Output

`main.pdf` – ~10–12 pages, ready for arXiv/workshop.
