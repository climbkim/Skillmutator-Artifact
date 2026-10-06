#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/data"
echo "== Table IV (cross-scanner matrix): recompute -> results/, compare vs expected/metrics.json =="
# verify_paper_match.py recomputes the 9x3 cross-scanner detection matrix from
# the bundled aggregate (data/derived/table3_aggregate.csv), writes the fresh
# matrix to ../results/derived/table4_cross_matrix.csv, and checks each cell
# against the paper golden in ../expected/metrics.json (values + tolerances live
# there, not in the script). build_table3.py is author-side regeneration from
# the raw scan tree (not shipped) and is intentionally not invoked here.
python scripts/verify_paper_match.py
