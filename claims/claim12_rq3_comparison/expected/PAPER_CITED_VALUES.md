# PAPER_CITED_VALUES — `fig:rq3_finding1`

Paper canonical values from `paper.tex` L848-855 (label `\label{fig:rq3_finding1}`).

## Header

- Caption: "Detection rate (%) on the GPT-5.4 oracle benchmark ($n{=}76$, `select` mode, GPT-5.4 judge). Rows are grouped into proprietary scanners, open-weight baselines, and the fine-tuned Qwen2.5-Coder-7B-Instruct scanner."
- Benchmark: GPT-5.4 oracle, $n=76$, `select` mode
- Judge: GPT-5.4

## Scanner detection rates (n=76, select mode, GPT-5.4 judge)

| Scanner | Group | Detection | Rate (%) |
|---|---|---|---|
| skill-security-scan | rule | 6/76 | 7.89% |
| Snyk Agent Scan | rule | 7/76 | 9.21% |
| SkillScan | rule | 1/76 | 1.32% |
| GPT-4o-mini | proprietary | 18/76 | 23.68% |
| GPT-5.4-mini | proprietary | 60/76 | 78.95% |
| GPT-5.4 | proprietary | 66/76 | 86.84% |
| Qwen2.5-Coder-7B-Instruct (base) | ours_base | 13/76 | **17.11%** |
| **Qwen2.5-Coder-7B-Instruct (ours)** | ours_ft | **67/76** | **88.16%** |

## Headline claims (Finding 4 narrative)

- Our fine-tuned scanner achieves 88.16% detection (67/76), improving over the base Qwen2.5-Coder-7B-Instruct by **71.05 pp** (17.11% → 88.16%).
- Exceeds GPT-5.4-mini by 9.21 pp (78.95% → 88.16%).
- Exceeds GPT-5.4 (frontier) self-detection by 1.32 pp (86.84% → 88.16%).

## Cross-source consistency

- Values cross-match with:
  - `table3_cross_scanner_matrix/` (rule-based + proprietary, GPT-5.4 oracle column)
  - `table6_finetune_base_models/` (Qwen2.5-Coder-7B-Instruct rows, prefill mode)
  - `table7_phase_ablation/` (Phase 1→4 chain reaches 88.16% at "+prefill" row)
- See `raw/scanners.csv` for machine-readable form.
