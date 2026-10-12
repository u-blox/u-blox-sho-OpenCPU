#!/bin/bash
# Helper script to migrate .venv from repo root to getting-started-sdk/

# This script lives in getting-started-sdk/scripts/.
SDK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$SDK_DIR/.." && pwd)"
OLD_VENV="$REPO_ROOT/.venv"
NEW_VENV="$SDK_DIR/.venv"

echo "Virtual Environment Migration Helper"
echo ""

if [ -d "$OLD_VENV" ]; then
    echo "Found .venv at repo root: $OLD_VENV"
    echo "New location should be: $NEW_VENV"
    echo ""
    
    if [ -d "$NEW_VENV" ]; then
        echo "[WARNING] .venv already exists at getting-started-sdk/"
        echo "   Remove the old one at repo root? (y/n)"
        read -p "   > " choice
        if [ "$choice" = "y" ]; then
            rm -rf "$OLD_VENV"
            echo "[OK] Old .venv removed"
        else
            echo "[WARNING] Skipped. You can manually remove it or run setup_venv.py again."
        fi
    else
        echo "[INFO] Moving .venv to getting-started-sdk/"
        mv "$OLD_VENV" "$NEW_VENV"
        echo "[OK] Virtual environment moved successfully"
        echo ""
        echo "Next step: Activate from getting-started-sdk directory"
        echo "  source .venv/bin/activate  (Linux/macOS/WSL)"
        echo "  .venv\\Scripts\\activate.bat  (Windows CMD)"
    fi
else
    echo "[OK] No .venv found at repo root"
    echo "   Virtual environment is already properly located in:"
    echo "   $NEW_VENV"
fi

echo ""
