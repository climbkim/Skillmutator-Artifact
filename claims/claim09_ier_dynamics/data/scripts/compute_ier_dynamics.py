# -*- coding: utf-8 -*-
"""Figure 4 — IER per-iteration detection rates.

For each GPT oracle (select mode), every (skill, category) scenario is followed
across refinement iterations 0-4. The denominator is the evaluable set: the
scenarios with at least one scanned refusal-free mutation (n = 48 / 63 / 76, the
Table 4 sets). At iteration k a scenario uses the verdicts of its latest
refusal-free iteration j <= k (meta.json classification == "normal"), the
refusal handling of the paper (§6.1). A scenario with no refusal-free mutation
yet, or without a verdict there, counts as not detected, so n is the same at
every iteration. Rates are aggregated per (oracle, iter, scanner) for
skill-security-scan (ss), Snyk Agent Scan (snyk) and the oracle's own LLM
scanner (llm). A scanner with no verdict at all for an oracle is left out.

Two inputs, one aggregation:
  --tree DIR     read a SkillMutator data tree (the layout written by the live
                 pipeline, i.e. $SKILLMUTATOR_DATA_ROOT):
                   <oracle>/select/<skill>/<category>/iter_K/meta.json
                   .../iter_K/{ss,snyk}/verdict.json
                   .../iter_K/llm/<oracle>-self/verdict.json
  (default)      read raw/ier_verdicts.csv, the masked export of that tree that
                 ships with this artifact (ids, refusal class and detected flags
                 only; no scanner text, judge reasons or injected content).

  --export CSV   with --tree, also write the masked export (how
                 raw/ier_verdicts.csv was produced).
  --out CSV      where to write the rate table
                 (default: ../results/derived/ier_dynamics.csv).
"""
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1]                 # claims/claim09_ier_dynamics/data
VERDICTS = DATA / "raw" / "ier_verdicts.csv"
DEFAULT_OUT = DATA.parent / "results" / "derived" / "ier_dynamics.csv"

ORACLES = ["gpt-4o-mini", "gpt-5.4-mini", "gpt-5.4"]
LLM_SELF = {o: f"{o}-self" for o in ORACLES}
ITERS = [0, 1, 2, 3, 4]
SCANNERS = ["ss", "snyk", "llm"]
FIELDS = ["oracle", "skill", "category", "iter", "classification"] + SCANNERS


def _detected(path: Path) -> str:
    """'True' / 'False', or '' when the verdict is missing or unreadable."""
    if not path.exists():
        return ""
    try:
        return "True" if bool(json.loads(path.read_text(encoding="utf-8")).get("detected")) else "False"
    except Exception:
        return ""


def _classification(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("classification") or ""
    except Exception:
        return ""


def rows_from_tree(root: Path) -> list[dict]:
    rows = []
    for oracle in ORACLES:
        base = root / oracle / "select"
        if not base.is_dir():
            continue
        for skill in sorted(p for p in base.iterdir() if p.is_dir()):
            for cat in sorted(p for p in skill.iterdir() if p.is_dir()):
                for it in ITERS:
                    d = cat / f"iter_{it}"
                    if not d.is_dir():
                        continue
                    rows.append({
                        "oracle": oracle, "skill": skill.name, "category": cat.name,
                        "iter": str(it),
                        "classification": _classification(d / "meta.json"),
                        "ss": _detected(d / "ss" / "verdict.json"),
                        "snyk": _detected(d / "snyk" / "verdict.json"),
                        "llm": _detected(d / "llm" / LLM_SELF[oracle] / "verdict.json"),
                    })
    return rows


def rows_from_csv(path: Path = VERDICTS) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _normal(e) -> bool:
    return e is not None and e["classification"] == "normal"


def aggregate_ier(rows: list[dict]) -> dict:
    """{(oracle, iter, scanner): (n, detected)}, fixed evaluable-set denominator."""
    by_scenario = {}
    for r in rows:
        by_scenario.setdefault((r["oracle"], r["skill"], r["category"]), {})[int(r["iter"])] = r
    ran = {(r["oracle"], sc) for r in rows for sc in SCANNERS if r[sc] != ""}
    agg = {}
    for (oracle, _, _), iters in by_scenario.items():
        # evaluable: at least one refusal-free mutation that was scanned
        if not any(_normal(e) and any(e[sc] != "" for sc in SCANNERS) for e in iters.values()):
            continue
        last_normal = None
        for it in ITERS:
            if _normal(iters.get(it)):
                last_normal = it
            for sc in SCANNERS:
                if (oracle, sc) not in ran:
                    continue
                hit = last_normal is not None and iters[last_normal][sc] == "True"
                n, d = agg.get((oracle, it, sc), (0, 0))
                agg[(oracle, it, sc)] = (n + 1, d + hit)
    return agg


def write_rates(agg: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["oracle", "iter", "scanner", "n", "detected", "rate_pct"])
        for (oracle, it, sc), (n, d) in sorted(agg.items()):
            w.writerow([oracle, it, sc, n, d, f"{100.0 * d / n:.2f}" if n else "0.00"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tree", type=Path, help="SkillMutator data tree ($SKILLMUTATOR_DATA_ROOT)")
    ap.add_argument("--export", type=Path, help="with --tree: write the masked verdict CSV here")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="rate table output")
    a = ap.parse_args()

    if a.tree:
        rows = rows_from_tree(a.tree)
        if not rows:
            print(f"[error] no <oracle>/select/... iterations under {a.tree}", file=sys.stderr)
            return 1
        if a.export:
            a.export.parent.mkdir(parents=True, exist_ok=True)
            with a.export.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
            print(f"wrote {a.export} ({len(rows)} rows)")
    elif a.export:
        ap.error("--export needs --tree")
    else:
        rows = rows_from_csv()

    agg = aggregate_ier(rows)
    write_rates(agg, a.out)
    print(f"wrote {a.out}")
    print(f"\n{'oracle':<14}{'scanner':<8}" + "".join(f"{'i' + str(i):>8}" for i in ITERS))
    for oracle in ORACLES:
        for sc in SCANNERS:
            cells = [agg.get((oracle, it, sc)) for it in ITERS]
            print(f"{oracle:<14}{sc:<8}" + "".join(f"{100.0 * d / n:>7.1f}%" if c and (n := c[0]) and (d := c[1]) is not None else f"{'-':>8}" for c in cells))
    return 0


if __name__ == "__main__":
    sys.exit(main())
