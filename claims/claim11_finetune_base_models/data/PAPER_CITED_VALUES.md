# Paper-cited Values — Per-model base-vs-fine-tuned detection (Finding 5, `fig:prefill_delta_comparison`)

Detection rate (%) of four base open-weight models and their best fine-tuned
variants on the 76-case SkillMutator benchmark, under the GPT-5.4 judge. The
prefill column forces the `## Phase 4: Category Mapping` header (the paper refers to this phase as Attack Category Labeling) as the
assistant-turn prefix. Values as reported in Finding 5 of the paper.

## Cell-by-cell verification target

| Base Model | base | fine-tuned no-prefill | fine-tuned prefill | Verified? |
|---|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | 17.1% | 79.0% | 88.2% | ✅ |
| Llama-3.1-8B-Instruct | 7.9% | 82.9% | 75.0% | ✅ |
| Mistral-7B-Instruct-v0.3 | 5.3% | 72.4% | 55.3% | ✅ |
| Gemma-2-9b-it | 10.5% | 59.2% | 56.6% | ✅ |

Verified by `scripts/verify_paper_match.py`. Gemma row retains the RQ1 3-section
evaluation; the other rows use the cross-oracle 4-section evaluation.
