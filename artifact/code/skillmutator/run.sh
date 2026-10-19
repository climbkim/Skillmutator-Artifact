#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# SkillMutator reproduction demo — mutate a sample skill, scan it, and build
# the mutation-side paper floats from the run:
#
#     Table 3  (safety-refusal summary)
#     Table 4   (cross-scanner detection matrix)
#     Table 5    (select vs no-select)
#     Figure 4   (Iterative Evasion Refinement per-iteration dynamics)
#
# These are the same floats the CPU-only claims (claim01 / claim02 / claim03 /
# claim09) verify against bundled verdicts; this script regenerates them LIVE
# from the released pipeline so the code path is demonstrably exercised.
#
#   *** REQUIRES an OpenAI API key (OPENAI_API_KEY). ***
# The adversarial oracle (mutation), the LLM scanner, and the judge all call the
# OpenAI API. The default model is the cheapest, gpt-4o-mini; override it below.
# The key is taken from the environment, or auto-loaded from a .env file.
#
# DEMO SCALE: by default this runs ONE sample skill against ONE oracle, so the
# generated floats prove the flow and show the paper's exact format — the
# numbers are sample-scale, NOT the paper's. Reproducing the paper's actual
# numbers needs the full benchmark (17 skills x 13 categories x 3 oracles x 5
# scanners + GPT-5.4 judge); see docs/REPRODUCE.md.
#
# Usage:
#   ./run.sh                         # sample skill, gpt-4o-mini oracle+scanner+judge
#   ./run.sh --model gpt-5.4-mini    # change the oracle / LLM-scanner model
#   ./run.sh --judge-model gpt-5.4   # evaluation judge for the LLM-scanner rows
#                                    #   (Figure 7 prompt; paper uses gpt-5.4)
#   ./run.sh --cross-scan            # also scan each scenario's final iteration
#                                    #   with the other two LLM scanners (Table 4
#                                    #   cross cells; extra API cost)
#   ./run.sh --iters 3 --mode no-select   # 3 iterations (iter_0..iter_2) / no-select pass
#   ./run.sh --keep-data             # keep other oracles/modes already in the data
#                                    #   tree (used by the top-level Tier 4 loop)
#   ./run.sh --skill path/to/skill   # mutate a different single skill folder
#                                    #   (the ./skills pool is then not used)
#   ./run.sh --env-file path/to/.env # load OPENAI_API_KEY from this .env file
#   ./run.sh --crawl 10              # (EXPERIMENTAL) crawl N community skills into
#                                    #   --skills-dir first, then mutate the whole
#                                    #   pool instead of the single sample
#                                    #   (default dir with --crawl: ./skills/<registry>,
#                                    #   so skills from different registries never mix)
#   ./run.sh --crawl 10 --registry clawhub --skills-dir ./skills/clawhub
#
# NOTE on --crawl: it drives scripts/crawl_skills.py. Bundled registries:
#   --registry anthropic : clone github.com/anthropics/skills, copy the 17 paper
#                          evaluation skills (the mutation-benchmark set).
#   --registry clawhub   : read a ClawHub manifest CSV (artifact/data/clawhub/
#                          clawhub_skills.csv, or $SKILLMUTATOR_CLAWHUB_CSV) and
#                          fetch each skill's SKILL.md from the ClawHub API.
# No skill bodies are redistributed; the backends re-fetch from public sources.
# If no skills are obtained, the demo falls back to the bundled sample skill.
# See docs/SKILLS_SETUP.md.
# ---------------------------------------------------------------------------
set -euo pipefail
_CALLER_PWD="$PWD"
cd "$(dirname "$0")"
# Run on its own, use the artifact's .venv like the top-level run.sh does.
[ -f ../../../claims/_pyenv.sh ] && source ../../../claims/_pyenv.sh

