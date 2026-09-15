# -*- coding: utf-8 -*-
"""Table 6 / Figure 5 (Finding 5) — recompute per-family base-vs-fine-tuned
detection from ../derived/table6_aggregate.csv (built by build_table6.py):

  * base:      recomputed as base_detected / canonical_base_denominator, the
               paper's n=76 convention (missing scan attempts imputed as
               'not detected'); the denominator is read from the golden.
  * no-prefill / prefill: read from the aggregate percentages.

The 12 recomputed cells are handed to the shared verifier, which writes
results/derived/table6_finetune.csv and compares them against the paper golden
in expected/metrics.json (values + tolerance live there).

Residual relational rule (Finding 5): fine-tuning improves every base family
(best fine-tuned > base), and Qwen is the strongest fine-tuned family. Operands
are the freshly recomputed rates; no fixed numbers live in this script.
"""
from __future__ import annotations
import csv, io, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # claims/
import _verify_common as V

CLAIM = Path(__file__).resolve().parents[2]
DERIVED = CLAIM / "data" / "derived"
GOLD = json.load(io.open(CLAIM / "expected" / "metrics.json", encoding="utf-8"))
DENOM = GOLD["canonical_base_denominator"]   # paper convention (n=76)

FAMILY = {
    "Qwen2.5-Coder-7B-Instruct": "Qwen",
    "Llama-3.1-8B-Instruct":     "Llama",
    "Mistral-7B-Instruct-v0.3":  "Mistral",
    "Gemma-2-9b-it":             "Gemma",
}

csv_path = DERIVED / "table6_aggregate.csv"
if not csv_path.is_file():
    sys.exit(f"[FATAL] {csv_path} missing -- run build_table6.py first")

computed, counts = {}, {}
for r in csv.DictReader(io.open(csv_path, encoding="utf-8")):
    fam = FAMILY.get(r["base_model"])
    if not fam:
        continue
    det = int(r["base_detected"])
    computed[f"{fam}/base"] = round(100.0 * det / DENOM, 1)
    counts[f"{fam}/base"] = (det, DENOM)
    computed[f"{fam}/ft_noprefill"] = round(float(r["finetuned_noprefill_pct"]), 1)
    computed[f"{fam}/ft_prefill"] = round(float(r["finetuned_prefill_pct"]), 1)

rc = V.verify(__file__, "metrics.json", computed,
              results_name="table6_finetune.csv",
              title="Table 6 — base-vs-fine-tuned recomputed vs expected/metrics.json (paper golden)\n",
              counts=counts)

# Residual relational rule (Finding 5): every family improves; Qwen strongest.
print("\nRelational rule — fine-tuning improves every family; Qwen strongest:")
best, rel_ok = {}, True
for fam in FAMILY.values():
    base = computed.get(f"{fam}/base")
    bft = max(computed.get(f"{fam}/ft_noprefill"), computed.get(f"{fam}/ft_prefill"))
    best[fam] = bft
    good = base is not None and bft > base
    rel_ok = rel_ok and good
    print(f"  [{'OK ' if good else 'XX '}] {fam:8s} base={base} -> best_ft={bft}")
strongest = max(best, key=best.get)
qwen_ok = strongest == "Qwen"
rel_ok = rel_ok and qwen_ok
print(f"  [{'OK ' if qwen_ok else 'XX '}] strongest fine-tuned family = {strongest} (expect Qwen)")
print("\n" + ("RELATIONAL OK" if rel_ok else "RELATIONAL FAIL"))

sys.exit(rc or (0 if rel_ok else 1))
