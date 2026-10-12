"""nordic_ncs_build.py commands on a fake NCS workspace (no west, toolchain or probe)."""

import subprocess
import sys

import pytest

import nordic_ncs_build as ncs

B2 = ncs.TARGETS["nora-b20-b21-b22"]


def sample(ws, rel):
    path = ws / rel
    path.mkdir(parents=True)
    (path / "CMakeLists.txt").write_text("")
    (path / "prj.conf").write_text("")
    return path


@pytest.fixture
def cfg():
    return {}


@pytest.fixture
def ws(tmp_path, monkeypatch, calls, cfg):
    """A workspace with the board, two samples and a recorded subprocess.call."""
    root = tmp_path / "ncs"
    (root / ".west").mkdir(parents=True)
    (root / "zephyr/boards/u-blox/ubx_evknorab2").mkdir(parents=True)
    sample(root, "zephyr/samples/hello_world")
    sample(root, "nrf/samples/matter/light_bulb")
    monkeypatch.setattr(ncs, "detect_workspace", lambda t: str(root))
    monkeypatch.setattr(ncs, "find_workspaces", lambda t: [root])
    monkeypatch.setattr(ncs, "detect_west", lambda: ["west"])
    monkeypatch.setattr(ncs, "workspace_revision", lambda w: ncs.NCS_REVISION)
    monkeypatch.setattr(ncs, "load_config", lambda t: dict(cfg))
    monkeypatch.setattr(ncs, "save_config", lambda t, c: cfg.clear() or cfg.update(c))
    monkeypatch.setattr(ncs.subprocess, "call", calls)
    return root


def parse(*argv):
    return ncs.build_parser().parse_args(["nora-b20-b21-b22", *argv])


@pytest.fixture
def no_workspace(monkeypatch):
    monkeypatch.setattr(ncs, "detect_workspace", lambda t: None)


# ---------------------------------------------------------------------------
# host and tool detection
# ---------------------------------------------------------------------------

def test_detect_west(monkeypatch):
    monkeypatch.setattr(ncs, "which", lambda name: "/usr/bin/west")
    assert ncs.detect_west() == ["/usr/bin/west"]
    monkeypatch.setattr(ncs, "which", lambda name: None)
    monkeypatch.setattr(ncs.subprocess, "run", lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0))
    assert ncs.detect_west() == [sys.executable, "-m", "west"]
    monkeypatch.setattr(ncs.subprocess, "run", lambda cmd, **kw: subprocess.CompletedProcess(cmd, 1))
    assert ncs.detect_west() is None