MODEL="gpt-4o-mini"
JUDGE_MODEL="gpt-4o-mini"
SKILL="examples/skills/weather-cache"   # self-authored benign sample (MIT)
SKILL_SET=0                             # 1 when --skill is given
ENV_FILE=""
CRAWL_N=0
REGISTRY="clawhub"
SKILLS_DIR=""                           # default ./skills (./skills/<registry> with --crawl)
MAX_ITERS="${MAX_ITERS:-2}"     # N iterations (iter_0..iter_{N-1}); paper: 5 for select, 3 for no-select
MUT_MODE="select"               # select (stealth-aware) | no-select (all 13 categories)
KEEP_DATA=0
CROSS_SCAN=0
while [ $# -gt 0 ]; do
  case "$1" in --model|--judge-model|--skill|--env-file|--crawl|--registry|--skills-dir|--iters|--mode)
    [ $# -ge 2 ] || { echo "error: $1 needs a value (try --help)" >&2; exit 2; } ;; esac
  case "$1" in
    --model)       MODEL="$2"; shift 2 ;;
    --judge-model) JUDGE_MODEL="$2"; shift 2 ;;
    --skill)       SKILL="$2"; SKILL_SET=1; shift 2 ;;
    --env-file)    ENV_FILE="$2"; shift 2 ;;
    --crawl)       CRAWL_N="$2"; shift 2 ;;
    --registry)    REGISTRY="$2"; shift 2 ;;
    --skills-dir)  SKILLS_DIR="$2"; shift 2 ;;
    --iters)       MAX_ITERS="$2"; shift 2 ;;
    --mode)        MUT_MODE="$2"; shift 2 ;;
    --keep-data)   KEEP_DATA=1; shift ;;
    --cross-scan)  CROSS_SCAN=1; shift ;;
    -h|--help)     sed -n '2,52p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1 (try --help)"; exit 2 ;;
  esac
done
if [ -n "$ENV_FILE" ]; then
  case "$ENV_FILE" in /*|[A-Za-z]:*) ;; *) ENV_FILE="$_CALLER_PWD/$ENV_FILE" ;; esac
  [ -f "$ENV_FILE" ] || { echo "error: --env-file not found: $ENV_FILE" >&2; exit 2; }
fi
if [ -z "$SKILLS_DIR" ]; then
  if [ "$CRAWL_N" -gt 0 ]; then SKILLS_DIR="./skills/$REGISTRY"; else SKILLS_DIR="./skills"; fi
fi
case "$MUT_MODE" in
  select|no-select) ;;
  *) echo "error: --mode must be select or no-select (got '$MUT_MODE')" >&2; exit 2 ;;
esac
case "$MODEL" in
  ""|*/*|.|..) echo "error: --model must be a model name such as gpt-4o-mini (got '$MODEL')" >&2; exit 2 ;;
esac

# Auto-load scanner credentials from a .env file so `./run.sh` works as a
# single command. Search order: --env-file, then .env beside run.sh and up to
# three parent directories; the first file found is used.
#   OPENAI_API_KEY : REQUIRED (adversarial oracle + LLM scanner + judge).
#   SNYK_TOKEN     : OPTIONAL — enables the Snyk Agent scanner. Without it the
#                    Snyk column is left unavailable and the demo still shows
#                    the LLM scanner vs. skill-security (the paper's key story).
#   LLM_PROVIDER / LLM_MODEL : OPTIONAL LLM-scanner defaults.
_load_env_var() {  # $1 = var name; only sets it if not already in the environment
  eval "[ -n \"\${$1:-}\" ]" && return 0
  for _env in "$ENV_FILE" .env ../.env ../../.env ../../../.env; do
    [ -n "$_env" ] && [ -f "$_env" ] || continue
    _val="$(grep -m1 "^$1=" "$_env" 2>/dev/null | cut -d= -f2- | tr -d '\r' | sed -e 's/^"//' -e 's/"$//' || true)"
    [ -n "$_val" ] || continue
    # skip .env.example placeholders, like the top-level run.sh
    case "$_val" in your_*|sk-xxx*|hf_xxx*|xxx*|"<"*) continue ;; esac
    export "$1=$_val"
    echo "   (loaded $1 from $_env)"
    return 0
  done
  return 1
}
_load_env_var OPENAI_API_KEY || true
_load_env_var SNYK_TOKEN    || echo "   (no SNYK_TOKEN found, or only a placeholder -> Snyk unavailable; its table cells show n/a)"
_load_env_var LLM_PROVIDER  || true
_load_env_var LLM_MODEL     || true
: "${OPENAI_API_KEY:?Set OPENAI_API_KEY (env var), or put it in a .env beside run.sh / pass --env-file}"

# Dependency guard (generation extras).
python - <<'PYCHK' || { echo "Missing generation deps. Install: ./install.sh --generate"; exit 1; }
import importlib.util, sys
need = ("openai","langchain_core","langchain_openai","langgraph","tiktoken","dotenv")
sys.exit(1 if [m for m in need if importlib.util.find_spec(m) is None] else 0)
PYCHK

# Judge preflight: one short call, so a key without access to the judge model
# fails here and not after the (costly) mutation step.
echo "== [check] evaluation judge ($JUDGE_MODEL) answers with this API key =="
python - "$JUDGE_MODEL" <<'PYJUDGE'
import sys
sys.path.insert(0, "analysis")
from skillmutator_utils.judge import JudgeError, judge_call
try:
    judge_call("preflight", "Data Exfiltration", "preflight", "", "(none)", "(empty)",
               model=sys.argv[1], retries=2)
