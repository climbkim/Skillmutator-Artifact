# Cross-Family Claude Judge — Paper Cited Values

This document maps every value that the paper takes from this cross-family judge
resource (`artifact/data/paper_shared/cross_family_judge/`) to its source rows, so a
reviewer can trace each value. All rates are on the 76-case GPT-5.4 oracle benchmark.

---

## Figure 5, §6.4 Fine-tuning Effectiveness — right panel (Claude-Opus-4.7 judge)

| paper value | value | source row in `derived/agreement_summary.csv` | source data |
|---|---|---|---|
| Qwen base | 7.9\% | `qwen-base` claude_det=6, n=76 | `verdicts_base/` (Qwen subset) |
| Qwen no-prefill | 75.0\% | `qwen-d3-noprefill` claude_det=57, n=76 | `verdicts_noprefill/` (Qwen subset) |
| Qwen prefill | **85.5\%** | `qwen-d3-prefill` claude_det=65, n=76 | `verdicts/` (Qwen subset of the cross-scanner manifest) |
| Qwen Δ | +10.5\,pp | 85.53 − 75.00 = 10.53 | computed |
| Llama base | 2.6\% | `llama-base` claude_det=2, n=76* | `verdicts_base/` (Llama subset, 65 cells + 11 imputed) |
| Llama no-prefill | **88.2\%** | `llama-d3-noprefill` claude_det=67, n=76 | `verdicts_noprefill/` (Llama subset) |
| Llama prefill | 76.3\% | `llama-d3-prefill` claude_det=58, n=76 | `verdicts_finetune/` (Llama subset) |
| Llama Δ | −11.9\,pp | 76.32 − 88.16 = −11.84 | computed |
| Mistral base | 5.3\% | `mistral-base` claude_det=4, n=76 | `verdicts_base/` (Mistral subset) |
| Mistral no-prefill | **68.4\%** | `mistral-d3-noprefill` claude_det=52, n=76 | `verdicts_noprefill/` (Mistral subset) |
| Mistral prefill | 55.3\% | `mistral-d3-prefill` claude_det=42, n=76 | `verdicts_finetune/` (Mistral subset) |
| Mistral Δ | −13.2\,pp | 55.26 − 68.42 = −13.16 | computed |
| Gemma base | 6.6\% | `gemma-base` claude_det=5, n=76 | `verdicts_base/` (Gemma subset) |
| Gemma no-prefill | 68.4\% | `gemma-d3-noprefill` claude_det=52, n=76 | `verdicts_noprefill/` (Gemma subset) |
| Gemma prefill | **69.7\%** | `gemma-d3-prefill` claude_det=53, n=76 | `verdicts_finetune/` (Gemma subset) |
| Gemma Δ | +1.3\,pp | 69.74 − 68.42 = +1.32 | computed |
| Dashed line: frontier GPT-5.4 scanner | 81.6\% (86.8\% in the left, GPT-5.4-judge panel) | `gpt-5.4-self`: 62/76 Claude, 66/76 GPT-5.4 | `verdicts/` (`gpt-5.4-self` subset) |

*Llama base has 11 missing scans: 65 cells measured and the 11 missing ones counted as
"not detected", so 2/76 = 2.63\% (the paper's n=76 denominator).

---

## §6.4 Fine-tuning Effectiveness — Finding 4 (Claude-judge sentence)

| paper wording | value | source |
|---|---|---|
| "Under a Claude-Opus-4.7 judge, the fine-tuned scanner remains ahead of GPT-5.4 by 3.9 pp (85.5% vs. 81.6%)" | 85.53 − 81.58 = 3.95 | `qwen-d3-prefill` claude_rate − `gpt-5.4-self` claude_rate |

## §6.4 Fine-tuning Effectiveness — Finding 5 (Claude-judge sentence)

| paper wording | value | source |
|---|---|---|
| "Qwen benefits from prefilling (+10.5 pp)" | +10.53 | `qwen-d3-prefill` − `qwen-d3-noprefill` (claude_rate) |
| "Llama and Mistral perform better without it (−11.9 pp and −13.2 pp)" | −11.84 / −13.16 | `llama-d3-*`, `mistral-d3-*` rows |
| "Gemma remains near-neutral, with a small +1.3 pp" | +1.32 | `gemma-d3-*` rows |

The GPT-5.4-judge counterparts in the same paragraph (+9.2 / −7.9 / −17.1 / −2.6 pp)
are verified by `claims/claim10_prefill_delta/`.

---

## Supplementary statistics (not cited in the final paper)

These come from the same verdicts and are kept for transparency:

| statistic | value | source |
|---|---|---|
| cells judged by both judges | 1,126 (301 + 228 + 304 + 293) | the four manifests |
| scanner/model-mode rows | 15 | `derived/agreement_summary.csv` |
| per-row Cohen's $\kappa$ | 0.425 (`qwen-d3-prefill`) to 1.000 (`gpt-4o-mini`, `gpt-5.4-mini`) | `kappa` column |
| GPT-5.4 − Claude rate | −5.26 pp (`gpt-5.4-self`), −2.63 pp (`qwen-d3-prefill`) | `delta_pp` column |
| judge-input caps | scanner output 12,000 characters, injected snippet 1,500 characters | see README (3) |

The judge-robustness results of Appendix B.2 (93.7% agreement with the rebuilt ground
truth and 96.1% with a Claude-Opus-5 judge) come from a separate experiment and are not
produced from this folder.

---

## How to check

Every value above can be read from `derived/agreement_summary.csv` (columns `gpt_rate`,
`claude_rate`, `delta_pp`, `kappa`); `derived/agreement_report.md` gives the same view per
scanner. The aggregation script is not shipped.
