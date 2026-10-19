# Table 4 — Cross-Scanner Detection Matrix (3 GPT oracles × 9 scanners)

## (1) Paper location

- **Paper location**: Table 4, §6.2 Evaluation of Existing Install-time Scanners
- **Caption**: "Cross-scanner detection rate (%) across three adversarial-oracle datasets. For GPT-4o-mini, three scenarios are excluded because they did not yield valid mutated skill packages after refusal handling, leaving 48 final evaluable mutations."

## (2) PAPER_TARGET_VALUES (camera-ready paper)

n: gpt-4o-mini 48 · gpt-5.4-mini 63 · gpt-5.4 76

| Scanner | gpt-4o-mini | gpt-5.4-mini | gpt-5.4 |
|---|---|---|---|
| **Rule-based / Commercial** | | | |
| skill-security-scan | 2.08% | 6.35% | 7.89% |
| Snyk Agent Scan | 16.67% | 9.52% | 9.21% |
| SkillScan API | 0.00% | 0.00% | 1.32% |
| **PI Detectors (inject input)** | | | |
| LLM-Guard | 2.08% | 0.00% | 3.95% |
| PIGuard | 39.58% | 4.76% | 17.11% |
| DataSentinel | 4.17% | 11.11% | 10.53% |
| **Proprietary LLM** | | | |
| GPT-4o-mini | 35.42% | 9.52% | 23.68% |
| GPT-5.4-mini | 79.17% | 71.43% | 78.95% |
| GPT-5.4 | **89.58%** | **88.89%** | **86.84%** |

## (3) Data source

| Scanner | source (not redistributed) | derived path (shipped) |
|---|---|---|
| skill-security-scan | scan reports on the 17 unmodified skills and on every mutated skill | `derived/skillscan_<oracle>_perscenario.csv` (per-cell ss_total_baseline·mutated) |
| Snyk Agent Scan | scan reports on the 17 unmodified skills and on every mutated skill | (3 GPT oracles) |
| SkillScan API | per-cell API responses (`result.json`) | `derived/skillscan_cross_summary.md` (aggregate) |
| LLM-Guard / PIGuard / DataSentinel | per-cell detector outputs on the injected snippets | `derived/pi_defense_gpt_oracles.csv` |
| GPT-4o-mini scanner | LLM scanner reports | judge → `derived/tab1_cross_matrix.csv` (3 GPT oracles) |
| GPT-5.4-mini scanner | same | same |
| GPT-5.4 scanner | same (self-scan) | same |

The aggregate checked by `run.sh` is `derived/table3_aggregate.csv`.

## (4) Reproduction commands

```bash
bash ../run.sh                           # both steps below
python scripts/build_table3.py           # derived/ per-source CSVs → ../results/derived/table3_aggregate.csv,
                                         #   checked against derived/table3_aggregate.csv
python scripts/verify_paper_match.py     # derived/table3_aggregate.csv vs expected/metrics.json
```

## (5) Dependencies

- the source scan tree (not redistributed) — copies of all LLM scanner scan.md (3 oracles × 17 skills × N cats × 5 iters)
- `artifact/code/skillmutator/analysis/skillmutator_utils/judge.py` (shipped) — `judge_call` (GPT-5.4 judge, JSON enforced)
- Adapter not required (proprietary scanners — OpenAI API & PI detector models)

## (6) ⚠️ Critical Denominator Convention

n=48 (gpt-4o-mini column) — by `evaluable_per_oracle`:
- all_attempted: **51** (raw scenario count, including refusals)
- evaluable_per_oracle: **48** (= 51 - 3 unrecoverable/missing-verdict, **paper canonical**)

`scripts/build_table3.py` divides by the evaluable counts
`EVALUABLE_N = {gpt-4o-mini: 48, gpt-5.4-mini: 63, gpt-5.4: 76}`.
- skill-security-scan and Snyk are counted on the 48-row per-scenario file
  (`derived/skillscan_gpt-4o-mini_perscenario.csv`).
- The LLM rows take their detected counts from `tab1_cross_matrix.csv` (51 scenarios) and the
  PI-detector rows from `pi_defense_gpt_oracles.csv` (49 scenarios).
- The 3 excluded GPT-4o-mini scenarios (frontend-design/data_integrity_risks,
  web-artifacts-builder/supply_chain_attack, pdf/configuration_weakening) have no evaluable
  mutation with a verdict (two are refused at every iteration; pdf/configuration_weakening has
  no verdict at iter_0 and is missing afterwards), so they count as not detected. For the
  GPT-4o-mini self-scan cell this can be checked against
  `claims/claim09_ier_dynamics/data/raw/ier_verdicts.csv`: 17 detections among the 48.

## (7) LLM-Guard × gpt-4o-mini

Paper Table 4 reports LLM-Guard as **2.1% / 0.0% / 4.0%** across the three GPT
oracles; the bundle recomputes **2.08% (1/48)**, 0.00% (0/63), and 3.95% (3/76),
which match the paper at 1-decimal rounding.

## (8) Verification status

✅ **27/27 cells verified** (3 GPT oracles × 9 scanners).

```bash
python scripts/verify_paper_match.py
# expected: 27 "[OK ]" lines, then ALL MATCH
```
