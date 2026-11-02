#!/usr/bin/env bash
# Removes everything install.sh created. Your source files are left alone.
set -euo pipefail

APP="no-metadata"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rm -rf "$DIR/.venv"
rm -f "$DIR/$APP"
rm -f "$HOME/.local/bin/$APP"
rm -f "$HOME/.local/share/applications/$APP.desktop"
command -v update-desktop-database >/dev/null 2>&1 \
  && update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true

echo "NO-METADATA uninstalled (environment, command and menu entry removed)."
