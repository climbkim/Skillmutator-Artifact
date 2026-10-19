# Base model weights — HF Hub pointers

Base model weights (each ~14-15 GB) are **NOT copied** to keep bundle size manageable.
Re-download from Hugging Face Hub at reproduction time. Each model is paired with a
LoRA adapter on Hugging Face (huggingface.co/climbkim/skillmutator-scanner-adapters, revision `a44e1da`), same base name.

## Models used in paper

| ID | HF Hub | Size (BF16) | Used by |
|---|---|---|---|
| Qwen2.5-Coder-7B-Instruct | `Qwen/Qwen2.5-Coder-7B-Instruct` | ~15 GB | Table 6 · Table 7 · Table 8 Qwen row · Figure 5 |
| Llama-3.1-8B-Instruct | `unsloth/Meta-Llama-3.1-8B-Instruct` (community mirror; original is gated) | ~16 GB | Figure 5 Llama bars |
| Mistral-7B-Instruct-v0.3 | `mistralai/Mistral-7B-Instruct-v0.3` | ~14 GB | Figure 5 Mistral bars |
| Gemma-2-9b-it | `google/gemma-2-9b-it` | ~18 GB | Figure 5 Gemma bars |

## Reproduction download

```bash
# After pip install huggingface_hub[hf_xet]
hf download Qwen/Qwen2.5-Coder-7B-Instruct --local-dir <dest>/Qwen2.5-Coder-7B-Instruct
hf download unsloth/Meta-Llama-3.1-8B-Instruct --local-dir <dest>/Llama-3.1-8B-Instruct
hf download mistralai/Mistral-7B-Instruct-v0.3 --local-dir <dest>/Mistral-7B-Instruct-v0.3
hf download google/gemma-2-9b-it --local-dir <dest>/Gemma-2-9b-it
```

## LoRA adapter pairing

| LoRA adapter | Base model | r / alpha | Target modules |
|---|---|---|---|
| Qwen fine-tuned adapter (Hugging Face) | Qwen2.5-Coder-7B-Instruct | 64 / 128 | down/gate/up/q/k/v/o_proj |
| Llama fine-tuned adapter (Hugging Face) | Llama-3.1-8B-Instruct | 64 / 128 | down/gate/up/q/k/v/o_proj |
| Mistral fine-tuned adapter (Hugging Face) | Mistral-7B-Instruct-v0.3 | 64 / 128 | down/gate/up/q/k/v/o_proj |
| Gemma fine-tuned adapter (Hugging Face) | Gemma-2-9b-it | 64 / 128 | down/gate/up/q/k/v/o_proj |
| Phase 4 (no refine) adapter (Hugging Face) | Qwen2.5-Coder-7B-Instruct | 64 / 128 | down/gate/up/q/k/v/o_proj |

The Phase 4 (no refine) adapter uses Qwen base — same as the fine-tuned adapter, with
deterministic refinement disabled in training data (160/1219 entries rebuilt from `.pre_refine.bak`).

## vLLM serving

```bash
# Install the tested stack with ./install.sh --finetune
# (torch 2.6.0, vllm 0.8.5.post1, transformers 4.55.4; Python 3.10-3.12).
# The paper's scans ran vLLM 0.19.1 on one A100 80GB (vLLM 0.19.1 itself
# requires torch 2.10.0 and transformers >= 4.56).

# Launch with adapter (note: --served-model-name MUST differ from --lora-modules key
# to avoid same-name collision that silently falls back to base model)
python -m vllm.entrypoints.openai.api_server \
    --model <base_path> --tokenizer <base_path> \
    --enable-lora --max-lora-rank 64 \
    --lora-modules <adapter_id>=<adapter_path> \
    --served-model-name <adapter_id>-base \
    --max-model-len 32768 --gpu-memory-utilization 0.85 --dtype bfloat16 \
    --host 0.0.0.0 --port 8000
```
