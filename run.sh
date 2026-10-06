#!/usr/bin/env bash
# =============================================================================
# SkillMutator artifact — top-level reproduction driver.
#
# This is a THIN dispatcher: it does no work of its own, it only invokes the
# already-modularised sub-run.sh scripts (claims/*/run.sh,
# artifact/code/skillmutator/run.sh, artifact/code/finetuning-framework/run.sh)
# with the right flags/env for the requested reproduction tier.
#
#   Tier 1  data verification      regenerate the paper tables/figures from the
#                                  bundled judge outputs. CPU only, no key/GPU.
#   Tier 2  sample skill (no train) live mutate->scan->build on ONE sample skill
#                                  (skillmutator, CPU+API) + released-adapter scan
#                                  on the bundled sample (finetune, GPU).
#   Tier 3  paper skills (no train) download the paper's skills and reproduce at
#                                  full scale with the RELEASED adapter. API +GPU
#   Tier 4  full incl. training    full 3-oracle benchmark (CPU+API) + LoRA
#                                  training from scratch (finetune, A100 80GB).
#
# The tier sets how deep the reproduction goes and thus its hardware needs. The
# only optional axis is whether you have a GPU:
#   --no-gpu   run ONLY the parts that need no GPU (the CPU claims and the
#              skillmutator CPU+API pipeline); skip the GPU finetune steps.
# The skillmutator side never needs a GPU; the finetune side (7B scanner
# inference / LoRA training) does.
#
# Usage:
#   ./run.sh --tier 1
#   ./run.sh --tier 2 --env-file /path/.env             # full tier (needs a GPU for FT)
#   ./run.sh --tier 2 --no-gpu --env-file /path/.env    # CPU/API only (skip FT scan)
#   ./run.sh --tier 4 --env-file /path/.env
#   ./run.sh --tier 3 --dry-run                         # print plan + HW/SW + cost, run nothing
#
# Per-tier hardware/software requirements and expected time+cost are printed
# before each tier runs (and are documented in full in use.txt).
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")"

TIER=""
NO_GPU=0
ENV_FILE=""
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --tier)      TIER="$2"; shift 2 ;;
    --no-gpu)    NO_GPU=1; shift ;;
    --env-file)  ENV_FILE="$2"; shift 2 ;;
    --dry-run)   DRY=1; shift ;;
    -h|--help)   sed -n '2,46p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1 (try --help)"; exit 2 ;;
  esac
done

case "$TIER" in 1|2|3|4) ;; *) echo "error: --tier must be 1, 2, 3 or 4 (try --help)"; exit 2 ;; esac

SM="artifact/code/skillmutator"
FT="artifact/code/finetuning-framework"
CLAIMS="claims"

# Load env vars from --env-file, else from `.env` beside run.sh, so every
# sub-script inherits them. Placeholder values (your_..._here / sk-xxx / hf_xxx /
# generic xxx) and already-set environment vars are left untouched.
[ -z "$ENV_FILE" ] && [ -f ".env" ] && ENV_FILE=".env"
if [ -n "$ENV_FILE" ] && [ -f "$ENV_FILE" ]; then
  for _k in OPENAI_API_KEY SNYK_TOKEN HF_TOKEN ANTHROPIC_API_KEY LLM_PROVIDER LLM_MODEL WANDB_API_KEY WANDB_PROJECT; do
    eval "[ -n \"\${$_k:-}\" ]" && continue
    _val="$(grep -m1 "^$_k=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '\r' | sed -e 's/^"//' -e 's/"$//' || true)"
    case "$_val" in ""|your_*|sk-xxx*|hf_xxx*|xxx*|"<"*) continue ;; esac
    export "$_k=$_val"
  done
  echo "   (loaded env from $ENV_FILE)"
fi

run_step() {  # $1 = human label; rest = command
  local label="$1"; shift
  echo; echo ">>> $label"; echo "    \$ $*"
  if [ "$DRY" = 1 ]; then echo "    (dry-run: not executed)"; return 0; fi
  "$@"
}
skip_gpu_note() {  # $1 = what is skipped
  echo; echo ">>> $1"; echo "    (skipped: --no-gpu — this step needs a GPU)"
}

