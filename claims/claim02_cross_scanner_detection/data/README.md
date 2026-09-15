# Table IV — Cross-Scanner Detection Matrix (3 GPT oracles × 9 scanners)

## (1) Paper location

- **LaTeX label**: `\label{tab:cross_matrix}` (implicit — caption refers to it)
- **Paper lines**: L707–L735 (paper.tex main version, SkillScan + PI Detectors **included**)
- **Caption**: "Detection rate (%) by scanner across four adversarial-oracle datasets."

## (2) PAPER_TARGET_VALUES (current paper.tex as-is)

n: gpt-4o-mini 48 · gpt-5.4-mini 63 · gpt-5.4 76

| Scanner | gpt-4o-mini | gpt-5.4-mini | gpt-5.4 |
|---|---|---|---|---|
| **Rule-based / Commercial** | | | |
| skill-security-scan | 2.08% | 6.35% | 7.89% |
| Snyk Agent Scan | 16.67% | 9.52% | 9.21% |
| SkillScan API | 0.00% | 0.00% | 1.32% |
| **PI Detectors (inject input)** | | | |
| LLM-Guard | 0.00% | 0.00% | 3.95% |
| PIGuard | 39.58% | 4.76% | 17.11% |
| DataSentinel | 4.17% | 11.11% | 10.53% |
| **Proprietary LLM** | | | |
| GPT-4o-mini | 35.42% | 9.52% | 23.68% |
| GPT-5.4-mini | 79.17% | 71.43% | 78.95% |
| GPT-5.4 | **89.58%** | **88.89%** | **86.84%** |

## (3) Data source

| Scanner | raw path | derived path |
|---|---|---|
| skill-security-scan | the source scan tree (not redistributed) + baseline `raw/skill-security-scan/baseline/` | `derived/skillscan_<oracle>_perscenario.csv` (per-cell ss_total_baseline·mutated) |
| Snyk Agent Scan | the source scan tree (not redistributed) + baseline `raw/snyk/baseline/` | (3 GPT oracles) |
| SkillScan API | `raw/skillscan/<oracle>/<sk>/<cat>/iter_4/result.json` (per cell) | `derived/skillscan_cross_summary.md` (aggregate) |
| LLM-Guard / PIGuard / DataSentinel | `raw/<det>/all_gpt_oracles_summary.csv` (GPT) | `derived/pi_defense_gpt_oracles.csv` (tab_pi_defense.csv) |
| GPT-4o-mini scanner | the source scan tree (not redistributed) | judge → `derived/tab1_cross_matrix.csv` (3 GPT oracles) |
| GPT-5.4-mini scanner | same (`.../llm/gpt-5.4-mini/`) | same |
| GPT-5.4 scanner | `.../llm/gpt-5.4-self/` | same |

## (4) Reproduction commands

```bash
cd table3_cross_scanner_matrix
python scripts/build_table3.py           # derived/* + raw/* → derived/table3_aggregate.csv
python scripts/verify_paper_match.py     # automated comparison
```

## (5) Dependencies (source scan tree, not redistributed)

- the source scan tree (not redistributed) — copies of all LLM scanner scan.md (3 oracles × 17 skills × N cats × 5 iters)
- the judge script (not redistributed) — judge_call (GPT-5.4 oracle, JSON enforced)
- Adapter not required (proprietary scanners — OpenAI API & PI detector models)

## (6) ⚠️ Critical Denominator Convention

n=48 (gpt-4o-mini column) — by `evaluable_per_oracle`:
- all_attempted: **51** (raw scenario count, including refusals)
- evaluable_per_oracle: **48** (= 51 - 3 unrecoverable/missing-verdict, **paper canonical**)

`tab1_cross_matrix.csv` and `tab_pi_defense.csv` use n=51 / n=49 respectively (raw counts).
`scripts/build_table3.py` applies a hardcoded `EVALUABLE_N = {gpt-4o-mini: 48}` to correct the paper
denominator.

Detailed explanation: see the "Denominator
conventions" section of the judge script (not redistributed) documentation.

## (7) LLM-Guard × gpt-4o-mini

Paper Table IV reports LLM-Guard as **2.1% / 0.0% / 4.0%** across the three GPT
oracles; the bundle recomputes **2.08% (1/48)**, 0.00% (0/63), and 3.95% (3/76),
which match the paper at 1-decimal rounding.

## (8) Verification status

✅ **27/27 cells verified** (3 GPT oracles × 9 scanners).

```bash
python scripts/verify_paper_match.py
# expected: [VERIFIED] All 27 Table IV cells match paper.
```
