# PAPER_CITED_VALUES — `tab:wild_eval` (Finding 7)

Paper canonical values from `Skillmutator.tex` (label `\label{tab:wild_eval}`).

## Header

- Caption: "In-the-wild ClawHub evaluation (n=200, 100 `clean` + 100 `suspicious`
  balanced across four severity tiers, 25 each)."
- Dataset: 200 real skills crawled from the ClawHub marketplace
  - 100 `clean` skills (single stratum)
  - 100 `suspicious` skills, 25 each across LOW / MED / HIGH / CRIT
    (severity graded by Skillspector; ClawHub removes the most severe
    `malicious` tier from its public catalog, so this measures transfer to
    borderline policy-violation cases, not overt malware)
- Scanner: Qwen2.5-Coder-7B-Instruct + LoRA (fine-tuned adapter), vLLM 0.7.3
  (post-rerun), concurrency=1

## Per-stratum accuracy

| Stratum | Accuracy (%) | Raw count |
|---|---|---|
| `clean` | **92.0%** | 92/100 |
| `suspicious / LOW` | 60.0% | 15/25 |
| `suspicious / MEDIUM` | 68.0% | 17/25 |
| `suspicious / HIGH` | **84.0%** | 21/25 |
| `suspicious / CRITICAL` | 80.0% | 20/25 |

## Aggregate

| Metric | Value |
|---|---|
| Accuracy (all 200) | **82.5%** (165/200) |
| FPR (false positive rate, on 100 clean) | **8.0%** (8/100) |

## Verdict / accuracy definition

A per-skill verdict is one of {DETECTED, PARTIAL, MISSED, CORRECT_PASS, FALSE_ALARM}.
A verdict counts as **correct** when:
- On `suspicious` skills: lenient D+P aggregation — DETECTED or PARTIAL (PARTIAL =
  scanner surfaces the right behavior in Uncategorized), supported by a ClawHub
  auditor finding-citation match.
- On `clean` skills: NOT a FALSE_ALARM (LLM agreement / no flag, or Skillspector
  confirmation). Aggregate accuracy = correct / 200; FPR = FALSE_ALARM / 100 clean.

## Methodology caveat

- The suspicious side reflects the **rerun12** measurement (vLLM 0.7.3,
  concurrency=1), which recovered originally truncated outputs from the c=4 run.
- The clean side is the 100-skill sample (original 25 + 75 additional
  auto-classified clean candidates, with the ambiguous cases resolved by manual
  review); 8 of the 100 clean skills are unsupported false alarms.
- Judge protocol: per-skill verdict from the scanner output; see `scripts/judge_spec.md`.

## Cited in paper body (Finding 7)

- "200 real skills crawled from the ClawHub marketplace"
- "100 skills are labeled `clean` and 100 are catalog-visible `suspicious`
  balanced across LOW, MED, HIGH, and CRIT severity tiers"
- "detects more HIGH&CRIT cases than LOW&MED cases"
- "raises only eight unsupported alarms among the 100 `clean` skills"

## Note — clean/suspicious slug name collision

Two marketplace slug strings (`agentic-email-skill`, `agentic-invoice-skill`)
appear in both the clean-100 and suspicious-100 samples, but they are *different*
skills that merely share a slug name (different SKILL.md content and version).
The n=200 set is therefore 200 distinct skills. The two sides are scored
independently (each over its own 100 rows), so `verify_paper_match.py` reads the
per-skill CSV as a 200-row list rather than a slug-keyed dict (which would
collapse the two name collisions and undercount to 198).
