# Raw Scan Pointers — Figure 6 RQ3 Finetune Comparison

This figure aggregates detection rates from 8 scanners on the n=76 GPT-5.4 oracle
benchmark. The underlying scan trees are already preserved in other bundle
folders to avoid duplication. `scanners.csv` (in this folder) is the
machine-readable summary; raw scan.md files live at the paths below.

## Per-scanner source (one row of `scanners.csv` per scanner)

| Scanner | Group | Raw scan path |
|---|---|---|
| `skill-security-scan` | rule | `../../table3_cross_scanner_matrix/raw/skill-security-scan/baseline/` + the source scan tree (not redistributed) |
| `Snyk Agent Scan` | rule | `../../table3_cross_scanner_matrix/raw/snyk/` + the source scan tree (not redistributed) |
| `SkillScan` | rule | `../../table3_cross_scanner_matrix/raw/skillscan/` (API responses) |
| `GPT-4o-mini` | proprietary | `gpt-4o-mini scan (last iteration, select mode) — source not redistributed` |
| `GPT-5.4-mini` | proprietary | `gpt-5.4-mini scan (last iteration, select mode) — source not redistributed` |
| `GPT-5.4` | proprietary | `gpt-5.4 self-scan (last iteration, select mode) — source not redistributed` |
| `Qwen2.5-Coder-7B-Instruct (base)` | ours_base | base Qwen2.5-Coder-7B scans (76 cells) — source not redistributed |
| `Qwen2.5-Coder-7B-Instruct (ours)` | ours_ft | fine-tuned Qwen2.5-Coder-7B scans, prefill (76 cells) — source not redistributed |

"last iteration" = the highest iteration whose classification is normal.

## Judge

All scanner outputs are adjudicated by the GPT-5.4 judge:
- Judge script: the judge script (not redistributed)
- Per-scanner judge CSV: see `../../table3_cross_scanner_matrix/derived/` and
  `../../table6_finetune_base_models/derived/`

## Aggregation chain

1. Per-scanner scan trees are judged → judge CSV per (skill, category) → 76 binary verdicts
2. Aggregate verdicts → detection rate (% out of 76)
3. Hard-coded into `scripts/plot_candidates.py` `SCANNERS` list constant
4. `scripts/export_scanners_csv.py` exports this list → `scanners.csv`

## Cross-source consistency

The 8 detection rates in `scanners.csv` cross-match:
- Rule-based + proprietary rows: `../../table3_cross_scanner_matrix/derived/table3_aggregate.csv` (GPT-5.4 oracle column)
- Qwen rows: `../../table6_finetune_base_models/derived/table6_aggregate.csv` (Qwen row, base + prefill cells)
- Final 88.16% row: also appears in `../../table7_phase_ablation/derived/` final row `+ prefill`

## No standalone raw scan tree in this folder

This folder intentionally **does not duplicate** the per-skill scan.md trees;
they live in the source folders listed above. The figure is a visualization of
already-derived aggregate values, not a primary measurement.
