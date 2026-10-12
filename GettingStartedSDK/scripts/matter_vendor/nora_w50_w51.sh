#!/usr/bin/env bash
# NORA-W50-W51 (TI CC35xx) Matter: build TI's own examples from the ti-matter fork.
#
#   nora_w50_w51.sh setup                    cc35xx submodules, bootstrap, SDK libraries
#   nora_w50_w51.sh build <example-dir> [gn args...]
#   nora_w50_w51.sh clean <example-dir>
#
# Host tools are looked up under $TI_HOME (default ~/ti). Override with
# TI_SYSCONFIG_ROOT, TI_WIFI_TOOLBOX_ROOT and GCC_ARMCOMPILER.
set -euo pipefail

SDK="${UBX_MATTER_SDK_ROOT:?UBX_MATTER_SDK_ROOT not set; run via ubx-matter nora-w50-w51}"
CHIP="${SDK}/ti-matter"
TI_SDK="${CHIP}/third_party/ti_simplelink_sdk/repo_cc35xx"
TI_HOME="${TI_HOME:-$HOME/ti}"
GCC_VERSION="12.3.rel1"
GCC_NAME="arm-gnu-toolchain-${GCC_VERSION}-x86_64-arm-none-eabi"
GCC_URL="https://developer.arm.com/-/media/Files/downloads/gnu/${GCC_VERSION}/binrel/${GCC_NAME}.tar.xz"

die() { echo "[FAIL] $*" >&2; exit 1; }
latest() { ls -d "$@" 2>/dev/null | sort -V | tail -1 || true; }

# Matter 1.5's Python env needs 3.11+, Ubuntu 22.04 ships 3.10.
use_python311() {
    python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' && return
    command -v python3.11 >/dev/null \
        || die "Python 3.11+ required. On Ubuntu 22.04: sudo add-apt-repository ppa:deadsnakes/ppa && sudo apt install python3.11 python3.11-venv python3.11-dev"
    local shim="${SDK}/.python311"
    mkdir -p "${shim}"
    ln -sf "$(command -v python3.11)" "${shim}/python3"
    ln -sf "$(command -v python3.11)" "${shim}/python"
    export PATH="${shim}:${PATH}"
}

find_tools() {
    SYSCFG="${TI_SYSCONFIG_ROOT:-$(latest "${TI_HOME}"/sysconfig_* "${TI_HOME}"/ccs*/ccs/utils/sysconfig_*)}"
    TOOLBOX="${TI_WIFI_TOOLBOX_ROOT:-$(latest "${TI_HOME}"/simplelink_wifi_toolbox_*)}"
    GCC="${GCC_ARMCOMPILER:-$(latest "${TI_HOME}/${GCC_NAME}")}"
    [ -x "${SYSCFG}/sysconfig_cli.sh" ] \
        || die "SysConfig not found under ${TI_HOME}. Install the Linux SysConfig 1.26.3 from ti.com/tool/SYSCONFIG, or set TI_SYSCONFIG_ROOT."
    [ -d "${TOOLBOX}" ] \
        || die "SimpleLink Wi-Fi Toolbox not found under ${TI_HOME}. Install the Linux Toolbox 4.2.4 from ti.com/tool/SIMPLELINK-WIFI-TOOLBOX, or set TI_WIFI_TOOLBOX_ROOT."
    echo "[INFO] SysConfig: ${SYSCFG}"
    echo "[INFO] Toolbox:   ${TOOLBOX}"
}

install_gcc() {
    GCC="${GCC_ARMCOMPILER:-${TI_HOME}/${GCC_NAME}}"
    if [ -x "${GCC}/bin/arm-none-eabi-gcc" ]; then
        echo "[OK] Arm GNU Toolchain ${GCC_VERSION}: ${GCC}"
        return
    fi
    echo "[INFO] Downloading Arm GNU Toolchain ${GCC_VERSION}"
    mkdir -p "${TI_HOME}"
    curl -fL "${GCC_URL}" | tar -xJ -C "${TI_HOME}"
}

activate() {
    [ -f "${CHIP}/scripts/activate.sh" ] || die "ti-matter missing at ${CHIP}. Run: ubx-matter nora-w50-w51 --clone"
    [ -d "${CHIP}/.environment" ] || die "Matter environment not bootstrapped. Run: ubx-matter nora-w50-w51 --install"
    use_python311
    set +u
    # shellcheck source=/dev/null
    source "${CHIP}/scripts/activate.sh" >/dev/null
    set -u
}

setup() {
    [ -d "${CHIP}/.git" ] || die "ti-matter missing at ${CHIP}. Run: ubx-matter nora-w50-w51 --clone"
    if ! grep -q '22.04' /etc/os-release; then
        echo "[WARNING] TI supports the CC35xx Matter build on Ubuntu 22.04 only."
    fi

    echo "=== cc35xx + linux submodules ==="
    ( cd "${CHIP}" && ./scripts/checkout_submodules.py --shallow --platform cc35xx linux --recursive )

    echo "=== Matter environment bootstrap ==="
    use_python311
    ( cd "${CHIP}" && set +u && source ./scripts/bootstrap.sh -p ti )

    echo "=== Arm GNU Toolchain ==="
    install_gcc

    echo "=== SimpleLink Wi-Fi SDK libraries ==="
    find_tools
    ( cd "${TI_SDK}" && \
      SYSCONFIG_TOOL="${SYSCFG}/sysconfig_cli.sh" \
      SIMPLELINK_WIFI_TOOLBOX_INSTALL_DIR="${TOOLBOX}" \
      CMAKE="$(command -v cmake)" \
      GCC_ARMCOMPILER="${GCC}" \
      make GENERATOR=Ninja build-gcc )
    echo "[OK] Setup complete."
}

build() {
    local dir="${1:?example directory required}"; shift
    find_tools
    activate
    cd "${dir}"
    echo "[INFO] Building $(basename "$(dirname "$(dirname "${dir}")")") for CC35xx"
    gn gen out/debug --args="ti_sysconfig_root=\"${SYSCFG}\" ti_simplelink_wifi_toolbox_root=\"${TOOLBOX}\" $*"
    ninja -C out/debug
    echo "[OK] Output in ${dir}/out/debug"
    echo "[INFO] Flash with the Wi-Fi Toolbox programmer using out/debug/tool_settings.json"
}

case "${1:-}" in
    setup) setup ;;
    build) shift; build "$@" ;;
    clean) rm -rf "${2:?example directory required}/out"; echo "[OK] Cleaned." ;;
    *)     echo "Usage: $0 setup | build <example-dir> [gn args] | clean <example-dir>"; exit 1 ;;
esac
