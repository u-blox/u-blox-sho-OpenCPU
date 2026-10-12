"""nora_w50_w51_build.py on a fake TI SimpleLink tree (no make, SysConfig, compiler or probe)."""

import json
import sys
from pathlib import PurePosixPath

import pytest

import nora_w50_w51_build as w5

BOARD = w5.DEFAULT_BOARD


@pytest.fixture
def calls_(monkeypatch, calls):
    monkeypatch.setattr(w5.subprocess, "call", calls)
    return calls


@pytest.fixture
def cfg(monkeypatch, tmp_path):
    path = tmp_path / "config" / "build.linux.json"
    path.parent.mkdir()
    monkeypatch.setattr(w5, "config_file", lambda: path)
    return path


def example(tree_root, group, name, chains=("ticlang", "gcc")):
    path = tree_root / "examples" / "rtos" / BOARD / group / name
    for chain in chains:
        (path / "freertos" / chain).mkdir(parents=True)
    return path


@pytest.fixture
def ws(tmp_path, monkeypatch, cfg):
    """Workspace with the wifi-examples repo, its SDK submodule and two examples."""
    root = tmp_path / "ws"
    repo = root / "wifi-examples"
    sdk = repo / "simplelink-wifi-sdk"
    sdk.mkdir(parents=True)
    (sdk / "imports.mak").write_text("CMAKE ?= cmake\n")
    (repo / "imports.mak").write_text("# repo\n")
    example(repo, "demos", "network_terminal")
    example(repo, "basic", "out_of_box", chains=("ticlang",))
    monkeypatch.setattr(w5, "detect_installed_sdk", lambda: None)
    monkeypatch.setattr(w5, "detect_tools", lambda: {
        "MAKE": "make", "CMAKE": "cmake", "SYSCONFIG_TOOL": "/ti/sysconfig_cli.sh",
        "GCC_ARMCOMPILER": "/opt/gcc", "GIT": "git"})
    monkeypatch.setenv("NORA_W50_W51_WORKSPACE", str(root))
    return root


def parse(*argv):
    return w5.build_parser().parse_args(list(argv))


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def test_host_kind(monkeypatch):
    monkeypatch.setattr(w5.os, "name", "nt")
    assert w5.host_kind() == "windows"
    monkeypatch.setattr(w5.os, "name", "posix")
    monkeypatch.setattr(w5.sys, "platform", "linux")
    monkeypatch.setattr(w5.Path, "read_text", lambda self: "Linux microsoft-standard-WSL2")
    assert w5.host_kind() == "wsl"

    def missing(self):
        raise OSError
    monkeypatch.setattr(w5.Path, "read_text", missing)
    assert w5.host_kind() == "linux"
    monkeypatch.setattr(w5.sys, "platform", "darwin")
    monkeypatch.setattr(w5.platform, "system", lambda: "Darwin")
    assert w5.host_kind() == "darwin"


def test_run(calls_):
    assert w5.run(["make"], cwd=w5.Path("x")) == 0
    calls_.returns = [2, 3]
    assert w5.run(["make"], check=False) == 2
    with pytest.raises(w5.Fail, match="exit code 3"):
        w5.run(["make"])


def test_newest_natural_order(tmp_path):
    for v in ("9.0", "10.1"):
        (tmp_path / f"sysconfig_{v}").mkdir()
    assert w5.newest([str(tmp_path / "sysconfig_*")]).name == "sysconfig_10.1"
    assert w5.newest([str(tmp_path / "none_*")]) is None


def test_newest_relative_pattern(tmp_path, monkeypatch):
    (tmp_path / "tool").mkdir()
    monkeypatch.chdir(tmp_path)
    assert w5.newest(["tool"]).name == "tool"


def test_short_and_mak_path(monkeypatch):
    monkeypatch.setattr(w5, "IS_WINDOWS", False)
    assert w5.mak_path("C:\\Program Files\\x") == "C:/Program Files/x"
    monkeypatch.setattr(w5, "IS_WINDOWS", True)
    assert w5.short_path("C:\\nospace") == "C:\\nospace"
    assert w5.short_path("C:\\Does Not Exist\\x") == "C:\\Does Not Exist\\x"


