# -*- coding: utf-8 -*-
"""Table X (tab:baseline_aggregate) — recompute per-scanner finding counts on the
17 unmodified skills from the bundled summaries, then hand them to the shared
verifier, which writes results/derived/table10_baseline_aggregate.csv and compares
them cell-by-cell against the paper golden in expected/metrics.json (values +
tolerances live there).

Each scanner contributes 4 checked cells: skills_with (# of 17 skills with >=1
finding), mean, max, total. The rule-based/commercial + proprietary-LLM rows are
read from baseline_summary_manual.csv (paper-canonical, manual-verified counts);
SkillScan (upload API) is recomputed from skillscan_unmodified_summary.csv.
The fine-tuned Qwen row is verified separately (count_qwen_phase3_findings.py) and
is not a checked cell here.
"""
import csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

DERIVED = Path(__file__).resolve().parents[1] / "derived"        # data/derived (inputs)


def load_summary(path):
    """Return {scanner_name: (with_find, mean, max, total)} from baseline_summary*.csv."""
    out = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row.get("scanner")
            if not name:
                continue
            with_find = int(row.get("skills_with_findings") or row.get("with_findings") or 0)
            mean = float(row.get("mean_findings") or row.get("mean") or 0)
            mx = int(row.get("max_findings") or row.get("max") or 0)
            tot = int(row.get("total_findings") or row.get("total") or 0)
            out[name] = (with_find, mean, mx, tot)
    return out


manual = load_summary(DERIVED / "baseline_summary_manual.csv")

# golden label -> key in baseline_summary_manual.csv
ROWS = [
    ("skill-security-scan", "skill-security-scan (Total Issues)"),
    ("Snyk Agent Scan",     "Snyk Agent Scan (HIGH severity)"),
    ("GPT-4o-mini",         "LLM scanner GPT-4o-mini (manual)"),
    ("GPT-5.4-mini",        "LLM scanner GPT-5.4-mini (manual)"),
    ("GPT-5.4",             "LLM scanner GPT-5.4 (manual)"),
]

computed, counts = {}, {}
for label, key in ROWS:
    t = manual.get(key)
    if not t:
        for cell in ("skills_with", "mean", "max", "total"):
            computed[f"{label}/{cell}"] = None
        continue
    wf, mean, mx, tot = t
    computed[f"{label}/skills_with"] = wf
    computed[f"{label}/mean"] = round(mean, 2)
    computed[f"{label}/max"] = mx
    computed[f"{label}/total"] = tot
    counts[f"{label}/skills_with"] = (wf, 17)

# SkillScan (upload API): recompute from the raw per-skill findings.
sk = DERIVED / "skillscan_unmodified_summary.csv"
if sk.is_file():
    with sk.open(encoding="utf-8") as f:
        rr = list(csv.DictReader(f))
    nf = [int(r.get("n_findings", 0) or 0) for r in rr]
    wf = sum(1 for n in nf if n > 0)
    tot = sum(nf)
    mx = max(nf) if nf else 0
    mean = tot / max(len(nf), 1)
    computed["SkillScan (upload API)/skills_with"] = wf
    computed["SkillScan (upload API)/mean"] = round(mean, 2)
    computed["SkillScan (upload API)/max"] = mx
    computed["SkillScan (upload API)/total"] = tot
    counts["SkillScan (upload API)/skills_with"] = (wf, 17)

print("[INFO] Qwen2.5-Coder-7B fine-tuned (prefill) row verified separately via "
      "count_qwen_phase3_findings.py; not a checked cell here.\n")

sys.exit(V.verify(__file__, "metrics.json", computed,
                  results_name="table10_baseline_aggregate.csv",
                  title="Table X - recomputed vs expected/metrics.json (paper golden)\n",
                  counts=counts))
