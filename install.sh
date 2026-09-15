#!/usr/bin/env bash
# Set up the reproduction environment for the SkillMutator artifact.
#
# Usage:
#   ./install.sh              core only — table/figure claims + Fine-tuning Data
#                             Pipeline (CPU only, no API key, no GPU)
#   ./install.sh --generate   + SkillMutator Pipeline extras (mutation generation
#                             + scan; needs an OpenAI API key at run time)
#   ./install.sh --finetune   + training / local 7B scanner inference (GPU, heavy:
#                             torch/transformers/peft/vllm)
#   ./install.sh --all        core + generate + finetune
#
# Env: PYTHON=<interpreter> to pick the base Python (default: python3).
set -euo pipefail
cd "$(dirname "$0")"

WANT_GENERATE=0
WANT_FINETUNE=0
for arg in "$@"; do
  case "$arg" in
    --generate) WANT_GENERATE=1 ;;
    --finetune) WANT_FINETUNE=1 ;;
    --all)      WANT_GENERATE=1; WANT_FINETUNE=1 ;;
    -h|--help)
      sed -n '3,13p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "unknown option: $arg (try --help)"; exit 2 ;;
  esac
done

PY="${PYTHON:-python3}"
echo "== creating virtual environment (.venv) =="
"$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate

echo "== installing core dependencies (claim verification) =="
# `python -m pip` is robust across Linux/macOS/Windows venvs; the self-upgrade is
# best-effort (some Windows venvs refuse it) and must not abort the install.
# Core set matches requirements.txt (core) and pyproject.toml [analysis] (minus
# matplotlib, which is only needed to regenerate the claim 10-12 figure plots).
python -m pip install --quiet --upgrade pip || true
python -m pip install --quiet pandas numpy pyyaml openpyxl

if [ "$WANT_GENERATE" = 1 ]; then
  echo "== installing SkillMutator Pipeline extras (generation) =="
  python -m pip install --quiet openai langchain-core langchain-openai langgraph tiktoken python-dotenv matplotlib
  # Snyk Agent Scan is a third-party scanner (Apache-2.0) distributed on PyPI as
  # `snyk-agent-scan`; it is NOT vendored into this repo. Fetch the pinned
  # version used in the paper. Best-effort: the demo degrades gracefully (Snyk
  # column left unavailable) if this fails or no SNYK_TOKEN is set at run time.
  echo "== installing the Snyk Agent scanner (snyk-agent-scan, third-party) =="
  python -m pip install --quiet "snyk-agent-scan==0.4.9" || \
    echo "   (snyk-agent-scan install failed; the Snyk scanner will be unavailable — this is non-fatal)"
  # skill-security-scan (MIT) is likewise third-party and NOT vendored; it is the
  # PyPI package `skill-security-scan` (github.com/huifer/skill-security-scan).
  echo "== installing the skill-security scanner (skill-security-scan, third-party) =="
  python -m pip install --quiet "skill-security-scan" || \
    echo "   (skill-security-scan install failed; that scanner will be skipped — this is non-fatal)"
  # The 1.0.0 wheel omits its default config/rules.yaml, so fetch the rules from the
  # tool's own repo (not vendored here) to the path the scan adapter passes via --rules.
  mkdir -p "$HOME/.cache/skillmutator"
  curl -fsSL "https://raw.githubusercontent.com/huifer/skill-security-scan/main/config/rules.yaml" \
       -o "$HOME/.cache/skillmutator/skill_security_rules.yaml" 2>/dev/null || \
    echo "   (could not fetch skill-security rules.yaml; that scanner will be skipped — non-fatal)"
fi

if [ "$WANT_FINETUNE" = 1 ]; then
  echo "== installing fine-tuning / local-scanner extras (GPU, heavy) =="
  python -m pip install torch transformers peft trl datasets accelerate vllm huggingface_hub sentencepiece
fi

echo
echo "Done. Reproduce a table/figure claim with, e.g.:"
echo "  cd claims/claim04_phase_ablation && ./run.sh"
if [ "$WANT_GENERATE" = 0 ]; then
  echo
  echo "For the SkillMutator Pipeline (mutation generation + scan), re-run with:"
  echo "  ./install.sh --generate      # then set OPENAI_API_KEY and run: cd artifact/code/skillmutator && ./run.sh   (or ./run.sh --tier 2)"
fi
if [ "$WANT_FINETUNE" = 0 ]; then
  echo "To train or run the local 7B scanner (GPU): ./install.sh --finetune"
fi
