# -*- coding: utf-8 -*-
"""Table V (tab:select_vs_noselect) — recompute per-scanner select/no-select
detection rates and their delta (pp), plus the 6-scanner average, from the
freshly rebuilt table (data/derived/tab_select_vs_noselect.csv, emitted by
build_table5.py), then hand them to the shared verifier, which writes
results/derived/table5_select_vs_noselect.csv and compares each cell against the
paper golden in expected/metrics.json (values + tolerances live there, not in
this script).

The 6-scanner average row is a recomputed aggregate: select/no-select are the
means of the six per-scanner rates and delta = mean(no-select) - mean(select).
Its paper-cited reference numbers are externalized into metrics.json like every
other cell; the script only recomputes and defers the comparison to the golden.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

DERIVED = Path(__file__).resolve().parents[1] / "derived"      # data/derived (inputs)

rows = {r["scanner"]: r for r in
        csv.DictReader((DERIVED / "tab_select_vs_noselect.csv").open(encoding="utf-8"))}

SCANNERS = ["skill-security-scan", "Snyk Agent Scan", "SkillScan API",
            "GPT-4o-mini scanner", "GPT-5.4-mini scanner", "GPT-5.4 scanner"]

computed, counts = {}, {}
sels, nsls = [], []
for scanner in SCANNERS:
    r = rows.get(scanner)
    if not r:
        computed[f"{scanner}/select"] = None
        computed[f"{scanner}/noselect"] = None
        computed[f"{scanner}/delta"] = None
        continue
    a_sel = float(r["rate_select_pct"])
    a_nsl = float(r["rate_noselect_pct"])
    a_delta = float(r["delta_pp"])
    sels.append(a_sel); nsls.append(a_nsl)
    computed[f"{scanner}/select"] = a_sel
    computed[f"{scanner}/noselect"] = a_nsl
    computed[f"{scanner}/delta"] = a_delta
    counts[f"{scanner}/select"] = (int(r["detected_select"]), int(r["n_select"]))
    counts[f"{scanner}/noselect"] = (int(r["detected_noselect"]), int(r["n_noselect"]))

# 6-scanner average (recomputed aggregate)
avg_sel = sum(sels) / len(sels) if sels else 0.0
avg_nsl = sum(nsls) / len(nsls) if nsls else 0.0
computed["Average (6 scanners)/select"] = round(avg_sel, 2)
computed["Average (6 scanners)/noselect"] = round(avg_nsl, 2)
computed["Average (6 scanners)/delta"] = round(avg_nsl - avg_sel, 2)

sys.exit(V.verify(__file__, "metrics.json", computed,
                  results_name="table5_select_vs_noselect.csv",
                  title="Table V — recomputed vs expected/metrics.json (paper golden)\n",
                  counts=counts))
