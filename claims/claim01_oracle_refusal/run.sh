#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/data"
echo "== Table III (oracle refusal): recompute -> results/, compare vs expected/metrics.json =="
# verify_paper_match.py recomputes per-oracle refusal metrics from the bundled
# aggregate (data/derived/table4_aggregate.csv), writes the fresh table to
# ../results/derived/table3_refusal.csv, and checks it against the paper golden
# in ../expected/metrics.json (values + tolerances live there, not in the script).
python scripts/verify_paper_match.py