@pytest.mark.parametrize("windows", [False, True])
def test_detectors(monkeypatch, tmp_path, windows):
    monkeypatch.setattr(w5, "IS_WINDOWS", windows)
    exe = ".exe" if windows else ""
    monkeypatch.setattr(w5, "EXE", exe)
    seen = []

    def fake_newest(patterns):
        seen.append(patterns)
        return tmp_path
    monkeypatch.setattr(w5, "newest", fake_newest)
    monkeypatch.setattr(w5.shutil, "which", lambda name: None)
    assert w5.detect_sysconfig() == tmp_path
    assert w5.detect_toolbox() == tmp_path
    assert w5.detect_ticlang() is None
    assert w5.detect_installed_sdk() is None
    assert w5.detect_gcc() is None
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / f"tiarmclang{exe}").write_text("")
    (tmp_path / "bin" / f"arm-none-eabi-gcc{exe}").write_text("")
    (tmp_path / "imports.mak").write_text("")
    assert w5.detect_ticlang() == tmp_path
    assert w5.detect_gcc() == tmp_path
    assert w5.detect_installed_sdk() == tmp_path
    assert all(("C:/" in p[0]) == windows for p in seen)


def test_detect_gcc_on_path(monkeypatch, tmp_path):
    monkeypatch.setattr(w5, "newest", lambda patterns: None)
    gcc = tmp_path / "gcc" / "bin" / "arm-none-eabi-gcc"
    monkeypatch.setattr(w5.shutil, "which", lambda name: str(gcc))
    assert w5.detect_gcc() == (tmp_path / "gcc").resolve()


def test_detect_make(monkeypatch, tmp_path):
    monkeypatch.setattr(w5, "IS_WINDOWS", False)
    monkeypatch.setattr(w5.shutil, "which", lambda name: "/usr/bin/make")
    assert w5.detect_make() == w5.Path("/usr/bin/make")
    monkeypatch.setattr(w5, "IS_WINDOWS", True)
    monkeypatch.setattr(w5, "newest", lambda patterns: tmp_path if "ccs" in patterns[0] else None)
    assert w5.detect_make() == tmp_path
    monkeypatch.setattr(w5, "newest", lambda patterns: None)
    monkeypatch.setattr(w5.shutil, "which", lambda name: "C:/bin/mingw32-make.exe" if name == "mingw32-make" else None)
    assert w5.detect_make() == w5.Path("C:/bin/mingw32-make.exe")
    monkeypatch.setattr(w5.shutil, "which", lambda name: None)
    assert w5.detect_make() is None


def test_detect_tools(monkeypatch):
    for name in ("detect_sysconfig", "detect_ticlang", "detect_gcc", "detect_toolbox", "detect_make"):
        monkeypatch.setattr(w5, name, lambda: None)
    monkeypatch.setattr(w5, "IS_WINDOWS", True)
    monkeypatch.setattr(w5.shutil, "which", lambda name: "/bin/git" if name == "git" else None)
    monkeypatch.setattr(w5, "newest", lambda patterns: w5.Path("C:/cmake/bin/cmake.exe"))
    tools = w5.detect_tools()
    assert set(tools) == {"CMAKE", "GIT"}


def test_config(cfg, monkeypatch, tmp_path):
    assert w5.load_config() == {}
    w5.save_config(workspace="/ws", source=None)
    w5.save_config(source="installed")
    assert json.loads(cfg.read_text()) == {"workspace": "/ws", "source": "installed"}
    cfg.write_text("{")
    assert w5.load_config() == {}
    monkeypatch.undo()
    monkeypatch.setattr(w5.target_paths, "resolve_config", lambda t, h: tmp_path / t / h)
    assert w5.config_file() == tmp_path / "nora_w50_w51" / w5.HOST


def test_resolve_tools_precedence(cfg, monkeypatch):
    monkeypatch.setattr(w5, "detect_tools", lambda: {"CMAKE": "detected", "MAKE": "detected"})
    w5.save_config(tools={"CMAKE": "saved"})
    tools = w5.resolve_tools(parse("--make", "flag", "doctor"))
    assert tools == {"CMAKE": "saved", "MAKE": "flag"}


