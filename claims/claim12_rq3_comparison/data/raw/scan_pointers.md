# Raw Scan Pointers — Figure 6 RQ3 Finetune Comparison

This figure aggregates detection rates from 8 scanners on the n=76 GPT-5.4 oracle
benchmark. The underlying scan trees are not redistributed. `scanners.csv` (in this folder) is the
machine-readable summary; the table below names each scanner's source, and the
cross-check paths point to the aggregates shipped with other claims.

## Per-scanner source (one row of `scanners.csv` per scanner)

| Scanner | Group | Raw scan path |
|---|---|---|
| `skill-security-scan` | rule | skill-security-scan reports on the unmodified and mutated skills — source not redistributed |
| `Snyk Agent Scan` | rule | Snyk Agent Scan reports on the unmodified and mutated skills — source not redistributed |
| `SkillScan` | rule | SkillScan API responses — source not redistributed |
| `GPT-4o-mini` | proprietary | `gpt-4o-mini scan (last iteration, select mode) — source not redistributed` |
| `GPT-5.4-mini` | proprietary | `gpt-5.4-mini scan (last iteration, select mode) — source not redistributed` |
| `GPT-5.4` | proprietary | `gpt-5.4 self-scan (last iteration, select mode) — source not redistributed` |
| `Qwen2.5-Coder-7B-Instruct (base)` | ours_base | base Qwen2.5-Coder-7B scans (76 cells) — source not redistributed |
| `Qwen2.5-Coder-7B-Instruct (ours)` | ours_ft | fine-tuned Qwen2.5-Coder-7B scans, prefill (76 cells) — source not redistributed |

"last iteration" = the highest iteration whose classification is normal.

## Judge

All scanner outputs are adjudicated by the GPT-5.4 judge:
- Judge script: `artifact/code/skillmutator/analysis/skillmutator_utils/judge.py` (shipped)
- Per-scanner aggregates: see `../../../claim02_cross_scanner_detection/data/derived/` and
  `../../../claim11_finetune_base_models/data/derived/`

## Aggregation chain

1. Per-scanner scan trees are judged → judge CSV per (skill, category) → 76 binary verdicts
2. Aggregate verdicts → detection rate (% out of 76)
3. Hard-coded into `scripts/plot_candidates.py` `SCANNERS` list constant
4. `scripts/export_scanners_csv.py` exports this list → `scanners.csv`

## Cross-source consistency

The 8 detection rates in `scanners.csv` cross-match:
- Rule-based + proprietary rows: `../../../claim02_cross_scanner_detection/data/derived/table3_aggregate.csv` (GPT-5.4 oracle column)
- Qwen rows: `../../../claim11_finetune_base_models/data/derived/table6_aggregate.csv` (Qwen row, base + prefill cells)
- Final 88.16% row: also appears in `../../../claim04_phase_ablation/data/derived/` final row `+ prefill`

## No standalone raw scan tree in this folder

This folder intentionally **does not duplicate** per-skill scan.md trees (they
are not redistributed); the cross-check paths above point to the shipped aggregates. The figure is a visualization of
already-derived aggregate values, not a primary measurement.
