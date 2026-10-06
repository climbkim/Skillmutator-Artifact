#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/data"

echo "== Figure 5 (prefill delta): recompute -> results/, compare vs expected/metrics.json =="
# verify_paper_match.py extracts the plotted detection-rate arrays from
# plot_prefill_delta.py, recomputes the per-family prefill delta, writes the
# fresh table to ../results/derived/fig5_prefill_delta.csv, and checks it against
# the paper golden in ../expected/metrics.json (values + tolerances live there,
# not in the script). It also asserts the residual relational rule (Finding 6:
# prefill helps Qwen, hurts Llama/Mistral/Gemma under the GPT-5.4 judge).
python scripts/verify_paper_match.py
