#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/data"

echo "== export scanners table (raw/scanners.csv) =="
python scripts/export_scanners_csv.py

echo "== Figure 6 (RQ3 comparison): recompute -> results/, compare vs expected/metrics.json =="
# verify_paper_match.py recomputes each scanner's detection rate as
# 100*detected/n (n read from the golden) from the bundled SCANNERS counts,
# writes the fresh table to ../results/derived/fig6_rq3_scanners.csv, and checks
# it against the paper golden in ../expected/metrics.json (values + tolerances
# live there, not in the script). It also asserts the residual relational rule
# (Finding 4: our fine-tuned scanner leads all scanners).
python scripts/verify_paper_match.py
