#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

python3 -m pip install --upgrade pyinstaller
pyinstaller --clean weewx_dashboard.spec

echo "Linux build complete: $PROJECT_DIR/dist/weewx-dashboard/"