except JudgeError as e:
    sys.exit(f"error: {e}\n       Pick a judge model this key can use (--judge-model); the paper uses gpt-5.4.")
PYJUDGE

# --- Skill selection ------------------------------------------------------
# Build the list of skills to mutate. Default: the single bundled sample.
# With --crawl N, first populate $SKILLS_DIR via scripts/crawl_skills.py, then
# mutate every skill found there.
SKILLS=()
if [ "$CRAWL_N" -gt 0 ]; then
  echo "== [crawl] fetch $CRAWL_N skills via crawl_skills.py (registry=$REGISTRY -> $SKILLS_DIR) =="
  mkdir -p "$SKILLS_DIR"
  if ! python scripts/crawl_skills.py --registry "$REGISTRY" \
         --target-count "$CRAWL_N" --output-dir "$SKILLS_DIR"; then
    echo "   crawl_skills.py did not produce skills for registry '$REGISTRY'."
    echo "   Check network access (anthropic: git clone; clawhub: ClawHub API +"
    echo "   a manifest CSV via \$SKILLMUTATOR_CLAWHUB_CSV), or drop skills into"
    echo "   $SKILLS_DIR manually (see docs/SKILLS_SETUP.md)."
  fi
  for _d in "$SKILLS_DIR"/*/; do
    [ -f "${_d}SKILL.md" ] && SKILLS+=("${_d%/}")
  done
  if [ "${#SKILLS[@]}" -eq 0 ]; then
    echo "   no crawled skills found -> falling back to the bundled sample skill."
  fi
fi
# No --crawl and no --skill, but --skills-dir already holds a pool of skills (each
# a subdir with a SKILL.md): mutate all of them. Lets you point the pipeline at
# your own skills. An explicit --skill always mutates just that one skill.
if [ "${#SKILLS[@]}" -eq 0 ] && [ "$SKILL_SET" = 0 ] && [ -d "$SKILLS_DIR" ]; then
  for _d in "$SKILLS_DIR"/*/; do
    [ -f "${_d}SKILL.md" ] && SKILLS+=("${_d%/}")
  done
  [ "${#SKILLS[@]}" -gt 0 ] && \
    echo "== [pool] mutating ${#SKILLS[@]} skill(s) already in $SKILLS_DIR (no --crawl) =="
fi
[ "${#SKILLS[@]}" -eq 0 ] && SKILLS=("$SKILL")

echo "== SkillMutator demo =="
echo "   oracle/scanner model : $MODEL   (default gpt-4o-mini; override with --model)"
echo "   judge model          : $JUDGE_MODEL (override with --judge-model; paper uses gpt-5.4)"
echo "   skills (${#SKILLS[@]})            : ${SKILLS[*]}"
echo "   NOTE: demo scale (${#SKILLS[@]} skill(s), 1 oracle). Full paper numbers -> docs/REPRODUCE.md."
echo

RESULTS="./demo-results"
export SKILLMUTATOR_DATA_ROOT="${SKILLMUTATOR_DATA_ROOT:-$PWD/demo-data}"
export SKILLMUTATOR_ORACLE="$MODEL"   # Table 5 (select) uses this oracle

# Only clean a data tree this script owns: its own ./demo-data, or a folder it
# created earlier (marker file). Any other non-empty folder is left untouched.
_MARK="$SKILLMUTATOR_DATA_ROOT/.skillmutator-run"
if [ "$SKILLMUTATOR_DATA_ROOT" != "$PWD/demo-data" ] && [ -d "$SKILLMUTATOR_DATA_ROOT" ] \
   && [ -n "$(ls -A "$SKILLMUTATOR_DATA_ROOT" 2>/dev/null)" ] && [ ! -f "$_MARK" ]; then
  echo "error: SKILLMUTATOR_DATA_ROOT=$SKILLMUTATOR_DATA_ROOT already holds data that this script did not create." >&2
  echo "       Refusing to clean it. Unset SKILLMUTATOR_DATA_ROOT (default ./demo-data) or point it at a new folder." >&2
  exit 2
fi

if [ "$KEEP_DATA" = 1 ]; then
  echo "== [0/5] Clean this run's working files + the $MODEL/$MUT_MODE part of the data tree (--keep-data) =="
  rm -rf "$RESULTS" "$SKILLMUTATOR_DATA_ROOT/$MODEL/$MUT_MODE" baseline_result analysis/rq1/scripts/outputs analysis/rq2/scripts/outputs analysis/paper_floats/outputs
