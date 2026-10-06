#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/data"

echo "== rebuild: build_table5.py =="
python scripts/build_table5.py

echo "== Table V (stealth-aware selection): recompute -> results/, compare vs expected/metrics.json =="
# verify_paper_match.py reads the freshly rebuilt table
# (data/derived/tab_select_vs_noselect.csv), recomputes per-scanner rates + the
# 6-scanner average, writes them to
# ../results/derived/table5_select_vs_noselect.csv, and checks each cell against
# the paper golden in ../expected/metrics.json (values + tolerances live there).
python scripts/verify_paper_match.py
