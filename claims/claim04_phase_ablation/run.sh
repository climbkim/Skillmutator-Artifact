#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/data"

echo "== rebuild: build_table7.py =="
python scripts/build_table7.py

echo "== Table VI (phase ablation): recompute -> results/, compare vs expected/metrics.json =="
python scripts/verify_paper_match.py
