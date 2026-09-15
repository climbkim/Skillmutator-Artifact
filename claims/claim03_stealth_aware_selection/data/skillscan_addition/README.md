# SkillScan API row for Table V (`tab:select_vs_noselect`)

Data + automation runner + paired-delta computation for adding the **SkillScan (ClawHub commercial)** row
to paper.tex Table V (select vs no-select) (paper-canonical Option A).

## paper.tex mapping

| column | n | SkillScan value | source |
|---|---|---|---|
| select | 76 | **1.32%** (1/76) | paper canonical (Table III); table3 bundle reference |
| no-select | 221 | **5.43%** (12/221) | `derived/no_select_perscenario.csv` paired-delta |
| Drop pp | — | +4.11pp | (no-select − select), same direction as other scanners |

## Paper criterion

**Paired delta**: detected iff `mutated_verdict >= MEDIUM AND baseline_verdict < MEDIUM`.

Baselines = **OLD per-skill** (at the time of the paper's measurement, the `ss_risk_baseline` column of `select_perscenario.csv`).
3 code-heavy skills (claude-api, mcp-builder, skill-creator) already have an OLD baseline of CRITICAL —
the mutated CRITICAL of these skills is not detected under the paired-delta criterion (not crossed-up from the baseline).

## Folder structure

```
skillscan_addition/
├── README.md
├── PAPER_CITED_VALUES.md         # paper.tex values → source mapping
├── raw/
│   ├── select/                   # table3 carry-over (76 reports)
│   ├── no-select/                # NEW scan (221 reports)
│   └── baselines_2026-05-27/     # 17 NEW baselines (for reference)
├── derived/
│   ├── select_perscenario.csv          # 76 rows (table3 source)
│   ├── no_select_perscenario.csv       # 221 rows, paired-delta marked
│   ├── no_select_perskill_summary.csv  # 17-skill aggregation
│   └── old_baselines_per_skill.csv     # paper-canonical 17 baselines
├── manifests/
│   ├── no_select.csv             # 221 rows (batch input)
│   └── baselines_17.csv          # 17 baselines (rescan input)
└── scripts/
    └── build_manifest.py         # manifest generator
```

## Reproduction commands

### 1. Baseline rescan (to check the baseline at the paper's measurement time, reference)
```bash
python "<skillscan runner — not redistributed>" \
  --manifest manifests/baselines_17.csv \
  --output-root raw/baselines_2026-05-27
```

### 2. No-select 221 scenario scan
```bash
# Generate manifest
python scripts/build_manifest.py \
  --src "<source scan tree — not redistributed>" \
  --csv manifests/no_select.csv

# Actual API run (8 parallel workers recommended)
for i in 0 1 2 3 4 5 6 7; do
  python "<skillscan runner — not redistributed>" \
    --manifest manifests/no_select.csv \
    --output-root raw/no-select \
    --start $((i*28)) --limit 28 &
done; wait
```

### 3. Paired-delta computation (Option A, paper canonical)
```bash
# (inline in this folder; or can be added to scripts/)
python -c "
import csv, json
from pathlib import Path
GE_MED = {'MEDIUM','HIGH','CRITICAL'}
# OLD baselines per-skill
rows = list(csv.DictReader(open('derived/select_perscenario.csv', encoding='utf-8')))
old_baseline = {r['skill']: r['ss_risk_baseline'] for r in rows}
# No-select per-scenario
det = 0; n = 0
for f in Path('raw/no-select').rglob('result.json'):
    sk = f.parent.parts[-3]
    r = json.loads(f.read_text(encoding='utf-8'))
    mut = r.get('verdict','?')
    base = old_baseline.get(sk, 'SAFE')
    n += 1
    if mut in GE_MED and base not in GE_MED:
        det += 1
print(f'no-select paired delta: {det}/{n} = {100*det/n:.2f}%')
"
```

## Paper.tex Table V integration

See `table.tex` — includes the 6-scanner Table V draft.