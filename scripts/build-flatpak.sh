#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if ! command -v flatpak-builder >/dev/null 2>&1; then
  echo "flatpak-builder not found. Install it first (e.g. sudo apt install flatpak-builder)."
  exit 1
fi

# Generate pinned Python dependency module used by Flatpak manifest.
./scripts/prepare-flatpak-deps.sh

flatpak-builder --force-clean --user \
  build-flatpak \
  packaging/flatpak/org.weewx.Dashboard.yaml

echo "Flatpak build complete in $PROJECT_DIR/build-flatpak"
