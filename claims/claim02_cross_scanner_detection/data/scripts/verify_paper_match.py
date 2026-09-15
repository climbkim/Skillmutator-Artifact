# -*- coding: utf-8 -*-
"""Table IV (tab:cross_matrix) — recompute the 9 scanner x 3 GPT-oracle
detection-rate matrix (27 cells) from the bundled aggregate
(data/derived/table3_aggregate.csv), then hand it to the shared verifier, which
writes results/derived/table4_cross_matrix.csv and compares each cell against
the paper golden in expected/metrics.json (values + tolerances live there, not
in this script)."""
from __future__ import annotations
import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

DERIVED = Path(__file__).resolve().parents[1] / "derived"      # data/derived (inputs)

# scanner rows, in paper Table IV order
SCANNERS = ["skill-security-scan", "Snyk Agent Scan", "SkillScan API",
            "LLM-Guard", "PIGuard", "DataSentinel",
            "GPT-4o-mini", "GPT-5.4-mini", "GPT-5.4"]
ORACLES = ["gpt-4o-mini", "gpt-5.4-mini", "gpt-5.4"]

agg = DERIVED / "table3_aggregate.csv"
if not agg.is_file():
    print(f"[FATAL] {agg} missing — run build_table3.py first")
    sys.exit(1)
rows = {r["scanner"]: r for r in csv.DictReader(agg.open(encoding="utf-8"))}

computed, counts = {}, {}
for scanner in SCANNERS:
    r = rows.get(scanner)
    for o in ORACLES:
        label = f"{scanner}/{o}"
        if not r:
            computed[label] = None
            continue
        computed[label] = float(r[f"{o}_rate"])
        counts[label] = (int(r[f"{o}_det"]), int(r[f"{o}_n"]))

sys.exit(V.verify(__file__, "metrics.json", computed,
                  results_name="table4_cross_matrix.csv",
                  title="Table IV — recomputed 9x3 matrix vs expected/metrics.json (paper golden)\n",
                  counts=counts))
