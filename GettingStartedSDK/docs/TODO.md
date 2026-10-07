# TODO

Open work on the Getting Started SDK, in rough priority order.
Last updated 2026-10-07 (branch `cmag_getting_started_sdk`, commit `384030e`).

## In progress / resume here

- [ ] **NCS v3.4.1 download into `C:\ncs\v3.4.1`** was started with
      `ubx-sdk.cmd nora-b2 --clone`. If it did not finish, re-run the same command;
      it skips `west init` and resumes `west update`.
- [ ] **Build NORA-B2 and ALMA-B2** once NCS is in place:
      `ubx-sdk.cmd nora-b2 --doctor --build hello_world`, then the same for `alma-b2`.
      `--doctor` should now pick `C:\ncs\v3.4.1` over the old v2.9.0 `~/ncs`.
      Builds may need the Nordic toolchain bundle in `C:\ncs\toolchains` on PATH
      (`nrfutil sdk-manager toolchain launch`) rather than the Arm GNU toolchain.
- [ ] **Re-run NORA-W3** `ubx-sdk.cmd nora-w3 --build project_hp`. The last attempt
      failed only because E: was full (`fatal error: when writing output to
      wlan_network.i`). Building on `/mnt/e` is slow; consider moving the Ameba-D
      SDK into the WSL2 filesystem.
- [ ] **Rewrite `docs/BUILD_TEST_RESULTS.md`** with real results. It is stale and
      self-contradictory. Verified so far on 2026-10-07:
      - IRIS-W1 `demo_apps/hello_world`, MCUXpresso 26.09.00-pvw2, Arm GCC 14.2.1
        auto-detected: 28,968 B flash (1.4% of 2 MB)
      - NORA-W4 `hello_world`, ESP-IDF 6.2.0, Windows: `.bin` 130,736 B, 88% of app
        partition free
      - NORA-W5 `ble_wifi_provisioning` (2026-09-28, not re-run)

## Disk space

- [ ] E: had only ~8.7 GB free. Check `%TEMP%\e_sizes.txt` (size scan of E:) and
      decide what to clean outside the SDK (Recycle Bin, `Matter`, `src`, ...).

## Matter

- [ ] NORA-W4 vendor build: `ubx-matter.cmd nora-w4 --install --build light`
      (proves the vendor-only build path end to end).
- [ ] NORA-W5: install Linux **SysConfig 1.26.3** and **SimpleLink Wi-Fi Toolbox
      4.2.4** into `~/ti` in the `Ubuntu-22.04` WSL distro (ti.com downloads), then
      `ubx-matter.cmd nora-w5 --install --build` (builds `lighting-app`).
- [ ] Wire `--build` for IRIS-W1 and NORA-W3 Matter (add
      `scripts/matter_vendor/iris_w1.sh` / `nora_w3.sh`); today they are list-only.

## CI

- [ ] Check the first GitLab pipelines went green (python 3.10 + 3.12). If jobs are
      stuck or the image pull fails, point `image:` at the internal registry.

## Hardware (needs EVKs)

- [ ] `--flash`, `--log` and `--mac` on every EVK, starting with IRIS-W1 and NORA-W5.
- [ ] Verify XDS110 flashing with the fixed `-param1 <serial>` argument (NORA-W5).

## RF configuration (needs the RF team)

- [ ] u-blox RF calibration / TX power assets for NORA-W5, NORA-B2 and ALMA-B2.
      Profiles in `modules/<TARGET>/profile.json` are `pending`; without assets the
      firmware is not regulatory compliant.

## Nice to have

- [ ] `scripts/setup_build_env.sh` still exports `ARMGCC_DIR` by hand; drop it or
      align it with the auto-detection in `iris_w1_build.py`.
- [ ] Space estimates in the drivers are rough; refine them from real clone sizes.
- [ ] `ubx_evkalmab2` board once u-blox publishes it (ALMA-B2 uses `nrf54lm20dk`).
- [ ] Review and merge `cmag_getting_started_sdk` to master.
