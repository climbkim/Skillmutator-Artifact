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
#   Tier 3  paper skills (no train) live mutate->scan->build on the paper's 17
#                                  Anthropic skills, one oracle at default settings
#                                  (CPU+API) + released-adapter scan (finetune, GPU).
#   Tier 4  full benchmark + train demo  full 3-oracle benchmark (CPU+API) + a short
#                                  LoRA training run on this run's mutations
#                                  (finetune, A100 80GB); scans use the released
#                                  adapter. Paper-scale training is not automated.
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
_CALLER_PWD="$PWD"
cd "$(dirname "$0")"

TIER=""
NO_GPU=0
ENV_FILE=""
DRY=0
while [ $# -gt 0 ]; do
  case "$1" in --tier|--env-file)
    [ $# -ge 2 ] || { echo "error: $1 needs a value (try --help)" >&2; exit 2; } ;; esac
  case "$1" in
    --tier)      TIER="$2"; shift 2 ;;
    --no-gpu)    NO_GPU=1; shift ;;
    --env-file)  ENV_FILE="$2"; shift 2 ;;
    --dry-run)   DRY=1; shift ;;
    -h|--help)   awk 'NR>1{print} NR>2 && /^# =====/{exit}' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1 (try --help)"; exit 2 ;;
  esac
done

