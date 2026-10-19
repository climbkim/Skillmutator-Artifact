# Table 8 — Per-Scan Operating Cost (Cost Envelope)

## (1) Paper location

- **Paper location**: Table 8, §6.5 Further Analyses (Finding 8)
- **Caption**: "Per-scan operating cost on the GPT-5.4 oracle benchmark ($n{=}76$). The local scanner cost is estimated based on the batch inference using A100 GPU rental at \$1.1/hour. \$/detection (\$/det.) = \$/skill ÷ recall."

## (2) PAPER_TARGET_VALUES

See [PAPER_CITED_VALUES.md](PAPER_CITED_VALUES.md).

Summary:

| Scanner | \$/skill | Recall | \$/det. |
|---|---|---|---|
| **Qwen-7B + ours** (local, A100 \$1.10/hr) | **\$0.00414** | **88.16%** | **\$0.00469** |
| GPT-4o-mini | \$0.00178 | 23.68% | \$0.00753 (1.60×) |
| GPT-5.4-mini | \$0.00664 | 78.95% | \$0.00841 (1.79×) |
| GPT-5.4 | \$0.02754 | 86.84% | \$0.03171 (6.76×) |

## (3) Data source

| Scanner | Source | Token reconstruction |
|---|---|---|
| GPT-4o-mini | last-iteration scans (3 missing skills rescanned) | API direct usage |
| GPT-5.4-mini | last-iteration scans | API direct usage |
| GPT-5.4 | self-scanner, API direct, body preserved | tiktoken (`o200k_base`) — mean abs Δ = 519 tokens vs API |
| Qwen-7B + ours (local) | fine-tuned Qwen2.5-Coder-7B scans (prefill) | vLLM single-stream throughput on A100 80GB |

### Shipped files
- `derived/m7_final.csv` — final aggregated cost/latency table (per-scanner aggregate)
- `derived/m7_per_scanner_oracle.csv` — per-scanner oracle-stratified breakdown
- `scripts/verify_paper_match.py` — recomputes Table 8 from `derived/` and checks it against `expected/metrics.json` (called by `run.sh`)

## (4) Reproduction commands

```bash
bash ../run.sh        # recompute Table 8 from derived/ and compare to expected/
```

Key constants used to build `derived/m7_final.csv`:
- `A100_USD_PER_HOUR = 1.10` — RunPod/vast.ai (user-chosen)
- OpenAI 2026-01 pricing for GPT-4o-mini / GPT-5.4-mini / GPT-5.4

## (5) Source scans

Cost/latency is derived from per-scanner source scan trees that are not redistributed.

## (6) Verification

Qwen-7B latency agrees across independent measurement sites (median 13.5 s).

## (7) Caveats

- **GPT-5.4 latency proxy**: the last-iteration raw timing metadata was missing, so latency 18.1s is taken from an adjacent GPT-5.4 scan (token length 96% match).
- **GPT-5.4 tiktoken reconstruction**: the scan body is preserved. Input/output tokens are reconstructed with tiktoken (o200k_base). Cross-check: on the GPT-4o-mini scanner, the tiktoken-vs-API-truth median delta = -4 tokens (0.05% error).
- **A100 pricing**: uses RunPod/vast.ai's \$1.10/hr. Self-hosting / on-demand cloud costs may differ.
- **OpenAI pricing snapshot**: 2026-01. API prices may change — see the reproducibility limitation in the paper's LLM Usage Statement.

