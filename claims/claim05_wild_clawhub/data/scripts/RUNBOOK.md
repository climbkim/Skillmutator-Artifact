# Serving the fine-tuned scanner with vLLM (full-scan runbook)

This runbook describes how to serve the fine-tuned Qwen2.5-Coder-7B scanner
adapter with vLLM and run it over skills, using the exact inference settings the
paper used. It requires a single GPU with >= 24 GB VRAM.

- **Adapter**: the fine-tuned Qwen2.5-Coder-7B LoRA adapter (hosted on Hugging
  Face; see huggingface.co/climbkim/skillmutator-scanner-adapters for the asset name). Download and extract it to a
  local directory, referred to below as `<ADAPTER_DIR>`.
- **Base model**: `Qwen/Qwen2.5-Coder-7B-Instruct`.
- **System prompt**: the released scanner's system prompt (quoted
  in the Notes section).

---

## Step 1 — Launch vLLM

```bash
vllm serve Qwen/Qwen2.5-Coder-7B-Instruct \
    --host 0.0.0.0 --port 8000 \
    --dtype bfloat16 \
    --max-model-len 32768 \
    --enable-lora --max-lora-rank 64 \
    --lora-modules scanner=<ADAPTER_DIR> \
    --served-model-name scanner
```

Wait for `Uvicorn running on http://0.0.0.0:8000`. Liveness check:

```bash
curl -s http://localhost:8000/v1/models | python -m json.tool   # expect "id": "scanner"
```

## Step 2 — Smoke test (one suspicious + one clean skill)

Point the smoke-test script at the served endpoint and two skill directories
(each containing a `SKILL.md` plus any `scripts/` / `references/`):

```bash
python smoke_test.py \
    --base-url http://localhost:8000/v1 \
    --model scanner \
    --suspicious-dir <path>/suspicious_skill/files \
    --clean-dir      <path>/clean_skill/files \
    --out smoke_test_results.json
```

Expected: ~10-30s per skill. The suspicious skill's output should contain a
`## Phase 4: Category Mapping` heading followed by one or more
`- [P#]` bullets citing file locations, and hits from the 13-category
vocabulary; the clean skill should flag few or none.

## Step 3 — Full scan

Iterate the smoke script (or a batch variant) over each skill's `files/`
directory, saving one report per skill, then run a judge comparing the
scanner's Phase 4 categories against the ClawHub `audit.json` ground truth (via
the finding-code mapping table under the corpus directory).

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `model not found: scanner` | LoRA not loaded / wrong served-name | Re-check `--lora-modules scanner=<ADAPTER_DIR>`; `curl /v1/models`. |
| Phase 4 heading missing | Endpoint dropped `continue_final_message` | Confirm vLLM >= 0.5; if a proxy strips `extra_body`, the smoke test reports it. |
| Suspicious and clean return identical generic text | Adapter not applied (answering as base model) | Restart vLLM with explicit `--enable-lora --max-lora-rank 64`. |
| Empty 13-cat hits on suspicious | Adapter loaded but not generalizing | Retry without prefill; if Phase 1-3 also missing, the adapter weights may be wrong. |
| 429 / timeout | KV cache full or vLLM busy | Re-check `--max-model-len 32768`; rerun. |

## Notes — exact inference settings (released scanner)

- **System prompt (Option B)**:
  > "You are an expert AI agent security analyst specializing in LLM-powered agent skill security. Your task is to analyze agent skills -- composed of SKILL.md instruction documents and Python helper scripts -- and produce a structured 4-Phase security analysis. Reason step-by-step, cite specific file locations and code patterns as evidence, and distinguish what a skill claims to do versus what it actually does. Your final output must list security findings with attack categories."
- **File rendering**: `read_skill_dir(skill_dir, max_chars=30_000)`.
- **Sampling**: `temperature=0`, `max_tokens=2048`, `frequency_penalty=0.3` (via `extra_body`); `max_model_len=32768`.
- **Prefill**: `## Phase 4: Category Mapping\n\n\n` as the assistant turn with `continue_final_message=True`.
