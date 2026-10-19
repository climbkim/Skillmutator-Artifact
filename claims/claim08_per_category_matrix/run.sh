#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../_pyenv.sh"
cd "$(dirname "$0")/data"
echo "== Table 11 (per-category matrix): recompute -> results/, compare vs expected/metrics.json =="
python scripts/verify_paper_match.py
