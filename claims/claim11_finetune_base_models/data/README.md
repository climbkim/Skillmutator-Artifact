# Per-model base-vs-fine-tuned detection (Finding 5)

## (1) Paper location

- **Finding 5**, Figure `fig:prefill_delta_comparison`: detection rate (%) of four
  base open-weight models and their fine-tuned variants on the 76-case SkillMutator
  benchmark, under the GPT-5.4 judge. The prefill column forces the
  `## Phase 4: Category Mapping` header as the assistant-turn prefix (the paper refers to this phase as Attack Category Labeling).

## (2) Paper-cited values

| Base Model | base (%) | fine-tuned no-prefill (%) | fine-tuned prefill (%) |
|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | 17.1 | 79.0 | **88.2** |
| Llama-3.1-8B-Instruct | 7.9 | **82.9** | 75.0 |
| Mistral-7B-Instruct-v0.3 | 5.3 | **72.4** | 55.3 |
| Gemma-2-9b-it | 10.5 | **59.2** | 56.6 |

Bold = better of {no-prefill, prefill} per row.

## (3) Bundled data (judge verdicts)

Only judge-level verdict CSVs are shipped (one row per scanned skill, columns
`skill,category,cat_folder,iter,detected,confidence,reason`). The raw scanner
trees are not redistributed.

| Model | base | fine-tuned no-prefill | fine-tuned prefill |
|---|---|---|---|
| Qwen | `judge/qwen-base.csv` (13/76) | `judge/qwen-finetuned_noprefill.csv` (60/76) | `judge/qwen-finetuned_prefill.csv` (67/76) |
| Llama | `judge/llama-base.csv` (6/65 → 7.9% canon-76) | `judge/llama-finetuned_noprefill.csv` (63/76) | `judge/llama-finetuned_prefill.csv` (57/76) |
| Mistral | `judge/mistral-base.csv` (4/76) | `judge/mistral-finetuned_noprefill.csv` (55/76) | `judge/mistral-finetuned_prefill.csv` (42/76) |
| Gemma | `judge/gemma-base.csv` (8/76) | `judge/gemma-finetuned_noprefill.csv` (45/76) | `judge/gemma-finetuned_prefill.csv` (43/76) |

## (4) Reproduce

```bash
python scripts/build_table6.py        # judge/ -> derived/table6_aggregate.csv
python scripts/verify_paper_match.py  # compare against PAPER_CITED_VALUES.md
```

CPU only; no API key or GPU needed for verification.

## (5) Fine-tuned adapters (for full re-inference only)

The LoRA adapters are hosted on Hugging Face, not bundled. See the Hugging Face adapter repo (huggingface.co/climbkim/skillmutator-scanner-adapters)
for the exact asset names (`Skillmutator_Scanner-<Model>.tar.gz`) and the base
models to load them onto. Re-inference needs a single >= 24 GB GPU.

## (6) Caveats

1. **Llama base denominator** — the Llama base judge CSV has 65 rows (11 missing
   scans on claude-api / pptx / skill-creator). The paper uses 76 as the
   canonical denominator, imputing the missing rows as "not detected"
   (6/76 = 7.9%); `verify_paper_match.py` applies this same rule.
2. **Gemma row** retains the RQ1 3-section evaluation; the other rows use the
   cross-oracle 4-section evaluation.
3. **Prefill is model-dependent** — prefill helps Qwen (+9.2pp) but hurts Llama
   and Mistral (-7.9pp, -17.1pp). The paper treats it as a model-specific
   decoding aid rather than a universally beneficial component.

## (7) Verification

Verified by `scripts/verify_paper_match.py` — all 4 model rows match the paper.
