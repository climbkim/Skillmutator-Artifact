#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/data"

echo "== Table VII (wild ClawHub): recompute -> results/, compare vs expected/metrics.json =="
# verify_paper_match.py recomputes per-stratum + aggregate accuracy from the
# bundled verdicts (data/derived), writes the fresh table to
# ../results/derived/table7_wild_eval.csv, and checks it against the paper golden
# in ../expected/table7.json (values + tolerances live there, not in the script).
python scripts/verify_paper_match.py
