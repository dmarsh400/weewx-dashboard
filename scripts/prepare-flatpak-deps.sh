#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if ! command -v flatpak-pip-generator >/dev/null 2>&1; then
  echo "flatpak-pip-generator not found."
  echo "Install with: python3 -m pip install --user flatpak-pip-generator --break-system-packages"
  exit 1
fi

flatpak-pip-generator \
  --output packaging/flatpak/python3-deps \
  --requirements-file packaging/flatpak/requirements-flatpak.txt

echo "Generated packaging/flatpak/python3-deps.json"
