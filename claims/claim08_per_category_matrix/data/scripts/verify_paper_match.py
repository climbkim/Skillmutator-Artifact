# -*- coding: utf-8 -*-
"""Table 11 (Appendix B.4) — recount TP/FN/FP/TN from the bundled
per-pair CSVs, recompute the 5 cell-level metrics and the 13-category FP spread,
then hand them to the shared verifier, which writes
results/derived/table11_cell_metrics.csv and compares them cell-by-cell against
the paper golden in expected/metrics.json (values + tolerances live there).

  raw/mutated_cells_tp.csv       76 (mutated skill, injected category) pairs;
                                 tp_judge = GPT-5.4 judge verdict -> TP / FN
  raw/qwen_unmodified_cells.csv  17 unmodified skills x 13 categories; a cell > 0
                                 means the scanner fired on that category -> FP / TN
"""
import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

RAW = Path(__file__).resolve().parents[1] / "raw"

with (RAW / "mutated_cells_tp.csv").open(encoding="utf-8") as f:
    mutated = list(csv.DictReader(f))
with (RAW / "qwen_unmodified_cells.csv").open(encoding="utf-8") as f:
    unmod = list(csv.DictReader(f))

CATS = [c for c in unmod[0].keys() if c not in ("skill", "row_total", "row_fire_cells")]

TP = sum(1 for r in mutated if r["tp_judge"] == "True")
FN = len(mutated) - TP
FP = sum(1 for r in unmod for c in CATS if int(r[c]) > 0)
TN = len(unmod) * len(CATS) - FP

sens = 100 * TP / (TP + FN)
spec = 100 * TN / (TN + FP)
prec = 100 * TP / (TP + FP)
f1 = 2 * prec * sens / (prec + sens)
bal = (sens + spec) / 2

computed = {
    "TP": TP, "FN": FN, "FP": FP, "TN": TN,
    "Sensitivity/Recall": round(sens, 4),
    "Specificity": round(spec, 4),
    "Precision": round(prec, 4),
    "F1": round(f1, 4),
    "Balanced Acc": round(bal, 4),
}
# Per-category FP spread (Appendix B.4, last paragraph): # of the 17 unmodified
# skills on which the scanner fires on each category.
for c in CATS:
    computed[f"FP skills/{c}"] = sum(1 for r in unmod if int(r[c]) > 0)

counts = {
    "Sensitivity/Recall": (TP, TP + FN),
    "Specificity": (TN, TN + FP),
    "Precision": (TP, TP + FP),
}

sys.exit(V.verify(__file__, "metrics.json", computed,
                  results_name="table11_cell_metrics.csv",
                  title=f"Table 11 (Appendix B) - recomputed vs expected/metrics.json "
                        f"(TP={TP} FP={FP} FN={FN} TN={TN})\n",
                  counts=counts))
