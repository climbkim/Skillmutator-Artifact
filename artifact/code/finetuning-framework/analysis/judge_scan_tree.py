"""judge_scan_tree.py -- batch-adjudicate a fine-tuned scanner's reports into a judge_summary.csv.

Joins three things:
  * the scenarios of one oracle/mode in the SkillMutator data tree
    (../skillmutator run.sh -> demo-data; meta.json + injected_content.md = ground truth),
  * the batch scan reports written by finetune/eval_infer_vllm.py
    (<scan-root>/mutations/<skill>/<run>/generate_skill/<category>/iter_<k>/report/<report-name>),
  * the evaluation judge (analysis/judge.py, the paper's Figure 7 prompt),
and writes one row per scenario:

    skill,category,cat_folder,iter,detected,confidence,reason

which is the input of analysis/rq3/scripts/build_tab_finetune.py (Figure 5) and
analysis/rq4/scripts/build_tab_phase_ablation.py (Table 6), and the format of the
paper's bundled judge files (claims/claim11_*/data/judge/, claims/claim04_*/data/judge/).

Scenario set and evaluation point follow Table 4 (skillmutator build_tab1_cross_matrix.py):
every attempted (skill, category) of the oracle/mode, judged at its last normal
iteration (n = 76 for gpt-5.4 select). A scenario with no normal iteration or no scan
report counts as not detected (paper rule) and is listed. A failed judge call is never
written as "not detected": a key/model error stops at once (exit 2); other failures are
listed after the remaining rows and the script exits 1 without writing the CSV.

Usage (from artifact/code/finetuning-framework):
    python analysis/judge_scan_tree.py \\
        --scan-root eval --data-root ../skillmutator/demo-data \\
        --oracle gpt-5.4 --mode select --judge-model gpt-5.4 \\
        --out-csv results_rq3/Qwen2.5-Coder-7B-Instruct_D3-prefill/judge_summary.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

FT_ROOT = Path(__file__).resolve().parent.parent
SM_ANALYSIS = FT_ROOT.parent / "skillmutator" / "analysis"
REPORT_NAME = "llm_report_finetune_qwen.md"   # eval_infer_vllm.py REPORT_FILENAME


def find_report(scan_root: Path, skill: str, ts: str, cat: str, it: int, name: str) -> Path | None:
    base = scan_root / "mutations" if (scan_root / "mutations").is_dir() else scan_root
    for run_dir in sorted((base / skill).glob(f"{ts}*")) if ts else []:
        p = run_dir / "generate_skill" / cat / f"iter_{it}" / "report" / name
        if p.is_file():
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scan-root", required=True, help="eval_infer_vllm.py --eval-dir (holds mutations/)")
    ap.add_argument("--data-root", required=True, help="SkillMutator data tree (e.g. ../skillmutator/demo-data)")
    ap.add_argument("--oracle", default="gpt-5.4")
    ap.add_argument("--mode", default="select", choices=["select", "no-select"])
    ap.add_argument("--judge-model", default="gpt-5.4")
    ap.add_argument("--report-name", default=REPORT_NAME, help="scan report file name in each iter_<k>/report/")
    ap.add_argument("--out-csv", required=True)
    args = ap.parse_args()

    os.environ["SKILLMUTATOR_DATA_ROOT"] = str(Path(args.data_root).resolve())
    sys.path.insert(0, str(SM_ANALYSIS))
    sys.path.insert(0, str(FT_ROOT))
    from skillmutator_utils.classifications import classify_all            # noqa: E402 (reads the env above)
    from skillmutator_utils.paths import MAX_ITER_BY_MODE, scenario_dir    # noqa: E402
    from skillmutator_utils.refusal import valid_scenarios                 # noqa: E402
    from analysis.judge import JudgeError, judge_call                      # noqa: E402
    from analysis.parsers import extract_scan_section                      # noqa: E402

    cls = classify_all(args.oracle, args.mode)
    scen = sorted(valid_scenarios(args.oracle, args.mode, criterion="all_attempted"))
    if not scen:
        print(f"[judge_scan_tree] no scenarios for {args.oracle}/{args.mode} under {args.data_root}", file=sys.stderr)
        return 2
    cap = MAX_ITER_BY_MODE[args.mode]
    rows, no_iter, no_report, failed = [], [], [], []
    for sk, cat in scen:
        lg = max((it for it in range(cap + 1) if cls.get((sk, cat, it)) == "normal"), default=None)
        if lg is None:
            no_iter.append(f"{sk}/{cat}")
            rows.append({"skill": sk, "category": "", "cat_folder": cat, "iter": "", "detected": False,
                         "confidence": "", "reason": "no normal iteration (counted as not detected)"})
            continue
        cell = scenario_dir(args.oracle, args.mode, sk, cat, lg)
        meta = json.loads((cell / "meta.json").read_text(encoding="utf-8")) if (cell / "meta.json").is_file() else {}
        label = meta.get("cat_label", cat.replace("_", " ").title())
        rep = find_report(Path(args.scan_root), sk, str(meta.get("ts", "")), cat, lg, args.report_name)
        if rep is None:
            no_report.append(f"{sk}/{cat}/iter_{lg}")
            rows.append({"skill": sk, "category": label, "cat_folder": cat, "iter": lg, "detected": False,
                         "confidence": "", "reason": "no scan report (counted as not detected)"})
            continue
        inj_p = cell / "injected_content.md"
        injected = inj_p.read_text(encoding="utf-8") if inj_p.is_file() else "(no injected_content)"
        if len(injected) > 1500:
            injected = injected[:1500] + "\n...[truncated]"
        try:
            j = judge_call(skill=sk, category=label, title=meta.get("scenario_title", ""),
                           disguise=meta.get("scenario_summary", ""), injected_snippet=injected,
                           scan_text=extract_scan_section(rep.read_text(encoding="utf-8", errors="replace")),
                           model=args.judge_model)
        except JudgeError as e:
            if e.fatal:
                print(f"[judge_scan_tree] error: {e}\n    Use a judge model this API key can access "
                      "(--judge-model); the paper uses gpt-5.4.", file=sys.stderr)
                return 2
            failed.append(f"{sk}/{cat}/iter_{lg}: {e}")
            continue
        rows.append({"skill": sk, "category": label, "cat_folder": cat, "iter": lg, "detected": j["detected"],
                     "confidence": j["confidence"], "reason": j["reason"]})
        print(f"    {sk}/{cat}/iter_{lg}: detected={j['detected']}")

    if failed:
        print(f"[judge_scan_tree] {len(failed)} judge call(s) failed; no CSV written. Re-run to retry:",
              file=sys.stderr)
        for f in failed:
            print(f"    {f}", file=sys.stderr)
        return 1
    out = Path(args.out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["skill", "category", "cat_folder", "iter", "detected", "confidence", "reason"])
        w.writeheader()
        w.writerows(rows)
    det = sum(1 for r in rows if r["detected"] is True)
    print(f"[judge_scan_tree] {args.oracle}/{args.mode}: {det}/{len(rows)} detected "
          f"({100 * det / len(rows):.2f}%) -> {out}")
    for name, lst in (("no normal iteration", no_iter), ("no scan report", no_report)):
        if lst:
            print(f"[judge_scan_tree] {len(lst)} scenario(s) with {name} (counted as not detected): "
                  + ", ".join(lst[:10]) + (" ..." if len(lst) > 10 else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
