#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if [[ ! -d ".venv-build" ]]; then
	python3 -m venv .venv-build
fi

# shellcheck disable=SC1091
source .venv-build/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

pyinstaller --clean weewx_dashboard.spec

echo "Linux build complete: $PROJECT_DIR/dist/weewx-dashboard/"
