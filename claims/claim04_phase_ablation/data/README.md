# Table VI — Four-phase schema ablation (Qwen2.5-Coder-7B)

## (1) Paper location

- **LaTeX label**: `\label{tab:finetune_rq2}`
- **Caption**: "Four-phase schema ablation on Qwen2.5-Coder-7B-Instruct."
- **Finding 6**: all four phases contribute to detection.

## (2) Paper-cited values (four-section consistent chain)

| Schema | Detection (no-prefill) | Δ from prev |
|---|---|---|
| Phase 1 (Purpose Grounding) | 1.32% (1/76) | — |
| + Phase 2 (Out-of-Scope Detection) | 25.00% (19/76) | +23.7pp |
| + Phase 3 (Principle Reasoning) | 57.89% (44/76) | +32.9pp |
| + Phase 4 (Category Labeling) | **67.11%** (51/76) | **+9.2pp (schema)** |
| + deterministic refinement | **78.95%** (60/76) | **+11.8pp (refine)** |
| + prefill (Phase 4 header forced) | **88.16%** (67/76) | **+9.2pp (prefill)** |

Three-piece decomposition: **schema +9.22pp · refine +11.84pp · prefill +9.21pp**.

## (3) Bundled data (judge verdicts)

Only judge-level verdict CSVs are shipped (columns
`skill,category,cat_folder,iter,detected,confidence,reason`). Each filename names
the schema configuration it evaluates; the raw scanner trees are not
redistributed.

| Row | Source CSV |
|---|---|
| Phase 1 | `judge/phase1_noprefill.csv` (1/76) |
| + Phase 2 | `judge/phase1-2_noprefill.csv` (19/76) |
| + Phase 3 | `judge/phase1-3_noprefill.csv` (44/76) |
| + Phase 4 (no refine) | `judge/phase1-4_noprefill.csv` (51/76) |
| + deterministic refinement | `judge/phase1-4_refine_noprefill.csv` (60/76) |
| + prefill | `judge/phase1-4_refine_prefill.csv` (67/76) |

Alternative Phase-4 (no-refine) evaluation variants are also bundled for
reference: `phase1-4_prefill.csv` (4-section prefill), `phase1-4_3section_*.csv`
(3-section eval), `phase1-4_pseries_*.csv` (P-series schema eval).

## (4) Reproduce

```bash
python scripts/build_table7.py        # judge/ -> derived/table7_aggregate.csv
python scripts/verify_paper_match.py  # compare against PAPER_CITED_VALUES.md
```

CPU only; no API key or GPU needed for verification.

## (5) Fine-tuned adapters (for full re-inference only)

The Qwen2.5-Coder-7B LoRA adapter is hosted on Hugging Face, not bundled. See
the Hugging Face adapter repo (huggingface.co/climbkim/skillmutator-scanner-adapters) for the exact asset name. The no-refinement ablation adapter is
not published (available on request; see `ETHICS.md`). Re-inference needs a single >= 24 GB GPU.

## (6) Evaluation note — four-section consistent chain

All six rows use the four-section evaluation, so the phase-by-phase progression
is measured consistently. The decomposition (Finding 6) is:

- **schema effect** (Phase 3 → Phase 4): +9.22pp (= 67.11 − 57.89)
- **refine effect** (Phase 4 → + refine): +11.84pp (= 78.95 − 67.11)
- **prefill effect** (+ refine → + prefill): +9.21pp (= 88.16 − 78.95)

## (7) Verification

Verified by `scripts/verify_paper_match.py` — all 6 rows match the paper.
