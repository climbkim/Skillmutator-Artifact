# PAPER_CITED_VALUES — Table 11 (Appendix B) Cell-level Matrix

Excerpt from the paper body → source in this folder.

## Appendix B.4 Per-Category Classifier Metrics

### Table 11 (Appendix B.4 Per-Category Classifier Metrics)

Caption: "Per-category classifier metrics for the fine-tuned Qwen scanner."
Paper values: Recall 88.2%, Precision 60.9%, F1 72.0%, Specificity 80.5%, Bal. Acc. 84.4%.

Definition (Appendix B.4): the positive set is the 76 (mutated skill, injected category)
pairs of the GPT-5.4 oracle, and a positive pair is a true positive when the GPT-5.4 judge
credits the scanner with detecting the injected attack. The negative set is the 17 × 13 = 221
pairs on the unmodified skills of Table 10, and a negative pair is a false positive when the
scanner's Phase 4 section for that category contains a non-`(none)` bullet.

| value | source file |
|---|---|
| `n_mut = 76` | `raw/mutated_cells_tp.csv` row count |
| `n_unmod = 221` | 17 skills × 13 categories = total cells in `raw/qwen_unmodified_cells.csv` |
| `TP = 67` | `derived/confusion_matrix.txt`: `TP=67` |
| `FN = 9` | derived: `FN=9` (= 76-67) |
| `FP = 43` | derived: `FP=43` |
| `TN = 178` | derived: `TN=178` (= 221-43) |
| **Sensitivity (TPR) = 88.16%** | derived: `Recall (TPR) = 88.16%` (= 67/76) |
| **Specificity = 80.54%** | derived: `Specificity = 80.54%` (= 178/221) |
| **Precision = 60.91%** | derived: `Precision = 60.91%` (= 67/110) |
| **F1 = 72.04%** | derived: `F1 = 72.04%` |
| **Balanced Accuracy = 84.35%** | derived: `Bal.Accuracy = 84.35%` (= (Sens+Spec)/2) |

### Per-category FP distribution (Appendix B.4 Per-Category Classifier Metrics) — 13 categories

Counts per category (number of the 17 unmodified skills flagged). The paper cites
Information Gathering 15/17, Code Quality Degradation 7/17, Data Integrity Risks 5/17,
"nine other categories fire on one to three skills each", and Privilege Escalation none:

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

## Narrative citations (Appendix B.4 Per-Category Classifier Metrics)

| paper wording | direct evidence in this folder |
|---|---|
| Appendix B.4 "Privilege Escalation fires on none because stealth-aware selection … rejected it for this corpus" | 0 rows in the Privilege Escalation category among the 76 cells of `raw/mutated_cells_tp.csv` |
| Appendix B.4 "keeping it in the denominator raises specificity by at most 1.6 pp" | Sens denominator 76 (not 12×7=84), Spec denominator 221 (not 12×17=204) |
| Appendix B.4 "This spread from 15 skills to none is incompatible with indiscriminate flagging." | Information Gathering 15 → Privilege Escalation 0 (13-list above) |
| Appendix B.4 "Nine other categories fire on one to three skills each." | Brand Hijacking=3, Over-engineering=3, Persistence Control=3, Supply Chain Attack=2, Advertising Injection=1, Configuration Weakening=1, Data Exfiltration=1, Disruption & Interference=1, False Attribution=1 (9 categories) |

## Automated verification

```bash
# 1. Verify the 5 metrics
grep -E "TP=67 FP=43 FN=9 TN=178|Recall.*88.16|Specificity.*80.54|Precision.*60.91|F1.*72.04|Bal.Accuracy.*84.35" \
    derived/confusion_matrix.txt | wc -l
# Expected: 6 lines (TP line + 5 metrics)

# 2. Verify the 13-category counts
grep -A 14 "Per-category FP cell count" derived/confusion_matrix.txt | \
    grep "fires on" | wc -l
# Expected: 13 lines
```