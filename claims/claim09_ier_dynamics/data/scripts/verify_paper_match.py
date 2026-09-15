# -*- coding: utf-8 -*-
"""Figure 4 (IER dynamics, pinD) — recompute the LLM self-scanner per-iteration
detection rate from the bundled ier_dynamics.csv (rate = 100 * detected / n),
then hand the recomputed values to the shared verifier, which writes
results/derived/fig4_ier_dynamics.csv and compares them cell-by-cell against the
paper golden in expected/metrics.json (values + tolerance live there).

Residual relational rule (paper: the first refinement step reduces detection):
iter_1 < iter_0 for every oracle. The comparison operands are the freshly
recomputed rates; no fixed numbers live in this script.
"""
import csv, io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

CSV = Path(__file__).resolve().parents[1] / "derived" / "ier_dynamics.csv"
rows = list(csv.DictReader(io.open(CSV, encoding="utf-8")))

# Recompute per-(oracle, iter) detection rate for the LLM self-scanner only.
computed, counts = {}, {}
per_iter = {}   # oracle -> {iter: rate} for the residual relational rule
for r in rows:
    if r["scanner"] != "llm":
        continue
    oracle, it = r["oracle"], int(r["iter"])
    det, n = int(r["detected"]), int(r["n"])
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
print("\n" + ("RELATIONAL OK" if rel_ok else "RELATIONAL FAIL"))

sys.exit(rc or (0 if rel_ok else 1))
