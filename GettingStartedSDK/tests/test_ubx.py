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
        if script in ("module_config.py", "matter_build.py") or rest[:1] in (["nora-b2"], ["alma-b2"]):
            rest = rest[1:]
        out.append((script, rest[0]))
    return out


# ---------------------------------------------------------------------------
# parse
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("argv", [[], ["--help"], ["-h"], ["help"], ["nora-w4"], ["nora-w4", "--help"]])
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


def test_nora_w1_is_not_iris_w1(capsys):
    assert ubx.parse(["nora-w1", "--list"]) == 1
    assert "NORA-W1 (ESP32)" in capsys.readouterr().out


@pytest.mark.parametrize("alias,key", [
    ("w50", "nora-w5"), ("nora-w51", "nora-w5"), ("iris-w10", "iris-w1"),
    ("NORA-W40", "nora-w4"), ("w30", "nora-w3"), ("alma", "alma-b2"), ("nora_b2", "nora-b2"),
])
def test_aliases(alias, key):
    assert ctx([alias, "--list"]).target.key == key


def test_every_alias_resolves():
    for alias, key in ubx.ALIASES.items():
        assert key in ubx.TARGETS, alias


def test_unknown_flag(capsys):
    assert ubx.parse(["nora-w4", "--bogus"]) == 1
    assert "Unknown argument" in capsys.readouterr().out


@pytest.mark.parametrize("flag", ["--variant", "--region"])
def test_value_flags_need_a_value(flag):
    assert ubx.parse(["nora-w3", flag]) == 1
    assert ubx.parse(["nora-w3", flag, "--rf-config"]) == 1


def test_optional_values_are_consumed():
    c = ctx(["nora-w4", "--build", "blink", "--flash", "COM3", "--mac", "COM4", "--log", "COM5"])
    assert (c.example, c.probe, c.mac_port, c.port) == ("blink", "COM3", "COM4", "COM5")


def test_optional_value_is_not_a_flag():
    c = ctx(["nora-w4", "--build", "--flash"])
    assert c.example is None and c.probe is None
    assert c.actions == {"build", "flash"}


def test_double_dash_passes_the_rest_verbatim():
    c = ctx(["iris-w1", "--build", "x", "--", "--config", "release", "--list"])
    assert c.extra == ["--config", "release", "--list"]
    assert c.actions == {"build"}


def test_clean_all_implies_clean():
    c = ctx(["nora-w4", "--clean-all"])
    assert "clean" in c.actions and c.clean_all


def test_matter_flag_points_to_matter_launcher(capsys):
    assert ubx.parse(["nora-w4", "--matter", "--build"]) == 1
    assert "ubx-matter nora-w4" in capsys.readouterr().out


@pytest.mark.parametrize("flag", ["--full", "--build-sdk", "--clean-all", "--rf-config", "--mac",
                                  "--variant", "--region"])
def test_sdk_only_flags_rejected_by_matter(flag):
    assert ubx.parse(["nora-w4", flag], matter=True) == 1


def test_flash_log_only_for_nordic_matter():
    assert ubx.parse(["nora-w4", "--flash"], matter=True) == 1
    assert ubx.parse(["nora-w5", "--log"], matter=True) == 1
    assert ctx(["nora-b2", "--flash", "--log"], matter=True).actions == {"flash", "log"}


def test_variant_without_rf_config_warns(capsys):
    ctx(["nora-w3", "--variant", "NORA-W301", "--build"])
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
    assert argv(["iris-w1", "--build", "x", "--", "-p"], "build") == ["build", "x", "-p"]


def test_full_only_for_iris():
    assert argv(["iris-w1", "--clone", "--full"], "clone") == ["clone", "--full"]
    assert argv(["nora-w4", "--clone", "--full"], "clone") == ["clone"]


def test_clean_variants():
    assert argv(["nora-w4", "--clean"], "clean") == ["clean"]
    assert argv(["nora-w4", "--clean-all"], "clean") == ["clean", "--all"]
    # NORA-W5 has no clean subcommand; a clean build stands in for it.
    assert argv(["nora-w5", "--clean"], "clean") == ["build", "network_terminal", "--clean"]
    assert argv(["nora-w5", "--clean-all"], "clean") is None


