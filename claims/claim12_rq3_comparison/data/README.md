# Figure 6 — RQ3 Detection Comparison (Fine-tuned vs Baselines)

## (1) Paper location

- **LaTeX label**: `\label{fig:rq3_finding1}`
- **Paper location**: §6.4, after Finding 4
- **Caption**: "Detection rate (%) on the GPT-5.4 oracle benchmark ($n{=}76$, `select` mode, GPT-5.4 judge). Rows are grouped into proprietary scanners, open-weight baselines, and the fine-tuned Qwen2.5-Coder-7B-Instruct scanner."

## (2) PAPER_TARGET_VALUES

See [PAPER_CITED_VALUES.md](PAPER_CITED_VALUES.md).

Summary (8 scanners, n=76, select mode, GPT-5.4 judge):

| Group | Scanner | Rate (%) |
|---|---|---|
| Rule-based | skill-security-scan / Snyk Agent Scan / SkillScan | 7.89 / 9.21 / 1.32 |
| Proprietary | GPT-4o-mini / GPT-5.4-mini / GPT-5.4 | 23.68 / 78.95 / 86.84 |
| Ours (base) | Qwen2.5-Coder-7B-Instruct (no FT) | 17.11 |
| Ours (FT+prefill) | Qwen2.5-Coder-7B-Instruct (ours) | **88.16** |

## (3) Data source

8 scanner detection rates are cross-sourced from:
- Rule-based: paper Table III (`table3_cross_scanner_matrix/`), GPT-5.4 oracle column
- Proprietary LLM: paper Table III, GPT-5.4 oracle column
- Qwen2.5-Coder-7B-Instruct base/ours: paper Table VI (`table6_finetune_base_models/`)
- Final headline 88.16% also appears in paper Table VII (`table7_phase_ablation/` final row "+prefill")

### Raw files (raw/)
- `scanners.csv` — 8 scanners × (label, detected, rate_pct, group)
- `scan_pointers.md` — canonical paths to per-scanner scan.md trees (in `table3_*/`, `table6_*/`, the source scan tree not redistributed). Figure 6 is a visualization of derived aggregates, not a primary measurement, so per-skill scan trees are not duplicated here.

### Figure files (top-level)
- `rq3_finding1.{pdf,png}` — paper canonical figure

## (4) Reproduction commands

```bash
cd figure8_rq3_finetune_comparison

# 1. Export SCANNERS table to CSV
python scripts/export_scanners_csv.py
# → writes raw/scanners.csv

# 2. Render 4 candidate visualizations
python scripts/plot_candidates.py
# → writes derived/candidate_{1..4}.{pdf,png}

# 3. (Manual) choose canonical figure → copy to rq3_finding1.{pdf,png}
```

## (5) Dependencies

- `matplotlib`, `numpy`
- Python ≥ 3.8

## (6) Verification status

Verified: values in `raw/scanners.csv` cross-match the paper's cross-scanner table and the fine-tuned final row at 88.16%.
