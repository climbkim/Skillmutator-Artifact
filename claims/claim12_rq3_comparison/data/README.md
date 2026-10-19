# Figure 6 — RQ3 Detection Comparison (Fine-tuned vs Baselines)

## (1) Paper location

- **Paper location**: Figure 6, §6.4 Fine-tuning Effectiveness (Finding 4)
- **Caption**: "Detection rate (%) on the GPT-5.4 oracle benchmark ($n{=}76$)."

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
- Rule-based: paper Table 4 (`claims/claim02_cross_scanner_detection/`), GPT-5.4 oracle column
- Proprietary LLM: paper Table 4, GPT-5.4 oracle column
- Qwen2.5-Coder-7B-Instruct base/ours: paper Figure 5 (`claims/claim11_finetune_base_models/`)
- Final headline 88.16% also appears in paper Table 6 (`claims/claim04_phase_ablation/`, final row "+prefill")

### Raw files (raw/)
- `scanners.csv` — 8 scanners × (label, detected, rate_pct, group)
- `raw/scan_pointers.md` — per-scanner source of each row (scan trees not redistributed) and the cross-check paths to the claim02, claim04 and claim11 aggregates. Figure 6 is a visualization of derived aggregates, not a primary measurement, so per-skill scan trees are not duplicated here.

### Figure files (top-level)
- `rq3_finding1.{pdf,png}` — paper canonical figure

## (4) Reproduction commands

```bash
bash ../run.sh                           # export + verify Figure 6 values

# Export the SCANNERS table to CSV
python scripts/export_scanners_csv.py
# → writes raw/scanners.csv

# Render the figure
python scripts/plot_candidates.py
# → writes derived/candidate_{1..4}.{pdf,png}
```

## (5) Dependencies

- `matplotlib`, `numpy`
- Python ≥ 3.8

## (6) Verification status

Verified: values in `raw/scanners.csv` cross-match the paper's cross-scanner table and the fine-tuned final row at 88.16%.
