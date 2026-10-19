#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../_pyenv.sh"
cd "$(dirname "$0")/data"

echo "== Figure 4 (IER dynamics): recompute -> results/, compare vs expected/metrics.json =="
# verify_paper_match.py recomputes the per-iteration detection rates from the
# masked verdicts in raw/ier_verdicts.csv, checks all 45 cells against
# derived/ier_dynamics.csv, writes the LLM self-scanner rates to
# ../results/derived/fig4_ier_dynamics.csv, and checks them against the paper
# golden in ../expected/metrics.json (values + tolerance live there, not in the
# script). It also asserts the relational rules iter_1 < iter_0 and
# max(iter_1..iter_4) < iter_0 (0-indexed; the paper labels iterations 1-5).
python scripts/verify_paper_match.py
