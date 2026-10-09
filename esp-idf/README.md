# ESP-IDF

Examples on how to apply RF calibration and limit TX power for compliance reasons
using the Espressif ESP-IDF. The output power configuration is product specific,
so each module has its own project.

## SDK resources

| Resource | Link |
|----------|------|
| Repository | [espressif/esp-idf](https://github.com/espressif/esp-idf) |
| Documentation (get started) | [ESP32](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/index.html) (NINA-W10), [ESP32-S3](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/index.html) (NORA-W10), [ESP32-C6](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c6/get-started/index.html) (NORA-W40) |
| RF calibration | [ESP-IDF RF calibration guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/RF_calibration.html) |
| Flashing tool | [espressif/esptool](https://github.com/espressif/esptool) |

| Module   | Folder                         | Remarks                    |
|----------|--------------------------------|----------------------------|
| NINA-W1  | [nina-w10](nina-w10/README.md) | Also reads OTP information |
| NORA-W1  | [nora-w10](nora-w10/README.md) |                            |
| NORA-W40 | [nora-w40](nora-w40/README.md) |                            |
