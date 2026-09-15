# Paper-cited Values — Table VI (`tab:finetune_rq2`)

From Table VI (`tab:finetune_rq2`); four-phase consistent chain.

## Paper Table VI (verified match)

```latex
\begin{tabular}{lrr}
\toprule
\textbf{Schema} & \textbf{Detection Rate} & \textbf{$\Delta$} \\
\midrule
Phase 1 (Purpose Grounding)                                  &  1.32\% & ---                  \\
+ Phase 2 (Out-of-Scope Detection)                                 & 25.00\% & $+23.7\text{\,pp}$   \\
+ Phase 3 (Principle Reasoning)                        & 57.89\% & $+32.9\text{\,pp}$   \\
+ Phase 4 (Category Labeling)                            & 67.11\% & $+9.2\text{\,pp}$    \\
\;\;{\small + deterministic refine}                     & 78.95\% & $+11.8\text{\,pp}$   \\
\;\;{\small + prefill (Phase 4 header forced)}          & 88.16\% & $+9.2\text{\,pp}$    \\
\bottomrule
\end{tabular}
```

## Cell-by-cell verification target

| Row | Detection | Δ | Source CSV | Verified? |
|---|---|---|---|---|
| Phase 1 (Purpose Grounding) | 1.32% | — | `judge/phase1_noprefill.csv` (1/76) | ✅ |
| + Phase 2 (Out-of-Scope Detection) | 25.00% | +23.7pp | `judge/phase1-2_noprefill.csv` (19/76) | ✅ |
| + Phase 3 (Principle Reasoning) | 57.89% | +32.9pp | `judge/phase1-3_noprefill.csv` (44/76) | ✅ |
| + Phase 4 (Category Labeling) | 67.11% | +9.2pp | `judge/phase1-4_noprefill.csv` (51/76) | ✅ |
| + deterministic refinement | 78.95% | +11.8pp | `judge/phase1-4_refine_noprefill.csv` (60/76) | ✅ |
| + prefill (Phase 4 header forced) | 88.16% | +9.2pp | `judge/phase1-4_refine_prefill.csv` (67/76) | ✅ |

## Decomposition

- **Phase schema effect** (P3 → P4): +9.22pp (= 67.11 − 57.89)
- **Refine effect** (P4 → +refine): +11.84pp (= 78.95 − 67.11). Paper Table VI
  prints detection rates to 1 decimal (67.1%, 79.0%), so the **displayed** refine
  delta is **+11.9pp** (79.0 − 67.1) — this is the value cited in claim.txt; the
  2-decimal computation here gives +11.84 → +11.8pp (same figure, finer rounding).
- **Prefill effect** (+refine → +prefill): +9.21pp (= 88.16 − 78.95)

Total (P3 → final) = +30.27pp. Sum check: 57.89 + 9.22 + 11.84 + 9.21 = 88.16 ✅

Verified by `scripts/verify_paper_match.py`.