def test_workspace_selection(cfg, monkeypatch, tmp_path):
    monkeypatch.delenv("NORA_W50_W51_WORKSPACE", raising=False)
    monkeypatch.setenv("NORA_W5_WORKSPACE", str(tmp_path / "old"))
    assert w5.default_workspace() == (tmp_path / "old").resolve()
    monkeypatch.delenv("NORA_W5_WORKSPACE")
    monkeypatch.setattr(w5, "HOST", "wsl")
    monkeypatch.setattr(w5.Path, "home", lambda: tmp_path)
    assert w5.default_workspace() == tmp_path / "nora-w50-w51"
    monkeypatch.setattr(w5, "HOST", "linux")
    assert w5.default_workspace() == w5.target_paths.sdk_dir(w5.TARGET)
    assert w5.workspace_of(parse("--workspace", str(tmp_path), "doctor")) == tmp_path.resolve()
    w5.save_config(workspace="/saved")
    assert w5.workspace_of(parse("doctor")) == w5.Path("/saved")


# ---------------------------------------------------------------------------
# trees and imports.mak
# ---------------------------------------------------------------------------

def test_discover_and_active_tree(ws, monkeypatch, tmp_path):
    tree = w5.active_tree(parse("doctor"))
    assert tree.name == "wifi-examples" and tree.sdk.name.lower() == "simplelink-wifi-sdk"
    assert [p.parent.name.lower() for p in tree.imports_mak()] == ["wifi-examples", "simplelink-wifi-sdk"]
    assert "wifi-examples" in str(tree)
    with pytest.raises(w5.Fail, match="not available"):
        w5.active_tree(parse("--source", "installed", "doctor"))
    installed = tmp_path / "ti" / "simplelink_wifi_sdk_1"
    installed.mkdir(parents=True)
    monkeypatch.setattr(w5, "detect_installed_sdk", lambda: installed)
    assert w5.active_tree(parse("doctor")).name == "installed"
    assert w5.active_tree(parse("--source", "wifi-examples", "doctor")).name == "wifi-examples"


def test_active_tree_custom_and_none(cfg, monkeypatch, tmp_path):
    monkeypatch.setattr(w5, "detect_installed_sdk", lambda: None)
    with pytest.raises(w5.Fail, match="no imports.mak"):
        w5.active_tree(parse("--sdk", str(tmp_path), "doctor"))
    (tmp_path / "imports.mak").write_text("")
    assert w5.active_tree(parse("--sdk", str(tmp_path), "doctor")).name == "custom"
    with pytest.raises(w5.Fail, match="no SDK found"):
        w5.active_tree(parse("--workspace", str(tmp_path / "empty"), "doctor"))


def test_submodule_sdk_fallback(tmp_path):
    (tmp_path / "examples").mkdir()
    (tmp_path / "examples" / "imports.mak").write_text("")
    assert w5.submodule_sdk(tmp_path) is None
    (tmp_path / "other_sdk").mkdir()
    (tmp_path / "other_sdk" / "imports.mak").write_text("")
    assert w5.submodule_sdk(tmp_path) == tmp_path / "other_sdk"


def test_patch_imports_mak(tmp_path, monkeypatch):
    monkeypatch.setattr(w5, "IS_WINDOWS", False)
    mak = tmp_path / "imports.mak"
    mak.write_bytes(b"#   CMAKE ?= /example\r\nCMAKE ?= cmake\r\nOTHER = 1\r\n")
    w5.patch_imports_mak(mak, {"CMAKE": "/opt/cmake", "PYTHON": "/usr/bin/python3"})
    text = mak.read_bytes().decode()
    assert "#   CMAKE ?= /example\r\n" in text
    assert f"{'CMAKE':<22} ?= /opt/cmake\r\n" in text and text.endswith(f"{'PYTHON':<22} ?= /usr/bin/python3\r\n")
    assert (tmp_path / "imports.mak.orig").read_bytes().startswith(b"#   CMAKE")
    w5.patch_imports_mak(mak, {})
    assert (tmp_path / "imports.mak.orig").read_bytes().startswith(b"#   CMAKE")


