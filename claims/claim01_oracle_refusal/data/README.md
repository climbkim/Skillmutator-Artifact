# Table III — Safety-Refusal Counts per Oracle (3 GPT oracles)

## (1) Paper location
- LaTeX label: `\label{tab:refusal_i4_summary}`
- Paper lines: L753-L775
- Caption: "Safety-refusal counts per adversarial oracle. Final-iter refusals re-pin to the last normal iteration."

## (2) PAPER_TARGET_VALUES (current paper.tex)

| Metric | gpt-4o-mini | gpt-5.4-mini | gpt-5.4 |
|---|---|---|---|
| Attempted (n) | 51 | 63 | 76 |
| Refusal rate at iter_4 | 23.53% | 42.86% | 9.21% |
| Refusals per iter (0/1/2/3/4) | 4/12/14/11/12 | 0/15/22/22/27 | 0/4/4/8/7 |
| Silent failure (iter_4) | 2 | 23 | 0 |
| Explicit refusal (iter_4) | 0 | 4 | 0 |
| Partial refusal (iter_4) | 10 | 0 | 7 |

## (3) Data source
- GPT oracles: `derived/tab2_refusal_per_iter.csv` (per-iter break) + `tab2_refusal_summary.csv` (totals)
- Build: `scripts/build_table4.py` → `derived/table4_aggregate.csv`
- Build pipeline source: the refusal-summary builder script + the source scan tree (not redistributed) (refusal classification)

## (4) Reproduction
```bash
python scripts/build_table4.py
python scripts/verify_paper_match.py   # ✅ 4 oracle rows verified
```

## (5) Dependencies (source scan tree, not redistributed)
- the source scan tree (not redistributed) (refusal source mutations)
- the judge script (not redistributed) (classification logic — keyword detectors HarmBench/StrongREJECT + structural signals)

## (6) Verification status
Verified: 4 oracles × 6 metrics all match the paper.
