SkillMutator — Paper Artifact
=============================

Paper: SkillMutator: Benchmarking and Defending Language-and-Code
       Cross-modal Attacks on LLM Agent Skills
Contact: climbkim@kaist.ac.kr

This artifact reproduces the 12 claimed tables/figures of the paper (Tables 3-8,
10, 11, Figures 4-6) and ships the mutation-generation framework, the fine-tuned
local scanner, the benchmark verdicts, and per-claim reproduction scripts.

The appendix results added in the camera-ready version are outside the 12 claims.
The judge-robustness numbers (Appendix B.2) can be recomputed with
artifact/data/paper_shared/gt_validation/compute_b2.py. Execution validation
(Appendix B.1), the held-out scanners (Table 12, Appendix B.5) and the external
benchmark (Table 13, Appendix B.6) are not verified by this artifact; the harness
for the held-out scanners is in artifact/code/external_scanners/.

This README.txt and README.md have the same content. Start here for WHAT
reproduces WHAT; see use.txt for the exact commands and options.

Availability
------------
  Component                                  Location (URL)
  Artifact bundle -- permanent archive (Zenodo concept DOI, resolves to the latest version)  https://doi.org/10.5281/zenodo.22768210
  Artifact bundle -- development repository  https://github.com/climbkim/SkillMutator-Artifact
  Source code (mutation pipeline + fine-tuning framework)  https://github.com/climbkim/SkillMutator
  Fine-tuned LoRA adapters (4 models, ~2.5GB), pinned to revision a44e1da  https://huggingface.co/climbkim/skillmutator-scanner-adapters/tree/a44e1da61a0b8d7d799a71221a20a10a0f3174a9
  External scanner: skill-security-scan (MIT)          https://github.com/huifer/skill-security-scan
  External scanner: Snyk Agent Scan (Apache-2.0)       https://github.com/snyk/agent-scan
  External scanner: Sentry Skill Scanner (Apache-2.0)  https://github.com/getsentry/skills
  External scanner: Cisco AI Defense Skill Scanner (Apache-2.0)  https://github.com/cisco-ai-defense/skill-scanner
  External scanner: SkillScan (MIT, out-of-paper)      https://github.com/NMitchem/SkillScan
  External scanner: Under the Hood (no license)        https://github.com/ShoumikSaha/agent-skill-security

External scanners are NOT redistributed -- install them from the sources above.
We drove them through the harness in artifact/code/external_scanners/; how each
was invoked (CLI, static vs. +LLM, verdict mapping) is in artifact/code/README.md
(Scanners), and the held-out result tables are available from the authors on request. The CPU
claim-verification path below is self-contained and needs none of these assets.

Public release: this artifact is released publicly under the MIT license
(license.txt). The code repositories above and the permanently archived bundle
(Zenodo concept DOI 10.5281/zenodo.22768210) are its public record.

Requirements
------------
  Tier 1  data verification (claims 01-12)    : any CPU; ./install.sh
            (pandas/numpy/pyyaml/openpyxl; Python >=3.10, tested 3.10/3.12/3.14); no key.
            Time: ~minutes.   Cost: $0 (no API calls).
  Tier 2  sample-skill demo                    : CPU (mutation) / CUDA GPU ~16GB
            (fine-tune scan); ./install.sh --generate (+ --finetune); OPENAI_API_KEY.
            Time: ~3-6 min (+10-20 min GPU).   Cost: ~a few US cents (+~$0.5 GPU).
  Tier 3  paper skills, default settings      : CPU + network / CUDA GPU ~16GB
            (fine-tune scan); ./install.sh --generate --finetune; OPENAI_API_KEY.
            Time: hours (+10-20 min GPU).   Cost: ~$2-3 API (est.) (+~$0.5 GPU).
            One oracle at default settings (gpt-4o-mini oracle and judge,
            2 iterations, no cross scans, no no-select pass), not the paper's
            procedure; use.txt section 4 gives the paper-setting command.
  Tier 4  full benchmark + training demo      : NVIDIA A100 80GB; ./install.sh --all;
            OPENAI_API_KEY.  Estimates (GPU at $1.10/h):
              1 skillmut  17 skills x3 oracles, iter_0-4, gpt-5.4 judge, cross
                          scans, + gpt-5.4 no-select pass   CPU+API ~3 h+  ~$30+ API (expected ~$200)
                          (this setting is not measured and costs more)
              2 FT demo   base Qwen 7B download, teacher distill of <= 24 skills,
                          5-step LoRA run, released-adapter scan of 1 mutated +
                          1 benign skill, judge + tables   A100+API ~1-2 h
                          ~$1-2 GPU + < $1 API (gpt-4o-mini teacher and judge)
            The training demo shows the process; it does not rebuild the paper's
              adapters. Paper-scale training is NOT automated: full corpus (1219
              examples, ~$40-60 with the GPT-5.4 teacher, RECORDED), 4 base families
              from scratch (MEASURED ~25 A100-h: Qwen 4.5/Llama 5.0/Gemma 10.0/
              Mistral ~5.5), vLLM batch scan (~3-4 A100-h). Verified at Tier 1
              (claims 04, 10, 11, 12; cost in claim06). Manual steps:
              artifact/code/finetuning-framework/docs/REPRODUCE.md.