case "$TIER" in 1|2|3|4) ;; *) echo "error: --tier must be 1, 2, 3 or 4 (try --help)"; exit 2 ;; esac
if [ -n "$ENV_FILE" ]; then
  case "$ENV_FILE" in /*|[A-Za-z]:*) ;; *) ENV_FILE="$_CALLER_PWD/$ENV_FILE" ;; esac
  [ -f "$ENV_FILE" ] || { echo "error: --env-file not found: $ENV_FILE" >&2; exit 2; }
fi

SM="artifact/code/skillmutator"
FT="artifact/code/finetuning-framework"
# Tiers 2-4 keep the live pipeline's data tree inside the skillmutator folder.
export SKILLMUTATOR_DATA_ROOT="$PWD/$SM/demo-data"
CLAIMS="claims"
source "$CLAIMS/_pyenv.sh"   # activate .venv (from install.sh) / python -> python3 fallback

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
 Data verification — regenerate the 12 claimed tables/figures from bundled outputs.
   HW : any CPU (no GPU).           SW : ./install.sh   (core deps only)
   Key: none.   Time: ~minutes.     Cost: $0 (no API calls).   (--no-gpu: no effect)
T1
  ;;
  2) cat <<'T2'
 Sample skill, no training.
   skillmutator: live mutate->scan->build on ONE sample skill (Tables 3/4/5 + Figure 4). CPU+API.
   finetune    : released-adapter scan of the bundled sample (no train). GPU.
   HW : CPU (skillmutator) + a CUDA GPU ~16GB for the 7B adapter scan (finetune).
        --no-gpu -> run the skillmutator demo only, skip the FT scan.
   SW : ./install.sh --generate  (+ --finetune for the finetune side).
   Key: OPENAI_API_KEY (oracle + LLM scanner + judge; judge on the FT side).
   Time: skillmutator ~3-6 min; finetune ~10-20 min (model load dominates).
   Cost (est., grounded in claim06):
     gpt-4o-mini default : a few US cents + ~$0.5 GPU (FT).
     GPT-5.4 paper setting: < $1 API + ~$0.5 GPU (FT).
T2
  ;;
  3) cat <<'T3'
 Paper skills, default settings, no training.
   skillmutator: live mutate->scan->build on the paper's 17 Anthropic evaluation
                 skills (git clone via `--crawl --registry anthropic`), ONE oracle
                 at the default settings: gpt-4o-mini oracle and judge, 2 iterations
                 (iter_0-1), no cross LLM scans, no no-select pass. This is not the
                 paper's procedure (3 oracles, iter_0-4, gpt-5.4 judge, cross scans,
                 no-select pass); use.txt section 4 gives the paper-setting command
                 for one oracle, and Tier 4 runs all of it. The ClawHub backend
                 (`--registry clawhub`, artifact/data/clawhub/clawhub_skills.csv) is
                 also available; see artifact/code/skillmutator/docs/SKILLS_SETUP.md.
   finetune    : released-adapter scan of one mutated + one benign skill (same as
                 Tier 2, no train). GPU.
   HW : CPU + network (skillmutator) + a CUDA GPU ~16GB for the 7B adapter scan.
        --no-gpu -> run the skillmutator step only, skip the FT scan.
   SW : ./install.sh --generate --finetune ; network (skills + HF adapter).
   Key: OPENAI_API_KEY.
   Time: hours (mutation scans are 15-76 s each); finetune ~10-20 min.
   Cost (est.): ~$2-3 API (gpt-4o-mini) + ~$0.5 GPU (FT).
T3
  ;;
  4) cat <<'T4'
 Full mutation benchmark + fine-tuning training demo.
   skillmutator: full benchmark over 3 oracles (gpt-4o-mini, gpt-5.4-mini, gpt-5.4),
                 5 iterations (iter_0-4), gpt-5.4 evaluation judge, cross LLM scans
                 (Table 4), + a gpt-5.4 no-select pass with cross LLM scans,
                 3 iterations (Table 5). CPU+API.
   finetune    : training-process demo. Teacher data-gen on up to 24 skills from the
                 last skillmutator pass, a 5-step LoRA run (Qwen), then a scan of one
                 mutated + one benign skill with the RELEASED adapter. A100 80GB.
                 It does not retrain the paper's adapters.
        --no-gpu -> run the 3-oracle mutation benchmark only, skip the finetune demo.
   HW : NVIDIA A100 80 GB (finetune demo).   SW : ./install.sh --all ; network.
   Key: OPENAI_API_KEY.
   Time / cost (est.):
     skillmutator : ~3 h+, ~$30+ API, expected ~$200 (the iter_0-4 + no-select + cross-scan +
                    gpt-5.4 judge run is not measured and costs more)
     finetune demo: ~1-2 h on an A100 incl. the ~15 GB base-model download
                    (~$1-2 GPU at the paper's $1.10/h); < $1 API with the default
                    gpt-4o-mini teacher and judge
   Paper-scale training (4 base families from scratch, ~25 A100-h MEASURED; full
     corpus distillation ~$40-60 with the GPT-5.4 teacher) is not automated. The
     paper's fine-tuning results are verified from bundled verdicts at Tier 1 and
     its cost in claim06. Manual steps: artifact/code/finetuning-framework/docs/REPRODUCE.md.
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
      bash "$SM/run.sh" --skill examples/skills/weather-cache ${ENV_FILE:+--env-file "$ENV_FILE"}
    if [ "$NO_GPU" = 1 ]; then
      skip_gpu_note "finetune: demo scan (released adapter, no train)"
    else
      run_step "finetune: demo scan (released adapter, no train)" \
        env SKIP_TRAIN=1 bash "$FT/run.sh"
    fi
    ;;

3)  # Paper skills, no training (released adapter).
    run_step "skillmutator: 17 Anthropic eval skills, default settings (auto-cloned, CPU+API)" \
      bash "$SM/run.sh" --crawl 17 --registry anthropic --skills-dir skills/anthropic ${ENV_FILE:+--env-file "$ENV_FILE"}
    if [ "$NO_GPU" = 1 ]; then
      skip_gpu_note "finetune: demo scan (released adapter, no train)"
    else
      run_step "finetune: demo scan (released adapter, no train)" \
        env SKIP_TRAIN=1 bash "$FT/run.sh"
    fi
    ;;

4)  # Full mutation benchmark + fine-tuning training demo.
    # Full benchmark = the 17 Anthropic eval skills (auto-cloned via --crawl
    # --registry anthropic) mutated by each oracle over 5 iterations
    # (iter_0-4, Figure 4; the no-select pass uses 3 iterations, iter_0-2). The LLM-scanner rows are adjudicated by the gpt-5.4
    # evaluation judge, and each scenario's final iteration is also scanned by the
    # other two LLM scanners (Table 4 cross cells). All runs accumulate into one
    # data tree (--keep-data); a gpt-5.4 no-select pass adds Table 5.
    run_step "clean the live data tree ($SM/demo-data)" rm -rf "$SM/demo-data"
    for m in gpt-4o-mini gpt-5.4-mini gpt-5.4; do
      run_step "skillmutator: full benchmark (oracle=$m, select, judge=gpt-5.4, CPU+API)" \
        bash "$SM/run.sh" --model "$m" --judge-model gpt-5.4 --iters 5 --cross-scan --keep-data \
             --crawl 17 --registry anthropic --skills-dir skills/anthropic ${ENV_FILE:+--env-file "$ENV_FILE"}
    done
    run_step "skillmutator: no-select pass (oracle=gpt-5.4, judge=gpt-5.4; Table 5)" \
      bash "$SM/run.sh" --model gpt-5.4 --judge-model gpt-5.4 --iters 3 --mode no-select --cross-scan --keep-data \
           --crawl 17 --registry anthropic --skills-dir skills/anthropic ${ENV_FILE:+--env-file "$ENV_FILE"}
    if [ "$NO_GPU" = 1 ]; then
      skip_gpu_note "finetune: training demo (data-gen + 5-step LoRA run) + released-adapter scan"
    else
      run_step "finetune: training demo (data-gen + 5-step LoRA run) + released-adapter scan" \
        bash "$FT/run.sh"
    fi
    ;;
esac

echo; echo "Tier $TIER dispatch complete$([ "$NO_GPU" = 1 ] && echo ' (--no-gpu: GPU steps skipped)')."
