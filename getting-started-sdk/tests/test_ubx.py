"""Launcher core (scripts/ubx.py): flag parsing, translation, ordering, WSL2 hop."""

import sys

import pytest

import matter_build
import ubx

SCRIPTS = ubx.SCRIPTS_DIR


@pytest.fixture
def native(monkeypatch, calls):
    """Run as if on Linux, with every driver call recorded instead of executed."""
    monkeypatch.setattr(ubx, "host_is_windows", lambda: False)
    monkeypatch.setattr(ubx.subprocess, "call", calls)
    return calls


@pytest.fixture
def windows(monkeypatch, calls):
    monkeypatch.setattr(ubx, "host_is_windows", lambda: True)
    monkeypatch.setattr(ubx.subprocess, "call", calls)
    monkeypatch.delenv("UBX_WSL_DISTRO", raising=False)
    monkeypatch.delenv("UBX_MATTER_ROOT", raising=False)
    return calls


def ctx(argv, matter=False):
    parsed = ubx.parse(argv, matter=matter)
    assert isinstance(parsed, ubx.Context), parsed
    return parsed


def steps(cmds):
    """Reduce recorded commands to (script, action) pairs."""
    out = []
    for cmd in cmds:
        script = cmd[1].replace("\\", "/").rsplit("/", 1)[-1]
        rest = cmd[2:]
        if script in ("module_config.py", "matter_build.py") or rest[:1] in (["nora-b20-b21-b22"], ["alma-b20-b21"]):
            rest = rest[1:]
        out.append((script, rest[0]))
    return out


# ---------------------------------------------------------------------------
# parse
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("argv", [[], ["--help"], ["-h"], ["help"], ["nora-w40"], ["nora-w40", "--help"]])
def test_help_exits_zero(argv, capsys):
    assert ubx.parse(argv) == 0
    assert "ubx-sdk <target>" in capsys.readouterr().out


def test_matter_help_is_separate(capsys):
    assert ubx.parse(["--help"], matter=True) == 0
    out = capsys.readouterr().out
    assert "ubx-matter <target>" in out
    assert "--rf-config" not in out


def test_unknown_target(capsys):
    assert ubx.parse(["nora-w99", "--list"]) == 1
    assert "Unknown target" in capsys.readouterr().out


@pytest.mark.parametrize("name", ["nora-w36", "nora-w56", "nora-w57", "nora-b26", "nora-b27"])
def test_uconnectxpress_parts_are_explained(name, capsys):
    assert ubx.parse([name, "--list"]) == 1
    assert "u-connectXpress" in capsys.readouterr().out


def test_nora_w1_is_not_iris_w10(capsys):
    assert ubx.parse(["nora-w1", "--list"]) == 1
    assert "NORA-W1 (ESP32)" in capsys.readouterr().out


@pytest.mark.parametrize("alias,key", [
    ("w50", "nora-w50-w51"), ("nora-w51", "nora-w50-w51"), ("iris-w10", "iris-w10"),
    ("NORA-W40", "nora-w40"), ("w30", "nora-w30"), ("alma", "alma-b20-b21"), ("nora_b20_b21_b22", "nora-b20-b21-b22"),
])
def test_aliases(alias, key):
    assert ctx([alias, "--list"]).target.key == key


@pytest.mark.parametrize("bare", ["nora-w3", "nora-w4", "nora-w5", "nora-b2", "alma-b2", "iris-w1"])
def test_bare_series_is_not_a_target(bare):
    assert ubx.resolve_target(bare) is None


def test_every_alias_resolves():
    for alias, key in ubx.ALIASES.items():
        assert key in ubx.TARGETS, alias


def test_unknown_flag(capsys):
    assert ubx.parse(["nora-w40", "--bogus"]) == 1
    assert "Unknown argument" in capsys.readouterr().out


@pytest.mark.parametrize("flag", ["--variant", "--region"])
def test_value_flags_need_a_value(flag):
    assert ubx.parse(["nora-w30", flag]) == 1
    assert ubx.parse(["nora-w30", flag, "--rf-config"]) == 1


def test_optional_values_are_consumed():
    c = ctx(["nora-w40", "--build", "blink", "--flash", "COM3", "--mac", "COM4", "--log", "COM5"])
    assert (c.example, c.probe, c.mac_port, c.port) == ("blink", "COM3", "COM4", "COM5")


