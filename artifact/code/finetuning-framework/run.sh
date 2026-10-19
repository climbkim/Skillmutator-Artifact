#!/usr/bin/env bash
# =============================================================================
# finetuning-framework end-to-end reproduction driver.
#
#   [A] data-gen : distill a training corpus from a skill collection (teacher;
#                  at most DATAGEN_MAX skills)
#   [B] train    : short LoRA run on that corpus (MAX_STEPS steps, Qwen config).
#                  It shows the training process; it does not rebuild the
#                  paper's adapters, and [C]-[F] use the released adapter.
#   [C] adapter  : download the RELEASED adapter from the Hub (used for scanning)
#   [D] scan     : scan a mutated skill with the fine-tuned adapter
#   [E] judge    : adjudicate the scan into a judge_summary.csv
#   [F] tables   : render paper-shaped tables/figures FROM THIS RUN's scan data
#
# Tables/figures are generated from the data produced in THIS run, not from
# hard-coded numbers: a small illustrative table in the paper's schema (one
# mutated + one benign skill). Paper-scale training and batch scanning are not
# automated here (see the note printed at the end and docs/REPRODUCE.md); the
# paper's fine-tuning floats are verified from bundled verdicts at Tier 1.
#
# >>> EXECUTION REQUIREMENT: NVIDIA A100 80 GB GPU. <<<
# The whole pipeline (teacher data-gen, LoRA training, adapter merge/inference)
# assumes an A100 80 GB. This is NOT the CPU-only claim-verification path — that
# lives under ../../claims/ and needs no GPU or API key.
#
# Env knobs (demo defaults shown):
#   BENIGN_SKILL=examples/skills/weather-cache   self-authored benign sample (MIT)
#   MUTATION_RESULTS=../skillmutator/demo-results
#                             mutations written by the SkillMutator step of the
#                             same run (./run.sh --tier 2 runs it first). No
#                             mutated skill is bundled with the artifact.
#   SKILLS_DIR=<auto>         corpus for [A] data-gen (default: BENIGN_SKILL +
#                             MUTATION_RESULTS, assembled under OUTPUT_DIR)
#   SCAN_TARGET=<auto>        mutated skill scanned in [D] (default: first
#                             mutation found under MUTATION_RESULTS)
#   SCAN_CATEGORY=<auto>      injected category of SCAN_TARGET
#   TEACHER=gpt-4o-mini       teacher model for [A] (cost-friendly default)
#   ADAPTER_REPO=<hf repo id> released adapter to download in [C] (REQUIRED for D-F)
#   ADAPTER_REVISION=<commit> Hub revision of the adapter (default: pinned paper release)
#   BASE_MODEL=Qwen/Qwen2.5-Coder-7B-Instruct
#   OUTPUT_DIR=./output_demo
#   MAX_STEPS=5               training steps for [B] (short demo run)
#   DATAGEN_MAX=24            skills distilled in [A] (benign first; 0 = all)
#   DATASET_DIR=$OUTPUT_DIR/dataset   corpus written by [A], read by [B]
#   SKIP_TRAIN=0 SKIP_SCAN=0  set to 1 to skip a stage
#   SKIP_DATAGEN=$SKIP_TRAIN  [A] only feeds [B], so it is skipped with SKIP_TRAIN=1
#
# Requires OPENAI_API_KEY (teacher in [A]; judge in [E]).
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")"
# Run on its own, use the artifact's .venv like the top-level run.sh does.
[ -f ../../../claims/_pyenv.sh ] && source ../../../claims/_pyenv.sh

# load a .env if present (OPENAI_API_KEY, ADAPTER_REPO, ...) before reading vars
for envf in .env ../.env ../../../.env; do
  if [ -f "$envf" ]; then set -a; . "$envf"; set +a; echo "[run.sh] loaded env: $envf"; break; fi
done

BENIGN_SKILL="${BENIGN_SKILL:-examples/skills/weather-cache}"
MUTATION_RESULTS="${MUTATION_RESULTS:-../skillmutator/demo-results}"
SKILLS_DIR="${SKILLS_DIR:-}"
SCAN_TARGET="${SCAN_TARGET:-}"
SCAN_CATEGORY="${SCAN_CATEGORY:-}"
TEACHER="${TEACHER:-gpt-4o-mini}"
JUDGE_MODEL="${JUDGE_MODEL:-gpt-4o-mini}"
BASE_MODEL="${BASE_MODEL:-Qwen/Qwen2.5-Coder-7B-Instruct}"
ADAPTER_REPO="${ADAPTER_REPO:-climbkim/skillmutator-scanner-adapters}"
ADAPTER_MODEL="${ADAPTER_MODEL:-Qwen2.5-Coder-7B-Instruct}"
OUTPUT_DIR="${OUTPUT_DIR:-./output_demo}"
MAX_STEPS="${MAX_STEPS:-5}"
DATAGEN_MAX="${DATAGEN_MAX:-24}"
DATASET_DIR="${DATASET_DIR:-$OUTPUT_DIR/dataset}"
SKIP_TRAIN="${SKIP_TRAIN:-0}"
SKIP_SCAN="${SKIP_SCAN:-0}"
SKIP_DATAGEN="${SKIP_DATAGEN:-$SKIP_TRAIN}"
CONFIG="src/skill_scanner_finetune/finetune/configs/qwen_default.yaml"