Cross-platform (Linux/macOS/Windows-WSL/Git Bash); Tier 1 tested on Ubuntu 22.04
(Python 3.12), Linux (Python 3.10), macOS (Python 3.12), Google Colab and
Windows Git Bash (Python 3.14). A pip-freeze lock per tier is recommended before
archival. The fine-tuning extras (./install.sh --finetune / --all, the GPU steps
of Tiers 2-4) need Python 3.10-3.12: the pinned vllm 0.8.5 and sentencepiece 0.2.0
have no 3.13+ builds (GPU path tested with Python 3.10). Pick the interpreter with
PYTHON=python3.12 ./install.sh --all; install.sh stops early on 3.13+.

What each tier runs
-------------------
Tiers are cumulative. Tier 1 only re-checks the paper numbers from bundled
outputs (the reviewer path -- start here); Tiers 2-4 progressively REGENERATE
those outputs live (need an API key, and a GPU for the scanner side;
nondeterministic).  [x]=done  [-]=not run

  Step performed                                              T1  T2  T3  T4
  Regenerate & PASS/FAIL-check the 12 paper floats (claims/)  [x] [-] [-] [-]
  Live mutate->scan (SkillMutator; regen Tables 3/4/5+Fig 4)  [-] [x] [x] [x]
      scale:                                              (sample)(17 skills,1 oracle)(17x3 oracles)
  Fine-tuning teacher data generation (distillation corpus)   [-] [-] [-] [x]   (<= 24 skills)
  Local 7B scanner inference with the RELEASED LoRA adapter   [-] [x] [x] [x]   (GPU; skip w/ --no-gpu)
  LoRA training (5-step demo; paper-scale not automated)      [-] [-] [-] [x]
  (Live runs rebuild Table 3 and Figure 4 in full, and the skill-security-scan, Snyk
   and LLM-scanner rows of Tables 4/5; SkillScan and prompt-injection-detector rows
   are verified at Tier 1 only.)

