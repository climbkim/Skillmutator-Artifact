# Table V — select vs no-select Mode Comparison (GPT-5.4 oracle)

## (1) Paper location

- **LaTeX label**: `\label{tab:select_vs_noselect}`
- **Paper lines**: L807–L828
- **Caption**: "Detection rate (%) for the `select` and `no-select` modes on the
  GPT-5.4 oracle dataset, adjudicated by GPT-5.4 judge."

## (2) PAPER_TARGET_VALUES (paper.tex as-is)

| Scanner | select | no-select | Δ |
|---|---|---|---|
| skill-security-scan | 7.89% | 12.09% | +4.20pp |
| Snyk Agent Scan | 9.21% | 16.74% | +7.53pp |
| SkillScan API | 1.32% (1/76) | 5.43% (12/221) | +4.11pp |
| GPT-4o-mini scanner | 23.68% | 36.74% | +13.06pp |
| GPT-5.4-mini scanner | 78.95% | 87.91% | +8.96pp |
| GPT-5.4 scanner | **86.84%** | **91.63%** | +4.79pp |
| **Average (6 scanners)** | **34.65%** | **41.76%** | **+7.10pp** |

(All scanners: select n=76 / no-select n=215. SkillScan was added later with its own scenario set
n=76/221, so its denominator differs — paper notation select 1.3% / no-select 5.4%.)

## (3) Data source

| Scanner | raw |
|---|---|
| ss | the source scan tree (not redistributed) |
| Snyk | same `.../snyk/{report.md,verdict.json}` |
| LLM scanners | same `.../llm/{gpt-4o-mini,gpt-5.4-mini,gpt-5.4-self}/scan.md` + judge_v2.json |

- select: 76 (skill, cat) cells (stealth-selected attack categories per skill)
- no-select: 215 cells (all 13 categories per all 17 skills)

Decision criterion: each scanner's verdict at the **last iteration** (carry-forward across refusals).

## (4) Reproduction commands

```bash
cd claim03_stealth_aware_selection
bash run.sh
#   → build_table5.py: regenerate derived/tab_select_vs_noselect.csv (6 scanners)
#   → verify_paper_match.py: ✅ 6/6 verified
```

`build_table5.py` re-aggregates the 5 API scanners from the bundled `judge/select_vs_noselect_verdicts.csv`
and SkillScan from the bundled `skillscan_addition/derived/*.csv`.
It reproduces on CPU alone, without an API key/GPU/original scan tree.

## (5) Dependencies (all bundled)

- `judge/select_vs_noselect_verdicts.csv` — final per-scenario decision flags for the 5 API scanners
- `skillscan_addition/derived/{select,no_select}_perscenario.csv` — SkillScan paired decisions
- the original scan.md tree (containing injected malicious mutation text) is not redistributed (see ETHICS.md)

## (6) Verification status

Verified: 6 scanner rows + Average row all match the paper.

## (7) Note — Average calculation

`Average (6 scanners)` is the simple mean of the 6 scanners (mean of each scanner's detection rate).
`scripts/verify_paper_match.py` computes it automatically. If any of the 6 scanner rows changes,
the average must be updated too. The SkillScan row is recomputed by `build_table5.py` from the bundled
`skillscan_addition/derived/{select,no_select}_perscenario.csv`
by the paired escalation (≥MEDIUM) criterion.