def test_optional_value_is_not_a_flag():
    c = ctx(["nora-w40", "--build", "--flash"])
    assert c.example is None and c.probe is None
    assert c.actions == {"build", "flash"}


def test_double_dash_passes_the_rest_verbatim():
    c = ctx(["iris-w10", "--build", "x", "--", "--config", "release", "--list"])
    assert c.extra == ["--config", "release", "--list"]
    assert c.actions == {"build"}


def test_clean_all_implies_clean():
    c = ctx(["nora-w40", "--clean-all"])
    assert "clean" in c.actions and c.clean_all


def test_matter_flag_points_to_matter_launcher(capsys):
    assert ubx.parse(["nora-w40", "--matter", "--build"]) == 1
    assert "ubx-matter nora-w40" in capsys.readouterr().out


@pytest.mark.parametrize("flag", ["--full", "--build-sdk", "--clean-all", "--rf-config", "--mac",
                                  "--mac-set", "--burn", "--variant", "--region"])
def test_sdk_only_flags_rejected_by_matter(flag):
    assert ubx.parse(["nora-w40", flag], matter=True) == 1


def test_mac_set_takes_address_and_optional_port():
    c = ctx(["nora-w40", "--mac-set", "02:12:34:56:78:9A", "COM4", "--burn"])
    assert (c.mac_address, c.mac_port, c.burn) == ("02:12:34:56:78:9A", "COM4", True)
    assert ubx.argv_for(c, "mac-set") == ["mac", "--address", "02:12:34:56:78:9A",
                                         "--serial", "COM4", "--burn"]
    assert ubx.argv_for(ctx(["iris-w10", "--mac-set", "02:00:00:00:00:01"]), "mac-set") == \
        ["mac", "--address", "02:00:00:00:00:01"]


def test_mac_set_needs_an_address_and_burn_needs_mac_set():
    assert ubx.parse(["nora-w40", "--mac-set"]) == 1
    assert ubx.parse(["nora-w40", "--mac", "--burn"]) == 1


def test_ubx_project_example_builds_from_the_repository(native, monkeypatch):
    monkeypatch.setattr(ubx.module_config, "load_state", lambda key: {"applied": [{}]})
    assert ubx.main(["nora-w40", "--build", "ubx/rf-calibration", "--log"]) == 0
    project = ubx.SDK_ROOT.parent / "esp-idf" / "nora-w40"
    assert native.cmds[0][2:] == ["build", str(project)]
    assert native.cmds[1][2:] == ["log", str(project)]


def test_ubx_example_needing_rf_config(native, monkeypatch, capsys):
    monkeypatch.setattr(ubx.module_config, "load_state", lambda key: {})
    assert ubx.main(["nora-w40", "--build", "ubx/rf-calibration"]) == 1
    assert "--rf-config" in capsys.readouterr().out
    assert not native.calls
    assert ubx.main(["nora-w40", "--variant", "NORA-W401", "--rf-config",
                     "--build", "ubx/rf-calibration"]) == 0


def test_ubx_drop_in_example_explains_instead_of_building(native, capsys):
    assert ubx.main(["iris-w10", "--build", "ubx/read-otp-parameters"]) == 1
    assert not native.calls
    assert "driver_examples/romapi/otp/main.c" in capsys.readouterr().out


def test_unknown_ubx_example(native, capsys):
    assert ubx.main(["nora-w40", "--build", "ubx/nope"]) == 1
    assert "No u-blox example" in capsys.readouterr().out


def test_flash_log_only_for_nordic_matter():
    assert ubx.parse(["nora-w40", "--flash"], matter=True) == 1
    assert ubx.parse(["nora-w50-w51", "--log"], matter=True) == 1
    assert ctx(["nora-b20-b21-b22", "--flash", "--log"], matter=True).actions == {"flash", "log"}


def test_variant_without_rf_config_warns(capsys):
    ctx(["nora-w30", "--variant", "NORA-W301", "--build"])
    assert "[WARNING]" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# argv_for: uniform action -> driver subcommand
# ---------------------------------------------------------------------------

def argv(argv_list, action, matter=False):
    return ubx.argv_for(ctx(argv_list, matter=matter), action)


@pytest.mark.parametrize("action", ["doctor", "install", "list"])
def test_simple_actions(action):
    for key in ubx.TARGETS:
        assert argv([key, f"--{action}"], action) == [action]


