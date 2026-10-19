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
#      --finetune / --all need Python 3.10-3.12, e.g. PYTHON=python3.12.
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
      sed -n '3,14p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "unknown option: $arg (try --help)"; exit 2 ;;
  esac
done

PY="${PYTHON:-python3}"
if [ "$WANT_FINETUNE" = 1 ]; then
  # The pinned fine-tuning set below (vllm 0.8.5, sentencepiece 0.2.0) has no
  # Python 3.13+ builds; check before creating the venv, not halfway through pip.
  if ! "$PY" -c 'import sys; sys.exit(0 if (3, 10) <= sys.version_info[:2] <= (3, 12) else 1)'; then
    _v="$("$PY" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo unknown)"
    echo "ERROR: the fine-tuning extras (--finetune / --all) need Python 3.10-3.12; '$PY' is $_v." >&2
    echo "       Re-run with a supported interpreter, e.g.  PYTHON=python3.12 ./install.sh --all" >&2
    echo "       (remove .venv first if it was created with another Python)." >&2
    echo "       Tier 1 and --generate work with any Python >= 3.10." >&2
    exit 1
  fi
fi
echo "== creating virtual environment (.venv) =="
# On Debian / Ubuntu / Google Colab the stdlib `venv` ships as a separate package,
# so `python3 -m venv` can fail with "No module named ensurepip". Catch that and
# print the one-line fix instead of aborting with an opaque traceback.
if ! "$PY" -m venv .venv; then
  echo "" >&2
  echo "ERROR: '$PY -m venv .venv' failed (often: 'No module named ensurepip')." >&2
  echo "On Debian / Ubuntu / Google Colab, install the venv package and re-run:" >&2
  echo "    sudo apt-get update && sudo apt-get install -y python3-venv" >&2
  echo "    # or the version-specific package named in the error, e.g. python3.13-venv" >&2
  exit 1
fi
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
  # Pinned, tested set (2026-10, RTX 3090 / driver 560, CUDA 12.x): torch 2.6.0 is the
  # CUDA 12.4 wheel and runs on drivers >= 525. Unpinned latest pulls a CUDA 13 torch
  # (needs driver >= 580) and an mcp version that breaks snyk-agent-scan.
  python -m pip install torch==2.6.0 transformers==4.55.4 peft==0.20.0 trl==0.21.0 \
    datasets==3.6.0 accelerate==1.10.1 vllm==0.8.5.post1 huggingface_hub==0.36.2 sentencepiece==0.2.0
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
