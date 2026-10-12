# TODO

Open work on the Getting Started SDK, in rough priority order.
Last updated 2026-10-12 (branch `cmag_getting_started_sdk`).

## In progress / resume here

- [x] Review pass (2026-10-12, dry-run and pytest only, nothing built): NCS `--build ... -- -D...`
      now reaches CMake; NCS `--flash` falls back to J-Link without nrfutil; `--clean-all`
      no longer deletes an NCS workspace or ESP-IDF the launcher did not fetch; a failing
      `--doctor` no longer blocks `--clone`/`--install`; `--clean --build` cleans the default
      example; driver hints name launcher commands (test-enforced); doc links are test-checked.
- [ ] Confirm on hardware the review changes that touch real tools: NCS `west build ... -- -DX=y`,
      `west flash -r jlink` fallback, NORA-W50-W51 fresh `--clone` inside WSL2 (now
      `~/ubx-sdk/sdks/simplelink-wifi/main`; an existing `~/nora-w50-w51` stays in use via the
      saved config).
- [ ] No launcher flag to force `west flash -r jlink` while nrfutil is installed (driver only).
- [x] NCS v3.4.1 is in `C:\ncs\v3.4.1`; NORA-B20-B21-B22 `hello_world` builds
      (2026-10-12, see `docs/BUILD_TEST_RESULTS.md`). The CMake configure step took
      about 4 minutes on this machine.
- [ ] **Build ALMA-B20-B21**: `ubx-sdk.cmd alma-b20-b21 --doctor --build hello_world`.
- [x] NORA-W50-W51 `--build-sdk` runs `configure` first, so the flow is launcher-only;
      `--flash` finds the Wi-Fi Toolbox in `C:\ti\simplelink_wifi_toolbox*` (2026-10-12).
- [x] NORA-W30 boot fault after `--flash` (2026-10-12): the image was fine; the
      chip was left under debugger control and faulted at its first low-power
      sleep. `--flash` now ends like pressing RESET (debug off, reset pin).
      `ATW?` answers in `--log`.
- [x] Ctrl+C in `--log` stops without a traceback on Windows (2026-10-12);
      cmd.exe still asks "Terminate batch job (Y/N)?".
- [ ] With several probes attached, `--flash` without a serial stops at
      nrfutil's interactive "select one" prompt; `--log` auto-detect picks a
      J-Link port, not the EVK-NORA-B2 FTDI console. Pick both from the probe serial.
      (J-Link targets already pick the board's probe, e.g. the IRIS-W10 MCU-Link.)
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
- [ ] IRIS-W10 `ubx/read-otp-parameters` is a drop-in file; make it a buildable
      `project` once `driver_examples/romapi/otp` exists in the MCUXpresso workspace.
      The MAC is read with `wifi_examples/wifi_cli` + `wlan-mac`; the `ubx/read-mac-address`
      drop-in was removed from the profile (2026-10-12): its base `wifi_examples/wifi_test_mode`
      is not in the board-only fetch, and the file contains non-breaking spaces gcc rejects.
      Ask the asset owner to fix the file if it should come back.
- [x] MAC on NORA-B20-B21-B22: u-blox programs no address; the Nordic FICR
      `DEVICEADDR` (random static) is used, shown by `bluetooth/beacon` (2026-10-12).
- [x] ALMA-B20-B21: treated like NORA-B2, no u-blox address in production; the FICR
      address is used (decided 2026-10-12).
- [ ] `--mac-set` runtime lines for the Nordic targets (own public address via the
      controller, or a static random identity with `bt_id_create()`), confirmed in NCS.
- [ ] Verify on hardware: NORA-W40 `--mac` derived addresses and `ubx/read-mac`,
      IRIS-W10 `wlan-mac`, NORA-W30 `ATW?`.
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

- [x] GitLab pipelines green (2026-10-12, #65992): tests on Python 3.10 and 3.14
      (96% coverage), ruff and shellcheck. #65982 had failed because the project
      had no runners; instance runners are now on and jobs carry `docker, linux`.
- [ ] April 2027 (Ubuntu 22.04 end of life): raise the minimum to Python 3.11
      (shims, `setup_venv.py`, CI matrix, ruff `--target-version`, docs).

## Hardware (needs EVKs; planned on one machine with every platform)

- [ ] `--flash`, `--log` and `--mac` on every EVK, starting with IRIS-W10 and NORA-W50-W51.
- [ ] Verify XDS110 flashing (NORA-W50-W51): `--flash` now passes the build's
      `tool_settings.json` to the toolbox programmer (as TI's Zephyr runner does), run from
      its folder, with `-param1 <serial>`. Confirm the SDK example build writes that file.

## RF configuration (needs the RF team)

- [ ] u-blox RF calibration / TX power assets for NORA-W50-W51, NORA-B20-B21-B22 and ALMA-B20-B21.
      Profiles in `modules/<target>/profile.json` are `pending`; without assets the
      firmware is not regulatory compliant.

## Nice to have

- [ ] Space estimates in the drivers are rough; refine them from real clone sizes.
- [ ] `--rf-config` patch ops fall back to `git apply` when GNU `patch` is not on PATH
      (Windows). It honours `core.autocrlf`, so with `autocrlf=true` a patched LF file is
      written back as CRLF. Harmless for SDKs cloned with the same setting; decide whether
      to pin `-c core.autocrlf=false` once a CRLF checkout has been tested.
- [ ] `ubx_evkalmab2` board once u-blox publishes it (ALMA-B20-B21 uses `nrf54lm20dk`).
- [ ] Review and merge `cmag_getting_started_sdk` to master.
