# PAPER_CITED_VALUES — `fig:prefill_delta_comparison`

Paper canonical values from `paper.tex` L791-796 (label `\label{fig:prefill_delta_comparison}`).

## Header

- Caption: "Detection rate (%) of base open-weight models (Qwen2.5-Coder-7B-Instruct, Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3, Gemma-2-9b-it) and their fine-tuned variants under no-prefill and Phase~4-prefill conditions, evaluated under the GPT-5.4 judge (left) and the Claude-Opus-4.7 judge (right). Dashed line: frontier GPT-5.4 scanner's detection rate."
- Source data: `paper.tex` Table 6 (`tab:rq3_main`, fine-tune base models)
- Format: 2-panel grouped bar (4 models × 3 modes [base / no-prefill / +prefill] × 2 judge panels)
- Reference line: frontier GPT-5.4 scanner detection rate

## Detection rates (%)

### GPT-5.4 judge panel

| Model | Base (no FT) | + FT, no prefill | + FT, prefill |
|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | 17.1 | 79.0 | **88.2** |
| Llama-3.1-8B-Instruct | 7.9 | 82.9 | 75.0 |
| Mistral-7B-Instruct-v0.3 | 5.3 | 72.4 | 55.3 |
| Gemma-2-9b-it | 10.5 | 59.2 | 56.6 |

Frontier GPT-5.4 reference: **86.8%**

### Claude-Opus-4.7 judge panel

| Model | Base (no FT) | + FT, no prefill | + FT, prefill |
|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | 7.9 | 75.0 | **85.5** |
| Llama-3.1-8B-Instruct | 2.6 | 88.2 | 76.3 |
| Mistral-7B-Instruct-v0.3 | 5.3 | 68.4 | 55.3 |
| Gemma-2-9b-it | 6.6 | 68.4 | 69.7 |

Frontier GPT-5.4 reference: **81.6%**

## Headline claims (Finding 6 narrative)

- **Fine-tuning gain per model** (best of no-prefill/prefill, GPT-5.4 judge):
  - Qwen: 17.1 → 88.2 (+71.1 pp)
  - Llama: 7.9 → 82.9 (+75.0 pp)
  - Mistral: 5.3 → 72.4 (+67.1 pp)
  - Gemma: 10.5 → 59.2 (+48.7 pp)
- **Prefill direction differs by family** (GPT-5.4 judge):
  - Qwen: +9.2 pp (gain)
  - Llama: −7.9 pp (loss)
  - Mistral: −17.1 pp (loss)
  - Gemma: −2.6 pp (near-neutral)
- **Cross-judge confirmation** (Claude-Opus-4.7):
  - Qwen prefill: +10.5 pp (gain)
  - Llama prefill: −11.9 pp (loss)
  - Mistral prefill: −13.2 pp (loss)
  - Gemma prefill: +1.3 pp (near-neutral)
- Direction confirmed by both judges for all 4 model families.

## Cited in paper body

- Finding 4 (L835): "Under a Claude-Opus-4.7 judge, the fine-tuned scanner remains ahead of GPT-5.4 by 3.95 pp (85.53% vs 81.58%)"
- Finding 6 (L854-): "improves Qwen by +9.2 pp, but reduces Llama, Mistral, and Gemma by −7.9 pp, −17.1 pp, and −2.6 pp, respectively"
- Finding 6 (Claude judge corroboration): "+10.5 pp ... −11.9 pp ... −13.2 pp ... +1.3 pp"