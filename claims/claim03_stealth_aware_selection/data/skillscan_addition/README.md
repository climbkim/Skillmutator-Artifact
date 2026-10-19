# SkillScan API row for Table 5 (§6.3.1 Stealth-aware Attack Selection)

Per-scenario SkillScan decisions and the paired-delta count behind the **SkillScan** row
of Table 5 (select vs no-select).

## Paper mapping

| column | n | SkillScan value | source |
|---|---|---|---|
| select | 76 | **1.32%** (1/76) | paper Table 4 (GPT-5.4 column) and Table 5 (select column) |
| no-select | 219 | **5.48%** (12/219) | `derived/no_select_perscenario.csv` paired-delta |
| Drop pp | — | +4.16pp | (no-select − select), same direction as other scanners |

## Paper criterion

**Paired delta**: detected iff `mutated_verdict >= MEDIUM AND baseline_verdict < MEDIUM`.

Baselines = **OLD per-skill** (at the time of the paper's measurement, the `ss_risk_baseline` column of `select_perscenario.csv`).
3 code-heavy skills (claude-api, mcp-builder, skill-creator) already have an OLD baseline of CRITICAL —
the mutated CRITICAL of these skills is not detected under the paired-delta criterion (not crossed-up from the baseline).

## Folder structure

```
skillscan_addition/
├── README.md
├── PAPER_CITED_VALUES.md         # paper values → source mapping
├── derived/
│   ├── select_perscenario.csv          # 76 rows (table3 source)
│   ├── no_select_perscenario.csv       # 221 rows, paired-delta marked
│   ├── no_select_perskill_summary.csv  # 17-skill aggregation
│   └── old_baselines_per_skill.csv     # paper-canonical 17 baselines
└── manifests/
    ├── no_select.csv             # 221 rows (batch input)
    └── baselines_17.csv          # 17 baselines (rescan input)
```

The SkillScan API was called once per manifest row (76 select reports, 221
no-select reports and 17 unmodified baselines). The raw API responses are not
redistributed; `derived/` holds the per-scenario decisions that `build_table5.py`
reads.

## Reproduction commands

The SkillScan API calls (17 baselines, 76 select and 221 no-select reports) need
the SkillScan service and the withheld mutated skills, so they are not part of the
bundle. The paper's paired-delta decision (detected when the mutated verdict is
MEDIUM or above and the unmodified skill's verdict is not) is stored per scenario
in `derived/no_select_perscenario.csv`; Table 5 counts it on the 219 evaluable scenarios:

```bash
python -c "
import csv
valid = {(r['skill'], r['cat_folder']) for r in csv.DictReader(open('../judge/select_vs_noselect_verdicts.csv', encoding='utf-8'))
         if r['mode'] == 'no-select' and r['valid'] == '1'}
rows = [r for r in csv.DictReader(open('derived/no_select_perscenario.csv', encoding='utf-8')) if (r['skill'], r['cat']) in valid]
det = sum(r['detected_paired_delta'] == 'True' for r in rows)
print(f'no-select paired delta: {det}/{len(rows)} = {100*det/len(rows):.2f}%')
"
# -> no-select paired delta: 12/219 = 5.48%
```
