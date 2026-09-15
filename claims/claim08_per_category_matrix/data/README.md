# Table XI (Appendix B) — Per-Category Confusion Matrix

Source data for `tab:cell_metrics` (per-category
classifier metrics for the fine-tuned scanner) under paper.tex Appendix `\label{app:cell_matrix}`.

## paper.tex mapping

| paper.tex location | cited content | source in this folder |
|---|---|---|
| `\label{tab:cell_metrics}` (subsection "Per-Category Confusion Matrix for the Fine-tuned Scanner") | Recall=88.16%, Precision=60.91%, F1=72.04%, Specificity=80.54%, Balanced Accuracy=84.35%. TP/FN/FP/TN raw counts absorbed from the caption: TP=67, FN=9, FP=43, TN=178 | `derived/confusion_matrix.txt` Framework A |
| Para 4 (per-category FP distribution, inline body) | per-category FP fire counts for the 13 categories: Information Gathering=15/17, Code Quality Degradation=7/17, Data Integrity Risks=5/17, Brand Hijacking=3/17, Over-engineering=3/17, Persistence Control=3/17, Supply Chain Attack=2/17, Advertising Injection=1/17, Configuration Weakening=1/17, Data Exfiltration=1/17, Disruption & Interference=1/17, False Attribution=1/17, Privilege Escalation=0/17 (43 total) | `derived/confusion_matrix.txt` + `raw/qwen_unmodified_cells.csv` |

## Evaluation unit

- **n_mut = 76** (mutated skill, injected category) pairs — paper §VI.A GPT-5.4 oracle `select` dataset
- **n_unmod = 17 × 13 = 221** (unmodified skill, canonical category) pairs — paper §VI.B 17 Anthropic-official skills × 13 category grid
- Total evaluation pairs: 297 (=76+221). The Privilege Escalation category has 0 mutated pairs (a result of stealth-aware selection)

## Folder structure

```
raw/
├── mutated_cells_tp.csv         ← 76 (skill, injected_cat) pairs, GPT-5.4 judge results
└── qwen_unmodified_cells.csv    ← 17 skills × 13 cats grid, Phase 4 fire counts

derived/
└── confusion_matrix.txt         ← final paper-cited metrics + 13-cat FP distribution

scripts/
└── build_cell_matrix.py         ← raw → derived (builder)
```

## Verified paper-cited values (`derived/confusion_matrix.txt` Framework A)

```
A_judge: TP=67 FP=43 FN=9 TN=178
  Recall (TPR) = 88.16%        ← paper Recall 88.16%
  Precision    = 60.91%        ← paper Precision 60.91%
  F1           = 72.04%        ← paper F1 72.04%
  Specificity  = 80.54%        ← paper Specificity 80.54%
  Bal.Accuracy = 84.35%        ← paper Balanced Accuracy 84.35%
```

**TP source**: GPT-5.4 paper-canonical judge (67/76 = 88.16%), consistent with paper §VI.A
**FP source**: 17 unmodified Anthropic skills × 13 category Phase 4 fire grid

## 13-category FP distribution (paper Per-Category Para 4 cited values)

| Category | FP fires on (out of 17 skills) | paper citation |
|---|---|---|
| Information Gathering | **15** | ✅ paper "15--0 spread" highest |
| Code Quality Degradation | 7 | ✅ paper "7/17 ... document-processing" |
| Data Integrity Risks | 5 | ✅ paper "5/17 ... document-processing" |
| Brand Hijacking | 3 | ✅ paper "3 skills each" |
| Over-engineering | 3 | ✅ paper "3 skills each" |
| Persistence Control | 3 | ✅ paper "3 skills each" |
| Supply Chain Attack | 2 | ✅ paper "Supply Chain Attack on 2" |
| Advertising Injection | 1 | ✅ paper "on only 1 each" |
| Configuration Weakening | 1 | ✅ paper "on only 1 each" |
| Data Exfiltration | 1 | ✅ paper "on only 1 each" |
| Disruption & Interference | 1 | ✅ paper "on only 1 each" |
| False Attribution | 1 | ✅ paper "on only 1 each" |
| Privilege Escalation | **0** | ✅ paper "Privilege Escalation on 0/17" + "15--0 spread" lowest |

→ directly consistent with paper "15--0 spread is incompatible with indiscriminate flagging".
→ sum of the 13 categories = 43 FP, all matching the raw count (consistent with Table 9 FP=43).

## Reproduction commands

```bash
# 1. raw → derived
python scripts/build_cell_matrix.py

# 2. grep-verify paper-cited values
grep -E "TP=67|Recall|Precision|F1|Specificity|Bal.Accuracy" derived/confusion_matrix.txt

# 3. Verify the 13-category counts
python -c "
import csv
rows = list(csv.DictReader(open('raw/qwen_unmodified_cells.csv', encoding='utf-8')))
cats = [c for c in rows[0].keys() if c not in ('skill','row_total','row_fire_cells')]
for c in cats:
    fires = sum(1 for r in rows if int(r[c]) > 0)
    print(f'{c:30s} {fires}/17')
"
```

## Caveats

`derived/confusion_matrix.txt` preserves both Framework results:
- **Framework A** (paper canonical): TP source = GPT-5.4 judge → 88.16%
- **Framework B** (raw Phase 4): TP source = Phase 4 fire on injected_cat → 10.53% (for reference)

The paper adopts A. B uses a self-fire-detection criterion, so cases where the fine-tuned LoRA classified into a different category (the judge scores them as detected) are missed → a conservative lower bound.

