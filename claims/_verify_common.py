# -*- coding: utf-8 -*-
"""Shared claim verifier (A-on-B).

Each claims/claimNN/data/scripts/verify_paper_match.py recomputes its metrics
from the bundled verdicts under data/derived, then calls verify() here to:
  (A) load the machine-readable paper golden from claimNN/expected/<golden>.json
      — the SINGLE source of the paper-cited values and tolerances,
  (B) write the freshly recomputed table to claimNN/results/derived/<results>,
      and compare it cell-by-cell against the golden, printing PASS/FAIL.

No expected values live in the Python; edit expected/<golden>.json to change them.

Golden JSON schema:
  {
    "paper_element": "Table VII (tab:wild_eval)",     # free text
    "metrics": { "<label>": <expected number>, ... }, # paper-cited values
    "tolerance_pp": 1.0                               # global tolerance, OR:
    # "tolerance_pp": { "_default": 1.0, "<label>": 0.5, ... }
  }
"""
import csv, io, json, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def _fmt(v):
    return "" if v is None else f"{v:g}"


def verify(script_file, golden_name, computed, results_name="metrics.csv",
           title="", counts=None):
    """script_file: caller __file__ (…/claimNN/data/scripts/verify_*.py).
    golden_name: JSON filename under claimNN/expected/.
    computed: {label: value|None}. counts: optional {label: (num, den)}.
    Writes claimNN/results/derived/<results_name>, prints a PASS/FAIL table,
    returns 0 (ALL MATCH) or 1 (MISMATCH)."""
    claim = Path(script_file).resolve().parents[2]            # …/claimNN
    golden = json.load(io.open(claim / "expected" / golden_name, encoding="utf-8"))
    metrics = golden["metrics"]
    tol = golden.get("tolerance_pp", 0.5)

    def tol_of(label):
        if isinstance(tol, dict):
            return tol.get(label, tol.get("_default", 0.5))
        return tol

    counts = counts or {}
    if title:
        print(title)
    print(f"  {'metric':30s} {'computed':>10s} {'expected':>10s} {'tol':>6s}")

    ok = True
    out_rows = []
    for label, exp in metrics.items():
        cv = computed.get(label)
        t = tol_of(label)
        if cv is None:
            good = False
            print(f"  [XX ] {label:28s} {'(missing)':>10s}")
        else:
            good = abs(cv - exp) <= t
            print(f"  [{'OK ' if good else 'XX '}] {label:28s} {cv:>10.4g} {exp:>10.4g} {t:>4}pp")
        ok = ok and good
        num, den = counts.get(label, ("", ""))
        out_rows.append([label, _fmt(cv), _fmt(exp), t, num, den, "OK" if good else "FAIL"])

    rdir = claim / "results" / "derived"
    rdir.mkdir(parents=True, exist_ok=True)
    with io.open(rdir / results_name, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["metric", "computed", "expected", "tol_pp", "numerator", "denominator", "status"])
        w.writerows(out_rows)
    print(f"\n[results] wrote {(rdir / results_name).relative_to(claim)}")
    print("\n" + ("ALL MATCH" if ok else "MISMATCH"))
    return 0 if ok else 1
