# Table 3 — Safety-Refusal Counts per Oracle (3 GPT oracles)

## (1) Paper location
- Paper location: Table 3, §6.1 Experimental Setup
- Caption: "Safety-refusal counts by adversarial oracle. When the final refinement iteration is a refusal, evaluation uses the most recent non-refusal mutation."

## (2) PAPER_TARGET_VALUES (camera-ready paper)

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
- Build pipeline source: `artifact/code/skillmutator/analysis/rq1/scripts/build_tab2_refusal_summary.py` over the per-iteration mutation tree (the paper's tree is not redistributed; a Tier 2/4 run writes the same layout, and `analysis/paper_floats/table3_refusal.py` rebuilds both CSVs from it)

## (4) Reproduction
```bash
python scripts/build_table4.py
python scripts/verify_paper_match.py   # ✅ 3 oracle rows verified
```

## (5) Dependencies
- the source scan tree (not redistributed) (refusal source mutations)
- `artifact/code/skillmutator/analysis/skillmutator_utils/classifications.py` (shipped): per-iteration class (normal / explicit_refusal / silent_failure / partial_refusal) from the refusal keyword list `REFUSAL_PATS` and structural signals (modified-file count, `SKILL.md` byte identity)
- Tier 1 checks Table 3 from the class labels already in `derived/`. A Tier 2-4 run labels its own cells with the same `classify_entry` rule (called by `scripts/consolidate_to_datatree.py`). Applied to the paper's raw oracle outputs, this rule reproduces all 1,595 paper labels of the four oracle/mode trees.

## (6) Verification status
Verified: 3 oracles × 10 metrics all match the paper.