PY="${PYTHON:-python}"
# make `python -m skill_scanner_finetune...` importable without pip-installing
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p "$OUTPUT_DIR"

# --- demo inputs: the benign sample + the mutation produced earlier in this run --
# SkillMutator writes mutations as
#   <MUTATION_RESULTS>/<skill>/<ts>_<mode>/generate_skill/<category>/iter_<N>/skills/SKILL.md
# and formatter_v3 labels any SKILL.md under .../generate_skill/<category>/iter_<N>/
# as a mutation of <category>, so that tree is used as-is.
if [ -z "$SCAN_TARGET" ]; then
  _found=""
  for _d in "$MUTATION_RESULTS"/*/*/generate_skill/*/iter_*/skills; do
    [ -f "$_d/SKILL.md" ] && _found="$_d"   # glob order: category, then iteration -> keeps the last
  done
  if [ -z "$_found" ]; then
    echo "[run.sh] no mutated skill under $MUTATION_RESULTS."
    echo "         Mutated skills are not bundled; generate one first with"
    echo "         ../skillmutator/run.sh (or ./run.sh --tier 2 from the artifact root),"
    echo "         or set SCAN_TARGET / SCAN_CATEGORY / SKILLS_DIR to your own skills."
    exit 1
  fi
  SCAN_TARGET="${_found%/}"
  if [ -z "$SCAN_CATEGORY" ]; then
    _cat="$(echo "$SCAN_TARGET" | sed -E 's#.*/generate_skill/([^/]+)/iter_.*#\1#')"
    SCAN_CATEGORY="$("$PY" -c 'import sys; sys.path.insert(0, "src"); from skill_scanner_finetune.dataset_builder.taxonomy import normalize_attack_category as n; print(n(sys.argv[1]) or sys.argv[1])' "$_cat")"
  fi
fi
if [ -z "$SKILLS_DIR" ]; then
  SKILLS_DIR="$OUTPUT_DIR/skills_input"
  rm -rf "$SKILLS_DIR"; mkdir -p "$SKILLS_DIR/benign"
  cp -r "$BENIGN_SKILL" "$SKILLS_DIR/benign/"
  if [ -d "$MUTATION_RESULTS" ]; then cp -r "$MUTATION_RESULTS" "$SKILLS_DIR/mutated"; fi
fi
echo "[run.sh] benign sample : $BENIGN_SKILL"
echo "[run.sh] scan target   : $SCAN_TARGET  (category: $SCAN_CATEGORY)"

echo "=============================================================="
echo " finetuning-framework run.sh  [GPU required for [B] train and [D] scan]"
echo "=============================================================="

: "${OPENAI_API_KEY:?[run.sh] OPENAI_API_KEY is required (teacher for [A], judge for [E]). Put it in a .env file.}"

# --- [A] training-data generation --------------------------------------------
if [ "$SKIP_DATAGEN" = "1" ]; then
  echo; echo "== [A] data-gen: SKIPPED (SKIP_DATAGEN=1; the corpus only feeds [B]) =="
else
  echo; echo "== [A] data-gen: distill training corpus from $SKILLS_DIR (teacher=$TEACHER, at most $DATAGEN_MAX skills) =="
  "$PY" scripts/prepare_dataset.py \
      --skills-dir "$SKILLS_DIR" \
      --teacher    "$TEACHER" \
      --max-items  "$DATAGEN_MAX" \
      --output-dir "$DATASET_DIR"
fi

# --- [B] short training run --------------------------------------------------
if [ "$SKIP_TRAIN" = "1" ]; then
  echo; echo "== [B] train: SKIPPED (SKIP_TRAIN=1) =="
else
  echo; echo "== [B] train: LoRA fine-tune on $DATASET_DIR (--max-steps $MAX_STEPS) =="
  echo "   (this demonstrates the training PROCESS; scanning below uses the"
  echo "    released adapter from [C], not this short run)"
  "$PY" scripts/train.py --config "$CONFIG" --max-steps "$MAX_STEPS" \
      --train-file "$DATASET_DIR/train.jsonl" --val-file "$DATASET_DIR/val.jsonl" \
      --output-dir "$OUTPUT_DIR/train"
  echo "[run.sh] short-run adapter -> $OUTPUT_DIR/train/final"
