#!/bin/bash
set -e

echo "======================================"
echo "  MailBlast Pro  — macOS App Builder"
echo "======================================"

# ── 1. Check Python ────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install from https://www.python.org or via Homebrew:"
    echo "  brew install python"
    exit 1
fi
echo "Python: $(python3 --version)"

# ── 2. Install / upgrade dependencies ─────────────────────────────────────────
echo ""
echo "Installing dependencies..."
python3 -m pip install --upgrade pip --quiet
python3 -m pip install --upgrade \
    pyinstaller \
    pyqt6 \
    cryptography \
    --quiet

echo "Dependencies installed."

# ── 3. Clean previous build ───────────────────────────────────────────────────
echo ""
echo "Cleaning previous build..."
rm -rf build dist

# ── 4. Build .app bundle ──────────────────────────────────────────────────────
echo ""
echo "Building MailBlast Pro.app ..."
python3 -m PyInstaller MailBlast.spec --clean --noconfirm

# ── 5. Verify output ──────────────────────────────────────────────────────────
APP="dist/MailBlast Pro.app"
if [ -d "$APP" ]; then
    echo ""
    echo "======================================"
    echo "  BUILD SUCCESSFUL"
    echo "  $APP"
    echo "======================================"
    echo ""
    echo "To run the app:"
    echo "  open \"$APP\""
    echo ""
    echo "To install — drag to Applications:"
    echo "  cp -r \"$APP\" /Applications/"
else
    echo ""
    echo "ERROR: Build failed — $APP not found."
    exit 1
fi
