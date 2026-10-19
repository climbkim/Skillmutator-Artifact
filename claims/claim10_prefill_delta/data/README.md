# Figure 5 — Prefill Delta Comparison (4 model families × 2 judges)

## (1) Paper location

- **Paper location**: Figure 5, §6.4 Fine-tuning Effectiveness (Finding 5)
- **Caption**: "Detection rate (%) of base open-weight models and their fine-tuned variants under no-prefill and Phase 4-prefill conditions, evaluated under the GPT-5.4 judge (left) and the Claude-Opus-4.7 judge (right). Dashed line: frontier GPT-5.4 scanner's detection rate."

## (2) PAPER_TARGET_VALUES

See [PAPER_CITED_VALUES.md](PAPER_CITED_VALUES.md).

Summary: 2-panel grouped bar chart, 4 open-weight models × {base, +FT no-prefill, +FT prefill} × {GPT-5.4 judge, Claude-Opus-4.7 judge}.

Headline numbers:
- Qwen prefill detection: 88.2% (GPT judge) / 85.5% (Claude judge)
- Frontier GPT-5.4 reference: 86.8% (GPT judge) / 81.6% (Claude judge)
- Prefill direction differs by family: Qwen +, Llama / Mistral −, Gemma neutral

## (3) Data source

The data is derived from claim11 (4 model families, GPT-5.4 judge) + Claude-Opus-4.7 cross-family judge re-evaluation.

| Source | Coverage |
|---|---|
| `../../claim11_finetune_base_models/data/derived/` | GPT-5.4 judge panel (left) — base + no-prefill + prefill rates for Qwen / Llama / Mistral / Gemma |
| the cross-family judge panel data (bundled under artifact/data/paper_shared/cross_family_judge/) | Claude-Opus-4.7 judge panel (right) — 1,126-prompt cross-family re-evaluation |

The data table is hard-coded as constants inside `scripts/plot_prefill_delta.py` (paper canonical chain 4-section consistent).

### Figure files
Bundled (this folder): `prefill_delta_comparison.{pdf,png}` — the paper's Figure 5 layout (one shared legend, "GPT-5.4 Scanner" reference line).

`scripts/plot_prefill_delta.py` re-plots the same values to `../results/figures/` (not tracked by git), in its own layout:
- `option_a_grouped_bar.{pdf,png}` — two panels (GPT-5.4 judge, Claude-Opus-4.7 judge), legend upper-left
- `option_a_grouped_bar_legend_right.{pdf,png}` — same, legend in each panel
- `option_b_delta_plot.{pdf,png}` — prefill − no-prefill per family and judge

## (4) Reproduction commands

```bash
bash ../run.sh                           # verify Figure 5 values
python scripts/plot_prefill_delta.py     # needs matplotlib
# → ../results/figures/option_a_grouped_bar.{pdf,png}, ... (3 figures)
```

## (5) Dependencies

- `matplotlib`, `numpy`
- Font: Times New Roman (or Liberation Serif / STIX / DejaVu Serif fallback)

## (6) Verification status

Verified: the data constants in scripts/plot_prefill_delta.py match PAPER_CITED_VALUES.md — all 24 cells (4 models × 3 modes × 2 judges).