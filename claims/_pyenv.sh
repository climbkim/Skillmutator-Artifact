# Sourced by run.sh and claims/*/run.sh: use the artifact's Python.
# - Activate the .venv created by install.sh (Linux/macOS or Git-Bash layout)
#   unless a virtualenv is already active.
# - If there is still no `python` on PATH (e.g. stock Ubuntu ships only
#   python3), put a temporary `python` -> python3 shim first on PATH so this
#   script and its children find it.
_artifact_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -z "${VIRTUAL_ENV:-}" ]; then
  set +u
  if [ -f "$_artifact_root/.venv/bin/activate" ]; then
    . "$_artifact_root/.venv/bin/activate"
  elif [ -f "$_artifact_root/.venv/Scripts/activate" ]; then
    . "$_artifact_root/.venv/Scripts/activate"
  fi
  set -u
fi
if ! command -v python >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
  _shim="$(mktemp -d "${TMPDIR:-/tmp}/smx-python.XXXXXX")"
  printf '#!/bin/sh\nexec "%s" "$@"\n' "$(command -v python3)" > "$_shim/python"
  chmod +x "$_shim/python"
  export PATH="$_shim:$PATH"
  unset _shim
fi
unset _artifact_root