def test_flash_and_log():
    assert argv(["iris-w1", "--flash", "123"], "flash") == ["flash", "demo_apps/hello_world", "--serial", "123"]
    assert argv(["iris-w1", "--log", "COM9"], "log") == ["log", "COM9"]
    # idf.py monitor needs the example directory.
    assert argv(["nora-w4", "--log", "COM9"], "log") == ["log", "hello_world", "--serial", "COM9"]


def test_unsupported_action_is_skipped(capsys):
    assert argv(["nora-w3", "--flash"], "flash") is None
    assert "not supported" in capsys.readouterr().out


def test_build_sdk_only_nora_w5():
    assert argv(["nora-w5", "--build-sdk"], "build-sdk") == ["build-sdk"]
    assert argv(["nora-w4", "--build-sdk"], "build-sdk") is None


def test_rf_config_and_mac_go_to_module_config():
    assert argv(["nora-w3", "--variant", "NORA-W301", "--region", "ETSI", "--rf-config"], "rf-config") == \
        ["apply", "--variant", "NORA-W301", "--region", "ETSI"]
    assert argv(["nora-w4", "--mac"], "mac") == ["mac"]
    assert argv(["nora-w4", "--mac", "COM7"], "mac") == ["mac", "--serial", "COM7"]


def test_matter_vendor_translation():
    assert argv(["nora-w5", "--list"], "list", matter=True) == ["list"]
    assert argv(["nora-w5", "--build"], "build", matter=True) == ["build"]
    assert argv(["nora-w4", "--build", "light"], "build", matter=True) == ["build", "light"]
    # '' keeps the extras out of the example slot.
    assert argv(["nora-w4", "--build", "--", "-DX=1"], "build", matter=True) == ["build", "", "-DX=1"]
    assert argv(["nora-w4", "--clean", "--build", "light"], "clean", matter=True) == ["clean", "light"]


def test_matter_ncs_translation():
    assert argv(["nora-b2", "--list"], "list", matter=True) == ["list", "--matter"]
    assert argv(["nora-b2", "--build"], "build", matter=True) == ["build", "matter/light_bulb"]
    assert argv(["alma-b2", "--build", "lock"], "build", matter=True) == ["build", "matter/lock"]
    assert argv(["nora-b2", "--build", "matter/lock"], "build", matter=True) == ["build", "matter/lock"]
    assert argv(["nora-b2", "--flash"], "flash", matter=True) == ["flash", "matter/light_bulb"]


# ---------------------------------------------------------------------------
# run: order, failure handling, driver selection
# ---------------------------------------------------------------------------

def test_actions_run_in_fixed_order(native):
    assert ubx.main(["nora-w4", "--log", "--build", "hello_world", "--clean", "--list", "--doctor"]) == 0
    assert steps(native.cmds) == [
        ("nora_w4_build.py", "doctor"),
        ("module_config.py", "status"),
        ("nora_w4_build.py", "list"),
        ("nora_w4_build.py", "clean"),
        ("nora_w4_build.py", "build"),
        ("nora_w4_build.py", "log"),
    ]


def test_full_action_order_matches_constant(native):
    flags = ["--log", "--mac", "--flash", "--build", "--clean", "--list", "--rf-config",
             "--build-sdk", "--install", "--clone", "--doctor"]
    assert ubx.main(["nora-w5", *flags]) == 0
    actions = [a for _, a in steps(native.cmds) if a != "status"]
    translated = {"apply": "rf-config"}
    # NORA-W5 maps --clean onto a clean build.
    order = [translated.get(a, a) for a in actions]
    assert order[:5] == ["doctor", "clone", "install", "build-sdk", "rf-config"]
    assert order[5:] == ["list", "build", "build", "flash", "mac", "log"]


def test_failure_stops_the_chain(native, capsys):
    native.returns = [1]
    assert ubx.main(["nora-w4", "--list", "--build"]) == 1
    assert len(native.calls) == 1
    assert "list failed" in capsys.readouterr().out


def test_failing_doctor_still_reports_rf_status(native):
    native.returns = [1]
    assert ubx.main(["nora-w4", "--doctor", "--build"]) == 1
    assert steps(native.cmds) == [("nora_w4_build.py", "doctor"), ("module_config.py", "status")]


