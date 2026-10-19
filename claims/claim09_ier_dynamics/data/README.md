# Figure 4 — IER Dynamics (per-iter detection decay)

## (1) Paper location
- Paper location: Figure 4, §6.3.2 Iterative Evasion Refinement
- Caption: "Per-iteration detection rate under iterative evasion refinement."

## (2) PAPER_TARGET_VALUES (text claim, §6.3.2 Iterative Evasion Refinement)
"LLM self-scanner detection drops between iter_0 and iter_1 (GPT-4o-mini 39.6% to 27.1%, GPT-5.4-mini 84.1% to 73.0%, GPT-5.4 92.1% to 85.5%)"

Plot data (per (oracle, iter, scanner)):
- GPT-4o-mini LLM iter_0..4: 39.6 / 27.1 / 33.3 / 27.1 / 35.4
- GPT-5.4-mini LLM iter_0..4: 84.1 / 73.0 / 68.3 / 74.6 / 71.4
- GPT-5.4 LLM iter_0..4: 92.1 / 85.5 / 86.8 / 84.2 / 86.8
- ss/snyk lines: see derived/ier_dynamics.csv

## (3) Data source
- `raw/ier_verdicts.csv` — masked per-iteration verdicts, 950 rows: `oracle, skill, category, iter, classification` (refusal class from `meta.json`) and the `detected` flag of `ss` (skill-security-scan), `snyk` (Snyk Agent Scan) and `llm` (the oracle's own LLM scanner). It holds no scanner text, judge reasons, injected content or paths.
- `derived/ier_dynamics.csv` — 3 oracles × 5 iters × 3 scanners = 45 rows (the table the figure is drawn from)
- `derived/ier_dynamics_summary.txt` — human-readable pivot tables
- `scripts/compute_ier_dynamics.py` — refusal-aware aggregation (`aggregate_ier`): at iteration k each scenario uses its latest refusal-free iteration ≤ k, the refusal handling of §6.1 Experimental Setup, and a scenario with no refusal-free mutation yet counts as not detected. The denominators stay at the Table 4 evaluable sets (n=48/63/76) at every iteration, and iteration 4 equals the Table 4 values. Reads `raw/ier_verdicts.csv` by default, or a full SkillMutator data tree with `--tree` (the layout the live pipeline writes; `--tree … --export raw/ier_verdicts.csv` is how the masked file was produced)
- `scripts/plot_ier_dynamics.py` — draws Figure 4 with the camera-ready settings into `../results/fig4_ier_dynamics.{pdf,png}`
- `scripts/verify_paper_match.py` — recomputes the 45 cells from `raw/ier_verdicts.csv`, checks them against `derived/ier_dynamics.csv` and the LLM rates against `expected/metrics.json` (called by `run.sh`)
- `image.png` / `image.pdf` — Figure 4 rendered from `derived/ier_dynamics.csv` (same output as `plot_ier_dynamics.py`)

## (4) Reproduction
```bash
bash ../run.sh                                   # recompute from raw/ and verify
python scripts/compute_ier_dynamics.py           # raw/ier_verdicts.csv -> ../results/derived/ier_dynamics.csv
python scripts/plot_ier_dynamics.py              # -> ../results/fig4_ier_dynamics.{pdf,png}

# after a live run (Tier 2-4), aggregate your own data tree instead:
python scripts/compute_ier_dynamics.py --tree "$SKILLMUTATOR_DATA_ROOT"
```

## (5) Dependencies
- Python standard library (aggregation, verification)
- matplotlib (plot only)

## (6) Verification status
Verified: key paper values match the CSV (GPT-4o-mini i0=39.6, i1=27.1; GPT-5.4-mini i0=84.1, i1=73.0; GPT-5.4 i0=92.1, i1=85.5).

Detailed caveat: the paper (§6.3.2 Iterative Evasion Refinement) states "every post-iter_1 iteration remains below the iter_1 detection level"; the paper counts iterations from 1, so paper iter_1 = data iter_0. Data check:
- GPT-4o-mini: max(i1..i4) = 35.4 < i0=39.6 ✅
- GPT-5.4-mini: max(i1..i4) = 74.6 < i0=84.1 ✅
- GPT-5.4: max(i1..i4) = 86.84 (i2 and i4) — i0=92.1 ✅
