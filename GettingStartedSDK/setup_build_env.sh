#!/bin/bash
# Setup build environment for IRIS-W10 and other u-blox modules
# Cross-platform compatible (Windows Git Bash, WSL2, Linux, macOS)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "Setting up u-blox build environment..."
echo "Working directory: $SCRIPT_DIR"

# Detect platform
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    PLATFORM="windows"
    PYTHON_BIN="$VENV_DIR/Scripts/python.exe"
    PIP_BIN="$VENV_DIR/Scripts/pip.exe"
else
    PLATFORM="unix"
    PYTHON_BIN="$VENV_DIR/bin/python"
    PIP_BIN="$VENV_DIR/bin/pip"
fi

echo "Platform: $PLATFORM"

# 1. Remove old .venv if corrupted
if [ -d "$VENV_DIR" ]; then
    echo "Removing old .venv..."
    rm -rf "$VENV_DIR"
fi

# 2. Detect system Python
if command -v python.exe &> /dev/null; then
    SYS_PYTHON=$(which python.exe)
elif command -v python3 &> /dev/null; then
    SYS_PYTHON=$(which python3)
elif command -v python &> /dev/null; then
    SYS_PYTHON=$(which python)
fi

if [ -z "$SYS_PYTHON" ]; then
    echo "ERROR: Python not found in PATH"
    exit 1
fi

echo "Using Python: $SYS_PYTHON"

# 3. Create fresh .venv
echo "Creating virtual environment..."
"$SYS_PYTHON" -m venv "$VENV_DIR"

# 4. Upgrade pip, setuptools, wheel
echo "Upgrading pip, setuptools, wheel..."
"$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel --quiet || true

# 5. Install build dependencies
echo "Installing build dependencies..."
PACKAGES="west pyyaml pyserial pylink-square"
"$PIP_BIN" install $PACKAGES --quiet || true

# 6. Find and set ARMGCC_DIR
echo "Detecting ARM GCC toolchain..."
if [[ "$PLATFORM" == "windows" ]]; then
    # Windows: Check common installation paths
    if [ -d "/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi" ]; then
        ARMGCC_DIR="/c/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
    elif command -v arm-none-eabi-gcc &> /dev/null; then
        ARMGCC_BIN=$(which arm-none-eabi-gcc)
        ARMGCC_DIR=$(dirname "$(dirname "$ARMGCC_BIN")")
    fi
else
    # Unix/Linux/WSL2
    if command -v arm-none-eabi-gcc &> /dev/null; then
        ARMGCC_BIN=$(which arm-none-eabi-gcc)
        ARMGCC_DIR=$(dirname "$(dirname "$ARMGCC_BIN")")
    elif [ -d "/opt/arm" ]; then
        ARMGCC_DIR="/opt/arm"
    fi
fi

if [ -z "$ARMGCC_DIR" ]; then
    echo "WARNING: ARM GCC not found. Set ARMGCC_DIR manually before building."
else
    echo "ARM GCC found at: $ARMGCC_DIR"
fi

# 7. Create activation script with environment variables
if [[ "$PLATFORM" == "windows" ]]; then
    # Windows batch activation wrapper
    cat > "$VENV_DIR/activate_build.bat" << 'EOF'
@echo off
REM Activate .venv and set build environment variables
call "%~dp0Scripts\activate.bat"
if defined ARMGCC_DIR (
    echo ARMGCC_DIR already set: %ARMGCC_DIR%
) else (
    set "ARMGCC_DIR=C:\Program Files\Arm\GNU Toolchain mingw-w64-x86_64-arm-none-eabi"
    echo ARMGCC_DIR set to: %ARMGCC_DIR%
)
echo Build environment ready. Available commands:
echo   - iris_w10_build.py list
echo   - iris_w10_build.py build demo_apps/hello_world
echo   - iris_w10_build.py log
echo   - iris_w10_build.py flash demo_apps/hello_world
EOF
    echo "Created: $VENV_DIR/activate_build.bat"
else
    # Unix activation wrapper
    cat > "$VENV_DIR/activate_build.sh" << EOF
#!/bin/bash
# Activate .venv and set build environment variables
source "$VENV_DIR/bin/activate"
export ARMGCC_DIR="${ARMGCC_DIR:-/opt/arm}"
echo "Build environment activated"
echo "ARMGCC_DIR: \$ARMGCC_DIR"
echo "Python: \$(python --version)"
echo "west: \$(west --version)"
EOF
    chmod +x "$VENV_DIR/activate_build.sh"
    echo "Created: $VENV_DIR/activate_build.sh"
fi

# 8. Summary
echo ""
echo "SUCCESS: Build environment setup complete"
echo ""
echo "Next steps:"
if [[ "$PLATFORM" == "windows" ]]; then
    echo "  1. Activate: $VENV_DIR\\activate_build.bat"
    echo "  2. Build:    python scripts/iris_w10_build.py build demo_apps/hello_world"
else
    echo "  1. Activate: source $VENV_DIR/activate_build.sh"
    echo "  2. Build:    python scripts/iris_w10_build.py build demo_apps/hello_world"
fi
echo ""
echo "Installed packages:"
"$PIP_BIN" list | grep -E "west|pyyaml|pyserial|pylink"
