#!/usr/bin/env bash
# NORA-W4 Matter Thermometer - driven by scripts/matter_build.py.
#
#   build.sh setup                       One-time ESP-IDF + esp-matter install
#   build.sh build [--wifi] [--clickboard | --hvac]
#   build.sh clean
#
# ESP-IDF and esp-matter come from UBX_MATTER_SDK_ROOT (set by the driver,
# fetched by 'ubx-matter nora-w4 --clone'). IDF_PATH / ESP_MATTER_PATH
# override it, e.g. to reuse an existing ~/esp checkout.
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SDK="${UBX_MATTER_SDK_ROOT:-}"
IDF_PATH="${IDF_PATH:-${SDK:+${SDK}/esp-idf}}"
ESP_MATTER_PATH="${ESP_MATTER_PATH:-${SDK:+${SDK}/esp-matter}}"
IMAGE_NAME="u-connect-matter-thermometer"

die() { echo "[FAIL] $*" >&2; exit 1; }

require_sdk() {
    [ -n "${IDF_PATH}" ] && [ -n "${ESP_MATTER_PATH}" ] \
        || die "UBX_MATTER_SDK_ROOT not set. Run via: ubx-matter nora-w4 --build thermometer"
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
    # shellcheck source=/dev/null
    . "${IDF_PATH}/export.sh"
    ( cd "${ESP_MATTER_PATH}" && ./install.sh --no-host-tool )
    echo "[OK] Setup complete."
}

activate() {
    require_sdk
    [ -f "${ESP_MATTER_PATH}/export.sh" ] || die "esp-matter not installed. Run: ubx-matter nora-w4 --install"
    # shellcheck source=/dev/null
    . "${IDF_PATH}/export.sh"
    export ESP_MATTER_PATH
    # shellcheck source=/dev/null
    . "${ESP_MATTER_PATH}/export.sh"
    export EXTRA_COMPONENT_DIRS="${ESP_MATTER_PATH}/components"
    export IDF_CCACHE_ENABLE=1
}

build() {
    local wifi=0 sensor="" defaults="sdkconfig.defaults"
    for arg in "$@"; do
        case "$arg" in
            --wifi)       wifi=1 ;;
            --clickboard) [ -z "$sensor" ] || die "--clickboard and --hvac share MikroBUS 1"; sensor="-DAPP_USE_DS2482=1" ;;
            --hvac)       [ -z "$sensor" ] || die "--clickboard and --hvac share MikroBUS 1"; sensor="-DAPP_USE_HVAC=1" ;;
            *) die "Unknown build option: $arg" ;;
        esac
    done
    [ "$wifi" -eq 1 ] && defaults="sdkconfig.defaults;sdkconfig.defaults.wifi"

    activate
    cd "${APP_DIR}"
    echo "[INFO] Network: $([ "$wifi" -eq 1 ] && echo 'Matter-over-Wi-Fi' || echo 'Matter-over-Thread (SED)')"
    echo "[INFO] Sensor:  ${sensor:-direct 1-Wire on GPIO15}"
    # shellcheck disable=SC2086
    idf.py ${sensor} -DSDKCONFIG_DEFAULTS="${defaults}" reconfigure
    idf.py build

    mkdir -p images
    cp -f build/bootloader/bootloader.bin           images/
    cp -f build/partition_table/partition-table.bin images/
    cp -f build/ota_data_initial.bin                images/
    cp -f "build/${IMAGE_NAME}.bin"                 images/
    echo "[OK] Images in ${APP_DIR}/images/"
}

case "${1:-}" in
    setup) setup ;;
    build) shift; build "$@" ;;
    clean) rm -rf "${APP_DIR}/build" "${APP_DIR}/sdkconfig" "${APP_DIR}/images"; echo "[OK] Cleaned." ;;
    *)     echo "Usage: $0 setup | build [--wifi] [--clickboard | --hvac] | clean"; exit 1 ;;
esac
