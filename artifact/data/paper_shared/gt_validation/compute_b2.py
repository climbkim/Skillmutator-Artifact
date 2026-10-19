# -*- coding: utf-8 -*-
"""Appendix B.2 Judge Robustness: recompute the judge-agreement numbers.

Reads b2_verdicts.csv (one row per scanner report, labels only) and prints:
  - the paper's GPT-5.4 verdicts (judged against the mutation log capped at
    1,500 characters) vs. a GPT-5.4 re-judgment against the complete ground
    truth, on all 301 scanner reports       -> paper: 93.7%, kappa 0.850
  - that complete-ground-truth GPT-5.4 judgment vs. a Claude-Opus-5 judgment,
    on the fine-tuned Qwen scanner's 76 reports  -> paper: 96.1%, kappa 0.847
Python standard library only.
"""
import csv
from pathlib import Path

ROWS = list(csv.DictReader(open(Path(__file__).resolve().parent / "b2_verdicts.csv", encoding="utf-8")))


def agreement(rows, a, b):
    pairs = [(r[a] == "True", r[b] == "True") for r in rows]
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    pa, pb = sum(x for x, _ in pairs) / n, sum(y for _, y in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return n, 100 * po, (po - pe) / (1 - pe)


for label, rows, a, b, paper in [
    ("GPT-5.4 paper (capped GT) vs GPT-5.4 complete GT, all reports",
     ROWS, "gpt54_paper_capped_gt", "gpt54_complete_gt", "93.7%, kappa 0.850, n=301"),
    ("GPT-5.4 complete GT vs Claude-Opus-5 complete GT, Qwen scanner",
     [r for r in ROWS if r["scanner"] == "qwen-d3-prefill"], "gpt54_complete_gt", "opus5_complete_gt",
     "96.1%, kappa 0.847, n=76"),
]:
    n, pct, k = agreement(rows, a, b)
    print(f"{label}: {pct:.1f}%, kappa {k:.3f}, n={n}   (paper: {paper})")
