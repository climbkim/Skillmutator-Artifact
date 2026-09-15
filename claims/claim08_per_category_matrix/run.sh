#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/data"
echo "== Table XI (per-category matrix): recompute -> results/, compare vs expected/metrics.json =="
python scripts/verify_paper_match.py