def test_drivers_run_with_this_python_from_sdk_root(native):
    ubx.main(["nora-w4", "--list"])
    call = native.calls[0]
    assert call["cmd"][0] == sys.executable
    assert call["cwd"] == str(ubx.SDK_ROOT)


def test_nordic_driver_gets_target_key(native):
    ubx.main(["alma-b2", "--list"])
    assert native.cmds[0][2:] == ["alma-b2", "list"]


def test_matter_uses_matter_driver(native):
    ubx.main(["nora-w5", "--doctor", "--list"], matter=True)
    assert steps(native.cmds) == [("matter_build.py", "doctor"), ("matter_build.py", "list")]
    assert native.cmds[0][2] == "nora-w5"


def test_ncs_matter_uses_ncs_driver(native):
    ubx.main(["nora-b2", "--list"], matter=True)
    assert native.cmds[0][1].endswith("nordic_ncs_build.py")
    assert native.cmds[0][2:] == ["nora-b2", "list", "--matter"]


def test_rf_config_runs_module_config(native):
    ubx.main(["nora-w3", "--variant", "NORA-W301", "--rf-config"])
    assert native.cmds[0][1].endswith("module_config.py")
    assert native.cmds[0][2:] == ["nora-w3", "apply", "--variant", "NORA-W301"]


def test_dry_run_executes_nothing(native, capsys):
    assert ubx.main(["nora-w4", "--dry-run", "--doctor", "--build"]) == 0
    assert not native.calls
    out = capsys.readouterr().out
    assert out.count("[DRY-RUN]") == 3


def test_dry_run_shows_the_wsl_hop(windows, capsys):
    assert ubx.main(["nora-w5", "--list", "--dry-run"], matter=True) == 0
    assert not windows.calls
    assert "[DRY-RUN] wsl -d Ubuntu-22.04" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# WSL2 hop
# ---------------------------------------------------------------------------

def test_linux_only_sdk_target_hops(windows):
    assert ubx.main(["nora-w3", "--build", "--wsl"]) == 0
    cmd = windows.cmds[0]
    assert cmd[:2] == ["wsl", "--"]
    assert "./ubx-sdk.sh nora-w3 --build" in cmd[-1]
    assert "--wsl" not in cmd[-1]


def test_no_wsl_suppresses_hop(windows):
    ubx.main(["nora-w3", "--list", "--no-wsl"])
    assert windows.cmds[0][0] == sys.executable


def test_windows_native_targets_do_not_hop(windows):
    ubx.main(["nora-w4", "--list"])
    assert windows.cmds[0][0] == sys.executable


@pytest.mark.parametrize("action", ["--doctor", "--list", "--clone", "--build"])
def test_vendor_matter_always_hops(windows, action):
    ubx.main(["nora-w4", action], matter=True)
    cmd = windows.cmds[0]
    assert cmd[:2] == ["wsl", "--"]
    assert "./ubx-matter.sh nora-w4" in cmd[-1]


def test_nora_w5_matter_uses_ubuntu_22_04(windows):
    ubx.main(["nora-w5", "--list"], matter=True)
    assert windows.cmds[0][:4] == ["wsl", "-d", "Ubuntu-22.04", "--"]


def test_distro_only_applies_to_matter(windows):
    ubx.main(["nora-w5", "--list"])
    assert windows.cmds[0][0] == sys.executable


def test_distro_override(windows, monkeypatch):
    monkeypatch.setenv("UBX_WSL_DISTRO", "Debian")
    ubx.main(["nora-w5", "--list"], matter=True)
    assert windows.cmds[0][:3] == ["wsl", "-d", "Debian"]


def test_ncs_matter_never_hops(windows):
    ubx.main(["nora-b2", "--build"], matter=True)
    assert windows.cmds[0][0] == sys.executable


def test_matter_root_is_forwarded_with_home_expansion(windows, monkeypatch):
    monkeypatch.setenv("UBX_MATTER_ROOT", "~/ubx-matter")
    ubx.main(["nora-w4", "--list"], matter=True)
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
