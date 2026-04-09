#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$BASE_DIR/.venv/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
  python3 -m venv "$BASE_DIR/.venv"
fi

"$VENV_PYTHON" -m pip install -r "$BASE_DIR/requirements.txt" >/dev/null
"$VENV_PYTHON" "$BASE_DIR/dashboard_dash.py"
