# Figure 4 — IER Dynamics (per-iter detection decay)

## (1) Paper location
- LaTeX label: `\label{fig:ier_dynamics}`
- Paper lines: L803-806
- Caption: "Per-iteration detection rate under Iterative Evasion Refinement, one panel per adversarial-oracle benchmark. Line colors distinguish scanner identity. Rule-based scanners (skill-security-scan, Snyk Agent Scan) are shown dashed, and the LLM self-scanner solid."

## (2) PAPER_TARGET_VALUES (text claim L851)
"LLM self-scanner detection drops between iter_0 and iter_1 (GPT-4o-mini 41.3% to 27.1%, GPT-5.4-mini 84.1% to 73.0%, GPT-5.4 92.1% to 85.5%)"

Plot data (per (oracle, iter, scanner)):
- GPT-4o-mini LLM iter_0..4: 41.3 / 27.1 / 33.3 / 27.1 / 35.4
- GPT-5.4-mini LLM iter_0..4: 84.1 / 73.0 / 68.3 / 74.6 / 71.4
- GPT-5.4 LLM iter_0..4: 92.1 / 85.5 / 86.8 / 84.2 / 86.8
- ss/snyk lines: see derived/ier_dynamics.csv

## (3) Data source
- `derived/ier_dynamics.csv` — 3 oracles × 5 iters × 3 scanners = 45 rows
- `derived/ier_dynamics_summary.txt` — human-readable pivot tables
- `scripts/compute_ier_dynamics.py` — raw aggregator (reads the source scan tree, not redistributed)
- `scripts/plot_ier_dynamics.py` — produces image.png + image.pdf
- `image.png` / `image.pdf` — paper-ready figure

## (4) Reproduction
```bash
cd figure4_ier_dynamics
SKILLMUTATOR_DATA_ROOT="<source scan tree — not redistributed>" \
  python scripts/compute_ier_dynamics.py    # → derived/ier_dynamics.csv
python scripts/plot_ier_dynamics.py         # → image.png + image.pdf
```

## (5) Dependencies
- the source scan tree (not redistributed) — 3 GPT oracle trees (select mode)
- matplotlib (plot)

## (6) Verification status
Verified: key paper values match the CSV (GPT-4o-mini i0=41.3, i1=27.1; GPT-5.4-mini i0=84.1, i1=73.0; GPT-5.4 i0=92.1, i1=85.5).

Detailed caveat: paper claim "every post-iter_0 iteration stays strictly below iter_0 detection level" — data check:
- GPT-4o-mini: max(i1..i4) = 35.4 < i0=41.3 ✅
- GPT-5.4-mini: max(i1..i4) = 73.5 < i0=84.1 ✅
- GPT-5.4: max(i1..i4) = 86.84 (i2 and i4) — i0=92.1 ✅
