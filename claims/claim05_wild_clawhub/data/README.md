# Table 7 — In-the-Wild ClawHub Evaluation (Finding 7)

## (1) Paper location

- **Paper location**: Table 7, §6.5 Further Analyses (Finding 7)
- **Caption**: "In-the-wild ClawHub evaluation ($n{=}200$, 100 `clean` +
  100 `suspicious` balanced across four severity tiers, 25 each)."

## (2) PAPER_TARGET_VALUES

See [PAPER_CITED_VALUES.md](PAPER_CITED_VALUES.md).

Summary:

| Stratum | Accuracy (%) |
|---|---|
| `clean` | 92.0% (92/100) |
| `suspicious / LOW` | 60.0% (15/25) |
| `suspicious / MEDIUM` | 68.0% (17/25) |
| `suspicious / HIGH` | 84.0% (21/25) |
| `suspicious / CRITICAL` | 80.0% (20/25) |

Aggregate: **Accuracy=82.5% (165/200)**, **FPR=8.0% (8/100)**.

## (3) Data source

200 skills from the ClawHub marketplace crawl:

- **suspicious (100 skills)** — stratified sample of 25 each across Skillspector severity LOW/MED/HIGH/CRIT
- **clean (100 skills)** — original 25 + 75 additional from the ClawHub-LLM `verdict=benign` pool
  (auto-classified clean candidates + manually reviewed ambiguous cases) sample

Scanner: fine-tuned adapter (Qwen2.5-Coder-7B-Instruct + LoRA r=64, α=128, 5 epochs),
Forced Prefix Pre-filling `## Phase 4: Category Mapping`, served with vLLM (paper scans: vLLM 0.21.0, A100 80GB),
concurrency=1, temperature=0, max_tokens=2048.

The raw scanner-output trees (`scan_out_clean/`, `scan_out_suspicious/`) contain
the full skill contents crawled from ClawHub and are large; they are kept outside
the bundle (available from the authors on request — see `ETHICS.md`). The
bundle ships only the per-skill verdicts needed to recompute the table.

### Derived files (derived/) — bundled
- `_judge_per_skill.csv` — per-skill verdict for all 200 skills (DETECTED/PARTIAL/MISSED/CORRECT_PASS/FALSE_ALARM);
  `first_run_verdict` is filled for the 12 re-scanned suspicious skills (see Caveats)
- `_judge_verdicts_v2.jsonl` — judge verdict stream (latest)

### Scripts (scripts/) — bundled
- `verify_paper_match.py` — recompute per-stratum accuracy + aggregate and compare to paper
- `judge_spec.md` — judge protocol spec (per-skill verdict labels)
- `RUNBOOK.md` — vLLM remote scan runbook (vast.ai A100), for regenerating scanner output

## (4) Reproduction commands

```bash
cd claim05_wild_clawhub
bash run.sh
#   → verify_paper_match.py: per-stratum accuracy from the 200-row per-skill CSV +
#     recompute Aggregate Accuracy(82.5%) / FPR(8.0%), compare against PAPER_CITED → ALL MATCH
```

Reproducible on CPU alone (uses bundled per-skill verdicts; rerunning the scanner requires vLLM +
fine-tuned adapter + GPU — see `scripts/RUNBOOK.md`).

## (5) Dependencies

- Fine-tuned Qwen2.5-Coder-7B adapter — hosted on Hugging Face (huggingface.co/climbkim/skillmutator-scanner-adapters, revision `a44e1da`)
- `artifact/data/paper_shared/base_models/MANIFEST.md` — Qwen2.5-Coder-7B-Instruct HF link + vLLM setup

## (6) Caveats — important methodological detail

- **Accuracy framing**: per-stratum "Accuracy (%)" and the aggregate over n=200.
  clean accuracy = not-a-false-alarm rate; suspicious accuracy = lenient
  (DETECTED + PARTIAL). Aggregate Accuracy = correct / 200 = 165/200 = 82.5%;
  FPR = FALSE_ALARM / 100 clean = 8/100 = 8.0%.
- **Re-scanned suspicious skills**: 12 suspicious skills that were MISSED because their first-run outputs were truncated or looped
  (vLLM concurrency 4) were re-scanned with concurrency 1; `_judge_per_skill.csv` holds the
  re-scanned verdicts (8 of 12 changed; first-run verdicts in `first_run_verdict`).
- **Lenient aggregation**: strict (DETECTED only) on the suspicious side is lower
  and not used in the paper. PARTIAL = "relevant behavior surfaced, often in
  Uncategorized" — see `scripts/judge_spec.md`.
- **Clean-100 expansion**: the clean stratum was expanded from 25 to 100 (75
  additional auto-classified candidates, ambiguous cases resolved by manual
  review); 8 of the 100 are unsupported false alarms.
- **clean/suspicious slug name collision**: 2 marketplace slug strings
  (`agentic-email-skill`, `agentic-invoice-skill`) appear in both samples, but
  they are *different* skills sharing a slug name (different content/version:
  clean = v1.0.9 / v1.0.10, suspicious = v1.0.1 for both; the manifest row in
  `artifact/data/clawhub/clawhub_skills.csv` lists the clean version) —
  the n=200 set is 200 distinct skills. The two sides are scored independently, so
  `verify_paper_match.py` reads the CSV as a 200-row list (not a slug-keyed dict).
- **ClawHub crawl ethics**: skills crawled from the public ClawHub catalog.
  ClawHub's auto-removed `malicious` tier is excluded by design (not accessible to
  public), so this measures transfer to borderline policy-violation cases, not
  overt malware. See paper Finding 7 body.

## (7) Verification status

✅ **Automated** — `scripts/verify_paper_match.py` recomputes per-stratum accuracy
(92.0 / 60.0 / 68.0 / 84.0 / 80.0) and the aggregate (Accuracy 82.5%, FPR 8.0%)
from the bundled 200-row per-skill CSV and confirms `ALL MATCH` against the paper.
