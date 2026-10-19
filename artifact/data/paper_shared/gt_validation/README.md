# `gt_validation/` — Appendix B.2 Judge Robustness

Verdict labels behind the judge-agreement numbers of Appendix B.2 Judge Robustness:

> "we rebuilt a complete ground truth by diffing each mutated skill against its
> original. Against this ground truth, the GPT-5.4 judge reproduces 93.7% of its
> verdicts (κ=0.850) on all 301 scanner reports, and it agrees with a
> Claude-Opus-5 judge on 96.1% (κ=0.847) of our scanner's 76 reports."

## Files

- `b2_verdicts.csv` — one row per scanner report (301 rows: GPT-5.4, GPT-5.4-mini
  and the fine-tuned Qwen scanner on all 76 GPT-5.4 mutations, GPT-4o-mini on 73,
  since 3 GPT-4o-mini scans do not exist). Columns:
  - `case_id`, `scanner`, `skill`, `cat_folder` — which report
  - `gpt54_paper_capped_gt` — the paper's GPT-5.4 verdict (ground truth capped at
    1,500 characters, as used in the main text)
  - `gpt54_complete_gt` (+ `_confidence`, `_error`) — GPT-5.4 re-judged against
    the complete ground truth with the same prompt
  - `opus5_complete_gt` (+ `_confidence`, `_error`) — Claude-Opus-5 judging the
    same complete ground truth
- `compute_b2.py` — recomputes the agreement and Cohen's κ (standard library only).

```bash
python compute_b2.py
# GPT-5.4 paper (capped GT) vs GPT-5.4 complete GT, all reports: 93.7%, kappa 0.850, n=301
# GPT-5.4 complete GT vs Claude-Opus-5 complete GT, Qwen scanner: 96.1%, kappa 0.847, n=76
```

## Not included

The complete ground-truth texts, the scanner reports and the judges' free-text
reasons quote the injected mutation content, so they are not redistributed
(see `ETHICS.md`). Only the verdict labels, confidences and error flags are shipped.