Reproduction at a glance (summary)
----------------------------------
Each claims/claimNN/ maps to one paper float; run.sh recomputes the aggregate
from bundled judge verdicts, writes it to results/, and compares it cell-by-cell
against the machine-readable paper golden in expected/metrics.json (paper-cited
values + tolerances; expected/PAPER_CITED_VALUES.md is the human-readable view),
printing ALL MATCH/MISMATCH. Claims 01-12 are CPU-only -- no API key, no GPU,
~minutes total. Table and figure numbers follow the paper; some internal script
and file names keep earlier draft numbers (e.g. claim01's build_table4.py builds
Table 3) and are identifiers only.

  Claim (dir)                     Paper float        Tier    Expected PASS (headline)
  claim01_oracle_refusal          Table 3            1 CPU   refusal 23.5/42.9/9.2% (4o-mini/5.4-mini/5.4)
  claim02_cross_scanner_detection Table 4            1 CPU   27/27 cells; rule-based 0-17%, GPT-5.4 up to 86.8%
  claim03_stealth_aware_selection Table 5            1 CPU   select vs no-select deltas match
  claim04_phase_ablation          Table 6            1 CPU   per-phase gains; refinement +11.9pp (Finding 6)
  claim05_wild_clawhub            Table 7            1 CPU   92.0% clean, 82.5% aggregate, 8.0% FPR (Finding 7)
  claim06_cost_envelope           Table 8            1 CPU   7B $0.0047/detection vs GPT-5.4 $0.0317 (Finding 8)
  claim07_unmodified_baseline     Table 10           1 CPU   LLM scanners flag 17/17 unmodified skills
  claim08_per_category_matrix     Table 11 (App. B)  1 CPU   recall 88.2%, precision 60.9%
  claim09_ier_dynamics            Figure 4           1 CPU   detection drops iter_0 -> iter_1 (all oracles)
  claim10_prefill_delta           Figure 5           1 CPU   Qwen +9.2pp; Llama/Mistral/Gemma down (Finding 5)
  claim11_finetune_base_models    Figure 5           1 CPU   4 families improve; Qwen strongest
  claim12_rq3_comparison          Figure 6           1 CPU   88.2% detection on n=76 (Finding 4)

  The two functional demos of core operation are NOT paper claims and are run
  directly from the code (no claims/ entry): the mutate->scan demo via
  artifact/code/skillmutator/run.sh (or ./run.sh --tier 2; needs OPENAI_API_KEY),
  and the distillation training-data generation via
  artifact/code/finetuning-framework/run.sh (Tier 4, capped demo).

