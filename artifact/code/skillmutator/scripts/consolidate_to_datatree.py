"""consolidate_to_datatree.py -- convert SkillMutator pipeline output into the
canonical Skillmutator-data tree.

The mutation pipeline writes a per-run layout:

    {result_root}/{skill}/{ts}_{mode}/
        generate_skill/{cat_safe}/iter_{K}/skills/        <- mutated package
        generate_skill_iter{K}/{skill}_{ts}.json          <- node result

This script rewrites it into the canonical tree consumed by all downstream
analyses (skillmutator_utils.paths):

    Skillmutator-data/{oracle}/{mode}/{skill}/{cat_folder}/iter_{K}/
        mutated/             <- full mutated skill package (SKILL.md + files)
        meta.json            <- {oracle, mode, skill, cat_folder, cat_label,
                                 iter, ts, scenario_title, scenario_summary,
                                 classification}
        injected_content.md  <- attack ground truth (from the node JSON)

`classification` is the refusal class (normal / explicit_refusal /
silent_failure / partial_refusal) from skillmutator_utils.classifications.
classify_entry, the rule used for the paper data tree (Table 3). The
byte-identity check needs the original skills (--skills).

Scanner outputs (ss/, snyk/, llm/<scanner>/) are NOT produced here; they are
populated by the scan/judge step, which is a separate concern.

Usage:
    python scripts/consolidate_to_datatree.py \\
        --result-root ./demo-results \\
        --oracle gpt-4o-mini \\
        --data-root ./skillmutator-data \\
        --skills examples/skills/weather-cache
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "analysis"))
from skillmutator_utils.classifications import classify_entry  # noqa: E402

# --- canonical category folder/label maps (mirror skillmutator_utils.paths) ---
CAT_FOLDER_FROM_LABEL = {
    "Advertising Injection":     "advertising_injection",
    "Brand Hijacking":           "brand_hijacking",
    "Code Quality Degradation":  "code_quality_degradation",
    "Configuration Weakening":   "configuration_weakening",
    "Data Exfiltration":         "data_exfiltration",
    "Data Integrity Risks":      "data_integrity_risks",
    "Disruption & Interference": "disruption_interference",
    "False Attribution":         "false_attribution",
    "Information Gathering":      "information_gathering",
    "Over-engineering":          "over-engineering",
    "Persistence Control":       "persistence_control",
    "Privilege Escalation":      "privilege_escalation",
    "Supply Chain Attack":       "supply_chain_attack",
}
CAT_LABEL_FROM_FOLDER = {v: k for k, v in CAT_FOLDER_FROM_LABEL.items()}

# Run-dir naming: example_skill_mutation -> "{ts}_{mode}";
# run_skill_mutation called directly -> "{ts}" only.
_TS_MODE_RE = re.compile(r"^(\d{8}_\d{6})_(.+)$")
_TS_ONLY_RE = re.compile(r"^(\d{8}_\d{6})$")


def _safe_dirname(name: str) -> str:
    """Mirror skill_mutator.process.skill_mutation._to_safe_dirname."""
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s]+", "_", name)
    return name


def _canonical_mode(mode_suffix: str) -> str:
    """Map a run-dir mode suffix to a canonical tree mode.

    'select' / 'select_llm-detect'        -> 'select'
    'no-select' / 'no-select_llm-detect'  -> 'no-select'
    """
    return "no-select" if mode_suffix.startswith("no-select") else "select"


def _label_for(cat_folder: str) -> str:
    return CAT_LABEL_FROM_FOLDER.get(cat_folder, cat_folder.replace("_", " ").title())


def _node_json(node_dir: Path, skill: str, ts: str, run_name: str) -> Path | None:
    """Node JSONs are named `{skill}_{run_dir name}.json` (e.g.
    `pdf_20260914_233924_select_llm-detect.json`); older runs used
    `{skill}_{ts}.json`. Return whichever exists."""
    for name in (f"{skill}_{run_name}.json", f"{skill}_{ts}.json"):
        p = node_dir / name
        if p.is_file():
            return p
    return None


def _generated_entry(run_dir: Path, skill: str, ts: str, it: int,
                     cat_folder: str) -> dict | None:
    """The generate_skill node entry (one generated mutation) for this category."""
    node_json = _node_json(run_dir / f"generate_skill_iter{it}", skill, ts, run_dir.name)
    if node_json is None:
        return None
    try:
        data = json.loads(node_json.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, list):
        return None
    for entry in data:
        if isinstance(entry, dict) and _safe_dirname(entry.get("attack_category", "")) == cat_folder:
            return entry
    return None


def _load_injected_content(run_dir: Path, skill: str, ts: str, it: int,
                           cat_folder: str) -> str | None:
    """Build injected_content.md text from the generate_skill node JSON.

    The node JSON is a list of generated-skill dicts; each has an
    `attack_category` and `modified_files[].injected_content`.
    """
    entry = _generated_entry(run_dir, skill, ts, it, cat_folder)
    if entry is not None:
        parts: list[str] = []
        for mod in entry.get("modified_files", []):
            if not isinstance(mod, dict):
                continue
            rel = mod.get("relative_path", "?")
            inj = (mod.get("injected_content") or "").strip()
            if inj:
                parts.append(f"## {rel}\n\n{inj}")
        return "\n\n".join(parts) if parts else None
    return None


def _scenario_title(run_dir: Path, skill: str, ts: str,
                    cat_folder: str) -> str:
    """Best-effort scenario title from the generate_scenarios node JSON."""
    node_json = _node_json(run_dir / "generate_scenarios", skill, ts, run_dir.name)
    if node_json is None:
        return ""
    try:
        data = json.loads(node_json.read_text(encoding="utf-8"))
    except Exception:
        return ""
    items = data if isinstance(data, list) else data.get("attack_scenarios", [])
    for sc in items or []:
        if not isinstance(sc, dict):
            continue
        if _safe_dirname(sc.get("attack_category", "")) == cat_folder:
            return sc.get("scenario_title") or sc.get("title") or ""
    return ""


def _md5(p: Path) -> str | None:
    """Same digest as classify_entry's byte-identity check."""
    return hashlib.md5(p.read_bytes()).hexdigest()[:12] if p.is_file() else None


