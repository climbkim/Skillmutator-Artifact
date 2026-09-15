# -*- coding: utf-8 -*-
"""Table III (tab:refusal_i4_summary) — recompute per-oracle refusal metrics
(n, final iter-4 refusal rate, per-iteration refusal counts iter0..4, and the
iter-4 mechanism split silent/explicit/partial) from the bundled aggregate
(data/derived/table4_aggregate.csv), then hand them to the shared verifier,
which writes results/derived/table3_refusal.csv and compares them cell-by-cell
against the paper golden in expected/metrics.json (values + tolerances live
there, not in this script)."""
from __future__ import annotations
import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

DERIVED = Path(__file__).resolve().parents[1] / "derived"      # data/derived (inputs)

rows = {r["oracle"]: r for r in
        csv.DictReader((DERIVED / "table4_aggregate.csv").open(encoding="utf-8"))}

ORACLES = ["gpt-4o-mini", "gpt-5.4-mini", "gpt-5.4"]

computed, counts = {}, {}
for oracle in ORACLES:
    r = rows.get(oracle)
    if not r:
        continue
    n = int(r["n"])
    computed[f"{oracle}/n"] = n
    computed[f"{oracle}/rate_pct"] = float(r["refusal_rate_pct"])
    per_iter = [int(x) for x in r["per_iter"].split("/")]
    for i, c in enumerate(per_iter):
        computed[f"{oracle}/per_iter{i}"] = c
    computed[f"{oracle}/iter4_silent"] = int(r["iter4_silent"])
    computed[f"{oracle}/iter4_explicit"] = int(r["iter4_explicit"])
    computed[f"{oracle}/iter4_partial"] = int(r["iter4_partial"])
    # final-iteration refusal rate = iter4 refusals / n
    counts[f"{oracle}/rate_pct"] = (per_iter[4] if len(per_iter) > 4 else "", n)

sys.exit(V.verify(__file__, "metrics.json", computed,
                  results_name="table3_refusal.csv",
                  title="Table III — recomputed vs expected/metrics.json (paper golden)\n",
                  counts=counts))
