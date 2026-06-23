#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Installing WeeWX Dashboard to user environment..."

if command -v pipx >/dev/null 2>&1; then
  pipx install --force "$PROJECT_DIR"
  INSTALL_BIN="$HOME/.local/bin/weewx-dashboard"
else
  echo "pipx not found; using pip --user fallback"
  python3 -m pip install --user --upgrade pip --break-system-packages
  python3 -m pip install --user "$PROJECT_DIR" --break-system-packages
  INSTALL_BIN="$HOME/.local/bin/weewx-dashboard"
fi

mkdir -p "$HOME/.local/share/applications"
cp "$PROJECT_DIR/packaging/weewx-dashboard.desktop" "$HOME/.local/share/applications/weewx-dashboard.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$HOME/.local/share/applications" || true
fi

echo
echo "Install complete."
echo "App launcher installed to: $HOME/.local/share/applications/weewx-dashboard.desktop"
echo "Binary installed to: $INSTALL_BIN"
echo
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo "Note: add $HOME/.local/bin to PATH if command is not found."
fi
