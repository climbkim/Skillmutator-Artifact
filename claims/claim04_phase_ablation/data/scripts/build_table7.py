"""build_table7.py — aggregate Table VI four-phase schema ablation rows.

Reproduces the six-row progression of Table VI (tab:finetune_rq2): each phase of
the training schema is added in turn (Phase 1..4), then deterministic refinement,
then forced Phase-4-header prefilling. Reads ../judge/*.csv and emits
../derived/table7_aggregate.csv.
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


def rate(csv_path: Path) -> tuple[int, int, float]:
    if not csv_path.is_file():
        return (0, 0, 0.0)
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    det = sum(1 for r in rows if r.get("detected") == "True")
    n = len(rows)
    return (det, n, 100.0 * det / max(n, 1))


def main() -> int:
    # Six-row four-phase schema chain (Table VI / tab:finetune_rq2), all rows
    # evaluated under the 4-section judge for a consistent progression.
    config = [
        ("Phase 1 (Purpose Grounding)",         "phase1_noprefill.csv"),
        ("+ Phase 2 (Out-of-Scope Detection)",  "phase1-2_noprefill.csv"),
        ("+ Phase 3 (Principle Reasoning)",     "phase1-3_noprefill.csv"),
        ("+ Phase 4 (Category Labeling)",       "phase1-4_noprefill.csv"),
        ("+ deterministic refinement",          "phase1-4_refine_noprefill.csv"),
        ("+ prefill (Phase 4 header forced)",   "phase1-4_refine_prefill.csv"),
    ]

    out_rows = []
    prev_pct = None
    print(f"{'Row':<55}{'count':>10}{'rate':>10}{'Δ':>10}")
    print("-" * 90)
    for label, csv_name in config:
        det, n, pct = rate(JUDGE / csv_name)
        delta = "" if prev_pct is None else f"+{pct-prev_pct:.1f}pp"
        print(f"  {label:<53}{det}/{n:<6}{pct:>7.2f}%{delta:>10}")
        out_rows.append({"row": label, "detected": det, "total": n, "rate_pct": f"{pct:.2f}", "delta_pp": delta})
        prev_pct = pct

    # Also report alternative Phase-4 (no-refine) evaluation variants
    print()
    print("Reference (alternative Phase-4 no-refine evals):")
    for label, csv_name in [
        ("Phase 4 no-refine, 3-section (prefill)",  "phase1-4_3section_prefill.csv"),
        ("Phase 4 no-refine, 4-section (noprefill)","phase1-4_noprefill.csv"),
        ("Phase 4 no-refine, 4-section (prefill)",  "phase1-4_prefill.csv"),
    ]:
        det, n, pct = rate(JUDGE / csv_name)
        print(f"  {label:<53}{det}/{n:<6}{pct:>7.2f}%")

    out_csv = DERIVED / "table7_aggregate.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"\n[written] {out_csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())