def test_build_uses_target_default():
    for key, target in ubx.TARGETS.items():
        assert argv([key, "--build"], "build") == ["build", target.default_example]


def test_build_forwards_extra():
    assert argv(["iris-w10", "--build", "x", "--", "-p"], "build") == ["build", "x", "-p"]


def test_full_only_for_iris():
    assert argv(["iris-w10", "--clone", "--full"], "clone") == ["clone", "--full"]
    assert argv(["nora-w40", "--clone", "--full"], "clone") == ["clone"]


@pytest.mark.parametrize("key", ["iris-w10", "nora-w30", "nora-w40", "nora-b20-b21-b22", "alma-b20-b21"])
def test_clone_version_becomes_revision(key):
    assert argv([key, "--clone", "v5.5.1", "--build"], "clone") == ["clone", "--revision", "v5.5.1"]


def test_clone_version_reaches_nora_w50_w51():
    assert argv(["nora-w50-w51", "--clone", "main"], "clone") == ["clone", "--revision", "main"]


def test_clone_without_version_takes_no_positional():
    ctx = ubx.parse(["nora-w40", "--clone", "--build", "hello_world"])
    assert ctx.sdk_version is None
    assert ctx.example == "hello_world"


def test_clean_variants():
    assert argv(["nora-w40", "--clean"], "clean") == ["clean"]
    assert argv(["nora-w40", "--clean-all"], "clean") == ["clean", "--all"]
    # NORA-W50-W51 has no clean subcommand; a clean build stands in for it.
    assert argv(["nora-w50-w51", "--clean"], "clean") == ["build", "network_terminal", "--clean"]
    assert argv(["nora-w50-w51", "--clean-all"], "clean") is None
    # NORA-W30 cleans only the project being built.
    assert argv(["nora-w30", "--clean", "--build", "project_hp"], "clean") == ["clean", "project_hp"]
    assert argv(["nora-w30", "--clean"], "clean") == ["clean"]
    # Every target except IRIS-W10 cleans just the example being built.
    assert argv(["nora-w40", "--clean", "--build", "hello_world"], "clean") == ["clean", "hello_world"]
    assert argv(["nora-b20-b21-b22", "--clean", "--build", "blinky"], "clean") == ["clean", "blinky"]
    assert argv(["iris-w10", "--clean", "--build", "hello_world"], "clean") == ["clean"]


def test_flash_and_log():
    assert argv(["iris-w10", "--flash", "123"], "flash") == ["flash", "demo_apps/hello_world", "--serial", "123"]
    assert argv(["iris-w10", "--log", "COM9"], "log") == ["log", "COM9"]
    # idf.py monitor needs the example directory.
    assert argv(["nora-w40", "--log", "COM9"], "log") == ["log", "hello_world", "--serial", "COM9"]


def test_unsupported_action_is_skipped(capsys):
    assert argv(["nora-w30", "--build-sdk"], "build-sdk") is None
    assert "not supported" in capsys.readouterr().out


def test_nora_w30_flash_and_log():
    assert argv(["nora-w30", "--flash", "1100005639"], "flash") == \
        ["flash", "project_hp", "--serial", "1100005639"]
    assert argv(["nora-w30", "--log", "COM191"], "log") == ["log", "COM191"]


def test_build_sdk_only_nora_w50_w51():
    assert argv(["nora-w50-w51", "--build-sdk"], "build-sdk") == ["build-sdk"]
    assert argv(["nora-w40", "--build-sdk"], "build-sdk") is None


def test_rf_config_and_mac_go_to_module_config():
    assert argv(["nora-w30", "--variant", "NORA-W301", "--region", "ETSI", "--rf-config"], "rf-config") == \
        ["apply", "--variant", "NORA-W301", "--region", "ETSI"]
    assert argv(["nora-w40", "--mac"], "mac") == ["mac"]
    assert argv(["nora-w40", "--mac", "COM7"], "mac") == ["mac", "--serial", "COM7"]


def test_set_overrides_a_profile_variable(capsys):
    assert argv(["iris-w10", "--rf-config", "--set", "flash_part=macronix-8mb", "--set", "a=b"], "rf-config") == \
        ["apply", "--set", "flash_part=macronix-8mb", "--set", "a=b"]
    assert ubx.parse(["iris-w10", "--rf-config", "--set", "flash_part"]) == 1
    assert ubx.parse(["iris-w10", "--rf-config", "--set"]) == 1
    assert "KEY=VALUE" in capsys.readouterr().out
    assert ubx.parse(["iris-w10", "--set", "a=b", "--rf-config"], matter=True) == 1
    ctx(["iris-w10", "--set", "a=b", "--build"])
    assert "--set only take effect with --rf-config" in capsys.readouterr().out


