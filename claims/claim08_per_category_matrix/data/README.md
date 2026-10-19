# Table 11 (Appendix B) — Per-Category Confusion Matrix

Source data for Table 11 (per-category
classifier metrics for the fine-tuned scanner) in Table 11, Appendix B.4 Per-Category Classifier Metrics.

## Paper mapping

| Paper location | cited content | source in this folder |
|---|---|---|
| Table 11, Appendix B.4 Per-Category Classifier Metrics | Recall=88.16%, Precision=60.91%, F1=72.04%, Specificity=80.54%, Balanced Accuracy=84.35%. TP/FN/FP/TN counts behind them: TP=67, FN=9, FP=43, TN=178 | `derived/confusion_matrix.txt` |
| Para 4 (per-category FP distribution, inline body) | per-category FP fire counts for the 13 categories: Information Gathering=15/17, Code Quality Degradation=7/17, Data Integrity Risks=5/17, Brand Hijacking=3/17, Over-engineering=3/17, Persistence Control=3/17, Supply Chain Attack=2/17, Advertising Injection=1/17, Configuration Weakening=1/17, Data Exfiltration=1/17, Disruption & Interference=1/17, False Attribution=1/17, Privilege Escalation=0/17 (43 total) | `derived/confusion_matrix.txt` + `raw/qwen_unmodified_cells.csv` |

## Evaluation unit

- **n_mut = 76** (mutated skill, injected category) pairs — GPT-5.4 oracle `select` dataset (§6.1 Experimental Setup)
- **n_unmod = 17 × 13 = 221** (unmodified skill, canonical category) pairs — the 17 unmodified Anthropic-official skills of Table 10 × 13 category grid
- Total evaluation pairs: 297 (=76+221). The Privilege Escalation category has 0 mutated pairs (a result of stealth-aware selection)

## Folder structure

```
raw/
├── mutated_cells_tp.csv         ← 76 (skill, injected_cat) pairs, GPT-5.4 judge results
└── qwen_unmodified_cells.csv    ← 17 skills × 13 cats grid, Phase 4 fire counts

derived/
└── confusion_matrix.txt         ← final paper-cited metrics + 13-cat FP distribution (informational)

scripts/
└── verify_paper_match.py        ← recounts TP/FN/FP/TN and the 13-cat FP spread from raw/, recomputes the metrics (called by run.sh)
```

## Verified paper-cited values (`derived/confusion_matrix.txt`)

```
TP=67 FP=43 FN=9 TN=178
  Recall (TPR) = 88.16%        ← paper Recall 88.2%
  Precision    = 60.91%        ← paper Precision 60.9%
  F1           = 72.04%        ← paper F1 72.0%
  Specificity  = 80.54%        ← paper Specificity 80.5%
  Bal.Accuracy = 84.35%        ← paper Bal. Acc. 84.4%
```

**TP rule**: a mutated pair is a true positive when the GPT-5.4 judge credits the scanner with detecting the injected attack (67/76), as in the main text
**FP rule**: an unmodified pair is a false positive when the scanner's Phase 4 section for that category contains a non-`(none)` bullet (17 skills × 13 categories)

## 13-category FP distribution (Appendix B.4 Per-Category Classifier Metrics, last paragraph)

| Category | FP fires on (out of 17 skills) | paper citation |
|---|---|---|
| Information Gathering | **15** | ✅ paper "Information Gathering fires on 15/17 skills" |
| Code Quality Degradation | 7 | ✅ paper "Code Quality Degradation (7/17) … concentrate on the document-processing skills" |
| Data Integrity Risks | 5 | ✅ paper "Data Integrity Risks (5/17) concentrate on the document-processing skills" |
| Brand Hijacking | 3 | ✅ paper "Nine other categories fire on one to three skills each" |
| Over-engineering | 3 | ✅ paper "Nine other categories fire on one to three skills each" |
| Persistence Control | 3 | ✅ paper "Nine other categories fire on one to three skills each" |
| Supply Chain Attack | 2 | ✅ paper "Nine other categories fire on one to three skills each" |
| Advertising Injection | 1 | ✅ paper "Nine other categories fire on one to three skills each" |
| Configuration Weakening | 1 | ✅ paper "Nine other categories fire on one to three skills each" |
| Data Exfiltration | 1 | ✅ paper "Nine other categories fire on one to three skills each" |
| Disruption & Interference | 1 | ✅ paper "Nine other categories fire on one to three skills each" |
| False Attribution | 1 | ✅ paper "Nine other categories fire on one to three skills each" |
| Privilege Escalation | **0** | ✅ paper "Privilege Escalation fires on none" |

→ directly consistent with paper "This spread from 15 skills to none is incompatible with indiscriminate flagging."
→ sum of the 13 categories = 43 FP, all matching the raw count (consistent with Table 11 FP=43).

## Reproduction commands

```bash
# 1. recount TP/FN/FP/TN + 13-category FP spread from raw/ and compare to expected/
bash ../run.sh

# 2. grep the paper-cited values in the informational summary
grep -E "TP=67|Recall|Precision|F1|Specificity|Bal.Accuracy" derived/confusion_matrix.txt

# 3. print the 13-category counts by hand
python -c "
import csv
rows = list(csv.DictReader(open('raw/qwen_unmodified_cells.csv', encoding='utf-8')))
cats = [c for c in rows[0].keys() if c not in ('skill','row_total','row_fire_cells')]
for c in cats:
    fires = sum(1 for r in rows if int(r[c]) > 0)
    print(f'{c:30s} {fires}/17')
"
```

