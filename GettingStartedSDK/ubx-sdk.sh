#!/usr/bin/env bash
# ============================================================================
# ubx-sdk.sh -- u-blox Getting Started SDK launcher (Linux / WSL2 / macOS)
# ============================================================================
# Thin shim: picks a Python interpreter (shared .venv first) and forwards
# every argument to scripts/ubx_sdk.py. All logic lives in scripts/ubx.py.
#
#   ./ubx-sdk.sh --help
#   ./ubx-sdk.sh nora-w4 --clone --install --build hello_world
#   ./ubx-sdk.sh nora-w3 --build
#
# Matter is an optional, separate layer: see ./ubx-matter.sh --help
# ============================================================================
set -euo pipefail

SDK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UBX_PY="${SDK_DIR}/scripts/ubx.py"

if [ ! -f "${UBX_PY}" ]; then
    echo "[FAIL] Not found: ${UBX_PY}" >&2
    exit 1
fi

# A Windows venv in the same folder has no bin/python, so this test also keeps
# a Windows-created .venv from being picked up under WSL.
if [ -x "${SDK_DIR}/.venv/bin/python" ]; then
    PY="${SDK_DIR}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PY="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PY="$(command -v python)"
else
    echo "[FAIL] No Python interpreter found. Install Python 3.10+." >&2
    exit 1
fi

exec "${PY}" "${UBX_PY}" "$@"