def test_matter_vendor_translation():
    assert argv(["nora-w50-w51", "--list"], "list", matter=True) == ["list"]
    assert argv(["nora-w50-w51", "--build"], "build", matter=True) == ["build"]
    assert argv(["nora-w40", "--build", "light"], "build", matter=True) == ["build", "light"]
    # '' keeps the extras out of the example slot.
    assert argv(["nora-w40", "--build", "--", "-DX=1"], "build", matter=True) == ["build", "", "-DX=1"]
    assert argv(["nora-w40", "--clean", "--build", "light"], "clean", matter=True) == ["clean", "light"]


def test_matter_ncs_translation():
    assert argv(["nora-b20-b21-b22", "--list"], "list", matter=True) == ["list", "--matter"]
    assert argv(["nora-b20-b21-b22", "--build"], "build", matter=True) == ["build", "matter/light_bulb"]
    assert argv(["alma-b20-b21", "--build", "lock"], "build", matter=True) == ["build", "matter/lock"]
    assert argv(["nora-b20-b21-b22", "--build", "matter/lock"], "build", matter=True) == ["build", "matter/lock"]
    assert argv(["nora-b20-b21-b22", "--flash"], "flash", matter=True) == ["flash", "matter/light_bulb"]


# ---------------------------------------------------------------------------
# run: order, failure handling, driver selection
# ---------------------------------------------------------------------------

def test_actions_run_in_fixed_order(native):
    assert ubx.main(["nora-w40", "--log", "--build", "hello_world", "--clean", "--list", "--doctor"]) == 0
    assert steps(native.cmds) == [
        ("nora_w40_build.py", "doctor"),
        ("module_config.py", "status"),
        ("nora_w40_build.py", "list"),
        ("module_config.py", "examples"),
        ("nora_w40_build.py", "clean"),
        ("nora_w40_build.py", "build"),
        ("nora_w40_build.py", "log"),
    ]


def test_full_action_order_matches_constant(native):
    flags = ["--log", "--mac", "--mac-set", "02:00:00:00:00:01", "--flash", "--build", "--clean",
             "--list", "--rf-config", "--build-sdk", "--install", "--clone", "--doctor"]
    assert ubx.main(["nora-w50-w51", *flags]) == 0
    actions = [a for _, a in steps(native.cmds) if a not in ("status", "examples")]
    translated = {"apply": "rf-config"}
    # NORA-W50-W51 maps --clean onto a clean build; --mac-set and --mac both call 'mac'.
    order = [translated.get(a, a) for a in actions]
    assert order[:5] == ["doctor", "clone", "install", "build-sdk", "rf-config"]
    assert order[5:] == ["list", "build", "build", "flash", "mac", "mac", "log"]
    assert native.cmds[-3][3:] == ["mac", "--address", "02:00:00:00:00:01"]


def test_failure_stops_the_chain(native, capsys):
    native.returns = [1]
    assert ubx.main(["nora-w40", "--list", "--build"]) == 1
    assert len(native.calls) == 1
    assert "list failed" in capsys.readouterr().out


def test_failing_doctor_still_reports_rf_status(native):
    native.returns = [1]
    assert ubx.main(["nora-w40", "--doctor", "--build"]) == 1
    assert steps(native.cmds) == [("nora_w40_build.py", "doctor"), ("module_config.py", "status")]


def test_failing_doctor_does_not_block_setup(native, capsys):
    native.returns = [1]
    assert ubx.main(["iris-w10", "--doctor", "--clone", "--build"]) == 0
    assert [a for _, a in steps(native.cmds)] == ["doctor", "status", "clone", "build"]
    assert "continuing with the setup steps" in capsys.readouterr().out


def test_extra_without_build_warns(capsys):
    ctx(["nora-w40", "--flash", "--", "--foo"])
    assert "passed to --build only" in capsys.readouterr().out


def test_clean_with_build_cleans_the_default_example():
    assert argv(["nora-w40", "--clean", "--build"], "clean") == ["clean", "hello_world"]
    assert argv(["iris-w10", "--clean", "--build"], "clean") == ["clean"]