@pytest.fixture
def no_toolchain(monkeypatch, tmp_path):
    for var in ("ZEPHYR_SDK_INSTALL_DIR", "GNUARMEMB_TOOLCHAIN_PATH"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("SystemDrive", str(tmp_path / "drive"))
    monkeypatch.setattr(ncs, "which", lambda name: None)
    monkeypatch.setattr(ncs.Path, "home", lambda: tmp_path / "home")
    return tmp_path


def test_detect_toolchain_order(no_toolchain, monkeypatch):
    tmp_path = no_toolchain
    if ncs.Path("/opt/zephyr-sdk").is_dir():
        pytest.skip("host has /opt/zephyr-sdk")
    assert ncs.detect_toolchain() is None
    (tmp_path / "home" / "zephyr-sdk").mkdir(parents=True)
    assert ncs.detect_toolchain() == str(tmp_path / "home" / "zephyr-sdk")
    monkeypatch.setattr(ncs, "which", lambda name: f"/bin/{name}" if name == "arm-none-eabi-gcc" else None)
    assert ncs.detect_toolchain() == "/bin/arm-none-eabi-gcc"
    monkeypatch.setenv("GNUARMEMB_TOOLCHAIN_PATH", str(tmp_path))
    assert ncs.detect_toolchain() == f"Arm GNU toolchain at {tmp_path}"
    monkeypatch.setenv("ZEPHYR_SDK_INSTALL_DIR", str(tmp_path))
    assert ncs.detect_toolchain() == f"Zephyr SDK at {tmp_path}"


def test_simple_tool_lookups(monkeypatch):
    monkeypatch.setattr(ncs.shutil, "which", lambda name: f"/bin/{name}")
    assert [ncs.detect_git(), ncs.detect_cmake(), ncs.detect_ninja(), ncs.detect_nrfutil()] == \
        ["/bin/git", "/bin/cmake", "/bin/ninja", "/bin/nrfutil"]


def test_config_round_trip(monkeypatch, tmp_path):
    path = tmp_path / "config" / "build.linux.json"
    monkeypatch.setattr(ncs, "config_file", lambda t: path)
    assert ncs.load_config(B2) == {}
    ncs.save_config(B2, {"workspace": "/ncs"})
    assert ncs.load_config(B2) == {"workspace": "/ncs"}
    path.write_text("{broken")
    assert ncs.load_config(B2) == {}


def test_config_file_uses_target_paths(monkeypatch, tmp_path):
    monkeypatch.setattr(ncs, "host_kind", lambda: "linux")
    monkeypatch.setattr(ncs.target_paths, "resolve_config", lambda slug, host: tmp_path / slug / host)
    assert ncs.config_file(B2) == tmp_path / "nora_b20_b21_b22" / "linux"


def test_workspace_revision_git_missing(monkeypatch):
    def boom(cmd, **kw):
        raise OSError("no git")
    monkeypatch.setattr(ncs.subprocess, "run", boom)
    assert ncs.workspace_revision("ws") is None


def test_find_workspaces_dedupes_and_needs_nrf(monkeypatch, tmp_path):
    good = tmp_path / "good"
    (good / ".west").mkdir(parents=True)
    (good / "nrf").mkdir()
    (tmp_path / "bare" / ".west").mkdir(parents=True)
    monkeypatch.setattr(ncs, "_workspace_candidates", lambda t: [good, tmp_path / "bare", good])
    assert ncs.find_workspaces(B2) == [good]


def test_workspace_candidates_on_windows(monkeypatch, tmp_path):
    drive = tmp_path / "C"
    (drive / "ncs" / "v3.4.1").mkdir(parents=True)
    monkeypatch.setenv("SystemDrive", str(drive))
    monkeypatch.setattr(ncs, "host_kind", lambda: "windows")
    monkeypatch.setattr(ncs.Path, "home", lambda: tmp_path / "home")
    monkeypatch.setattr(ncs, "load_config", lambda t: {"workspace": str(tmp_path / "cfg")})
    monkeypatch.setattr(ncs.target_paths, "installed_sdks", lambda slug: [])
    monkeypatch.delenv("ZEPHYR_BASE", raising=False)
    found = ncs._workspace_candidates(B2)
    assert found[0] == tmp_path / "cfg"
    assert drive / "ncs" / "v3.4.1" in found


def test_env_override_without_west_is_ignored(monkeypatch, tmp_path):
    monkeypatch.setenv(ncs.WORKSPACE_ENV, str(tmp_path))
    assert ncs.detect_workspace(B2) is None


def test_saved_workspace_is_used(monkeypatch, tmp_path):
    (tmp_path / ".west").mkdir()
    monkeypatch.delenv(ncs.WORKSPACE_ENV, raising=False)
    monkeypatch.setattr(ncs, "load_config", lambda t: {"workspace": str(tmp_path)})
    assert ncs.detect_workspace(B2) == str(tmp_path)


# ---------------------------------------------------------------------------
# samples
# ---------------------------------------------------------------------------

def test_resolve_example_forms(ws):
    assert ncs.resolve_example(str(ws), "zephyr/samples/hello_world") == ws / "zephyr/samples/hello_world"
    assert ncs.resolve_example(str(ws), "hello_world") == ws / "zephyr/samples/hello_world"
    assert ncs.resolve_example(str(ws), "light_bulb") == ws / "nrf/samples/matter/light_bulb"


def test_resolve_example_ambiguous_and_missing(ws, capsys):
    sample(ws, "nrf/samples/a/blinky")
    sample(ws, "nrf/samples/b/blinky")
    assert ncs.resolve_example(str(ws), "blinky") is None
    assert "ambiguous" in capsys.readouterr().out
    assert ncs.resolve_example(str(ws), "nope") is None
    assert "not found" in capsys.readouterr().out


@pytest.mark.parametrize("matter,shown,hidden", [
    (False, "hello_world", None),
    (True, "matter/light_bulb", "hello_world"),
])
def test_list(ws, capsys, matter, shown, hidden):
    args = parse("list", *(["--matter"] if matter else []))
    assert ncs.cmd_list(B2, args) == 0
    out = capsys.readouterr().out
    assert shown in out
    assert hidden is None or hidden not in out


def test_list_empty(ws, tmp_path, monkeypatch):
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(ncs, "detect_workspace", lambda t: str(empty))
    assert ncs.cmd_list(B2, parse("list")) == 1


@pytest.mark.parametrize("verb", [["list"], ["build"], ["flash"], ["install"]])
def test_commands_need_a_workspace(no_workspace, verb, capsys):
    assert parse(*verb).func(B2, parse(*verb)) == 1
    assert "not found" in capsys.readouterr().out


@pytest.mark.parametrize("verb", [["build"], ["flash"]])
def test_commands_need_west(ws, monkeypatch, verb):
    monkeypatch.setattr(ncs, "detect_west", lambda: None)
    assert parse(*verb).func(B2, parse(*verb)) == 1


# ---------------------------------------------------------------------------
# build / clean / flash / log
# ---------------------------------------------------------------------------

def test_build_command_line(ws, cfg, calls, capsys):
    assert ncs.cmd_build(B2, parse("build", "--clean", "hello_world", "--", "-DFOO=1")) == 0
    out = ws / "build" / "hello_world"
    assert calls.cmds[0] == ["west", "build", "-b", B2.board, "-d", str(out), "--pristine",
                             str(ws / "zephyr/samples/hello_world"), "-DFOO=1"]
    assert cfg == {"last_example": "zephyr/samples/hello_world", "last_board": B2.board}
    assert f"Artifacts in {out / 'zephyr'}" in capsys.readouterr().out


def test_build_unknown_board_warns(ws, calls, capsys):
    assert ncs.cmd_build(B2, parse("build", "--board", "custom/board")) == 0
    assert "not a known" in capsys.readouterr().out


def test_build_failure(ws, cfg, calls):
    calls.returns = [2]
    assert ncs.cmd_build(B2, parse("build")) == 2
    assert cfg == {}


def test_build_unknown_sample(ws):
    assert ncs.cmd_build(B2, parse("build", "nope")) == 1


def test_clean_paths(ws, capsys):
    out = ws / "build" / "hello_world"
    out.mkdir(parents=True)
    assert ncs.cmd_clean(B2, parse("clean", "hello_world")) == 0
    assert not out.exists() and (ws / "build").exists()
    assert ncs.cmd_clean(B2, parse("clean", "hello_world")) == 0
    assert "not found" in capsys.readouterr().out
    assert ncs.cmd_clean(B2, parse("clean", "nope")) == 1
    assert ncs.cmd_clean(B2, parse("clean")) == 0
    assert not (ws / "build").exists()


def test_clean_all_removes_workspace(ws, cfg):
    cfg["workspace"] = str(ws)
    assert ncs.cmd_clean(B2, parse("clean", "--all")) == 0
    assert not ws.exists() and "workspace" not in cfg


def test_clean_without_workspace(no_workspace):
    assert ncs.cmd_clean(B2, parse("clean")) == 0


def test_flash(ws, calls, capsys):
    assert ncs.cmd_flash(B2, parse("flash")) == 1
    assert "Build first" in capsys.readouterr().out
    (ws / "build" / "hello_world").mkdir(parents=True)
    assert ncs.cmd_flash(B2, parse("flash", "--runner", "jlink", "--serial", "1050")) == 0
    assert calls.cmds[-1] == ["west", "flash", "-d", str(ws / "build" / "hello_world"),
                              "-r", "jlink", "--dev-id", "1050"]
    calls.returns = [1]
    assert ncs.cmd_flash(B2, parse("flash")) == 1
    assert ncs.cmd_flash(B2, parse("flash", "nope")) == 1


def test_log_uses_serial_logger(monkeypatch):
    import serial_logger
    monkeypatch.setattr(serial_logger, "open_serial_monitor", lambda port, baud: (port, baud))
    assert ncs.cmd_log(B2, parse("log", "COM5", "--baudrate", "9600")) == ("COM5", 9600)


# ---------------------------------------------------------------------------
# clone / install / doctor / main
# ---------------------------------------------------------------------------

def test_clone_fresh_workspace(tmp_path, monkeypatch, calls):
    cfg = {}
    monkeypatch.setattr(ncs, "detect_west", lambda: ["west"])
    monkeypatch.setattr(ncs.subprocess, "call", calls)
    monkeypatch.setattr(ncs.target_paths, "check_space", lambda *a: True)
    monkeypatch.setattr(ncs, "load_config", lambda t: dict(cfg))
    monkeypatch.setattr(ncs, "save_config", lambda t, c: cfg.update(c))
    dest = tmp_path / "ncs" / "v3.4.0"
    assert ncs.cmd_clone(B2, parse("clone", "--revision", "v3.4.0", "--workspace", str(dest))) == 0
    assert calls.cmds == [
        ["west", "init", "-m", ncs.NCS_MANIFEST_URL, "--mr", "v3.4.0", str(dest)],
        ["west", "update"], ["west", "zephyr-export"]]
    assert cfg == {"workspace": str(dest), "revision": "v3.4.0"}


@pytest.mark.parametrize("returns,expected_calls", [([1], 1), ([0, 4], 2)])
def test_clone_failures(tmp_path, monkeypatch, calls, returns, expected_calls):
    monkeypatch.setattr(ncs, "detect_west", lambda: ["west"])
    monkeypatch.setattr(ncs.subprocess, "call", calls)
    monkeypatch.setattr(ncs.target_paths, "check_space", lambda *a: True)
    calls.returns = list(returns)
    assert ncs.cmd_clone(B2, parse("clone", "--workspace", str(tmp_path / "ws"))) != 0
    assert len(calls.calls) == expected_calls


def test_clone_existing_workspace_and_no_west(ws, monkeypatch, calls, capsys):
    assert ncs.cmd_clone(B2, parse("clone", "--workspace", str(ws))) == 0
    assert "already initialised" in capsys.readouterr().out
    assert calls.cmds[0] == ["west", "update"]
    monkeypatch.setattr(ncs, "detect_west", lambda: None)
    assert ncs.cmd_clone(B2, parse("clone")) == 1


def test_install(ws, calls, monkeypatch, capsys):
    assert ncs.cmd_install(B2, parse("install")) == 1
    req = ws / "zephyr/scripts/requirements.txt"
    req.parent.mkdir(parents=True)
    req.write_text("")
    monkeypatch.setattr(ncs, "detect_toolchain", lambda: None)
    assert ncs.cmd_install(B2, parse("install")) == 0
    assert calls.cmds[0] == [sys.executable, "-m", "pip", "install", "-r", str(req)]
    assert "No Arm toolchain" in capsys.readouterr().out
    calls.returns = [1]
    assert ncs.cmd_install(B2, parse("install")) == 1


@pytest.fixture
def tools(monkeypatch):
    for name in ("detect_git", "detect_cmake", "detect_ninja", "detect_toolchain", "detect_nrfutil"):
        monkeypatch.setattr(ncs, name, lambda _n=name: f"/bin/{_n}")
    monkeypatch.setattr(ncs, "host_kind", lambda: "linux")


def test_doctor_ready(ws, tools, capsys):
    assert ncs.cmd_doctor(B2, parse("doctor")) == 0
    assert "Ready to build" in capsys.readouterr().out


def test_doctor_reports_problems(ws, tools, monkeypatch, tmp_path, capsys):
    other = tmp_path / "other"
    monkeypatch.setattr(ncs, "find_workspaces", lambda t: [ws, other])
    monkeypatch.setattr(ncs, "workspace_revision", lambda w: "v2.9.0")
    monkeypatch.setattr(ncs, "board_available", lambda w, b: False)
    monkeypatch.setattr(ncs, "detect_cmake", lambda: None)
    assert ncs.cmd_doctor(B2, parse("doctor")) == 1
    out = capsys.readouterr().out
    assert "Workspace is v2.9.0" in out and "Other NCS workspaces" in out
    assert "Missing: cmake, board" in out and "Toolchain Manager" in out


def test_doctor_without_workspace(no_workspace, tools, monkeypatch, capsys):
    monkeypatch.setattr(ncs, "find_workspaces", lambda t: [])
    monkeypatch.setattr(ncs, "detect_west", lambda: ["west"])
    assert ncs.cmd_doctor(B2, parse("doctor")) == 1
    assert "Missing: workspace" in capsys.readouterr().out


def test_use_lists_nothing(no_workspace, monkeypatch):
    monkeypatch.setattr(ncs, "find_workspaces", lambda t: [])
    assert ncs.cmd_use(B2, parse("use")) == 1


def test_main(monkeypatch, capsys):
    monkeypatch.setattr(ncs.target_paths, "ensure", lambda slug: None)
    monkeypatch.setattr(sys, "argv", ["nordic_ncs_build.py", "nora-w99", "doctor"])
    assert ncs.main() == 1
    assert "Unknown target" in capsys.readouterr().out

    def interrupted(target, args):
        raise KeyboardInterrupt
    monkeypatch.setattr(ncs, "cmd_doctor", interrupted)
    monkeypatch.setattr(sys, "argv", ["nordic_ncs_build.py", "ALMA_B20_B21", "doctor"])
    assert ncs.main() == 130
