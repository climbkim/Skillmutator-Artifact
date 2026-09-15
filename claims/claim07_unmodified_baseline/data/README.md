# Table X — Baseline findings on 17 unmodified Anthropic skills

## (1) Paper location

- **LaTeX label**: `\label{tab:baseline_aggregate}`
- **Caption**: "Per-scanner finding counts on the 17 unmodified Anthropic skills.
  The Skills column reports the count and fraction of skills with at least one
  finding."

## (2) Paper-cited values

| Scanner | Skills | Mean | Max | Total |
|---|---|---|---|---|
| **Rule-based / Commercial** | | | | |
| `skill-security-scan` | 9/17 | 18.2 | 190 | 309 |
| Snyk Agent Scan | 4/17 | 0.4 | 2 | 6 |
| SkillScan (upload API) | 5/17 | 0.4 | 2 | 6 |
| **Proprietary LLM** | | | | |
| GPT-4o-mini | 17/17 | 7.1 | 9 | 121 |
| GPT-5.4-mini | 17/17 | 6.4 | 10 | 109 |
| GPT-5.4 | 17/17 | 9.6 | 14 | 163 |
| **Fine-tuned student (ours)** | | | | |
| Qwen2.5-Coder-7B fine-tuned (prefill) | 17/17 | 7.4 | 22 | 126 |

## (3) Bundled data

Aggregate/verdict-level CSVs only (raw scanner trees are not redistributed):

- `derived/baseline_summary_manual.csv` — canonical per-scanner summary (verification source)
- `derived/baseline_summary.csv` — parser output (informational; shows where manual correction was applied)
- `derived/skillscan_unmodified_summary.csv` — SkillScan per-skill finding counts
- `derived/baseline_findings.csv`, `derived/manual_findings.csv` — per-finding detail

## (4) Reproduce

```bash
./run.sh    # runs scripts/verify_paper_match.py against the bundled summaries
```

CPU only; no API key or GPU needed.

## (5) Dependencies

- No external OpenAI API calls (all verdicts already collected).
- No adapter weights needed (verification parses the bundled summaries only).

## (6) Notes

1. **GPT-scanner counting variant** — `verify_paper_match.py` checks the
   manually-verified summary (`baseline_summary_manual.csv`) against the paper's
   121/109/163 totals and reports the parser-vs-manual delta for transparency.
2. **Fine-tuned Qwen2.5-Coder-7B and SkillScan rows** use the "excluding
   Uncategorized" counting convention documented in the verification script.

## (7) Verification

Verified by `scripts/verify_paper_match.py` — all core Table X cells match the paper.
