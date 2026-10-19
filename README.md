# SkillMutator — Paper Artifact

**Paper:** SkillMutator: Benchmarking and Defending Language-and-Code Cross-modal
Attacks on LLM Agent Skills

**Contact:** climbkim@kaist.ac.kr

This artifact reproduces the 12 claimed tables/figures of the paper (Tables 3–8,
10, 11, Figures 4–6) and ships the mutation-generation framework, the fine-tuned
local scanner, the benchmark verdicts, and per-claim reproduction scripts.

The appendix results added in the camera-ready version are outside the 12 claims.
The judge-robustness numbers (Appendix B.2) can be recomputed with
`artifact/data/paper_shared/gt_validation/compute_b2.py`. Execution validation
(Appendix B.1), the held-out scanners (Table 12, Appendix B.5) and the external
benchmark (Table 13, Appendix B.6) are not verified by this artifact; the harness
for the held-out scanners is in `artifact/code/external_scanners/`.

> The repository root also provides the plain-text `README.txt` (same content),
> `install.sh`, `license.txt`, `use.txt` (command + option reference), and
> `metadata.toml`. **Start here for *what* reproduces *what*; see `use.txt` for
> the exact commands and options.**

## Availability

| Component | Location (URL) |
|---|---|
| Artifact bundle — permanent archive (Zenodo concept DOI, resolves to the latest version) | https://doi.org/10.5281/zenodo.22768210 |
| Artifact bundle — development repository | https://github.com/climbkim/SkillMutator-Artifact |
| Source code — mutation pipeline + fine-tuning framework | https://github.com/climbkim/SkillMutator |
| Fine-tuned LoRA adapters (4 base models, ~2.5 GB), pinned to revision `a44e1da` | https://huggingface.co/climbkim/skillmutator-scanner-adapters/tree/a44e1da61a0b8d7d799a71221a20a10a0f3174a9 |
| External scanner — skill-security-scan (MIT) | https://github.com/huifer/skill-security-scan |
| External scanner — Snyk Agent Scan (Apache-2.0) | https://github.com/snyk/agent-scan |
| External scanner — Sentry Skill Scanner (Apache-2.0) | https://github.com/getsentry/skills |
| External scanner — Cisco AI Defense Skill Scanner (Apache-2.0) | https://github.com/cisco-ai-defense/skill-scanner |
| External scanner — SkillScan (MIT) (out-of-paper) | https://github.com/NMitchem/SkillScan |
| External scanner — Under the Hood (no license) | https://github.com/ShoumikSaha/agent-skill-security |

External scanners are **not redistributed** — install them from the sources
above. We drove them through the harness in
[`artifact/code/external_scanners/`](artifact/code/external_scanners/); how each
was invoked (CLI, static vs. +LLM mode, verdict mapping) is documented in
[`artifact/code/README.md`](artifact/code/README.md) (Scanners), and the held-out
result tables are available from the authors on request. The CPU
claim-verification path is fully self-contained and needs none of these assets.

**Public release.** This artifact is released publicly under the MIT license
(`license.txt`). The code repositories above and the permanently archived bundle
(Zenodo concept DOI `10.5281/zenodo.22768210`) are its public record; the
mutation pipeline, fine-tuning framework, benchmark verdicts, and per-claim
reproduction scripts are all part of the public release.

## Requirements

| Tier | Hardware | Software | Key | Time | Cost |
|---|---|---|---|---|---|
| **1 — data verification** (claims 01–12) | any CPU | `./install.sh` (pandas, numpy, pyyaml, openpyxl); Python ≥ 3.10 (tested 3.10, 3.12, 3.14) | none | ~minutes | **$0** |
| **2 — sample skill demo** | CPU (mutation) / a CUDA GPU ~16 GB (fine-tune scan) | `./install.sh --generate` (+ `--finetune`) | `OPENAI_API_KEY` | ~3–6 min (+10–20 min GPU) | ~a few US cents (+~$0.5 GPU) |
| **3 — paper skills, default settings** | CPU + network / a CUDA GPU ~16 GB (fine-tune scan) | `./install.sh --generate --finetune` | `OPENAI_API_KEY` | hours (+10–20 min GPU) | ~$2–3 API (est.) (+~$0.5 GPU) |
| **4 — full benchmark + training demo** | NVIDIA A100 80 GB | `./install.sh --all` | `OPENAI_API_KEY` | ~3 h+ mutation benchmark + ~1–2 h A100 (est.) | ~$30+ API (expected ~$200) + ~$1–2 GPU (est.) |