def consolidate(result_root: Path, oracle: str, data_root: Path,
                default_mode: str = "select", dry_run: bool = False,
                baseline_md5: dict[str, str] | None = None) -> dict:
    stats = {"copied": 0, "skipped": 0, "no_injected": 0, "errors": 0}
    classes: dict[str, int] = {}
    baseline_md5 = baseline_md5 or {}

    for skill_dir in sorted(p for p in result_root.iterdir() if p.is_dir()):
        skill = skill_dir.name
        for run_dir in sorted(p for p in skill_dir.iterdir() if p.is_dir()):
            m = _TS_MODE_RE.match(run_dir.name)
            if m:
                ts, mode = m.group(1), _canonical_mode(m.group(2))
            elif _TS_ONLY_RE.match(run_dir.name):
                # No mode suffix in the dir name -> fall back to --mode.
                ts, mode = run_dir.name, default_mode
            else:
                continue

            gs_root = run_dir / "generate_skill"
            if not gs_root.is_dir():
                continue

            for cat_dir in sorted(p for p in gs_root.iterdir() if p.is_dir()):
                cat_folder = cat_dir.name  # already _to_safe_dirname output
                for iter_dir in sorted(p for p in cat_dir.iterdir() if p.is_dir()):
                    if not iter_dir.name.startswith("iter_"):
                        continue
                    try:
                        it = int(iter_dir.name.split("_")[1])
                    except (IndexError, ValueError):
                        continue

                    skills_src = iter_dir / "skills"
                    if not (skills_src / "SKILL.md").is_file():
                        continue

                    dst_iter = (data_root / oracle / mode / skill
                                / cat_folder / f"iter_{it}")
                    dst_mutated = dst_iter / "mutated"

                    if (dst_mutated / "SKILL.md").is_file():
                        stats["skipped"] += 1
                        continue

                    if dry_run:
                        print(f"[dry] {skills_src}  ->  {dst_mutated}")
                        stats["copied"] += 1
                        continue

                    try:
                        dst_mutated.mkdir(parents=True, exist_ok=True)
                        for item in skills_src.iterdir():
                            target = dst_mutated / item.name
                            if item.is_dir():
                                shutil.copytree(item, target, dirs_exist_ok=True)
                            else:
                                shutil.copy2(item, target)

                        # meta.json
                        entry = _generated_entry(run_dir, skill, ts, it, cat_folder)
                        cls = (classify_entry(entry, baseline_md5.get(skill),
                                              skills_src / "SKILL.md")
                               if entry is not None else "missing")
                        classes[cls] = classes.get(cls, 0) + 1
                        meta = {
                            "oracle": oracle,
                            "mode": mode,
                            "skill": skill,
                            "cat_folder": cat_folder,
                            "cat_label": _label_for(cat_folder),
                            "iter": it,
                            "ts": ts,
                            "scenario_title": _scenario_title(
                                run_dir, skill, ts, cat_folder),
                            # mutation summary = the disguise framing the
                            # evaluation judge receives (judge.py)
                            "scenario_summary": (entry or {}).get("summary", ""),
                            "classification": cls,
                        }
                        (dst_iter / "meta.json").write_text(
                            json.dumps(meta, ensure_ascii=False, indent=2),
                            encoding="utf-8")

                        # injected_content.md
                        injected = _load_injected_content(
                            run_dir, skill, ts, it, cat_folder)
                        if injected:
                            (dst_iter / "injected_content.md").write_text(
                                injected, encoding="utf-8")
                        else:
                            stats["no_injected"] += 1

                        stats["copied"] += 1
                    except Exception as e:  # noqa: BLE001
                        stats["errors"] += 1
                        print(f"[error] {skills_src}: {e}", file=sys.stderr)

    stats["classes"] = classes
    return stats


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--result-root", required=True,
                    help="SkillMutator pipeline output root.")
    ap.add_argument("--oracle", required=True,
                    help="Oracle name for the tree (e.g. claude-opus-4-7).")
    ap.add_argument("--data-root", default="skillmutator-data",
                    help="Canonical tree root (default: ./skillmutator-data).")
    ap.add_argument("--mode", default="select", choices=["select", "no-select"],
                    help="Fallback mode for run dirs with no '_{mode}' suffix "
                         "(run_skill_mutation direct output). Default: select.")
    ap.add_argument("--dry-run", action="store_true",
                    help="List planned copies without writing.")
    ap.add_argument("--skills", nargs="*", default=[],
                    help="Original (unmutated) skill folders, for the "
                         "classification's SKILL.md byte-identity check.")
    args = ap.parse_args()

    result_root = Path(args.result_root)
    if not result_root.is_dir():
        sys.exit(f"[error] result-root not found: {result_root}")
    baseline_md5 = {Path(s).name: _md5(Path(s) / "SKILL.md") for s in args.skills}
    baseline_md5 = {k: v for k, v in baseline_md5.items() if v}

    print(f"[consolidate] result-root: {result_root}")
    print(f"[consolidate] oracle     : {args.oracle}")
    print(f"[consolidate] data-root  : {args.data_root}")
    print(f"[consolidate] dry-run    : {args.dry_run}\n")

    stats = consolidate(result_root, args.oracle, Path(args.data_root),
                        default_mode=args.mode, dry_run=args.dry_run,
                        baseline_md5=baseline_md5)

    print(f"\n[done] copied={stats['copied']}  skipped(existing)={stats['skipped']}"
          f"  no_injected_content={stats['no_injected']}  errors={stats['errors']}")
    if stats["classes"]:
        print("[classification] " + "  ".join(
            f"{k}={v}" for k, v in sorted(stats["classes"].items())))
    missing = sorted({p.name for p in result_root.iterdir() if p.is_dir()} - set(baseline_md5))
    if missing and not args.dry_run:
        print(f"[note] no original skill given for {', '.join(missing)} (--skills): "
              "byte-identity check skipped for these cells.")
    if stats["no_injected"]:
        print("[note] scenarios with no injected_content.md: the generate_skill "
              "node JSON was missing or had no injected_content for that category.")
    print("[note] scanner outputs (ss/, snyk/, llm/) are populated by the "
          "separate scan/judge step, not by this script.")


if __name__ == "__main__":
    main()