fi

if [ "$SKIP_SCAN" = "1" ]; then
  echo; echo "== [D]-[F] scan/judge/tables: SKIPPED (SKIP_SCAN=1) =="
  echo "[run.sh] done (data-gen + train only)."
  exit 0
fi

# --- [C] download + extract the released adapter -----------------------------
echo; echo "== [C] adapter: download+extract released LoRA adapter ($ADAPTER_MODEL) =="
ADAPTER_DIR="$("$PY" scripts/fetch_adapter.py --repo "$ADAPTER_REPO" --model "$ADAPTER_MODEL" --out "$OUTPUT_DIR/adapter" | tail -1)"
echo "[run.sh] adapter dir: $ADAPTER_DIR"

# --- [D] scan a positive (mutated) and a negative (benign) sample skill ------
SCAN_BENIGN="${SCAN_BENIGN:-$BENIGN_SKILL}"
mkdir -p "$OUTPUT_DIR/scan"
echo; echo "== [D] scan (positive): $SCAN_TARGET with fine-tuned adapter =="
"$PY" -m skill_scanner_finetune.finetune.infer \
    --base "$BASE_MODEL" --lora "$ADAPTER_DIR" \
    --skill "$SCAN_TARGET" | tee "$OUTPUT_DIR/scan/scan_pos.md"
echo; echo "== [D] scan (negative/unmodified): $SCAN_BENIGN =="
"$PY" -m skill_scanner_finetune.finetune.infer \
    --base "$BASE_MODEL" --lora "$ADAPTER_DIR" \
    --skill "$SCAN_BENIGN" | tee "$OUTPUT_DIR/scan/scan_neg.md"

# --- [E] judge both scans into positive / negative judge_summary CSVs ---------
echo; echo "== [E] judge: adjudicate scans -> judge_summary.csv / judge_neg.csv =="
"$PY" analysis/judge_scan_to_csv.py \
    --scan-file     "$OUTPUT_DIR/scan/scan_pos.md" \
    --skill         "$(basename "$SCAN_TARGET")" \
    --category      "$SCAN_CATEGORY" \
    --injected-file "$SCAN_TARGET/SKILL.md" \
    --judge-model   "$JUDGE_MODEL" \
    --out-csv       "$OUTPUT_DIR/scan/judge_summary.csv"
"$PY" analysis/judge_scan_to_csv.py \
    --scan-file     "$OUTPUT_DIR/scan/scan_neg.md" \
    --skill         "$(basename "$SCAN_BENIGN")" \
    --category      "NONE" \
    --injected-file "$SCAN_BENIGN/SKILL.md" \
    --judge-model   "$JUDGE_MODEL" \
    --out-csv       "$OUTPUT_DIR/scan/judge_neg.csv"

# --- [F] render every fine-tuning-side float as a claims-mirroring CSV --------
echo; echo "== [F] tables: build paper-structured CSVs from this run's data =="
"$PY" analysis/build_claim_tables.py \
    --judge-csv "$OUTPUT_DIR/scan/judge_summary.csv" \
    --neg-csv   "$OUTPUT_DIR/scan/judge_neg.csv" \
    --out-dir   "$OUTPUT_DIR/claim_tables" \
    --label     "this run"

echo; echo "== [F] check: verify generated CSVs match the paper structure =="
"$PY" analysis/check_claim_tables.py --tables-dir "$OUTPUT_DIR/claim_tables"

echo; echo "=============================================================="
echo " done. paper-structured CSVs (claims-mirroring) -> $OUTPUT_DIR/claim_tables"
echo " one subdir per float (claim04/05/06/07/08/11/12), each a CSV in the"
echo " paper's row/column structure; measured cells filled from this run,"
echo " multi-run cells left as skeleton (status=full-mode)."
echo "=============================================================="
echo
echo "Paper-scale training is not automated by this script. It means: the full"
echo "corpus (prepare_dataset.py --teacher gpt-5.4, no --max-items), a full run"
echo "per base model (MAX_STEPS=-1; only the Qwen config is shipped), a batch"
echo "scan of the n=76 GPT-5.4-oracle tree (skill_scanner_finetune.finetune.eval_infer_vllm),"
echo "then analysis/rq3/scripts/build_tab_finetune.py (Figure 5) and"
echo "analysis/rq4/scripts/build_tab_phase_ablation.py (Table 6). See"
echo "docs/REPRODUCE.md. The paper's values are verified at Tier 1."
