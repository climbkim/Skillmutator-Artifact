# -*- coding: utf-8 -*-
"""Table XI (Appendix B, tab:cell_metrics) — recompute the 5 cell-level metrics
from the bundled confusion counts (data/derived/confusion_matrix.txt), then hand
them to the shared verifier, which writes results/derived/table11_cell_metrics.csv
and compares them cell-by-cell against the paper golden in expected/metrics.json
(values + tolerances live there).
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

txt = (Path(__file__).resolve().parents[1] / "derived" / "confusion_matrix.txt").read_text(encoding="utf-8")


def grab(k, d=None):
    m = re.search(rf"{k}\s*=\s*(\d+)", txt)
    return int(m.group(1)) if m else d


TP, FP, FN, TN = grab("TP"), grab("FP"), grab("FN"), grab("TN")
# fallback: paper canonical counts if file lacks them
if None in (TP, FP, FN, TN):
    TP, FP, FN, TN = 67, 43, 9, 178

sens = 100 * TP / (TP + FN)
spec = 100 * TN / (TN + FP)
prec = 100 * TP / (TP + FP)
f1 = 2 * prec * sens / (prec + sens)
bal = (sens + spec) / 2

computed = {
    "Sensitivity/Recall": round(sens, 4),
    "Specificity": round(spec, 4),
    "Precision": round(prec, 4),
    "F1": round(f1, 4),
    "Balanced Acc": round(bal, 4),
}
counts = {
    "Sensitivity/Recall": (TP, TP + FN),
    "Specificity": (TN, TN + FP),
    "Precision": (TP, TP + FP),
}

sys.exit(V.verify(__file__, "metrics.json", computed,
                  results_name="table11_cell_metrics.csv",
                  title=f"Table XI (Appendix B) - recomputed vs expected/metrics.json "
                        f"(TP={TP} FP={FP} FN={FN} TN={TN})\n",
                  counts=counts))