else
  echo "== [0/5] Clean prior demo artifacts (fresh run) =="
  rm -rf "$RESULTS" "$SKILLMUTATOR_DATA_ROOT" baseline_result analysis/rq1/scripts/outputs analysis/rq2/scripts/outputs analysis/paper_floats/outputs
fi
mkdir -p "$SKILLMUTATOR_DATA_ROOT" && touch "$_MARK"

echo "== [1/5] Mutate the skill(s) (oracle=$MODEL, mode=$MUT_MODE, iterations=$MAX_ITERS, iter_0..iter_$((MAX_ITERS-1))) =="
for _skill in "${SKILLS[@]}"; do
  echo "   -> mutating: $_skill"
  python scripts/run_mutation.py "$_skill" \
      --provider openai --model "$MODEL" \
      --mode "$MUT_MODE" --max-iters "$MAX_ITERS" --use-llm-detect \
      --result-dir "$RESULTS"
done

echo "== [2/5] Consolidate the run into the canonical data tree ($SKILLMUTATOR_DATA_ROOT) =="
# Also labels each cell's refusal class (Table 3); the original skills are
# needed for the SKILL.md byte-identity check.
python scripts/consolidate_to_datatree.py \
    --result-root "$RESULTS" --oracle "$MODEL" \
    --data-root "$SKILLMUTATOR_DATA_ROOT" --mode "$MUT_MODE" \
    --skills "${SKILLS[@]}"

echo "== [3/5] Populate per-scanner verdicts into the tree (from the run's scan results) =="
# The mutation step (--use-llm-detect) already scanned + adjudicated each cell and
# wrote comparison_<skill>.csv (ss/snyk/llm detected). Bridge those into the
# <cell>/<scanner>/verdict.json cells the builders read.
for _skill in "${SKILLS[@]}"; do
  _csv="$RESULTS/comparison_$(basename "$_skill").csv"
  [ -f "$_csv" ] || { echo "   (no comparison CSV for $(basename "$_skill"), skipping)"; continue; }
  python scripts/populate_verdicts.py \
      --comparison-csv "$_csv" \
      --oracle "$MODEL" --mode "$MUT_MODE" \
      --data-root "$SKILLMUTATOR_DATA_ROOT" --scanner-model "$MODEL"
done

echo "== [4/5] Evaluation judge for the LLM-scanner rows (judge=$JUDGE_MODEL$([ "$CROSS_SCAN" = 1 ] && echo ', cross-scan')) =="
# Re-adjudicate the LLM-scanner reports with the evaluation judge (Figure 7 prompt),
# replacing the refinement loop's in-run decision for the LLM rows; with
# --cross-scan, first scan each final iteration with the other two LLM scanners.
_cross=""; [ "$CROSS_SCAN" = 1 ] && _cross="--cross-scan"
python scripts/judge_llm_scanners.py \
    --result-root "$RESULTS" --oracle "$MODEL" --mode "$MUT_MODE" \
    --data-root "$SKILLMUTATOR_DATA_ROOT" --judge-model "$JUDGE_MODEL" $_cross

echo "== [5/5] Build the paper floats from the run =="
python analysis/paper_floats/table3_refusal.py      || true
python analysis/paper_floats/table4_cross_scanner.py || true
python analysis/paper_floats/table5_select.py        || true
python analysis/paper_floats/figure4_ier.py          || true

# Keep only the paper-labelled per-float folders; drop raw intermediate outputs.
rm -rf analysis/rq1/scripts/outputs analysis/rq2/scripts/outputs

echo
echo "Demo complete. Generated floats (paper format, demo scale):"
echo "   analysis/paper_floats/outputs/<float>/  — one folder per paper float:"
echo "     table3_refusal/  table4_cross_scanner/  table5_select/  figure4_ier/"
echo "Run with the full benchmark + gpt-5.4 judge to reproduce the paper's numbers (docs/REPRODUCE.md)."
echo "   n/a in a table = no verdict for that cell (not run in this run, or scanner unavailable)."
python - "$RESULTS" <<'PYSNYK' || true
import csv, glob, sys
rows = [r for f in glob.glob(sys.argv[1] + "/comparison_*.csv")
        for r in csv.DictReader(open(f, encoding="utf-8-sig"))]
off = sum(str(r.get("snyk_available", "")).strip().lower() not in ("true", "1", "yes") for r in rows)
if rows and off:
    print(f"   NOTE: Snyk was unavailable for {off}/{len(rows)} cells (missing or rejected "
          "SNYK_TOKEN, or scanner not installed); its cells show n/a.")
PYSNYK