def test_examples_boards_and_build_dir(ws):
    tree = w5.active_tree(parse("doctor"))
    assert sorted(w5.find_examples(tree, BOARD)) == ["network_terminal", "out_of_box"]
    assert w5.find_examples(tree, "NOPE") == {}
    assert w5.list_boards(tree) == [BOARD]
    assert w5.list_boards(w5.Tree("x", ws, ws / "none")) == []
    with pytest.raises(w5.Fail, match="have: ticlang"):
        w5.build_dir(w5.find_examples(tree, BOARD)["out_of_box"], "gcc")


@pytest.mark.parametrize("windows,hint", [(True, "winget"), (False, "apt")])
def test_make_cmd(monkeypatch, windows, hint):
    assert w5.make_cmd({"MAKE": "make"}, 4, "clean") == ["make", "-j4", "clean"]
    assert w5.make_cmd({"MAKE": "make"}, 1) == ["make"]
    monkeypatch.setattr(w5, "IS_WINDOWS", windows)
    with pytest.raises(w5.Fail, match=hint):
        w5.make_cmd({}, 1)


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

class WslPath(PurePosixPath):
    def is_dir(self):
        return False


def test_doctor(ws, capsys, monkeypatch):
    w5.cmd_doctor(parse("doctor"))
    out = capsys.readouterr().out
    assert "all required tools found" in out and f"boards: {BOARD}" in out
    monkeypatch.setattr(w5, "HOST", "wsl")
    monkeypatch.setattr(w5, "detect_tools", lambda: {"CMAKE": "C:/Program Files/CMake/cmake.exe"})
    monkeypatch.setattr(w5, "workspace_of", lambda args: WslPath("/mnt/c/ws"))
    monkeypatch.setattr(w5, "discover_trees", lambda ws: {})
    w5.cmd_doctor(parse("doctor"))
    out = capsys.readouterr().out
    assert "very slow" in out and "missing: GIT, MAKE, SYSCONFIG_TOOL" in out
    assert "none found" in out and "spaces" in out


def test_clone(ws, calls_, cfg, monkeypatch):
    ws = ws.resolve()  # the driver resolves the workspace; CI temp paths may be 8.3 names
    monkeypatch.setattr(w5.target_paths, "check_space", lambda *a: True)
    (ws / "coresdk-examples" / ".git").mkdir(parents=True)
    w5.cmd_clone(parse("clone", "--update"))
    assert calls_.cmds == [
        ["git", "clone", "--recurse-submodules", w5.REPOS["wifi-examples"], str(ws / "wifi-examples")],
        ["git", "-C", str(ws / "coresdk-examples"), "pull", "--ff-only"],
        ["git", "-C", str(ws / "coresdk-examples"), "submodule", "update", "--init", "--recursive"]]
    assert w5.Path(json.loads(cfg.read_text())["workspace"]) == ws.resolve()


def test_clone_checks_space(ws, monkeypatch, calls_):
    monkeypatch.setattr(w5.target_paths, "check_space", lambda *a: False)
    monkeypatch.setattr(w5, "HOST", "wsl")
    monkeypatch.setattr(w5, "workspace_of", lambda args: ws)
    with pytest.raises(SystemExit):
        w5.cmd_clone(parse("clone", "--repo", "wifi-examples"))
    assert not calls_.calls


def test_install_prints_links(capsys):
    w5.cmd_install(parse("install"))
    assert "SIMPLELINK-WIFI-SDK" in capsys.readouterr().out


def test_configure(ws, cfg, monkeypatch):
    w5.cmd_configure(parse("configure"))
    sdk_mak = ws / "wifi-examples" / "simplelink-wifi-sdk" / "imports.mak"
    assert f"{'GCC_ARMCOMPILER':<22} ?= /opt/gcc" in sdk_mak.read_text()
    saved = json.loads(cfg.read_text())
    assert saved["source"] == "wifi-examples" and saved["tools"]["CMAKE"] == "cmake"
    monkeypatch.setattr(w5, "resolve_tools", lambda args: {"CMAKE": "cmake"})
    with pytest.raises(w5.Fail, match="SYSCONFIG_TOOL, TICLANG_ARMCOMPILER or GCC_ARMCOMPILER"):
        w5.cmd_configure(parse("configure"))


