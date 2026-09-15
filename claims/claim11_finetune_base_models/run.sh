#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/data"

echo "== rebuild aggregate from per-model judge CSVs: build_table6.py =="
python scripts/build_table6.py

echo "== Table 6 (fine-tune base models): recompute -> results/, compare vs expected/metrics.json =="
# verify_paper_match.py recomputes per-family base-vs-fine-tuned detection from
# derived/table6_aggregate.csv (base via the canonical n=76 denominator read from
# the golden), writes the fresh table to ../results/derived/table6_finetune.csv,
# and checks it against the paper golden in ../expected/metrics.json (values +
# tolerance live there, not in the script). It also asserts the residual
# relational rule (Finding 5: every family improves, Qwen strongest).
python scripts/verify_paper_match.py
