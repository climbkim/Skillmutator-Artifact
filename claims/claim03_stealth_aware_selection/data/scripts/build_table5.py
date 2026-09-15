"""build_table5.py — Table V (select vs no-select) detection rates.

Self-contained: reads two bundled sources and re-aggregates per-scanner
detection rates for the stealth-aware-selection vs no-select comparison.

  1. ../judge/select_vs_noselect_verdicts.csv
     (one row per gpt-5.4 scenario = skill x category x mode, with each API
     scanner's final-iteration detection flag) -> the five API scanners
     skill-security-scan, Snyk, GPT-4o-mini, GPT-5.4-mini, GPT-5.4.

  2. ../skillscan_addition/derived/{select,no_select}_perscenario.csv
     -> SkillScan (added later on its own scenario set): a scenario counts as
     detected when the mutated risk escalates to >= MEDIUM relative to the
     paired baseline.

No raw scan tree and no API key/GPU are needed: the verdicts are bundled. (The
raw scan.md tree that produced these verdicts contains the injected malicious
mutation text and is therefore NOT redistributed; see use.txt / ETHICS.md.)

Emits ../derived/tab_select_vs_noselect.csv (the file verify_paper_match.py
checks against the paper).
"""
from __future__ import annotations
import csv, sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
VERDICTS = ROOT / "judge" / "select_vs_noselect_verdicts.csv"
SS_DIR = ROOT / "skillscan_addition" / "derived"
OUT = ROOT / "derived" / "tab_select_vs_noselect.csv"

# verdict-CSV column -> (paper label, scanner_path)
SCANNERS = [
    ("det_ss",         "skill-security-scan",  "ss"),
    ("det_snyk",       "Snyk Agent Scan",      "snyk"),
    ("det_gpt4omini",  "GPT-4o-mini scanner",  "llm/gpt-4o-mini"),
    ("det_gpt54mini",  "GPT-5.4-mini scanner", "llm/gpt-5.4-mini"),
    ("det_gpt54self",  "GPT-5.4 scanner",      "llm/gpt-5.4-self"),
]

_RISK = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def _row(label, path, sn, sd, nn, nd):
    srate = 100 * sd / sn if sn else 0.0
    nrate = 100 * nd / nn if nn else 0.0
    return {
        "scanner": label, "scanner_path": path,
        "n_select": sn, "detected_select": sd, "rate_select_pct": f"{srate:.2f}",
        "n_noselect": nn, "detected_noselect": nd, "rate_noselect_pct": f"{nrate:.2f}",
        "delta_pp": f"{nrate - srate:+.2f}",
    }


def _skillscan_row():
    """SkillScan: paired escalation to >= MEDIUM on its own scenario set."""
    sel = list(csv.DictReader((SS_DIR / "select_perscenario.csv").open(encoding="utf-8")))
    nsl = list(csv.DictReader((SS_DIR / "no_select_perscenario.csv").open(encoding="utf-8")))
    sn = len(sel)
    sd = sum(
        1 for r in sel
        if _RISK.get(r["ss_risk_mutated"].strip().upper(), 0) >= 2
        and _RISK.get(r["ss_risk_mutated"].strip().upper(), 0) > _RISK.get(r["ss_risk_baseline"].strip().upper(), 0)
    )
    nn = len(nsl)
    nd = sum(1 for r in nsl if r["detected_paired_delta"].strip().lower() == "true")
    return _row("SkillScan API", "skillscan", sn, sd, nn, nd)


def main() -> None:
    rows = list(csv.DictReader(VERDICTS.open(encoding="utf-8")))
    agg = {"select": defaultdict(int), "no-select": defaultdict(int)}
    for r in rows:
        m = r["mode"]
        agg[m]["n"] += 1
        for col, _, _ in SCANNERS:
            agg[m][col] += int(r[col])

    # API scanners (rule-based/commercial first, then LLM scanners) with
    # SkillScan slotted right after Snyk to match the paper's table order.
    out_rows = []
    for col, label, path in SCANNERS:
        sn, nn = agg["select"]["n"], agg["no-select"]["n"]
        out_rows.append(_row(label, path, sn, agg["select"][col], nn, agg["no-select"][col]))
        if col == "det_snyk":
            out_rows.append(_skillscan_row())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"[saved] {OUT.relative_to(ROOT)}\n")

    print("=== select vs no-select (six scanners) - from bundled verdicts ===")
    print(f"{'Scanner':<24}{'sel n':>7}{'sel %':>9}{'nsl n':>8}{'nsl %':>9}{'Delta':>9}")
    print("-" * 66)
    for r in out_rows:
        print(f"{r['scanner']:<24}{r['detected_select']:>4}/{r['n_select']:<3}"
              f"{r['rate_select_pct']:>8}%{r['detected_noselect']:>4}/{r['n_noselect']:<3}"
              f"{r['rate_noselect_pct']:>7}%{r['delta_pp']:>8}pp")


if __name__ == "__main__":
    main()
