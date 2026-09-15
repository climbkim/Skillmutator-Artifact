# -*- coding: utf-8 -*-
"""Figure 6 (fig:rq3_finding1) — recompute scanner detection on the GPT-5.4
oracle benchmark (n=76, select mode, GPT-5.4 judge). Detected counts come from
the bundled SCANNERS table (export_scanners_csv.py, mirrors the plot); each
scanner's detection rate is recomputed as 100 * detected / n (n read from the
golden). The recomputed counts + rates are handed to the shared verifier, which
writes results/derived/fig6_rq3_scanners.csv and compares them cell-by-cell
against the paper golden in expected/metrics.json (values + tolerances live
there).

Residual relational rule (Finding 4): our fine-tuned Qwen scanner has the
highest detection rate of all scanners (beats every rule-based, proprietary, and
base baseline, including the frontier GPT-5.4 self-scanner). Operands are the
freshly recomputed rates; no fixed numbers live in this script.
"""
import io, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_scanners_csv import SCANNERS   # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

CLAIM = Path(__file__).resolve().parents[2]
GOLD = json.load(io.open(CLAIM / "expected" / "metrics.json", encoding="utf-8"))
N = GOLD["n"]   # benchmark size (paper: n=76)

computed, counts = {}, {}
rates = {}   # label -> recomputed rate, for the residual relational rule
for label, det, _rate_in_table, _grp in SCANNERS:
    rate = round(100.0 * det / N, 2)
    computed[f"{label}/det"] = det
    computed[f"{label}/rate"] = rate
    counts[f"{label}/rate"] = (det, N)
    rates[label] = rate

rc = V.verify(__file__, "metrics.json", computed,
              results_name="fig6_rq3_scanners.csv",
              title="Figure 6 — RQ3 scanner detection recomputed vs expected/metrics.json (paper golden)\n",
              counts=counts)

# Residual relational rule (Finding 4): our fine-tuned scanner is the best.
OURS = "Qwen2.5-Coder-7B-Instruct (ours)"
print("\nRelational rule — our fine-tuned scanner leads all scanners:")
top = max(rates, key=rates.get)
rel_ok = top == OURS
print(f"  [{'OK ' if rel_ok else 'XX '}] top scanner = {top} ({rates[top]:.2f}%) (expect '{OURS}')")
print("\n" + ("RELATIONAL OK" if rel_ok else "RELATIONAL FAIL"))

sys.exit(rc or (0 if rel_ok else 1))
