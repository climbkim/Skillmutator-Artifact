"""build_table6.py — aggregate Figure 5 detection rates from per-model judge CSVs.

Reads ../judge/{base,d3-noprefill,d3-prefill}.csv for each of 4 base models and
emits ../derived/table6_aggregate.csv with the 3-column layout:

  base_model, base_pct, finetuned_noprefill_pct, finetuned_prefill_pct
"""
from __future__ import annotations
import csv, sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
JUDGE = ROOT / "judge"
DERIVED = ROOT / "derived"
DERIVED.mkdir(exist_ok=True)


def detection_rate(csv_path: Path, denom: int = 76) -> tuple[int, int]:
    """Return (detected_count, total_rows). For Llama base denom may be 65 (scan gap)."""
    if not csv_path.is_file():
        return (0, 0)
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    detected = sum(1 for r in rows if r.get("detected") == "True")
    return (detected, len(rows))


def main():
    out_rows = []
    for short, label in [
        ("qwen",    "Qwen2.5-Coder-7B-Instruct"),
        ("llama",   "Llama-3.1-8B-Instruct"),
        ("mistral", "Mistral-7B-Instruct-v0.3"),
        ("gemma",   "Gemma-2-9b-it"),
    ]:
        base_d, base_t = detection_rate(JUDGE / f"{short}-base.csv")
        np_d, np_t = detection_rate(JUDGE / f"{short}-finetuned_noprefill.csv")
        pf_d, pf_t = detection_rate(JUDGE / f"{short}-finetuned_prefill.csv")
        # Paper reports x/76 — use base denom from base_t, fine-tuned uses np_t (typically 76)
        out_rows.append({
            "base_model": label,
            "base_detected":  base_d, "base_total":  base_t, "base_pct":  f"{100*base_d/max(base_t,1):.1f}",
            "finetuned_noprefill_detected": np_d, "finetuned_noprefill_total": np_t, "finetuned_noprefill_pct": f"{100*np_d/max(np_t,1):.1f}",
            "finetuned_prefill_detected":   pf_d, "finetuned_prefill_total":   pf_t, "finetuned_prefill_pct":   f"{100*pf_d/max(pf_t,1):.1f}",
        })

    out_csv = DERIVED / "table6_aggregate.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    print(f"=== Figure 5 aggregate ===")
    print(f"{'Base model':<32} {'base':>8} {'FT-noprefill':>12} {'FT-prefill':>12}")
    for r in out_rows:
        print(f"{r['base_model']:<32} {r['base_detected']}/{r['base_total']:<4} ({r['base_pct']:>5}%)  "
              f"{r['finetuned_noprefill_detected']:>2}/{r['finetuned_noprefill_total']:<3} ({r['finetuned_noprefill_pct']:>5}%)  "
              f"{r['finetuned_prefill_detected']:>2}/{r['finetuned_prefill_total']:<3} ({r['finetuned_prefill_pct']:>5}%)")
    print(f"\n[written] {out_csv}")


if __name__ == "__main__":
    main()