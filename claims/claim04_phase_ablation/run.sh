#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../_pyenv.sh"
cd "$(dirname "$0")/data"

echo "== rebuild: build_table7.py =="
python scripts/build_table7.py

echo "== Table 6 (phase ablation): recompute -> results/, compare vs expected/metrics.json =="
python scripts/verify_paper_match.py
