# PAPER_CITED_VALUES — Table XI (Appendix B) Cell-level Matrix

Excerpt from paper.tex body → source in this folder.

## §VI.B Appendix Cell-level Confusion Matrix

### Table `tab:cell_metrics` (L1127)

```
\caption{Cell-level confusion matrix for the fine-tuned Qwen2.5-Coder-7B scanner
(prefill, GPT-5.4 oracle, n_mut=76, n_unmod=221).
TP source is the GPT-5.4 judge of §III.B (paper-canonical 67/76);
FP cells are extracted directly from the Phase 3 grid of the
unmodified-skill scans.}
```

| paper value | source file |
|---|---|
| `n_mut = 76` | `raw/mutated_cells_tp.csv` row count |
| `n_unmod = 221` | 17 skills × 13 categories = total cells in `raw/qwen_unmodified_cells.csv` |
| `TP = 67` | `derived/confusion_matrix.txt` Framework A: `TP=67` |
| `FN = 9` | derived: `FN=9` (= 76-67) |
| `FP = 43` | derived: `FP=43` |
| `TN = 178` | derived: `TN=178` (= 221-43) |
| **Sensitivity (TPR) = 88.16%** | derived: `Recall (TPR) = 88.16%` (= 67/76) |
| **Specificity = 80.54%** | derived: `Specificity = 80.54%` (= 178/221) |
| **Precision = 60.91%** | derived: `Precision = 60.91%` (= 67/110) |
| **F1 = 72.04%** | derived: `F1 = 72.04%` |
| **Balanced Accuracy = 84.35%** | derived: `Bal.Accuracy = 84.35%` (= (Sens+Spec)/2) |

### Table `fig:fp_per_cat` (L1147-L1178) — 13 categories

Direct excerpt from the paper Appendix:

```
Information Gathering          & 15 \\
Code Quality Degradation       &  7 \\
Data Integrity Risks           &  5 \\
Brand Hijacking                &  3 \\
Over-engineering               &  3 \\
Persistence Control            &  3 \\
Supply Chain Attack            &  2 \\
Advertising Injection          &  1 \\
Configuration Weakening        &  1 \\
Data Exfiltration              &  1 \\
Disruption \& Interference     &  1 \\
False Attribution              &  1 \\
Privilege Escalation           &  0 \\
```

→ source: `derived/confusion_matrix.txt` "Per-category FP cell count" block (13 lines, all match).

Raw grid: sum of the 13 category columns in `raw/qwen_unmodified_cells.csv`.

## Narrative citations (L1125 + L1176)

| paper wording | direct evidence in this folder |
|---|---|
| L1125 `Privilege Escalation does not appear in mutated set` | 0 rows in the Privilege Escalation category among the 76 cells of `raw/mutated_cells_tp.csv` |
| L1125 `13-category denominator preserved ... at most 1.6pp on Specificity` | Sens denominator 76 (not 12×7=84), Spec denominator 221 (not 12×17=204) |
| L1176 `15--0 spread is the signature of a discriminative classifier` | Information Gathering 15 → Privilege Escalation 0 (13-list above) |
| L1176 `categories with 0-1 fires (Privilege Escalation, Advertising Injection, ...)` | Privilege Escalation=0, Advertising=1, Config Weakening=1, Data Exfil=1, Disruption=1, False Attr=1 (6 items) |

## Automated verification

```bash
# 1. Verify the 5 Framework A metrics
grep -E "TP=67 FP=43 FN=9 TN=178|Recall.*88.16|Specificity.*80.54|Precision.*60.91|F1.*72.04|Bal.Accuracy.*84.35" \
    derived/confusion_matrix.txt | wc -l
# Expected: 6 lines (TP line + 5 metrics)

# 2. Verify the 13-category counts
grep -A 14 "Per-category FP cell count" derived/confusion_matrix.txt | \
    grep "fires on" | wc -l
# Expected: 13 lines
```