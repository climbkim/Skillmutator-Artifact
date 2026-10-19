# -*- coding: utf-8 -*-
"""Figure 4 (IER dynamics, refusal-aware aggregation) — recompute the per-iteration detection rates
from the masked per-iteration verdicts (raw/ier_verdicts.csv) with
compute_ier_dynamics.py, then hand the LLM self-scanner rates to the shared
verifier, which writes results/derived/fig4_ier_dynamics.csv and compares them
cell-by-cell against the paper golden in expected/metrics.json (values +
tolerance live there).

Consistency check: all 45 recomputed (oracle, iter, scanner) cells must equal the
bundled plot table derived/ier_dynamics.csv, which plot_ier_dynamics.py draws.

Residual relational rule (paper: the first refinement step reduces detection):
iter_1 < iter_0 for every oracle. The comparison operands are the freshly
recomputed rates; no fixed numbers live in this script.
"""
import csv, io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _verify_common as V
from compute_ier_dynamics import rows_from_csv, aggregate_ier

agg = aggregate_ier(rows_from_csv())          # {(oracle, iter, scanner): (n, detected)}

# Consistency: recomputed cells == bundled plot table.
CSV = Path(__file__).resolve().parents[1] / "derived" / "ier_dynamics.csv"
bundled = {(r["oracle"], int(r["iter"]), r["scanner"]): (int(r["n"]), int(r["detected"]))
           for r in csv.DictReader(io.open(CSV, encoding="utf-8"))}
same = sum(1 for k, v in agg.items() if bundled.get(k) == v)
table_ok = same == len(agg) == len(bundled)
print(f"[{'OK ' if table_ok else 'XX '}] derived/ier_dynamics.csv reproduced from raw/ier_verdicts.csv: "
      f"{same}/{len(bundled)} cells\n")

# Recompute per-(oracle, iter) detection rate for the LLM self-scanner only.
computed, counts = {}, {}
per_iter = {}   # oracle -> {iter: rate} for the residual relational rule
for (oracle, it, sc), (n, det) in sorted(agg.items()):
    if sc != "llm":
        continue
    v = round(100.0 * det / n, 1)
    label = f"{oracle}/iter{it}"
    computed[label] = v
    counts[label] = (det, n)
    per_iter.setdefault(oracle, {})[it] = v

rc = V.verify(__file__, "metrics.json", computed,
              results_name="fig4_ier_dynamics.csv",
              title="Figure 4 — IER dynamics recomputed vs expected/metrics.json (paper golden)\n",
              counts=counts)

# Residual relational rule: detection drops iter_0 -> iter_1 for each oracle.
print("\nRelational rule — first refinement step reduces detection (iter_1 < iter_0):")
rel_ok = True
for oracle, iters in sorted(per_iter.items()):
    i0, i1 = iters.get(0), iters.get(1)
    good = i0 is not None and i1 is not None and i1 < i0
    rel_ok = rel_ok and good
    print(f"  [{'OK ' if good else 'XX '}] {oracle:14s} iter_0={i0} -> iter_1={i1}")

# Every later iteration stays below iter_0 (0-indexed; paper/Figure 4 label: iter 1 vs. iter 2-5).
print("\nRelational rule — every later iteration stays below iter_0 (iter_1..iter_4 < iter_0):")
for oracle, iters in sorted(per_iter.items()):
    i0 = iters.get(0)
    later = [iters.get(k) for k in (1, 2, 3, 4)]
    good = i0 is not None and None not in later and max(later) < i0
    rel_ok = rel_ok and good
    print(f"  [{'OK ' if good else 'XX '}] {oracle:14s} iter_0={i0} > max(iter_1..4)={max(v for v in later if v is not None)}")
print("\n" + ("RELATIONAL OK" if rel_ok else "RELATIONAL FAIL"))

sys.exit(rc or (0 if (rel_ok and table_ok) else 1))
