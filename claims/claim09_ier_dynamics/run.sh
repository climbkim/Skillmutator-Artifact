#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/data"

echo "== Figure 4 (IER dynamics): recompute -> results/, compare vs expected/metrics.json =="
# verify_paper_match.py recomputes the LLM self-scanner per-iteration detection
# rate from derived/ier_dynamics.csv, writes the fresh table to
# ../results/derived/fig4_ier_dynamics.csv, and checks it against the paper
# golden in ../expected/metrics.json (values + tolerance live there, not in the
# script). It also asserts the residual relational rule iter_1 < iter_0.
python scripts/verify_paper_match.py
