# -*- coding: utf-8 -*-
"""Table VII (Finding 7, wild ClawHub) — recompute per-stratum accuracy and the
aggregate (Accuracy / FPR) over the n=200 evaluation set from the bundled judge
verdicts, then hand the recomputed metrics to the shared verifier, which writes
results/derived/table7_wild_eval.csv and compares them cell-by-cell against the
paper golden in expected/metrics.json (values + tolerances live there).

Per-stratum accuracy: clean = not a false alarm; suspicious = lenient D+P
(DETECTED or PARTIAL), paper protocol. Suspicious side uses the rerun12
measurement (_rerun12_new_verdicts.json merged on top of the base per-skill CSV).
"""
import csv, io, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

D = Path(__file__).resolve().parents[1] / "derived"            # data/derived (inputs)
data = list(csv.DictReader(io.open(D / "_judge_per_skill.csv", encoding="utf-8")))

# rerun12 recovered verdicts (suspicious side only)
rerun = D / "_rerun12_new_verdicts.json"
rerun_map = {}
if rerun.exists():
    for it in json.load(io.open(rerun, encoding="utf-8")):
        if it.get("slug") and it.get("verdict"):
            rerun_map[it["slug"]] = it["verdict"]
n_applied = 0
for r in data:
    if r["group"] == "suspicious" and r["slug"] in rerun_map:
        r["verdict"] = rerun_map[r["slug"]]
        n_applied += 1
print(f"rerun12 recovered verdicts applied: {n_applied}/12\n")


def correct(r):
    v = r["verdict"].upper()
    if r["group"] == "clean":
        return v != "FALSE_ALARM"
    return v in ("DETECTED", "PARTIAL")


STRAT = [("clean", None), ("suspicious", "LOW"), ("suspicious", "MEDIUM"),
         ("suspicious", "HIGH"), ("suspicious", "CRITICAL")]

computed, counts = {}, {}
for grp, sev in STRAT:
    sub = [r for r in data if r["group"] == grp and (sev is None or r["sks_severity"] == sev)]
    key = f"{grp}/{sev}"
    if not sub:
        computed[key] = None
        continue
    c = sum(1 for r in sub if correct(r))
    computed[key] = round(100 * c / len(sub), 1)
    counts[key] = (c, len(sub))

clean = [r for r in data if r["group"] == "clean"]
n_correct = sum(1 for r in data if correct(r))
n_fa = sum(1 for r in clean if r["verdict"].upper() == "FALSE_ALARM")
computed["aggregate/accuracy"] = round(100 * n_correct / len(data), 1)
computed["aggregate/fpr"] = round(100 * n_fa / len(clean), 1)
counts["aggregate/accuracy"] = (n_correct, len(data))
counts["aggregate/fpr"] = (n_fa, len(clean))

sys.exit(V.verify(__file__, "metrics.json", computed,
                  results_name="table7_wild_eval.csv",
                  title="Table VII — recomputed vs expected/metrics.json (paper golden)\n",
                  counts=counts))
