#!/usr/bin/env bash
# NORA-W4 (ESP32-C6) Matter: build Espressif's own esp-matter examples.
#
#   nora_w4.sh setup                    ESP-IDF tools + esp-matter install
#   nora_w4.sh build <example-dir> [idf.py args...]
#   nora_w4.sh clean <example-dir>
set -euo pipefail

SDK="${UBX_MATTER_SDK_ROOT:?UBX_MATTER_SDK_ROOT not set; run via ubx-matter nora-w4}"
IDF_PATH="${IDF_PATH:-${SDK}/esp-idf}"
ESP_MATTER_PATH="${ESP_MATTER_PATH:-${SDK}/esp-matter}"

die() { echo "[FAIL] $*" >&2; exit 1; }

require_sdk() {
    [ -f "${IDF_PATH}/export.sh" ] || die "ESP-IDF missing at ${IDF_PATH}. Run: ubx-matter nora-w4 --clone"
    [ -d "${ESP_MATTER_PATH}/components" ] || die "esp-matter missing at ${ESP_MATTER_PATH}. Run: ubx-matter nora-w4 --clone"
}

setup() {
    require_sdk
    echo "=== ESP-IDF tools (esp32c6) ==="
    "${IDF_PATH}/install.sh" esp32c6

    echo "=== esp-matter submodules (esp32 + linux only) ==="
    ( cd "${ESP_MATTER_PATH}" && git submodule update --init --depth 1 )
    ( cd "${ESP_MATTER_PATH}/connectedhomeip/connectedhomeip" \
        && ./scripts/checkout_submodules.py --platform esp32 linux --shallow )

    echo "=== esp-matter install (pigweed bootstrap) ==="
    set +u
    # shellcheck source=/dev/null
    . "${IDF_PATH}/export.sh"
    set -u
    ( cd "${ESP_MATTER_PATH}" && ./install.sh --no-host-tool )
    echo "[OK] Setup complete."
}

activate() {
    require_sdk
    [ -f "${ESP_MATTER_PATH}/export.sh" ] || die "esp-matter not installed. Run: ubx-matter nora-w4 --install"
    set +u
    # shellcheck source=/dev/null
    . "${IDF_PATH}/export.sh"
    export ESP_MATTER_PATH
    # shellcheck source=/dev/null
    . "${ESP_MATTER_PATH}/export.sh"
    set -u
    export IDF_CCACHE_ENABLE=1
}

build() {
    local dir="${1:?example directory required}"; shift
    activate
    cd "${dir}"
    [ -f sdkconfig ] && grep -q 'CONFIG_IDF_TARGET="esp32c6"' sdkconfig || idf.py set-target esp32c6
    idf.py build "$@"
    echo "[OK] Output in ${dir}/build"
}

case "${1:-}" in
    setup) setup ;;
    build) shift; build "$@" ;;
    clean) rm -rf "${2:?example directory required}/build" "${2}/sdkconfig"; echo "[OK] Cleaned." ;;
    *)     echo "Usage: $0 setup | build <example-dir> [idf.py args] | clean <example-dir>"; exit 1 ;;
esac
