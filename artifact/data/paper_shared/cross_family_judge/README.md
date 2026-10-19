> **Artifact packaging note.** This directory ships the **verdict-level and
> aggregate outputs** cited in the paper. The author-side build scripts that
> regenerate them read the raw scanner/scan tree and injected-mutation content,
> which are **not redistributed** — the malicious mutations cannot be published
> (see `use.txt` / `ETHICS.md`). For runnable, self-contained reproduction use
> the per-claim scripts under `claims/`. Raw data is available from the authors
> on request (climbkim@kaist.ac.kr).
# Cross-Family Claude Judge — Shared Resource

## (1) Purpose

This shared resource takes the detection results produced by the paper-canonical GPT-5.4 judge
and re-judges them with a **cross-family Claude Opus 4.7 judge** under a byte-identical prompt,
validating self-judge bias. Over a total of **1,126 cell** ($15$ scanner/model-mode rows),
it computes the agreement between the GPT-5.4 verdict and Claude verdict, and Cohen's $\kappa$.

Because it reinforces several paper tables at once, it is placed as a shared resource rather than a single table folder
(the same paradigm as `artifact/code/skillmutator/analysis/skillmutator_utils/judge.py`, which holds the GPT-5.4 judge code).

## (2) Affected paper locations

| paper location | cited data |
|---|---|
| Figure 5, §6.4 Fine-tuning Effectiveness — right panel (Claude-Opus-4.7 judge): 4 base models × base / no-prefill / prefill | base, fine-tuned no-prefill and fine-tuned prefill rows of `derived/agreement_summary.csv` (`claude_rate`) |
| Figure 5, right panel — dashed line (frontier GPT-5.4 scanner under the Claude judge, 81.6%) | `gpt-5.4-self` row of the cross-scanner manifest (62/76) |
| §6.4 Fine-tuning Effectiveness — Finding 4: "Under a Claude-Opus-4.7 judge, the fine-tuned scanner remains ahead of GPT-5.4 by 3.9 pp (85.5% vs. 81.6%)" | `qwen-d3-prefill` (65/76) vs `gpt-5.4-self` (62/76) |
| §6.4 Fine-tuning Effectiveness — Finding 5: "The Claude-Opus-4.7 judge confirms the same qualitative pattern …" (+10.5 / −11.9 / −13.2 / +1.3 pp) | prefill − no-prefill `claude_rate` per family |

The per-row agreement and Cohen's $\kappa$ in `derived/` are supplementary and are not
cited in the final paper. The judge-robustness numbers of Appendix B.2 (93.7% and the
Claude-Opus-5 judge's 96.1%) come from a separate experiment, not from this folder.

## (3) Data structure

| folder/file | content |
|---|---|
| `manifest.csv` | cross-scanner manifest (301 cells, 4 LLM scanners) |
| `manifest_finetune.csv` | finetune-prefill manifest (228 cells, 3 fine-tuned LoRA models) |
| `manifest_noprefill.csv` | finetune-noprefill manifest (304 cells, 4 fine-tuned LoRA models) |
| `manifest_base.csv` | base-model manifest (293 cells, 4 un-tuned base models) |
| `verdicts/`, `verdicts_finetune/`, `verdicts_noprefill/`, `verdicts_base/` | 142 Claude verdict JSONs (1,126 cell). Each verdict is a `{case_id, scanner, detected, confidence, reason}` schema. |
| `derived/agreement_summary.csv` | 15 row × 12 column aggregate (n, det, rate, Δ, agreement, κ, TT/TF/FT/FF) |
| `derived/agreement_report.md` | auto-generated markdown report |

The Claude verdicts were produced from batches of 8 cells built from the four
manifests (scanner output capped at 12,000 characters and the injected snippet at
1,500 characters, truncation marked with `...[truncated]`), using the same judge
prompt as the paper's GPT-5.4 judge. The batch files and the builder scripts are
not shipped; the manifests, verdicts and `derived/` aggregates above are.

### 1,126 cell distribution

| Manifest | cells | scanners |
|---|---|---|
| cross-scanner (`manifest.csv`) | 301 | gpt-4o-mini (73), gpt-5.4-mini, gpt-5.4-self, qwen-d3-prefill |
| finetune-prefill (`manifest_finetune.csv`) | 228 | llama-d3-prefill, mistral-d3-prefill, gemma-d3-prefill |
| finetune-noprefill (`manifest_noprefill.csv`) | 304 | qwen-d3-noprefill, llama-d3-noprefill, mistral-d3-noprefill, gemma-d3-noprefill |
| base (`manifest_base.csv`) | 293 | qwen-base, llama-base (65), mistral-base, gemma-base |
| **Total** | **1,126** | — |

## (4) Reproduction

The Claude Opus 4.7 verdicts were produced by a Claude Code sub-agent that read
each batch and wrote the verdict JSONs above; no external API script is involved,
and the batch files and builder scripts are not shipped. The agreement and
Cohen's $\kappa$ values are in `derived/agreement_summary.csv` (per-scanner view in
`derived/agreement_report.md`), computed from the four manifests (GPT-5.4 verdicts)
and the four verdict folders (Claude verdicts) in this directory.

## (5) Dependencies (source scan tree, not redistributed)

| resource | purpose |
|---|---|
| the source scan tree (not redistributed) — per-cell meta.json / injected_content.md | the manifest builder extracts scenario meta and injected content |
| `artifact/code/skillmutator/analysis/skillmutator_utils/judge.py` | paper-canonical GPT-5.4 judge call code; the Claude judge requests used byte-identical copies of its `JUDGE_SYSTEM` and `JUDGE_USER_TEMPLATE` |
| GPT-5.4 judge CSVs of the four proprietary LLM scanners (not redistributed) | gpt54_detected/confidence/reason source of the cross-scanner manifest |
| `claims/claim11_finetune_base_models/data/judge/*.csv` | gpt54_detected/confidence/reason source of the finetune/base manifest |

## (6) Verification status

✅ **Verified** — 1,126/1,126 cells judged by both judges (per-row $\kappa$ 0.43–1.00 in
`derived/agreement_summary.csv`). The prefill direction agrees for Qwen, Llama and
Mistral; Gemma is near-neutral (+1.3 pp under Claude vs −2.6 pp under GPT-5.4), as the
paper states in Finding 5.

See `derived/agreement_report.md` for detailed verification results.