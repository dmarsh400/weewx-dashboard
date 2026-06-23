#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if ! command -v flatpak-builder >/dev/null 2>&1; then
  echo "flatpak-builder not found. Install it first (e.g. sudo apt install flatpak-builder)."
  exit 1
fi

./scripts/build-flatpak.sh

flatpak-builder --user --repo=repo --force-clean \
  build-flatpak packaging/flatpak/org.weewx.Dashboard.yaml

flatpak --user remote-add --if-not-exists weewx-local repo
flatpak --user install -y weewx-local io.github.weewxdashboard

echo "Installed. Launch with: flatpak run io.github.weewxdashboard"
