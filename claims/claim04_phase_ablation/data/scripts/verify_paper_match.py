# -*- coding: utf-8 -*-
"""Table VI (tab:finetune_rq2, Finding 6) — recompute the four-phase schema
progression detection rates (and the schema/refine/prefill decomposition deltas)
from the aggregate built by build_table7.py, then hand them to the shared verifier,
which writes results/derived/table6_finetune_rq2.csv and compares them cell-by-cell
against the paper golden in expected/metrics.json (values + tolerances live there).
"""
import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

DERIVED = Path(__file__).resolve().parents[1] / "derived"        # data/derived (inputs)
agg = DERIVED / "table7_aggregate.csv"
if not agg.is_file():
    print(f"[FATAL] {agg} missing - run build_table7.py first", file=sys.stderr)
    sys.exit(1)

rows = list(csv.DictReader(agg.open(encoding="utf-8")))

# Row order in table7_aggregate.csv matches build_table7.py's config (by index).
LABELS = [
    "Phase 1 (Purpose Grounding)",
    "+ Phase 2 (Out-of-Scope Detection)",
    "+ Phase 3 (Principle Reasoning)",
    "+ Phase 4 (Category Labeling)",
    "+ deterministic refinement",
    "+ prefill (Phase 4 header forced)",
]
rate = [float(r["rate_pct"]) for r in rows]

computed, counts = {}, {}
for i, label in enumerate(LABELS):
    if i < len(rate):
        computed[label] = rate[i]
        counts[label] = (int(rows[i]["detected"]), int(rows[i]["total"]))
    else:
        computed[label] = None

# Finding 6 decomposition deltas (recomputed from the rates above).
if len(rate) >= 6:
    computed["delta/schema (P3->P4)"] = round(rate[3] - rate[2], 2)
    computed["delta/refine (P4->+refine)"] = round(rate[4] - rate[3], 2)
    computed["delta/prefill (+refine->+prefill)"] = round(rate[5] - rate[4], 2)

sys.exit(V.verify(__file__, "metrics.json", computed,
                  results_name="table6_finetune_rq2.csv",
                  title="Table VI - recomputed vs expected/metrics.json (paper golden)\n",
                  counts=counts))