# --- per-tier expectation banners (HW / SW / time / cost) --------------------
print_banner() {
  local mode=""; [ "$NO_GPU" = 1 ] && mode="  [--no-gpu: CPU/API only]"
  echo "=============================================================="
  echo " SkillMutator artifact — TIER $TIER$mode"
  echo "=============================================================="
  case "$TIER" in
  1) cat <<'T1'
 Data verification — regenerate every paper table/figure from bundled outputs.
   HW : any CPU (no GPU).           SW : ./install.sh   (core deps only)
   Key: none.   Time: ~minutes.     Cost: $0 (no API calls).   (--no-gpu: no effect)
T1
  ;;
  2) cat <<'T2'
 Sample skill, no training.
   skillmutator: live mutate->scan->build on ONE sample skill (Tbl III/IV/V+Fig4). CPU+API.
   finetune    : released-adapter scan of the bundled sample (MODE=demo, no train). GPU.
   HW : CPU (skillmutator) + a CUDA GPU ~16GB for the 7B adapter scan (finetune).
        --no-gpu -> run the skillmutator demo only, skip the FT scan.
   SW : ./install.sh --generate  (+ --finetune for the finetune side).
   Key: OPENAI_API_KEY (oracle + LLM scanner + judge; teacher + judge on FT side).
   Time: skillmutator ~3-6 min; finetune ~10-20 min (model load dominates).
   Cost (est., grounded in claim06):
     gpt-4o-mini default : a few US cents + ~$0.5 GPU (FT).
     GPT-5.4 paper setting: < $1 API + ~$0.5 GPU (FT).
T2
  ;;
  3) cat <<'T3'
 Paper skills, no training (RELEASED adapter).
   Downloads the paper's skills and reproduces at full scale. The skillmutator
   step auto-downloads the 17 Anthropic evaluation skills (git clone via
   `--crawl --registry anthropic`); the ClawHub community backend
   (`--registry clawhub`, reading artifact/data/clawhub/clawhub_skills.csv) is
   also available for the wild-eval / training corpus. See
   artifact/code/skillmutator/docs/SKILLS_SETUP.md.
   HW : CPU + network (skillmutator) + A100-class GPU for vLLM batch scan (FT).
        --no-gpu -> run the skillmutator full-scale mutation only, skip the FT scan.
   SW : ./install.sh --generate --finetune ; network (skills + HF adapter).
   Key: OPENAI_API_KEY.
   Time: hours (mutation scans are 15-76 s each; FT batch scan ~1-2 A100-h).
   Cost (est., single oracle, n~76):
     gpt-4o-mini : ~$2-3 API + ~1-2 A100-h (~$2-4).
     GPT-5.4     : ~$15-25 API + ~1-2 A100-h (~$2-4).
T3
  ;;
  4) cat <<'T4'
 FULL reproduction incl. training.  ~1.5 DAYS total, budgeted generously.
   skillmutator: full benchmark over 3 oracles (gpt-4o-mini, gpt-5.4-mini, gpt-5.4). CPU+API.
   finetune    : teacher data-gen + LoRA training of Figure 5's 4 base families
                 from scratch + inference. A100 80GB.
        --no-gpu -> run the 3-oracle mutation benchmark only, skip FT train+scan.
   HW : NVIDIA A100 80 GB (training + vLLM).   SW : ./install.sh --all ; network.
   Key: OPENAI_API_KEY.
   Per-stage time / cost (GPU at the paper's $1.10/h, claim06):
     0 setup    (deps + base 7B ~15GB + adapters ~2.5GB) CPU+net  ~1.5 h  bandwidth
     1 skillmut (mutate 17 skills x3 oracles + LLM-scan)  CPU+API  ~3   h  ~$30 API (est.)
     2 data-gen (teacher 4-phase distill -> 1219-ex corpus, ~4,900 calls) API ~5-10 h  ~$40-60 (GPT-5.4 teacher, RECORDED ledger; ~$4 if gpt-4o-mini)
     3 training (4 base families, 5 epochs, from scratch) A100     ~25  h  ~25 A100-h ~$28 (MEASURED: Qwen 4.5 / Llama 5.0 / Gemma 10.0 / Mistral ~5.5)
     4 inference(batch-scan eval set per model, vLLM)     A100     ~3   h  ~3-4 A100-h ~$3-4
     5 judge+build (adjudicate + render floats)           API+CPU  ~1   h  ~$1-3
     TOTAL                                                A100 80GB ~1.5 day (~40h)  ~$75 (gpt-4o-mini teacher) - ~$130 (GPT-5.4 teacher), incl. ~28 A100-h (~$31)
   Notes: Fig 5 compares 4 base families, each trained from scratch (loop
     BASE_MODEL over the 4) -> multi-model training is what makes this ~1.5 days; a
     single Qwen scanner alone is only 4.5 h. The teacher distillation (stage 2) is
     the heavy API step -- RECORDED at ~$40-60 with GPT-5.4 (run.sh demo default is
     gpt-4o-mini ~$4). Stage-1 eval gen is estimated (per-scan scanning ~$3 total).
     Also redoing every Table VI phase + a/epoch ablation is the full ~72 A100-h
     (~3-day, ~$80) campaign. Reviewers verify all of it from verdicts at Tier 1.
T4
  ;;
  esac
  echo "=============================================================="
}

