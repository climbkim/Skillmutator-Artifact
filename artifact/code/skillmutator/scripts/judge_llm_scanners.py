"""judge_llm_scanners.py - evaluation step for the LLM-scanner rows of the paper
floats (Table 4, Table 5, Figure 4).

For every cell of one oracle/mode in the canonical data tree:

  1. self scan   : copy the oracle's own LLM-scanner report written by the
                   mutation run (<result-root>/<skill>/<ts>_*/generate_skill/<cat>/
                   iter_<N>/logs/llm-scanner/*.md) to llm/<oracle>-self/scan.md.
  2. cross scans : with --cross-scan, scan the scenario's final refusal-free
                   iteration with every other LLM scanner model and store the
                   reports as llm/<model>/scan.md (Table 4 cross cells).
  3. judge       : adjudicate every llm/<scanner>/scan.md with the evaluation
                   judge (--judge-model; the paper uses gpt-5.4 with the prompt of
                   Figure 7, analysis/skillmutator_utils/judge.py) and write
                   verdict.json. This replaces the refinement loop's in-run LLM
                   decision for the LLM rows, as in the paper's evaluation.

A failed judge call or cross scan leaves the cell without a verdict and makes
the script exit non-zero (after the other cells), so run.sh stops before the
tables are built. A key or model-access error stops at the first call.

Usage (run.sh calls this after consolidate + populate_verdicts):
    python scripts/judge_llm_scanners.py --result-root ./demo-results \\
        --oracle gpt-5.4 --mode select --data-root ./demo-data \\
        --judge-model gpt-5.4 [--cross-scan]
"""
from __future__ import annotations
import argparse, json, os, shlex, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LLM_SCANNER = REPO_ROOT / "src" / "skill_mutator" / "scanners" / "llm_scanner" / "scanner.py"
LLM_MODELS = ["gpt-4o-mini", "gpt-5.4-mini", "gpt-5.4"]


def _newest_md(d: Path) -> Path | None:
    mds = sorted(d.glob("*.md"), key=lambda p: p.stat().st_mtime) if d.is_dir() else []
    return mds[-1] if mds else None


def _self_report(result_root: Path, skill: str, ts: str, cat: str, it: int) -> Path | None:
    for run_dir in sorted((result_root / skill).glob(f"{ts}*")):
        md = _newest_md(run_dir / "generate_skill" / cat / f"iter_{it}" / "logs" / "llm-scanner")
        if md:
            return md
    return None


def _scan(skill_dir: Path, model: str, provider: str) -> str | None:
    """Run the LLM scanner on one skill folder; return the report text."""
    with tempfile.TemporaryDirectory() as out:
        r = subprocess.run(
            [sys.executable, str(LLM_SCANNER), "-p", provider, "-s", str(skill_dir),
             "-m", model, "-o", out],
            capture_output=True, text=True, encoding="utf-8", cwd=str(REPO_ROOT),
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        md = _newest_md(Path(out))
        if r.returncode != 0 or md is None:
            print(f"    [warn] {model} scan failed on {skill_dir}: {(r.stderr or r.stdout)[-200:]}")
            return None
        return md.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--result-root", required=True)
    ap.add_argument("--oracle", required=True)
    ap.add_argument("--mode", default="select")
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--judge-model", default="gpt-5.4")
    ap.add_argument("--cross-scan", action="store_true",
                    help="also scan each scenario's final iteration with the other LLM scanners")
    ap.add_argument("--provider", default="openai")
    args = ap.parse_args()

    os.environ["SKILLMUTATOR_DATA_ROOT"] = str(Path(args.data_root).resolve())
    sys.path.insert(0, str(REPO_ROOT / "analysis"))
    from skillmutator_utils.judge import JudgeError, judge_scanner_output  # noqa: E402  (reads the env above)
    from skillmutator_utils.paths import MAX_ITER_BY_MODE  # noqa: E402

    result_root = Path(args.result_root)
    base = Path(args.data_root) / args.oracle / args.mode
    if not base.is_dir():
        print(f"[judge_llm_scanners] no cells under {base}")
        return 0
    self_sub = f"llm/{args.oracle}-self"
    cap = MAX_ITER_BY_MODE[args.mode]
    cross_models = [m for m in LLM_MODELS if m != args.oracle] if args.cross_scan else []
    n_self = n_cross = n_judged = 0
    failed_scan: list[str] = []
    failed_judge: list[str] = []

    for skill_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        for cat_dir in sorted(p for p in skill_dir.iterdir() if p.is_dir()):
            iters = sorted(int(p.name.split("_")[1]) for p in cat_dir.glob("iter_*") if p.is_dir())
            final_it = None
            for it in iters:
                cell = cat_dir / f"iter_{it}"
                meta = json.loads((cell / "meta.json").read_text(encoding="utf-8")) if (cell / "meta.json").is_file() else {}
                if meta.get("classification", "normal") == "normal" and it <= cap:
                    final_it = it
                # 1. self report
                md = _self_report(result_root, skill_dir.name, str(meta.get("ts", "")), cat_dir.name, it)
                if md:
                    dst = cell / self_sub / "scan.md"
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(md, dst)
                    n_self += 1
            # 2. cross scans on the final refusal-free iteration
            if final_it is not None and cross_models:
                cell = cat_dir / f"iter_{final_it}"
                for m in cross_models:
                    dst = cell / "llm" / m / "scan.md"
                    if dst.is_file():
                        continue
                    text = _scan(cell / "mutated", m, args.provider)
                    if text:
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        dst.write_text(text, encoding="utf-8")
                        n_cross += 1
                    else:
                        failed_scan.append(f"{skill_dir.name}/{cat_dir.name}/iter_{final_it} llm/{m}")
            # 3. judge every LLM report of this scenario
            for it in iters:
                for scan_md in sorted((cat_dir / f"iter_{it}" / "llm").glob("*/scan.md")):
                    sub = f"llm/{scan_md.parent.name}"
                    slot = f"{skill_dir.name}/{cat_dir.name}/iter_{it} {sub}"
                    try:
                        j = judge_scanner_output(args.oracle, args.mode, skill_dir.name, cat_dir.name,
                                                 it, sub, force=True, model=args.judge_model)
                    except JudgeError as e:
                        if e.fatal:
                            print(f"[judge_llm_scanners] error: {e}", file=sys.stderr)
                            print("    The evaluation judge cannot run with this API key. Use a judge model "
                                  "the key can access (--judge-model); the paper uses gpt-5.4.", file=sys.stderr)
                            return 2
                        failed_judge.append(slot)
                        print(f"    {slot}: JUDGE FAILED ({e})")
                        continue
                    n_judged += 1
                    print(f"    {slot}: detected={j['detected']}")

    print(f"[judge_llm_scanners] oracle={args.oracle} mode={args.mode} judge={args.judge_model}: "
          f"self reports={n_self}, cross scans={n_cross}, judged={n_judged}")
    if failed_scan or failed_judge:
        print(f"[judge_llm_scanners] incomplete: {len(failed_scan)} cross scan(s) and "
              f"{len(failed_judge)} judge call(s) failed. These cells have no verdict:", file=sys.stderr)
        for f in failed_scan:
            print(f"    scan  {f}", file=sys.stderr)
        for f in failed_judge:
            print(f"    judge {f}", file=sys.stderr)
        print("    Re-run this step alone (from artifact/code/skillmutator; finished cross scans are kept), "
              "then the [5/5] build commands of run.sh:", file=sys.stderr)
        print("    python " + " ".join(shlex.quote(a) for a in sys.argv), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
