"""build_table3.py — aggregate Table 4: 9 scanners x 3 GPT oracles cross-matrix.

Rebuilds the cross-scanner aggregate from the shipped per-source CSVs and checks
it against derived/table3_aggregate.csv (the file run.sh verifies). The result is
written to ../results/derived/table3_aggregate.csv; the shipped file is not
overwritten.

Sources (all under derived/):
  - skillscan_<oracle>_perscenario.csv : skill-security-scan (any new finding vs.
    the unmodified skill) and Snyk Agent Scan (new HIGH finding) per scenario
  - skillscan_cross_summary.md         : SkillScan API (>= MEDIUM) per oracle
  - tab1_cross_matrix.csv              : GPT-{4o-mini,5.4-mini,5.4} detected counts
    (its n=51 for gpt-4o-mini is the all-attempted count; the paper uses the
    evaluable n=48, see EVALUABLE_N)
  - pi_defense_gpt_oracles.csv         : LLM-Guard / PIGuard / DataSentinel on the
    injected snippet
"""
from __future__ import annotations
import csv, re, sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]                 # claims/claim02_*/data
DERIVED = ROOT / "derived"
OUT = ROOT.parent / "results" / "derived" / "table3_aggregate.csv"

ORACLES = ["gpt-4o-mini", "gpt-5.4-mini", "gpt-5.4"]
# Evaluable mutations per oracle (paper n=48/63/76; 3 GPT-4o-mini scenarios have
# no valid mutated package after refusal handling).
EVALUABLE_N = {"gpt-4o-mini": 48, "gpt-5.4-mini": 63, "gpt-5.4": 76}


def load_csv(path: Path) -> list[dict]:
    return list(csv.DictReader(path.open(encoding="utf-8"))) if path.is_file() else []


def ss_snyk(oracle: str) -> tuple[int, int, int]:
    """(skill-security-scan detected, Snyk detected, n) from the per-scenario CSV."""
    rows = load_csv(DERIVED / f"skillscan_{oracle}_perscenario.csv")
    ss_det = sum(1 for r in rows if int(r["ss_total_mutated"]) > int(r["ss_total_baseline"]))
    snyk_det = sum(1 for r in rows if int(r.get("snyk_new_HIGH", 0)) > 0)
    return ss_det, snyk_det, len(rows)


def skillscan(content: str) -> dict[str, tuple[int, int]]:
    """Per-oracle >= MEDIUM count from the skillscan_cross_summary.md table row
    `| gpt-4o-mini | ... | 0/48 (0.00%) |`."""
    out = {}
    for line in content.splitlines():
        m = re.match(r"\|\s*(\S+)\s*\|.*?\|\s*(\d+)/(\d+)\s*\(([\d.]+)%\)\s*\|\s*$", line)
        if m and m.group(1) in ORACLES:
            out[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    return out


def llm_scanner(scanner_key: str) -> dict[str, tuple[int, int]]:
    out = {}
    for r in load_csv(DERIVED / "tab1_cross_matrix.csv"):
        if r["scanner_key"] == scanner_key:
            for o in ORACLES:
                out[o] = (int(r[f"{o}_det"]), EVALUABLE_N[o])
    return out


def pi_detector(detector: str) -> dict[str, tuple[int, int]]:
    """Detected on the injected snippet (inject_det) over the evaluable n."""
    out = {}
    for r in load_csv(DERIVED / "pi_defense_gpt_oracles.csv"):
        if r["detector"] == detector and r["oracle"] in EVALUABLE_N:
            out[r["oracle"]] = (int(r["inject_det"]), EVALUABLE_N[r["oracle"]])
    return out


def main() -> int:
    ss_data, snyk_data = {}, {}
    for o in ORACLES:
        ss_det, snyk_det, n = ss_snyk(o)
        ss_data[o], snyk_data[o] = (ss_det, n), (snyk_det, n)
    sscan_data = skillscan((DERIVED / "skillscan_cross_summary.md").read_text(encoding="utf-8"))

    def make_row(label: str, data: dict) -> dict:
        row = {"scanner": label}
        for o in ORACLES:
            d, n = data.get(o, (0, 0))
            row[f"{o}_det"], row[f"{o}_n"], row[f"{o}_rate"] = d, n, f"{100.0 * d / max(n, 1):.2f}"
        return row

    rows_out = [
        make_row("skill-security-scan", ss_data),
        make_row("Snyk Agent Scan", snyk_data),
        make_row("SkillScan API", sscan_data),
        make_row("LLM-Guard", pi_detector("llmguard")),
        make_row("PIGuard", pi_detector("piguard")),
        make_row("DataSentinel", pi_detector("datasentinel")),
        make_row("GPT-4o-mini", llm_scanner("gpt-4o-mini")),
        make_row("GPT-5.4-mini", llm_scanner("gpt-5.4-mini")),
        make_row("GPT-5.4", llm_scanner("gpt-5.4")),
    ]

    print(f"{'Scanner':<22}" + "".join(f"{o:>22}" for o in ORACLES))
    print("-" * 88)
    for r in rows_out:
        print(f"{r['scanner']:<22}" + "".join(
            f"{r[f'{o}_rate'] + '% (' + str(r[f'{o}_det']) + '/' + str(r[f'{o}_n']) + ')':>22}" for o in ORACLES))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows_out)
    print(f"\n[written] results/derived/{OUT.name}")

    rebuilt = [{k: str(v) for k, v in r.items()} for r in rows_out]
    same = rebuilt == load_csv(DERIVED / "table3_aggregate.csv")
    print(f"[{'OK ' if same else 'XX '}] rebuilt aggregate "
          f"{'matches' if same else 'DIFFERS from'} derived/table3_aggregate.csv")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
