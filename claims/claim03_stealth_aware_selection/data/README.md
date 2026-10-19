# Table 5 — select vs no-select Mode Comparison (GPT-5.4 oracle)

## (1) Paper location

- **Paper location**: Table 5, §6.3.1 Stealth-aware Attack Selection
- **Caption**: "Detection rate (%) for the `select` and `no-select` modes on the GPT-5.4 oracle dataset."

## (2) PAPER_TARGET_VALUES (camera-ready paper)

| Scanner | select | no-select | Δ |
|---|---|---|---|
| skill-security-scan | 7.89% | 12.33% | +4.43pp |
| Snyk Agent Scan | 9.21% | 16.89% | +7.68pp |
| SkillScan API | 1.32% (1/76) | 5.48% (12/219) | +4.16pp |
| GPT-4o-mini scanner | 23.68% | 36.07% | +12.39pp |
| GPT-5.4-mini scanner | 78.95% | 87.67% | +8.72pp |
| GPT-5.4 scanner | **86.84%** | **91.32%** | +4.48pp |
| **Average (6 scanners)** | **34.65%** | **41.63%** | **+6.98pp** |

(All scanners, SkillScan included: select n=76 / no-select n=219 — paper notation for SkillScan
select 1.3% / no-select 5.5%.)

## (3) Data source

| Scanner | raw |
|---|---|
| ss | the source scan tree (not redistributed) |
| Snyk | same `.../snyk/{report.md,verdict.json}` |
| LLM scanners | same `.../llm/{gpt-4o-mini,gpt-5.4-mini,gpt-5.4-self}/scan.md` + judge_v2.json |

- select: 76 (skill, cat) cells (stealth-selected attack categories per skill)
- no-select: 221 (skill, cat) scenarios (all 13 categories × 17 skills); the 219 with at least one refusal-free mutation form the denominator (2 were refusals at every
  iteration; 4 refused at iter_0 and are evaluated on their latest refusal-free mutation, §6.1 Experimental Setup)

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