# PAPER_CITED_VALUES — Table 8, §6.5 Further Analyses

Paper canonical values for Table 8 (cost envelope), §6.5 Further Analyses.

## Header

- Caption: "Per-scan operating cost on the GPT-5.4 oracle benchmark ($n{=}76$). The local scanner cost is estimated based on the batch inference using A100 GPU rental at \$1.1/hour. \$/detection (\$/det.) = \$/skill ÷ recall."
- Benchmark: GPT-5.4 oracle, $n=76$, `select` mode, last iteration
- A100 pricing: \$1.10 / hr (RunPod / vast.ai)
- OpenAI pricing (2026-01 snapshot):
  - GPT-4o-mini: \$0.15 / 1M input, \$0.60 / 1M output
  - GPT-5.4-mini: \$0.25 / 1M input, \$2.00 / 1M output
  - GPT-5.4: \$1.25 / 1M input, \$10.00 / 1M output

## Rows

| Scanner | \$/skill | Recall | \$/det. | Multiplier (\$/det) |
|---|---|---|---|---|
| **Qwen-7B + ours** (local) | **\$0.00414** | **88.16%** | **\$0.00469** | **1.00×** |
| GPT-4o-mini | \$0.00178 | 23.68% | \$0.00753 | 1.60× |
| GPT-5.4-mini | \$0.00664 | 78.95% | \$0.00841 | 1.79× |
| GPT-5.4 | \$0.02754 | 86.84% | \$0.03171 | 6.76× |

## Derived headline claims (Finding 8 narrative)

- Local Qwen-7B scanner is the cheapest per detected attack among all four scanners.
- 1.60× cheaper than mid-tier GPT-4o-mini.
- 1.79× cheaper than mid-tier GPT-5.4-mini.
- 6.76× cheaper than frontier GPT-5.4.
- Achieves +1.32 pp higher recall than the frontier (88.16% vs 86.84%).

## Cited in paper body

- Finding 8 cites \$/det multipliers and 88.16% vs 86.84% comparison.
- LLM Usage Statement: see `LLM Usage Statement` section for model versions used.