def test_build_sdk(ws, calls_):
    w5.cmd_build_sdk(parse("build-sdk", "--toolchain", "gcc", "--clean"))
    assert calls_.cmds == [["make", "clean"], ["make", "build-gcc"]]
    assert calls_.calls[1]["cwd"].lower().endswith("simplelink-wifi-sdk")
    w5.cmd_build_sdk(parse("build-sdk"))
    assert calls_.cmds[-1] == ["make"]


def test_list(ws, capsys):
    w5.cmd_list(parse("list"))
    out = capsys.readouterr().out
    assert f"{BOARD}/demos" in out and "[gcc, ticlang]" in out
    with pytest.raises(w5.Fail, match="no examples for board NOPE"):
        w5.cmd_list(parse("list", "--board", "NOPE"))


def test_build(ws, calls_, capsys):
    bdir = ws / "wifi-examples/examples/rtos" / BOARD / "demos/network_terminal/freertos/ticlang"
    (bdir / "network_terminal.out").write_text("")
    w5.cmd_build(parse("-j", "8", "build", "network_terminal", "--clean"))
    assert calls_.cmds == [["make", "clean"], ["make", "-j8"]]
    assert "network_terminal.out" in capsys.readouterr().out
    with pytest.raises(w5.Fail, match="Did you mean: network_terminal"):
        w5.cmd_build(parse("build", "network"))
    with pytest.raises(w5.Fail, match="Run 'list'"):
        w5.cmd_build(parse("build", "zzz"))
    with pytest.raises(w5.Fail, match="no examples for board"):
        w5.cmd_build(parse("build", "--all", "--board", "NOPE"))


def test_build_all_keep_going(ws, calls_, capsys):
    calls_.returns = [0, 2]
    with pytest.raises(w5.Fail, match="failed: out_of_box"):
        w5.cmd_build(parse("-j", "1", "build", "--all", "--keep-going"))
    assert "FAILED out_of_box" in capsys.readouterr().out
    calls_.returns = [2]
    with pytest.raises(w5.Fail, match="exit code 2"):
        w5.cmd_build(parse("build", "--all"))


def test_all_runs_every_step(monkeypatch):
    steps = []
    for name in ("cmd_clone", "cmd_configure", "cmd_build_sdk", "cmd_build"):
        monkeypatch.setattr(w5, name, lambda args, _n=name: steps.append(_n))
    w5.cmd_all(parse("all", "--clone"))
    assert steps == ["cmd_clone", "cmd_configure", "cmd_build_sdk", "cmd_build"]
    steps.clear()
    w5.cmd_all(parse("all"))
    assert "cmd_clone" not in steps


def test_log(monkeypatch):
    import serial_logger
    monkeypatch.setattr(serial_logger, "open_serial_monitor", lambda port, baud: (port, baud))
    assert w5.cmd_log(parse("log", "COM7")) == ("COM7", 115200)


def test_flash(ws, monkeypatch, capsys):
    import flash_helper
    monkeypatch.setattr(flash_helper, "flash_xds110", lambda fw, serial: (fw, serial))
    assert w5.cmd_flash(parse("flash", "nope")) == 1
    assert w5.cmd_flash(parse("flash", "network_terminal")) == 1
    assert "No firmware found" in capsys.readouterr().out
    bdir = ws / "wifi-examples/examples/rtos" / BOARD / "demos/network_terminal/freertos/ticlang"
    (bdir / "app.out").write_text("")
    assert w5.cmd_flash(parse("flash", "network_terminal", "--serial", "L41")) == (str(bdir / "app.out"), "L41")


def test_main(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["nora_w50_w51_build.py", "build"])
    assert w5.main() == 2

    def fail(args):
        raise w5.Fail("boom")

    def interrupt(args):
        raise KeyboardInterrupt
    for func, rc in ((fail, 1), (interrupt, 130), (lambda args: None, 0)):
        monkeypatch.setattr(w5, "cmd_doctor", func)
        monkeypatch.setattr(sys, "argv", ["nora_w50_w51_build.py", "doctor"])
        assert w5.main() == rc
    assert "ERROR: boom" in capsys.readouterr().out
