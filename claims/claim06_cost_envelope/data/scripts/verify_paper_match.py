# -*- coding: utf-8 -*-
"""Table VIII (tab:cost_envelope, Finding 4) — recompute per-scanner operating cost
from the bundled m7_final.csv, then hand the metrics to the shared verifier, which
writes results/derived/table8_cost_envelope.csv and compares them cell-by-cell
against the paper golden in expected/metrics.json (values + tolerances live there).

Finding 4 "lowest $/detected" (argmin) is externalized numerically: the minimum
cost_per_detected recomputed across all four scanners must equal the golden
"lowest/$per_detected" value (0.00469 = Qwen-7B + ours). If any other scanner
dropped below Qwen the recomputed minimum would change and the cell would fail,
so the equality check enforces the argmin without hard-coding a scanner name.
"""
import csv, io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

CSV = Path(__file__).resolve().parents[1] / "derived" / "m7_final.csv"
rows = {r["scanner"]: r for r in csv.DictReader(io.open(CSV, encoding="utf-8"))}

SCANNERS = ["Qwen-7B + ours", "GPT-4o-mini", "GPT-5.4-mini", "GPT-5.4"]
computed = {}
for name in SCANNERS:
    r = rows.get(name)
    if not r:
        computed[f"{name}/$per_skill"] = None
        computed[f"{name}/recall"] = None
        computed[f"{name}/$per_detected"] = None
        continue
    computed[f"{name}/$per_skill"] = round(float(r["med_cost_usd"]), 5)
    computed[f"{name}/recall"] = round(float(r["recall_pct"]), 2)
    computed[f"{name}/$per_detected"] = round(float(r["cost_per_detected_usd"]), 5)

# Finding 4 argmin: cheapest $/detected across all scanners (must be Qwen-7B + ours).
best = min(rows.values(), key=lambda r: float(r["cost_per_detected_usd"]))
computed["lowest/$per_detected"] = round(float(best["cost_per_detected_usd"]), 5)
print(f"lowest $/detected scanner (Finding 4): {best['scanner']}\n")

sys.exit(V.verify(__file__, "metrics.json", computed,
                  results_name="table8_cost_envelope.csv",
                  title="Table VIII - recomputed vs expected/metrics.json (paper golden)\n"))
