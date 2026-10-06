// SPDX-License-Identifier: Apache-2.0
//
// CHIPProjectConfig — per-device Matter SDK overrides for the NORA-W40
// thermometer. Picked to match a battery-powered SED:
//
//   - Long subscription max-interval ceiling (60 min) so controllers can
//     poll us infrequently without hammering the radio.
//   - Smaller mDNS / DNSSD footprint (we publish only what a sensor needs).
//   - Test VID/PID — replace with real DAC-issued IDs before shipping.

#pragma once

// Test certificate / spec-defined commissioning values. ALWAYS swap before
// CSA submission.
#define CHIP_DEVICE_CONFIG_DEVICE_VENDOR_ID                             0xFFF1
#define CHIP_DEVICE_CONFIG_DEVICE_PRODUCT_ID                            0x8011
#define CHIP_DEVICE_CONFIG_DEVICE_PRODUCT_NAME                          "u-blox NORA-W40 Thermometer"
#define CHIP_DEVICE_CONFIG_DEVICE_VENDOR_NAME                           "u-blox"
#define CHIP_DEVICE_CONFIG_DEVICE_HARDWARE_VERSION                      1
#define CHIP_DEVICE_CONFIG_DEVICE_HARDWARE_VERSION_STRING               "EVK-NORA-W40 v1.0"

// Subscribe min/max bounds — favour battery life.
#define CHIP_CONFIG_MIN_SUBSCRIPTION_INTERVAL_S                          5
#define CHIP_CONFIG_MAX_SUBSCRIPTION_INTERVAL_S                       3600

// Allow more parallel sessions than the default just in case the multi-admin
// demo box has all four ecosystems subscribed at once.
#define CHIP_CONFIG_MAX_FABRICS                                          5
