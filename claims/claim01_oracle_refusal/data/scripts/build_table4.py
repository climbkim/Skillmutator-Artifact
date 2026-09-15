"""build_table4.py — assemble Table III (refusal behavior, 3 GPT oracles).

Aggregates per-iter counts (iter_0..4) for each oracle from:
  - derived/tab2_refusal_per_iter.csv (GPT oracles, all-iter)

Output: derived/table4_aggregate.csv with one row per oracle.
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "derived"

ORACLES = ["gpt-4o-mini", "gpt-5.4-mini", "gpt-5.4"]
N_TOTAL = {"gpt-4o-mini": 51, "gpt-5.4-mini": 63, "gpt-5.4": 76}


def gpt_per_iter(oracle: str) -> tuple[list[int], dict]:
    """Return ([iter0..iter4 refusal counts], iter4_mechanisms)."""
    rows = list(csv.DictReader((DERIVED / "tab2_refusal_per_iter.csv").open(encoding="utf-8")))
    rows = [r for r in rows if r["oracle"] == oracle and r["mode"] == "select"]
    per_iter = [0, 0, 0, 0, 0]
    iter4_mech = {"silent": 0, "explicit": 0, "partial": 0}
    for r in rows:
        i = int(r["iter"])
        if i > 4: continue
        exp = int(r["explicit_refusal"])
        sil = int(r["silent_failure"])
        par = int(r["partial_refusal"])
        per_iter[i] = exp + sil + par
        if i == 4:
            iter4_mech = {"silent": sil, "explicit": exp, "partial": par}
    return per_iter, iter4_mech




def main():
    rows_out = []
    for oracle in ORACLES:
        per_iter, mech = gpt_per_iter(oracle)
        n = N_TOTAL[oracle]
        i4_refusals = per_iter[4]
        rate_pct = 100.0 * i4_refusals / n
        rows_out.append({
            "oracle": oracle,
            "n": n,
            "refusal_rate_pct": f"{rate_pct:.2f}",
            "per_iter": "/".join(str(c) for c in per_iter),
            "iter4_silent": mech["silent"],
            "iter4_explicit": mech["explicit"],
            "iter4_partial": mech["partial"],
        })

    print(f"{'Oracle':<18}{'n':>5}{'final-rate%':>13}{'per-iter (0-4)':>22}{'silent':>10}{'expl':>6}{'partial':>9}")
    print("-" * 90)
    for r in rows_out:
        print(f"  {r['oracle']:<16}{r['n']:>5}{r['refusal_rate_pct']:>12}%{r['per_iter']:>22}"
              f"{r['iter4_silent']:>10}{r['iter4_explicit']:>6}{r['iter4_partial']:>9}")

    out_csv = DERIVED / "table4_aggregate.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        for r in rows_out:
            w.writerow(r)
    print(f"\n[written] {out_csv}")


if __name__ == "__main__":
    main()