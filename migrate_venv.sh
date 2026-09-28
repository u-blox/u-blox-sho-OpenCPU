#!/bin/bash
# Helper script to migrate .venv from repo root to GettingStartedSDK/

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OLD_VENV="$REPO_ROOT/.venv"
NEW_VENV="$REPO_ROOT/GettingStartedSDK/.venv"

echo "🔧 Virtual Environment Migration Helper"
echo ""

if [ -d "$OLD_VENV" ]; then
    echo "Found .venv at repo root: $OLD_VENV"
    echo "New location should be: $NEW_VENV"
    echo ""
    
    if [ -d "$NEW_VENV" ]; then
        echo "⚠️  .venv already exists at GettingStartedSDK/"
        echo "   Remove the old one at repo root? (y/n)"
        read -p "   > " choice
        if [ "$choice" = "y" ]; then
            rm -rf "$OLD_VENV"
            echo "✅ Old .venv removed"
        else
            echo "⚠️  Skipped. You can manually remove it or run setup_venv.py again."
        fi
    else
        echo "📦 Moving .venv to GettingStartedSDK/"
        mv "$OLD_VENV" "$NEW_VENV"
        echo "✅ Virtual environment moved successfully"
        echo ""
        echo "Next step: Activate from GettingStartedSDK directory"
        echo "  source .venv/bin/activate  (Linux/macOS/WSL)"
        echo "  .venv\\Scripts\\activate.bat  (Windows CMD)"
    fi
else
    echo "✅ No .venv found at repo root"
    echo "   Virtual environment is already properly located in:"
    echo "   $NEW_VENV"
fi

echo ""
