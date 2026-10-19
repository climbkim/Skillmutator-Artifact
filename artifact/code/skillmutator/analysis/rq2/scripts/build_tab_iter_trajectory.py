"""build_tab_iter_trajectory.py — Analysis 2 (per-iter detection rate, select
mode, all 3 oracles). Carry-forward rule: at iter K, each scenario uses verdict
at last_good_iter ≤ K, and one with no refusal-free mutation yet counts as not
detected. Denom fixed = evaluable scenarios (n = 48 / 63 / 76).
Scanners as in paper Figure 4: skill-security-scan, Snyk, and the oracle's own
LLM scanner. A scanner with no verdict at all (not run or unavailable) is left out.

Outputs:
  outputs/tab_iter_trajectory.csv  (long form)
"""
import csv, sys
from pathlib import Path
import sys

# Put the repo's `analysis/` directory on sys.path so `skillmutator_utils/`
# is importable regardless of the cwd this script is launched from.
_ANALYSIS_ROOT = Path(__file__).resolve().parents[2]
if str(_ANALYSIS_ROOT) not in sys.path:
    sys.path.insert(0, str(_ANALYSIS_ROOT))

from skillmutator_utils.refusal import aggregate_per_iter
from skillmutator_utils.paths import ORACLES

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = Path("outputs/tab_iter_trajectory.csv")


def scanners_for(oracle: str) -> list:
    return ["ss", "snyk", f"llm/{oracle}-self"]


def main():
    out_rows = []
    not_run = []
    for oracle in ORACLES:
        for sc in scanners_for(oracle):
            iter_rows = aggregate_per_iter(oracle, "select", sc, rule="carry_forward")
            if not any(r["n"] for r in iter_rows) or not any(r["verdicts"] for r in iter_rows):
                not_run.append(f"{oracle} {sc}")
                continue
            for r in iter_rows:
                out_rows.append({
                    "oracle": oracle, "mode": "select", "scanner": sc,
                    "iter": r["iter"], "n": r["n"],
                    "detected": r["detected"],
                    "carried_forward": r["carried_forward"],
                    "rate_pct": f"{r['rate_pct']:.2f}",
                })
    if not out_rows:
        print("[error] no scanner has verdicts in the data tree", file=sys.stderr)
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows: w.writerow(r)
    print(f"[saved] {OUT}\n")

    # Pretty print per oracle
    for oracle in ORACLES:
        scanners = scanners_for(oracle)
        if not any(r["oracle"] == oracle for r in out_rows):
            print(f"--- {oracle} dataset: not run ---\n")
            continue
        nl = next((r["n"] for r in out_rows if r["oracle"]==oracle and r["iter"]==0), 0)
        print(f"--- {oracle} dataset (n = {nl}, carry-forward) ---")
        print(f"{'Scanner':<24}" + "".join(f"{f'iter_{i}':>11}" for i in range(5)))
        for sc in scanners:
            line = f"  {sc:<22}"
            for it in range(5):
                row = next((r for r in out_rows
                            if r["oracle"]==oracle and r["scanner"]==sc and r["iter"]==it), None)
                if row is None: line += f" {'n/a':>10}"
                else:
                    line += f" {row['detected']:>3}/{row['n']:<3}{float(row['rate_pct']):>5.2f}%"
            print(line)
        print()
    if not_run:
        print("n/a (not run or unavailable, left out of the figure): " + ", ".join(not_run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