def test_drivers_run_with_this_python_from_sdk_root(native):
    ubx.main(["nora-w40", "--list"])
    call = native.calls[0]
    assert call["cmd"][0] == sys.executable
    assert call["cwd"] == str(ubx.SDK_ROOT)


def test_nordic_driver_gets_target_key(native):
    ubx.main(["alma-b20-b21", "--list"])
    assert native.cmds[0][2:] == ["alma-b20-b21", "list"]


def test_matter_uses_matter_driver(native):
    ubx.main(["nora-w50-w51", "--doctor", "--list"], matter=True)
    assert steps(native.cmds) == [("matter_build.py", "doctor"), ("matter_build.py", "list")]
    assert native.cmds[0][2] == "nora-w50-w51"


def test_ncs_matter_uses_ncs_driver(native):
    ubx.main(["nora-b20-b21-b22", "--list"], matter=True)
    assert native.cmds[0][1].endswith("nordic_ncs_build.py")
    assert native.cmds[0][2:] == ["nora-b20-b21-b22", "list", "--matter"]


def test_rf_config_runs_module_config(native):
    ubx.main(["nora-w30", "--variant", "NORA-W301", "--rf-config"])
    assert native.cmds[0][1].endswith("module_config.py")
    assert native.cmds[0][2:] == ["nora-w30", "apply", "--variant", "NORA-W301"]


def test_dry_run_executes_nothing(native, capsys):
    assert ubx.main(["nora-w40", "--dry-run", "--doctor", "--build"]) == 0
    assert not native.calls
    out = capsys.readouterr().out
    assert out.count("[DRY-RUN]") == 3


def test_dry_run_shows_the_wsl_hop(windows, capsys):
    assert ubx.main(["nora-w50-w51", "--list", "--dry-run"], matter=True) == 0
    assert not windows.calls
    assert "[DRY-RUN] wsl -d Ubuntu-22.04" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# WSL2 hop
# ---------------------------------------------------------------------------

def test_linux_only_sdk_target_hops(windows):
    assert ubx.main(["nora-w30", "--build", "--wsl"]) == 0
    cmd = windows.cmds[0]
    assert cmd[:2] == ["wsl", "--"]
    assert "./ubx-sdk.sh nora-w30 --build" in cmd[-1]
    assert "--wsl" not in cmd[-1]


def test_failed_wsl_hop_suggests_vmcompute_restart(windows, capsys):
    windows.returns = [1]
    assert ubx.main(["nora-w30", "--build"]) == 1
    out = capsys.readouterr().out
    assert "net stop vmcompute" in out and "net start vmcompute" in out


@pytest.mark.parametrize("rc", [0, 130])
def test_wsl_fix_not_shown_on_success_or_ctrl_c(windows, capsys, rc):
    windows.returns = [rc]
    ubx.main(["nora-w30", "--build"])
    assert "vmcompute" not in capsys.readouterr().out


def test_missing_wsl_exe_suggests_vmcompute_restart(windows, monkeypatch, capsys):
    def boom(cmd, **kwargs):
        raise FileNotFoundError("wsl")
    monkeypatch.setattr(ubx.subprocess, "call", boom)
    assert ubx.main(["nora-w30", "--build"]) == 1
    assert "net start vmcompute" in capsys.readouterr().out


def test_no_wsl_suppresses_hop(windows):
    ubx.main(["nora-w30", "--list", "--no-wsl"])
    assert windows.cmds[0][0] == sys.executable


def test_ctrl_c_stops_quietly(native, monkeypatch, capsys):
    seen = []

    def interrupted(cmd, **kwargs):
        seen.append(cmd)
        raise KeyboardInterrupt
    monkeypatch.setattr(ubx.subprocess, "call", interrupted)
    assert ubx.main(["nora-w40", "--flash", "--log"]) == 130
    assert len(seen) == 1 and "Stopped (Ctrl+C)" in capsys.readouterr().out
    monkeypatch.setattr(ubx, "run", lambda *a: (_ for _ in ()).throw(KeyboardInterrupt))
    assert ubx.main(["nora-w40", "--log"]) == 130