Determinism: the CPU claims are deterministic recomputations from bundled
verdicts (values and tolerances in each claim's expected/metrics.json). The
live pipeline is nondeterministic (LLM sampling); Tier-2/3/4 outputs are close
to, not bit-identical with, the paper -- reproduce headline numbers as a mean
over repeated runs and pin model snapshots + seeds where supported.

Quick start (one command per tier)
----------------------------------
  # Tier 1  verify the 12 table/figure claims  CPU, no key, free, ~minutes   <-- START HERE
  ./install.sh && ./run.sh --tier 1

  # Tier 2  live demo on the sample skill   needs OPENAI_API_KEY (in .env)
  ./install.sh --generate && ./run.sh --tier 2 --no-gpu --env-file .env   # no GPU
  ./install.sh --all      && ./run.sh --tier 2 --env-file .env            # with a GPU (adds FT scan)

  # Tier 3  paper skills, default settings   key + (GPU unless --no-gpu) + network
  ./install.sh --all && ./run.sh --tier 3 --env-file .env

  # Tier 4  full benchmark + training demo   key + A100 80GB + network
  ./install.sh --all && ./run.sh --tier 4 --env-file .env

Before you start (two fresh-clone notes):
  - Permissions: the scripts are committed executable, but if your clone drops the
    bit ("permission denied"), just prefix bash:
        bash install.sh && bash run.sh --tier 1
    (and "bash claims/claimNN/run.sh" for a single claim).
  - venv on Debian / Ubuntu / Google Colab: if install.sh stops at "python3 -m venv"
    with "No module named ensurepip", install the separate venv package once and re-run:
        sudo apt-get update && sudo apt-get install -y python3-venv
    (or the version-specific package named in the error, e.g. python3.13-venv).

Options (add to any tier):
  - --no-gpu          skip the GPU finetune step (skillmutator side never needs a GPU)
  - --env-file PATH   load OPENAI_API_KEY
  - --dry-run         preview the plan + HW/SW/cost

Single claims run directly (cd claims/claim04_phase_ablation && ./run.sh);
full command/option reference in use.txt.

Expected Results
----------------
Values a successful run should reproduce, organized by paper float. Each Tier-1
claim's run.sh checks these against expected/metrics.json and prints ALL MATCH;
full per-float values also live in each claims/claimNN/expected/.

claim01 — Table 3: Oracle safety-refusal
  Oracle        Refusal rate     per-iter (0-4)
  gpt-4o-mini   23.53% (n=51)    4/12/14/11/12
  gpt-5.4-mini  42.86% (n=63)    0/15/22/22/27
  gpt-5.4        9.21% (n=76)    0/4/4/8/7

claim02 — Table 4: Cross-scanner detection, % by oracle (n=48/63/76)
  Scanner               4o-mini  5.4-mini  5.4
  skill-security-scan     2.08     6.35    7.89
  Snyk Agent Scan        16.67     9.52    9.21
  SkillScan API           0.00     0.00    1.32
  LLM-Guard               2.08     0.00    3.95
  PIGuard                39.58     4.76   17.11
  DataSentinel            4.17    11.11   10.53
  GPT-4o-mini            35.42     9.52   23.68
  GPT-5.4-mini           79.17    71.43   78.95
  GPT-5.4                89.58    88.89   86.84

claim03 — Table 5: Stealth-aware selection: select / no-select / delta (%)
  skill-security-scan    7.89 / 12.33 / +4.43
  Snyk Agent Scan        9.21 / 16.89 / +7.68
  SkillScan API          1.32 /  5.48 / +4.16
  GPT-4o-mini scanner   23.68 / 36.07 / +12.39
  GPT-5.4-mini scanner  78.95 / 87.67 / +8.72
  GPT-5.4 scanner       86.84 / 91.32 / +4.48
  Average (6 scanners)  34.65 / 41.63 / +6.98

claim04 — Table 6: Four-phase ablation (Finding 6): detection %
  Phase 1 (Purpose Grounding)          1.32
  + Phase 2 (Out-of-Scope Detection)  25.00
  + Phase 3 (Principle Reasoning)     57.89
  + Phase 4 (Category Labeling)       67.11
  + deterministic refinement          78.95
  + prefill (Phase-4 header forced)   88.16
  (deltas: schema +9.22, refinement +11.84, prefill +9.21 pp)

claim05 — Table 7: In-the-wild ClawHub (Finding 7)
  clean 92.0% ; suspicious LOW/MED/HIGH/CRIT 60.0/68.0/84.0/80.0% ;
  Aggregate 82.5% (FPR 8.0%)

claim06 — Table 8: Cost envelope (Finding 8): $/scan | recall | $/detection
  Qwen-7B + ours   0.00414 | 88.16% | 0.00469   (lowest $/detection)
  GPT-4o-mini      0.00178 | 23.68% | 0.00753
  GPT-5.4-mini     0.00664 | 78.95% | 0.00841
  GPT-5.4          0.02754 | 86.84% | 0.03171

claim07 — Table 10: Unmodified-baseline findings: skills-with / mean / max / total
  skill-security-scan     9/17 / 18.18 / 190 / 309
  Snyk Agent Scan         4/17 /  0.35 /   2 /   6
  GPT-4o-mini            17/17 /  7.12 /   9 / 121
  GPT-5.4-mini           17/17 /  6.41 /  10 / 109
  GPT-5.4                17/17 /  9.59 /  14 / 163
  SkillScan (upload API)  5/17 /  0.35 /   2 /   6

claim08 — Table 11: Per-category cell metrics (Appendix B)
  Recall 88.16% ; Precision 60.91% ; Specificity 80.54% ; F1 72.04% ;
  Balanced Acc 84.35%  (TP=67, FP=43, FN=9, TN=178)

claim09 — Figure 4: IER dynamics (see claims/claim09_ier_dynamics/data/image.png)
  Detection drops iter_0->iter_1 for every oracle, then plateaus:
  gpt-4o-mini 39.6->27.1, gpt-5.4-mini 84.1->73.0, gpt-5.4 92.1->85.5 (%).

claim10/claim11 — Figure 5: Phase-4 prefill, 4 base families (Finding 5;
  see claims/claim10_prefill_delta/data/prefill_delta_comparison.png)
  Prefill model-dependent (GPT-5.4 judge): Qwen +9.2, Llama -7.9, Mistral -17.1,
  Gemma -2.6 pp. Fine-tuning lifts all (base->ft): Qwen 17.1->88.2, Llama
  7.9->82.9, Mistral 5.3->72.4, Gemma 10.5->59.2 %.

claim12 — Figure 6: Fine-tuned vs frontier (Finding 4;
  see claims/claim12_rq3_comparison/data/rq3_finding1.png)
  On the n=76 GPT-5.4-oracle set: Qwen-7B (ours) 88.16% (67/76) -- matches/exceeds
  GPT-5.4 (86.84%) and GPT-5.4-mini (78.95%); rule-based/commercial scanners
  1.32-9.21% (GPT-4o-mini 23.68%, untuned Qwen base 17.11%).


SkillMutator Pipeline
---------------------
Mutate a sample skill, then scan it (live):
  - Run: ./install.sh --generate  ->  set OPENAI_API_KEY  ->
         cd artifact/code/skillmutator && ./run.sh   (or ./run.sh --tier 2)
  - What: mutates the bundled self-authored sample (examples/skills/weather-cache, MIT) with
    gpt-4o-mini, 1 refinement iteration, LLM-mode detection -> regenerates
    Tables 3/4/5 + Figure 4 (demo scale; a few cents; nondeterministic).
  - Paper skills: add --crawl N --registry {anthropic,clawhub} (see use.txt).
  - Stage map: paper Stages 1-4 -> analyze_skill / select_attacks /
    generate_scenarios / generate_skill
    (see artifact/code/README.md).

Fine-tuning Data Pipeline
-------------------------
Distillation data = a skill's SKILL.md (input) -> teacher four-phase analysis (target).
  - Demo input (no third-party content, no bundled mutation): the self-authored
    benign examples/skills/weather-cache plus the mutation that the SkillMutator
    step of the same Tier 2 run writes to artifact/code/skillmutator/demo-results/
    (generated at run time, gitignored).
  - Full corpus (1219 examples / 68 skills) NOT bundled -- from the authors on request.
  - Producing pipeline: artifact/code/finetuning-framework/
    (prepare_dataset -> formatter_v3 -> train -> merge -> serve -> run_scanner).
  - Tiers: inspect the format on CPU (no key); Tier 4 distills a capped corpus
    (API teacher) and runs a short training demo (A100); the full corpus and
    paper-scale training are not automated. Released adapters are on
    Hugging Face (Availability); Tiers 2-4 scan with them.

Directory layout
----------------
  artifact/
    code/
      skillmutator/          mutation + scan pipeline (src/skill_mutator/:
                             process/, scanners/llm_scanner (ours),
                             crawler/, llm/, utils/)
      finetuning-framework/  4-phase teacher analysis + reasoning-trajectory
                             distillation
      external_scanners/     held-out third-party scanner harness
      docs/                  attack_categories.json + code-level notes
    data/
      skills/                self-authored sample skill + SOURCES.csv
                             (third-party originals not redistributed)
      clawhub/               ClawHub corpus as metadata CSV (296 skills; raw not shipped)
      paper_shared/          judge configs, GT validation, cross-family judge,
                             base-model manifest
  infrastructure/            infrastructure.json (public-infra entry: URLs, resources, allocation)
  claims/                    claim01-12 (paper tables/figures); each has claim.txt,
                             run.sh, expected/  (functional demos live in
                             artifact/code/)
  install.sh  run.sh  README.txt  README.md  license.txt  use.txt  metadata.toml
  ETHICS.md

Safety / ethics
---------------
The benchmark consists of adversarial (mutated) Agent Skills with injected
malicious instructions, to be used ONLY as scanner inputs in an isolated
environment -- do not install or execute them against a live agent. These mutated
skills are NOT bundled (to prevent misuse); they are generated on disk only when
the live pipeline (Tier 2-4) is run. Payloads are
inert templates (no real credentials/secrets/live endpoints); raw scanner text
and full mutations are withheld (verdicts/aggregates only). See ETHICS.md
and use.txt. No personal data is included.

Public release
--------------
This artifact is publicly released under the MIT License (see license.txt) for
research and defensive use. Please cite the ACSAC 2026 paper (BibTeX in README.md).
