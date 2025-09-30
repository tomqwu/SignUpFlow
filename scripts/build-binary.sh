#!/usr/bin/env bash
# Build standalone binary with PyInstaller

set -e

echo "Building standalone roster binary..."

# Install PyInstaller if not already installed
poetry run pip install pyinstaller

# Build binary
poetry run pyinstaller \
    --name roster \
    --onefile \
    --console \
    roster_cli/main.py

echo "Binary created at: dist/roster"
echo "Test with: ./dist/roster --help"