def test_flash_and_log_stay_on_windows_after_the_hop(windows):
    assert ubx.main(["nora-w30", "--build", "--flash", "--log", "COM191"]) == 0
    hop, flash, log = windows.cmds
    assert hop[:2] == ["wsl", "--"]
    assert hop[-1].startswith("export UBX_SKIP_ACTIONS=flash,log && ")
    assert flash[0] == sys.executable and flash[2:] == ["flash", "project_hp"]
    assert log[2:] == ["log", "COM191"]


def test_flash_alone_does_not_hop(windows):
    assert ubx.main(["nora-w30", "--flash"]) == 0
    assert [c[2] for c in windows.cmds] == ["flash"]


def test_failed_hop_skips_flash(windows):
    windows.returns = [2]
    assert ubx.main(["nora-w30", "--build", "--flash"]) == 2
    assert len(windows.calls) == 1


def test_skipped_actions_inside_the_hop(native, monkeypatch):
    monkeypatch.setenv(ubx.SKIP_ACTIONS_ENV, "flash,log")
    assert ubx.main(["nora-w30", "--build", "--flash", "--log"]) == 0
    assert [c[2] for c in native.cmds] == ["build"]


def test_windows_native_targets_do_not_hop(windows):
    ubx.main(["nora-w40", "--list"])
    assert windows.cmds[0][0] == sys.executable


@pytest.mark.parametrize("action", ["--doctor", "--list", "--clone", "--build"])
def test_vendor_matter_always_hops(windows, action):
    ubx.main(["nora-w40", action], matter=True)
    cmd = windows.cmds[0]
    assert cmd[:2] == ["wsl", "--"]
    assert "./ubx-matter.sh nora-w40" in cmd[-1]


def test_nora_w50_w51_matter_uses_ubuntu_22_04(windows):
    ubx.main(["nora-w50-w51", "--list"], matter=True)
    assert windows.cmds[0][:4] == ["wsl", "-d", "Ubuntu-22.04", "--"]


def test_distro_only_applies_to_matter(windows):
    ubx.main(["nora-w50-w51", "--list"])
    assert windows.cmds[0][0] == sys.executable


def test_distro_override(windows, monkeypatch):
    monkeypatch.setenv("UBX_WSL_DISTRO", "Debian")
    ubx.main(["nora-w50-w51", "--list"], matter=True)
    assert windows.cmds[0][:3] == ["wsl", "-d", "Debian"]


def test_ncs_matter_never_hops(windows):
    ubx.main(["nora-b20-b21-b22", "--build"], matter=True)
    assert windows.cmds[0][0] == sys.executable


def test_matter_root_is_forwarded_with_home_expansion(windows, monkeypatch):
    monkeypatch.setenv("UBX_MATTER_ROOT", "~/ubx-matter")
    ubx.main(["nora-w40", "--list"], matter=True)
    assert 'export UBX_MATTER_ROOT="$HOME"/ubx-matter' in windows.cmds[0][-1]


def test_wsl_path_conversion(tmp_path):
    if sys.platform != "win32":
        pytest.skip("drive-letter conversion is Windows-only")
    assert ubx.to_wsl_path(ubx.Path("C:/Users/x")) == "/mnt/c/Users/x"


# ---------------------------------------------------------------------------
# Consistency between tables, scripts and help text
# ---------------------------------------------------------------------------

def test_driver_scripts_exist():
    for target in ubx.TARGETS.values():
        assert (SCRIPTS / target.script).is_file(), target.script


def test_shim_line_endings():
    # cmd.exe misparses LF-only batch files.
    for shim in ubx.SDK_ROOT.glob("*.cmd"):
        data = shim.read_bytes()
        assert data.count(b"\n") == data.count(b"\r\n"), shim.name
    for shim in ubx.SDK_ROOT.glob("*.sh"):
        assert b"\r\n" not in shim.read_bytes(), shim.name


def test_help_lists_every_target():
    for key in ubx.TARGETS:
        assert f"  {key} " in ubx.USAGE
        assert f"  {key} " in ubx.MATTER_USAGE


def test_help_lists_flags_in_action_order():
    flags = [f"--{a}" for a in ubx.ACTION_ORDER]
    positions = [ubx.USAGE.index(f"  {f} ") for f in flags]
    assert positions == sorted(positions)


def test_matter_targets_match_launcher():
    vendor = set(matter_build.TARGETS)
    ncs = {k for k, t in ubx.TARGETS.items() if t.script == "nordic_ncs_build.py"}
    assert vendor | ncs == set(ubx.TARGETS)
    assert not vendor & ncs
