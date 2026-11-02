#!/usr/bin/env bash
# NO-METADATA installer (Linux / macOS)
#
# One-time setup. Creates a private environment inside this folder, installs the
# dependencies, and adds a `no-metadata` command plus an app-menu launcher.
# After this you never need to activate a venv again.
#
# Usage:  ./install.sh
set -euo pipefail

APP="no-metadata"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$DIR/.venv"
BIN_DIR="$HOME/.local/bin"
APPS_DIR="$HOME/.local/share/applications"

say()  { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!!\033[0m  %s\n' "$*"; }
die()  { printf '\033[1;31mxx\033[0m  %s\n' "$*" >&2; exit 1; }

# ---- 1. Python ---------------------------------------------------------------
command -v python3 >/dev/null 2>&1 || die "python3 not found. Install Python 3.8+ first."
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' \
  || die "Python 3.8 or newer is required."

# ---- 2. Tkinter (system package, cannot be installed with pip) ---------------
if ! python3 -c 'import tkinter' >/dev/null 2>&1; then
  warn "Tkinter is missing (it is a system package, not a pip package)."
  if   command -v apt-get >/dev/null 2>&1; then PKG_CMD="sudo apt-get install -y python3-tk python3-venv"
  elif command -v dnf     >/dev/null 2>&1; then PKG_CMD="sudo dnf install -y python3-tkinter"
  elif command -v pacman  >/dev/null 2>&1; then PKG_CMD="sudo pacman -S --needed --noconfirm tk"
  elif command -v zypper  >/dev/null 2>&1; then PKG_CMD="sudo zypper install -y python3-tk"
  elif command -v brew    >/dev/null 2>&1; then PKG_CMD="brew install python-tk"
  else PKG_CMD=""; fi

  [ -n "$PKG_CMD" ] || die "Install Tkinter for your system manually, then re-run ./install.sh"

  echo "    I can run:  $PKG_CMD"
  read -r -p "    Run it now? [Y/n] " ans || ans=""
  case "${ans:-Y}" in
    [Nn]*) die "Install Tkinter, then re-run ./install.sh" ;;
  esac
  $PKG_CMD
  python3 -c 'import tkinter' >/dev/null 2>&1 \
    || die "Tkinter still not importable. If your Python is from pyenv/conda, use /usr/bin/python3 instead."
fi

# ---- 3. Private virtual environment ------------------------------------------
if [ ! -x "$VENV/bin/python" ]; then
  say "Creating private environment in $VENV"
  python3 -m venv "$VENV" 2>/dev/null || {
    warn "python3-venv is missing."
    if command -v apt-get >/dev/null 2>&1; then
      sudo apt-get install -y python3-venv
      python3 -m venv "$VENV"
    else
      die "Could not create a virtual environment."
    fi
  }
fi

say "Installing dependencies"
"$VENV/bin/python" -m pip install --quiet --upgrade pip || warn "Could not upgrade pip (continuing)."
"$VENV/bin/python" -m pip install --quiet -r "$DIR/requirements.txt"

# ---- 4. Launcher script ------------------------------------------------------
LAUNCHER="$DIR/$APP"
cat > "$LAUNCHER" <<'EOF'
#!/usr/bin/env bash
# Launches NO-METADATA with its private environment (no venv activation needed).
SELF="$(readlink -f "${BASH_SOURCE[0]}")"
DIR="$(dirname "$SELF")"
exec "$DIR/.venv/bin/python" "$DIR/no_metadata.py" "$@"
EOF
chmod +x "$LAUNCHER"

# ---- 5. `no-metadata` command on PATH ----------------------------------------
mkdir -p "$BIN_DIR"
ln -sf "$LAUNCHER" "$BIN_DIR/$APP"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) warn "$BIN_DIR is not on your PATH. Add this to ~/.bashrc:  export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac

# ---- 6. App-menu entry (Linux) -----------------------------------------------
if [ "$(uname -s)" = "Linux" ]; then
  mkdir -p "$APPS_DIR"
  cat > "$APPS_DIR/$APP.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=NO-METADATA
Comment=Remove sensitive metadata from photos, images and media
Exec=$LAUNCHER
Terminal=false
Categories=Utility;Graphics;Security;
Keywords=metadata;exif;privacy;gps;
EOF
  chmod +x "$APPS_DIR/$APP.desktop"
  command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
fi

# ---- 7. Optional ffmpeg note -------------------------------------------------
if ! command -v ffmpeg >/dev/null 2>&1; then
  warn "ffmpeg not found. Images will work, but video/audio need it:  sudo apt install ffmpeg"
fi

say "Done. Start NO-METADATA with any of:"
echo "      no-metadata             (from any terminal)"
echo "      $LAUNCHER"
echo "      or search 'NO-METADATA' in your app menu"