print_banner

# --- Tier dispatch (delegates to the existing sub-run.sh's) ------------------
# skillmutator steps run on CPU+API and always execute. finetune steps need a
# GPU and are skipped under --no-gpu (except Tier-1 claims, which are CPU).
case "$TIER" in

1)  # CPU claim/data verification. No key, no GPU (both sides' claims are CPU).
    ALL_CLAIMS="claim01_oracle_refusal claim02_cross_scanner_detection claim03_stealth_aware_selection claim04_phase_ablation claim05_wild_clawhub claim06_cost_envelope claim07_unmodified_baseline claim08_per_category_matrix claim09_ier_dynamics claim10_prefill_delta claim11_finetune_base_models claim12_rq3_comparison"
    for c in $ALL_CLAIMS; do run_step "claim: $c" bash "$CLAIMS/$c/run.sh"; done
    ;;

2)  # Sample skill, no training.
    run_step "skillmutator: sample mutate->scan->build (CPU+API)" \
      bash "$SM/run.sh" ${ENV_FILE:+--env-file "$ENV_FILE"}
    if [ "$NO_GPU" = 1 ]; then
      skip_gpu_note "finetune: demo scan (released adapter, no train)"
    else
      run_step "finetune: demo scan (released adapter, no train)" \
        env MODE=demo SKIP_TRAIN=1 bash "$FT/run.sh"
    fi
    ;;

3)  # Paper skills, no training (released adapter).
    run_step "skillmutator: full-scale over the 17 Anthropic eval skills (auto-cloned, CPU+API)" \
      bash "$SM/run.sh" --crawl 17 --registry anthropic --skills-dir "$SM/skills" ${ENV_FILE:+--env-file "$ENV_FILE"}
    if [ "$NO_GPU" = 1 ]; then
      skip_gpu_note "finetune: full-scale scan with released adapter (no train)"
    else
      run_step "finetune: full-scale scan with released adapter (no train)" \
        env MODE=full SKIP_TRAIN=1 bash "$FT/run.sh"
    fi
    ;;

4)  # Full reproduction incl. training.
    # Full benchmark = the 17 Anthropic eval skills mutated by each oracle
    # (auto-cloned via --crawl --registry anthropic); judge fixed to gpt-5.4.
    for m in gpt-4o-mini gpt-5.4-mini gpt-5.4; do
      run_step "skillmutator: full benchmark (oracle=$m, judge=gpt-5.4, CPU+API)" \
        bash "$SM/run.sh" --model "$m" --judge-model gpt-5.4 \
             --crawl 17 --registry anthropic --skills-dir "$SM/skills" ${ENV_FILE:+--env-file "$ENV_FILE"}
    done
    if [ "$NO_GPU" = 1 ]; then
      skip_gpu_note "finetune: full train-from-scratch + scan"
    else
      run_step "finetune: full train-from-scratch + scan" \
        env MODE=full bash "$FT/run.sh"
    fi
    ;;
esac

echo; echo "Tier $TIER dispatch complete$([ "$NO_GPU" = 1 ] && echo ' (--no-gpu: GPU steps skipped)')."