Cross-platform (Linux/macOS/Windows-WSL/Git Bash); Tier 1 tested on Ubuntu 22.04
(Python 3.12), Linux (Python 3.10), macOS (Python 3.12), Google Colab and
Windows Git Bash (Python 3.14). A `pip freeze` lock for each tier is recommended
before archival. See `use.txt` for the exact per-tier commands.
The fine-tuning extras (`./install.sh --finetune` / `--all`, the GPU steps of
Tiers 2–4) need **Python 3.10–3.12**: the pinned vllm 0.8.5 and sentencepiece 0.2.0
have no 3.13+ builds (GPU path tested with Python 3.10). Pick the interpreter with
`PYTHON=python3.12 ./install.sh --all`; `install.sh` stops early on 3.13+.

### Tier 4 stage breakdown

Tier 4 chains the full SkillMutator benchmark with a short fine-tuning demo
(estimates; GPU cost at the paper's **$1.10/h**, claim06):

| # | Stage | HW | Time | Cost |
|---|---|---|---|---|
| 1 | **SkillMutator benchmark** — 17 skills × 3 oracles, iter_0–4, gpt-5.4 judge, cross LLM scans, + a gpt-5.4 no-select pass (→ Tables 3/4/5 + Fig 4) | CPU + API | ~3 h+ | ~$30+ API, expected ~$200 (this setting is not measured and costs more) |
| 2 | **Fine-tuning demo** — download base Qwen 7B (~15 GB) + released adapter; teacher distillation of up to 24 skills from the last SkillMutator pass (`DATAGEN_MAX`); a 5-step LoRA run on Qwen (`MAX_STEPS`); scan of 1 mutated + 1 benign skill with the **released** adapter; judge + tables | A100 + API | ~1–2 h | ~$1–2 GPU + < $1 API (gpt-4o-mini teacher and judge) |

The training demo shows the training process; it does not rebuild the paper's
adapters, and its short-run adapter is not used for scanning.

**Paper-scale training is not automated.** Rebuilding the paper's adapters means
distilling the full corpus (1219 examples from 68 skills, ~4,900 calls, ~$40–60
with the GPT-5.4 teacher, RECORDED), training four base families from scratch
(5 epochs, LoRA r64/α128; MEASURED ~25 A100-h: Qwen 4.5 / Llama 5.0 / Gemma 10.0 /
Mistral ~5.5 h), and batch-scanning the evaluation set with vLLM (~3–4 A100-h).
These results are verified from bundled verdicts at Tier 1 (claims 04, 10, 11, 12)
and their cost in claim06. The manual steps are in
`artifact/code/finetuning-framework/docs/REPRODUCE.md`.

## What each tier runs

The tiers are cumulative: **Tier 1** just re-checks the paper numbers from bundled
outputs (the reviewer path — start here); **Tiers 2–4** progressively *regenerate*
those outputs live, so they need an API key and (for the scanner side) a GPU, and
are nondeterministic.

| Step performed | T1 | T2 | T3 | T4 |
|---|:--:|:--:|:--:|:--:|
| Regenerate & PASS/FAIL-check the 12 paper tables/figures vs. cited values (`claims/`) | ✅ | — | — | — |
| Live **mutate → scan** with the SkillMutator pipeline (regenerates Tables 3/4/5 + Fig 4 ³) | — | ✅ 1 sample skill | ✅ 17 Anthropic skills, 1 oracle ² | ✅ 17 skills × 3 oracles |
| Fine-tuning **teacher** data generation (reasoning-trajectory distillation corpus) | — | — | — | ✅ ≤ 24 skills |
| Local **7B scanner inference** with the **released** LoRA adapter | — | ✅ ¹ | ✅ | ✅ |
| **LoRA training** (5-step demo run on Qwen; paper-scale training is not automated) | — | — | — | ✅ demo |

¹ GPU step; skipped by `--no-gpu` (the SkillMutator/CPU+API side still runs).
² Default settings (gpt-4o-mini oracle and judge, 2 iterations, no cross LLM scans,
no no-select pass), not the paper's procedure. `use.txt` section 4 gives the
paper-setting command for one oracle; Tier 4 runs the full benchmark.
³ Live runs rebuild Table 3 and Figure 4 in full, and the skill-security-scan, Snyk and
LLM-scanner rows of Tables 4/5. The SkillScan and prompt-injection-detector rows are
verified at Tier 1 only (the live pipeline does not run those scanners).

## Reproduction at a glance (summary)

Each `claims/claimNN/` maps to one paper float; `run.sh` recomputes the
aggregate from the bundled judge verdicts, writes it to `results/`, and compares
it cell-by-cell against the machine-readable paper golden in
`expected/metrics.json` (paper-cited values + tolerances;
`expected/PAPER_CITED_VALUES.md` is the human-readable view), printing
`ALL MATCH`/`MISMATCH`. **Claims 01–12 are CPU-only — no API key, no GPU,
~minutes total.** Table and figure numbers follow the paper; some internal
script and file names keep earlier draft numbers (e.g. claim01's `build_table4.py`
builds Table 3) and are identifiers only.

| Claim | Paper float | What it verifies | Tier | Expected PASS (headline) |
|---|---|---|---|---|
| [claim01](claims/claim01_oracle_refusal) | Table 3 | Oracle safety-refusal rates differ | 1 · CPU | 23.5 / 42.9 / 9.2 % (4o-mini / 5.4-mini / 5.4) |
| [claim02](claims/claim02_cross_scanner_detection) | Table 4 | Rule/commercial/PI scanners miss mutations (Finding 1–2) | 1 · CPU | 27/27 cells; rule-based 0–17 %, GPT-5.4 up to 86.8 % |
| [claim03](claims/claim03_stealth_aware_selection) | Table 5 | Stealth-aware selection lowers detection | 1 · CPU | select vs no-select Δ per scanner match |
| [claim04](claims/claim04_phase_ablation) | Table 6 | Four-phase schema: monotonic gains; refinement +11.9 pp (Finding 6) | 1 · CPU | per-phase deltas match |
| [claim05](claims/claim05_wild_clawhub) | Table 7 | In-the-wild eval, 200 ClawHub skills (Finding 7) | 1 · CPU | 92.0 % clean, 82.5 % aggregate, 8.0 % FPR |
| [claim06](claims/claim06_cost_envelope) | Table 8 | Local 7B scanner lowest cost per detection (Finding 8) | 1 · CPU | 7B $0.0047/detection vs GPT-5.4 $0.0317 |
| [claim07](claims/claim07_unmodified_baseline) | Table 10 | LLM scanners flag 17/17 unmodified skills | 1 · CPU | 17/17 findings |
| [claim08](claims/claim08_per_category_matrix) | Table 11 (App. B) | Per-category confusion matrix (n=76 + 221) | 1 · CPU | recall 88.2 %, precision 60.9 % |
| [claim09](claims/claim09_ier_dynamics) | Figure 4 | Iterative Evasion Refinement dynamics | 1 · CPU | detection drops iter_0 → iter_1 for all oracles |
| [claim10](claims/claim10_prefill_delta) | Figure 5 | Phase-4 prefill is model-dependent (Finding 5) | 1 · CPU | Qwen +9.2 pp; Llama/Mistral/Gemma ↓ |
| [claim11](claims/claim11_finetune_base_models) | Figure 5 | Distillation improves 4 base families (Finding 5) | 1 · CPU | all improve; Qwen strongest |
| [claim12](claims/claim12_rq3_comparison) | Figure 6 | 7B scanner reaches frontier (Finding 4) | 1 · CPU | 88.2 % detection on n=76 |

The two functional demos of core operation are **not** paper claims and are run
directly from the code (no `claims/` entry): the end-to-end **mutate → scan** demo
via `artifact/code/skillmutator/run.sh` (or `./run.sh --tier 2`; needs
`OPENAI_API_KEY`), and the **distillation training-data** generation via
`artifact/code/finetuning-framework/run.sh` (Tier 4, capped demo). See the two sections below.

Determinism: the CPU claims are deterministic recomputations from bundled
verdicts (values and tolerances are in each claim's `expected/metrics.json`). The **live pipeline is
nondeterministic** (LLM sampling); Tier-2/3/4 outputs are close to, not
bit-identical with, the paper — reproduce headline numbers as a mean over
repeated runs, and pin model snapshots + seeds where supported.

## Quick start

```bash
# Tier 1  verify the 12 table/figure claims  CPU · no key · free · ~minutes   <-- START HERE
./install.sh && ./run.sh --tier 1

# Tier 2  live demo on the sample skill   needs OPENAI_API_KEY (in .env)
./install.sh --generate && ./run.sh --tier 2 --no-gpu --env-file .env     # no GPU
./install.sh --all      && ./run.sh --tier 2 --env-file .env              # with a GPU (adds FT scan)

# Tier 3  paper skills, default settings   key + (GPU unless --no-gpu) + network
./install.sh --all && ./run.sh --tier 3 --env-file .env

# Tier 4  full benchmark + training demo   key + A100 80GB + network
./install.sh --all && ./run.sh --tier 4 --env-file .env
```

**Before you start (two fresh-clone notes):**
- *Permissions.* The scripts are committed executable, but if your clone drops the
  bit (`permission denied`), just prefix `bash`: `bash install.sh && bash run.sh --tier 1`
  (and `bash claims/claimNN/run.sh` for a single claim).
- *venv on Debian / Ubuntu / Google Colab.* If `install.sh` stops at `python3 -m venv`
  with `No module named ensurepip`, install the separate venv package once and re-run:
  `sudo apt-get update && sudo apt-get install -y python3-venv` (or the version-specific
  package named in the error, e.g. `python3.13-venv`).

Options (add to any tier):
- `--no-gpu` — skip the GPU finetune step (the skillmutator side never needs a GPU)
- `--env-file PATH` — load `OPENAI_API_KEY`
- `--dry-run` — preview the plan + HW/SW/cost

Single claims run directly (`cd claims/claim04_phase_ablation && ./run.sh`); full command/option reference in [`use.txt`](use.txt).

## 📊 Expected Results

The values a successful run should reproduce, organized by paper float. Each
Tier-1 claim's `run.sh` checks these against `expected/metrics.json` and prints
`ALL MATCH`; the full per-float values also live in each `claims/claimNN/expected/`.

### claim01 — Table 3: Oracle safety-refusal

| Oracle | Refusal rate | per-iter (0–4) |
|---|---|---|
| gpt-4o-mini | 23.53 % (n=51) | 4 / 12 / 14 / 11 / 12 |
| gpt-5.4-mini | 42.86 % (n=63) | 0 / 15 / 22 / 22 / 27 |
| gpt-5.4 | 9.21 % (n=76) | 0 / 4 / 4 / 8 / 7 |

### claim02 — Table 4: Cross-scanner detection

Detection rate (%), scanner × adversarial oracle (n = 48 / 63 / 76):

| Scanner | gpt-4o-mini | gpt-5.4-mini | gpt-5.4 |
|---|--:|--:|--:|
| skill-security-scan | 2.08 | 6.35 | 7.89 |
| Snyk Agent Scan | 16.67 | 9.52 | 9.21 |
| SkillScan API | 0.00 | 0.00 | 1.32 |
| LLM-Guard | 2.08 | 0.00 | 3.95 |
| PIGuard | 39.58 | 4.76 | 17.11 |
| DataSentinel | 4.17 | 11.11 | 10.53 |
| GPT-4o-mini | 35.42 | 9.52 | 23.68 |
| GPT-5.4-mini | 79.17 | 71.43 | 78.95 |
| GPT-5.4 | 89.58 | 88.89 | 86.84 |

### claim03 — Table 5: Stealth-aware selection

Detection (%), select vs. no-select (Δ = no-select − select):

| Scanner | select | no-select | Δ |
|---|--:|--:|--:|
| skill-security-scan | 7.89 | 12.33 | +4.43 |
| Snyk Agent Scan | 9.21 | 16.89 | +7.68 |
| SkillScan API | 1.32 | 5.48 | +4.16 |
| GPT-4o-mini scanner | 23.68 | 36.07 | +12.39 |
| GPT-5.4-mini scanner | 78.95 | 87.67 | +8.72 |
| GPT-5.4 scanner | 86.84 | 91.32 | +4.48 |
| **Average (6 scanners)** | 34.65 | 41.63 | **+6.98** |

### claim04 — Table 6: Four-phase ablation (Finding 6)

| Configuration | Detection |
|---|--:|
| Phase 1 (Purpose Grounding) | 1.32 |
| + Phase 2 (Out-of-Scope Detection) | 25.00 |
| + Phase 3 (Principle Reasoning) | 57.89 |
| + Phase 4 (Category Labeling) | 67.11 |
| + deterministic refinement | 78.95 |
| + prefill (Phase-4 header forced) | 88.16 |

Decomposed deltas: schema +9.22, refinement +11.84, prefill +9.21 pp.

### claim05 — Table 7: In-the-wild ClawHub (Finding 7)

| Stratum | Expected accuracy |
|---|--:|
| clean | 92.0 % |
| suspicious / LOW · MED · HIGH · CRIT | 60.0 · 68.0 · 84.0 · 80.0 % |
| **Aggregate** | **82.5 %** (FPR 8.0 %) |

### claim06 — Table 8: Cost envelope (Finding 8)

| Scanner | $/scan | Recall | $/detection |
|---|--:|--:|--:|
| **Qwen-7B + ours** | **0.00414** | 88.16 % | **0.00469** |
| GPT-4o-mini | 0.00178 | 23.68 % | 0.00753 |
| GPT-5.4-mini | 0.00664 | 78.95 % | 0.00841 |
| GPT-5.4 | 0.02754 | 86.84 % | 0.03171 |

The local 7B scanner has the **lowest cost per detection**.

### claim07 — Table 10: Unmodified-baseline findings

Findings on the 17 unmodified skills (skills-with-findings / mean / max / total):

| Scanner | skills | mean | max | total |
|---|--:|--:|--:|--:|
| skill-security-scan | 9/17 | 18.18 | 190 | 309 |
| Snyk Agent Scan | 4/17 | 0.35 | 2 | 6 |
| GPT-4o-mini | 17/17 | 7.12 | 9 | 121 |
| GPT-5.4-mini | 17/17 | 6.41 | 10 | 109 |
| GPT-5.4 | 17/17 | 9.59 | 14 | 163 |
| SkillScan (upload API) | 5/17 | 0.35 | 2 | 6 |

### claim08 — Table 11: Per-category cell metrics (Appendix B)

Recall **88.16 %** · Precision 60.91 % · Specificity 80.54 % · F1 72.04 % ·
Balanced Acc 84.35 % (from TP=67, FP=43, FN=9, TN=178).

### claim09 — Figure 4: Iterative Evasion Refinement dynamics

![Figure 4 — IER dynamics](claims/claim09_ier_dynamics/data/image.png)

LLM self-scanner detection (%) drops iter_0 → iter_1 for every oracle, then
plateaus: gpt-4o-mini 39.6 → 27.1, gpt-5.4-mini 84.1 → 73.0, gpt-5.4 92.1 → 85.5.

### claim10 / claim11 — Figure 5: Phase-4 prefill across four base families (Finding 5)

![Figure 5 — prefill delta](claims/claim10_prefill_delta/data/prefill_delta_comparison.png)

Prefill is model-dependent (GPT-5.4 judge): Qwen **+9.2**, Llama −7.9, Mistral
−17.1, Gemma −2.6 pp. Fine-tuning lifts all four families (base → fine-tuned):
Qwen 17.1 → 88.2, Llama 7.9 → 82.9, Mistral 5.3 → 72.4, Gemma 10.5 → 59.2 %.

### claim12 — Figure 6: Fine-tuned vs. frontier (Finding 4)

![Figure 6 — RQ3 comparison](claims/claim12_rq3_comparison/data/rq3_finding1.png)

Detection on the n = 76 GPT-5.4-oracle set: **Qwen-7B (ours) 88.16 %** (67/76) —
matching/exceeding GPT-5.4 (86.84 %) and GPT-5.4-mini (78.95 %), while rule-based
and commercial scanners stay at 1.32 – 9.21 % (GPT-4o-mini 23.68 %, the untuned Qwen
base 17.11 %).

## SkillMutator Pipeline

Mutate a sample skill, then scan it (live):

- **Run:** `./install.sh --generate` → set `OPENAI_API_KEY` → `cd artifact/code/skillmutator && ./run.sh` (or `./run.sh --tier 2`).
- **What it does:** mutates the bundled self-authored sample (`examples/skills/weather-cache`, MIT) with `gpt-4o-mini`, 1 refinement iteration, LLM-mode detection → regenerates Tables 3/4/5 + Figure 4 (demo scale; a few ¢; nondeterministic).
- **Paper skills:** add `--crawl N --registry {anthropic,clawhub}` (see `use.txt`).
- **Stage map:** paper Stages 1–4 → `analyze_skill` / `select_attacks` / `generate_scenarios` / `generate_skill` (see [`artifact/code/README.md`](artifact/code/README.md)).

## Fine-tuning Data Pipeline

Distillation data = a skill's `SKILL.md` (input) → the teacher's four-phase security analysis (target).

- **Demo input** (no third-party content, no bundled mutation): the self-authored benign `examples/skills/weather-cache` plus the mutation that the SkillMutator step of the same Tier 2 run writes to `artifact/code/skillmutator/demo-results/` (generated at run time, gitignored).
- **Full corpus** (1219 examples / 68 skills) not bundled — from the authors on request.
- **Producing pipeline:** `artifact/code/finetuning-framework/` (`prepare_dataset → formatter_v3 → train → merge → serve → run_scanner`; see its docs).
- **Tiers:** inspect the format on CPU (no key); Tier 4 distills a capped corpus (API teacher) and runs a short training demo (A100); the full corpus and paper-scale training are not automated. Released adapters are on Hugging Face (Availability); Tiers 2–4 scan with them.

## Directory layout

```
artifact/
  code/
    skillmutator/          mutation + scan pipeline (src/skill_mutator/: process/,
                           scanners/llm_scanner (ours), crawler/, llm/, utils/)
    finetuning-framework/  4-phase teacher analysis + reasoning-trajectory distillation
    external_scanners/     held-out third-party scanner harness
    docs/                  attack_categories.json + code-level notes
  data/
    skills/                self-authored sample skill + SOURCES.csv (originals not shipped)
    clawhub/               ClawHub corpus as metadata CSV (296 skills; raw files not shipped)
    paper_shared/          judge configs, GT validation, cross-family judge, base-model manifest
infrastructure/            infrastructure.json (public-infra entry: URLs, resources, allocation)
claims/                    claim01–12 (paper tables/figures); each has claim.txt,
                           run.sh, expected/  (functional demos live in artifact/code/)
install.sh   run.sh   README.txt   README.md   license.txt   use.txt   metadata.toml
ETHICS.md
```

## Safety / ethics

The benchmark consists of adversarial (mutated) Agent Skills with injected
malicious instructions, to be used **only** as scanner inputs in an isolated
environment — do not install or execute them against a live agent. These mutated
skills are **not bundled** (to prevent misuse); they are generated on disk only
when the live pipeline (Tier 2–4) is run. Payloads are
inert templates (no real credentials/secrets/live endpoints); raw scanner text
and full mutations are withheld (verdicts/aggregates only). See
[`ETHICS.md`](ETHICS.md) and [`use.txt`](use.txt). No personal data is included.

## License & citation

Publicly released under the **MIT License** (see [`license.txt`](license.txt))
for research and defensive use.

```bibtex
@inproceedings{skillmutator2026,
  title     = {SkillMutator: Benchmarking and Defending Language-and-Code
               Cross-modal Attacks on LLM Agent Skills},
  booktitle = {Annual Computer Security Applications Conference (ACSAC)},
  year      = {2026}
}
```
