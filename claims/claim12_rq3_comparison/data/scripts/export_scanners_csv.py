"""Export the SCANNERS table from plot_candidates.py to a CSV for verification.

Outputs raw/scanners.csv with columns: label, detected, rate_pct, group.
This mirrors the in-script tuple constant so external verification can
cross-check paper-cited values without executing the plot pipeline.
"""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]

SCANNERS = [
    # Rule-based / commercial
    ("skill-security-scan",                        6,  7.89, "rule"),
    ("Snyk Agent Scan",                            7,  9.21, "rule"),
    ("SkillScan",                                  1,  1.32, "rule"),
    # Proprietary LLM scanners
    ("GPT-4o-mini",                               18, 23.68, "proprietary"),
    ("GPT-5.4-mini",                              60, 78.95, "proprietary"),
    ("GPT-5.4",                                   66, 86.84, "proprietary"),
    # Ours (Qwen2.5-Coder-7B-Instruct base vs fine-tuned + prefill)
    ("Qwen2.5-Coder-7B-Instruct (base)",          13, 17.11, "ours_base"),
    ("Qwen2.5-Coder-7B-Instruct (ours)",          67, 88.16, "ours_ft"),
]


def main():
    out = ROOT / "raw" / "scanners.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label", "detected", "rate_pct", "group"])
        for row in SCANNERS:
            w.writerow(row)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()