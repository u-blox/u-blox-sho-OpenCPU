# TODO

Open work on the Getting Started SDK, in rough priority order.
Last updated 2026-10-12 (branch `cmag_getting_started_sdk`).

## In progress / resume here

- [ ] **NCS v3.4.1 download into `C:\ncs\v3.4.1`** was started with
      `ubx-sdk.cmd nora-b20-b21-b22 --clone`. If it did not finish, re-run the same command;
      it skips `west init` and resumes `west update`.
- [ ] **Build NORA-B20-B21-B22 and ALMA-B20-B21** once NCS is in place:
      `ubx-sdk.cmd nora-b20-b21-b22 --doctor --build hello_world`, then the same for `alma-b20-b21`.
      `--doctor` should now pick `C:\ncs\v3.4.1` over the old v2.9.0 `~/ncs`.
      Builds may need the Nordic toolchain bundle in `C:\ncs\toolchains` on PATH
      (`nrfutil sdk-manager toolchain launch`) rather than the Arm GNU toolchain.
- [ ] **Re-run NORA-W30** `ubx-sdk.cmd nora-w30 --build project_hp`. The last attempt
      failed only because E: was full (`fatal error: when writing output to
      wlan_network.i`). Building on `/mnt/e` is slow; consider moving the Ameba-D
      SDK into the WSL2 filesystem.
- [ ] **Re-run each target once** after the move to `sdks/<vendor>/<version>/`
      and record it in `docs/BUILD_TEST_RESULTS.md` (rewritten 2026-10-12 with
      only the verified results).

## Asset layout (after merging `mhan-new-structure`)

- [x] Vendor SDKs moved to `sdks/<vendor>/<version>/` and per-host config to
      `modules/<target>/config/` (2026-10-12). Old-layout migration code, legacy
      short keys, `migrate_venv.*`, `setup_build_env.sh`, stale build folders and
      the repo-root `mcuxpresso-sdk/` removed.
- [ ] NORA-W50-W51 Matter: `/root/ubx-matter/NORA-W5` was renamed to `nora-w50-w51`
      (2026-10-12) and its bootstrap environment removed. Run
      `ubx-matter.cmd nora-w50-w51 --install` once to bootstrap it again.
- [ ] `--rf-config` writes module-specific RF data into the shared
      `sdks/<vendor>/<version>/` tree. Two modules on one vendor SDK version would
      overwrite each other; move the RF data into the build project before that happens.
- [ ] Agree with the asset owner on folder names for the coming targets:
      `simplelink/nora-w50-w51/`, `zephyr/nora-b20-b21-b22/`, `zephyr/alma-b20-b21/`
      (target key as the module folder, like `esp-idf/nora-w40/`).
- [ ] `esp-idf/nora-w10/` and `esp-idf/nina-w10/` stay asset-only (NORA-W1/NINA-W1 are
      not targets of this SDK). Confirm.
- [ ] IRIS-W10 `ubx/read-mac-address` and `ubx/read-otp-parameters` are drop-in files.
      Make them buildable `project` examples once the matching base example exists in
      the MCUXpresso workspace (`wifi_examples/wifi_test_mode`, `driver_examples/romapi/otp`
      were not found in the board-only fetch).
- [ ] `--mac-set` runtime lines for NORA-W50-W51, NORA-B20-B21-B22 and ALMA-B20-B21
      (only IRIS-W10, NORA-W30 and NORA-W40 are documented). `--burn` is wired for
      NORA-W40 (espefuse) only; untested on hardware.
- [ ] Zephyr `BOARD_ROOT=<repo>/zephyr` for targets that need a u-blox board that is not
      upstream. Not needed today: `ubx_evknorab2` is upstream, ALMA-B20-B21 uses the DK.

## Disk space

- [ ] E: had only ~8.7 GB free. Check `%TEMP%\e_sizes.txt` (size scan of E:) and
      decide what to clean outside the SDK (Recycle Bin, `Matter`, `src`, ...).

## Matter

- [ ] NORA-W40 vendor build: `ubx-matter.cmd nora-w40 --install --build light`
      (proves the vendor-only build path end to end).
- [ ] NORA-W50-W51: install Linux **SysConfig 1.26.3** and **SimpleLink Wi-Fi Toolbox
      4.2.4** into `~/ti` in the `Ubuntu-22.04` WSL distro (ti.com downloads), then
      `ubx-matter.cmd nora-w50-w51 --install --build` (builds `lighting-app`).
- [ ] Wire `--build` for IRIS-W10 and NORA-W30 Matter (add
      `scripts/matter_vendor/iris_w10.sh` / `nora_w30.sh`); today they are list-only.

## CI

- [ ] Check the first GitLab pipelines went green (python 3.10 + 3.12). If jobs are
      stuck or the image pull fails, point `image:` at the internal registry.

## Hardware (needs EVKs)

- [ ] `--flash`, `--log` and `--mac` on every EVK, starting with IRIS-W10 and NORA-W50-W51.
- [ ] Verify XDS110 flashing with the fixed `-param1 <serial>` argument (NORA-W50-W51).

## RF configuration (needs the RF team)

- [ ] u-blox RF calibration / TX power assets for NORA-W50-W51, NORA-B20-B21-B22 and ALMA-B20-B21.
      Profiles in `modules/<target>/profile.json` are `pending`; without assets the
      firmware is not regulatory compliant.

## Nice to have

- [ ] Space estimates in the drivers are rough; refine them from real clone sizes.
- [ ] `ubx_evkalmab2` board once u-blox publishes it (ALMA-B20-B21 uses `nrf54lm20dk`).
- [ ] Review and merge `cmag_getting_started_sdk` to master.
