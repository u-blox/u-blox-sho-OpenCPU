"""iris_w10_build.py commands on a fake MCUXpresso west workspace (no west, toolchain or probe)."""

import argparse
import subprocess
import sys

import pytest

import iris_w10_build as iris


def ns(**kw):
    base = {"all": False, "board": iris.DEFAULT_BOARD, "example": "hello_world", "config": "debug",
            "toolchain": "armgcc", "pristine": False, "full": False, "revision": None,
            "serial": None, "port": None}
    return argparse.Namespace(**{**base, **kw})


class Recorder(list):
    rc = 0

    def __call__(self, cmd, **kw):
        self.append((cmd, kw))
        return subprocess.CompletedProcess(cmd, self.rc, "", "")

    @property
    def cmds(self):
        return [c for c, _ in self]


@pytest.fixture
def run(monkeypatch):
    rec = Recorder()
    monkeypatch.setattr(iris.subprocess, "run", rec)
    return rec


@pytest.fixture
def cfg(monkeypatch):
    data = {}
    monkeypatch.setattr(iris, "load_config", lambda: dict(data))
    monkeypatch.setattr(iris, "save_config", lambda c: data.clear() or data.update(c))
    return data


def example(ws, rel):
    path = ws / "mcuxsdk" / "examples" / rel
    path.mkdir(parents=True)
    (path / "CMakeLists.txt").write_text("")
    return path


@pytest.fixture
def ws(tmp_path, monkeypatch, cfg):
    root = tmp_path / "mcuxpresso"
    (root / ".west").mkdir(parents=True)
    example(root, "demo_apps/hello_world")
    example(root, "wifi_examples/wifi_cli")
    monkeypatch.setattr(iris, "detect_workspace", lambda: str(root))
    monkeypatch.setattr(iris, "west_cmd", lambda: ["west"])
    monkeypatch.setattr(iris, "armgcc_dir", lambda: ("/gcc", "ARMGCC_DIR"))
    return root


# ---------------------------------------------------------------------------
# detection
# ---------------------------------------------------------------------------

def test_is_venv_active(monkeypatch):
    monkeypatch.setattr(iris.sys, "base_prefix", "/base")
    monkeypatch.setattr(iris.sys, "prefix", "/venv")
    assert iris.is_venv_active()
    monkeypatch.setattr(iris.sys, "prefix", "/base")
    assert not iris.is_venv_active()


def test_python_detection(monkeypatch, run, tmp_path):
    assert iris._python_has_pip("py") and iris.detect_python() == sys.executable
    run.rc = 1
    monkeypatch.setattr(iris, "host_kind", lambda: "linux")
    assert iris.detect_python() == sys.executable
    other = tmp_path / "python.exe"
    other.write_text("")
    monkeypatch.setattr(iris, "host_kind", lambda: "windows")
    monkeypatch.setattr(iris, "which", lambda name: str(other))
    monkeypatch.setattr(iris, "_python_has_pip", lambda exe: exe == str(other.resolve()))
    assert iris.detect_python() == str(other.resolve())


def test_python_has_pip_handles_errors(monkeypatch):
    def boom(*a, **k):
        raise OSError
    monkeypatch.setattr(iris.subprocess, "run", boom)
    assert not iris._python_has_pip("py")


@pytest.mark.parametrize("func,found", [(iris.detect_west, "/bin/west"), (iris.west_cmd, ["/bin/west"])])
def test_west_lookup(monkeypatch, run, func, found):
    monkeypatch.setattr(iris, "which", lambda name: "/bin/west")
    assert func() == found
    monkeypatch.setattr(iris, "which", lambda name: None)
    assert "-m" in func()
    run.rc = 1
    assert func() is None

    def boom(*a, **k):
        raise OSError
    monkeypatch.setattr(iris.subprocess, "run", boom)
    assert func() is None


@pytest.mark.parametrize("name", ["detect_cmake", "detect_ninja", "detect_arm_gcc"])
def test_windows_tool_lookup(monkeypatch, name):
    monkeypatch.delenv("ARMGCC_DIR", raising=False)
    monkeypatch.setattr(iris, "which", lambda tool: f"/usr/bin/{tool}")
    monkeypatch.setattr(iris, "host_kind", lambda: "linux")
    assert getattr(iris, name)().startswith("/usr/bin/")
    monkeypatch.setattr(iris, "host_kind", lambda: "windows")
    monkeypatch.setattr(iris, "newest", lambda patterns: "C:/Program Files/tool.exe")
    monkeypatch.setattr(iris, "short_path", lambda p: "C:/PROGRA~1/tool.exe")
    assert getattr(iris, name)() == "C:/PROGRA~1/tool.exe"
    assert iris.detect_git() == "/usr/bin/git"


def test_arm_gcc_from_armgcc_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(iris, "host_kind", lambda: "linux")
    gcc = tmp_path / "bin" / "arm-none-eabi-gcc"
    gcc.parent.mkdir()
    gcc.write_text("")
    monkeypatch.setenv("ARMGCC_DIR", str(tmp_path))
    assert iris.detect_arm_gcc() == str(gcc)


def test_detect_workspace(monkeypatch, tmp_path):
    saved = tmp_path / "saved"
    (saved / ".west").mkdir(parents=True)
    monkeypatch.setattr(iris, "load_config", lambda: {"workspace": str(saved)})
    assert iris.detect_workspace() == str(saved)
    monkeypatch.setattr(iris, "load_config", lambda: {})
    monkeypatch.setattr(iris.target_paths, "installed_sdks", lambda t: [tmp_path / "x", saved])
    assert iris.detect_workspace() == str(saved)
    monkeypatch.setattr(iris.target_paths, "installed_sdks", lambda t: [])
    assert iris.detect_workspace() is None


def test_config_round_trip(monkeypatch, tmp_path):
    path = tmp_path / "build.json"
    monkeypatch.setattr(iris, "config_file", lambda: path)
    assert iris.load_config() == {}
    iris.save_config({"workspace": "/ws"})
    assert iris.load_config() == {"workspace": "/ws"}
    path.write_text("{")
    assert iris.load_config() == {}


def test_config_file(monkeypatch, tmp_path):
    monkeypatch.setattr(iris, "host_kind", lambda: "linux")
    monkeypatch.setattr(iris.target_paths, "resolve_config", lambda t, h: tmp_path / t / h)
    assert iris.config_file() == tmp_path / "iris_w10" / "linux"


def test_examples_root(tmp_path):
    assert iris.examples_root(str(tmp_path)) is None
    (tmp_path / "examples").mkdir()
    assert iris.examples_root(str(tmp_path)) == tmp_path / "examples"


def test_resolve_example(ws, capsys):
    assert iris.resolve_example(str(ws), "demo_apps/hello_world") == ws / "mcuxsdk/examples/demo_apps/hello_world"
    assert iris.resolve_example(str(ws), "wifi_cli") == ws / "mcuxsdk/examples/wifi_examples/wifi_cli"
    example(ws, "other/wifi_cli")
    assert iris.resolve_example(str(ws), "wifi_cli") is None
    assert "ambiguous" in capsys.readouterr().out
    assert iris.resolve_example(str(ws), "nope") is None
    assert iris.resolve_example(str(ws / "empty"), "x") is None


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

@pytest.fixture
def tools(monkeypatch):
    for name in ("detect_python", "detect_git", "detect_west", "detect_cmake", "detect_ninja",
                 "detect_arm_gcc"):
        monkeypatch.setattr(iris, name, lambda: "/tool")
    monkeypatch.setattr(iris, "host_kind", lambda: "linux")
    monkeypatch.setattr(iris, "config_file", lambda: "cfg.json")


def test_doctor(ws, tools, monkeypatch, capsys):
    assert iris.cmd_doctor(ns()) == 0
    monkeypatch.setattr(iris, "armgcc_dir", lambda: (None, "not found"))
    monkeypatch.setattr(iris, "detect_workspace", lambda: None)
    assert iris.cmd_doctor(ns()) == 1
    assert "No Arm GNU toolchain" in capsys.readouterr().out


def test_clone_targeted(tmp_path, monkeypatch, run, cfg):
    monkeypatch.setattr(iris, "west_cmd", lambda: ["west"])
    monkeypatch.setattr(iris, "detect_workspace", lambda: None)
    monkeypatch.setattr(iris.target_paths, "check_space", lambda *a: True)
    assert iris.cmd_clone(ns(revision="v25.09.00")) == 0
    ws = iris.target_paths.sdk_dir(iris.TARGET, "v25.09.00")
    assert run.cmds == [["west", "init", "-m", iris.MANIFEST_URL, ws.name, "--mr", "v25.09.00"],
                        ["west", "update_board", "--set", "board", iris.DEFAULT_BOARD]]
    assert cfg == {"workspace": str(ws), "board": iris.DEFAULT_BOARD}


def test_clone_existing_full_and_failures(ws, monkeypatch, run, capsys):
    monkeypatch.setattr(iris.target_paths, "check_space", lambda *a: True)
    assert iris.cmd_clone(ns(full=True)) == 0
    assert run.cmds == [["west", "update"]]
    run.rc = 1
    assert iris.cmd_clone(ns()) == 1
    assert "Retry with --full" in capsys.readouterr().out
    monkeypatch.setattr(iris.target_paths, "check_space", lambda *a: False)
    assert iris.cmd_clone(ns(full=True)) == 1
    monkeypatch.setattr(iris, "west_cmd", lambda: None)
    assert iris.cmd_clone(ns()) == 1


def test_clone_init_failure(monkeypatch, run):
    monkeypatch.setattr(iris, "west_cmd", lambda: ["west"])
    monkeypatch.setattr(iris, "detect_workspace", lambda: None)
    monkeypatch.setattr(iris.target_paths, "check_space", lambda *a: True)
    run.rc = 2
    assert iris.cmd_clone(ns()) == 2 and len(run) == 1


def test_install(ws, tools, monkeypatch, run, capsys):
    assert iris.cmd_install(ns()) == 0
    assert "SDK not cloned yet" in capsys.readouterr().out
    reqs = ws / "mcuxsdk/scripts/requirements-base.txt"
    reqs.parent.mkdir(parents=True)
    reqs.write_text("")
    assert iris.cmd_install(ns()) == 0
    assert run.cmds[-1] == ["/tool", "-m", "pip", "install", "-r", str(reqs)]
    for host, hint in (("windows", "MCUXpresso Installer"), ("linux", "sudo apt install")):
        monkeypatch.setattr(iris, "host_kind", lambda h=host: h)
        monkeypatch.setattr(iris, "detect_ninja", lambda: None)
        assert iris.cmd_install(ns()) == 0
        assert hint in capsys.readouterr().out


def test_install_failures(ws, tools, monkeypatch, run):
    reqs = ws / "mcuxsdk/scripts/requirements-base.txt"
    reqs.parent.mkdir(parents=True)
    reqs.write_text("")
    run.rc = 1
    assert iris.cmd_install(ns()) == 1
    monkeypatch.setattr(iris.subprocess, "run", lambda cmd, **kw: subprocess.CompletedProcess(
        cmd, 1 if "-r" in cmd else 0))
    assert iris.cmd_install(ns()) == 1
    monkeypatch.setattr(iris, "detect_python", lambda: None)
    assert iris.cmd_install(ns()) == 1


def test_list(ws, capsys):
    example(ws, "a/b/c")
    assert iris.cmd_list(ns()) == 0
    out = capsys.readouterr().out
    assert "demo_apps/hello_world" in out and "a/b/c" not in out


def test_list_failures(ws, monkeypatch, capsys):
    import shutil
    shutil.rmtree(ws / "mcuxsdk" / "examples")
    assert iris.cmd_list(ns()) == 1
    (ws / "examples").mkdir()
    assert iris.cmd_list(ns()) == 0
    assert "No examples found" in capsys.readouterr().out
    monkeypatch.setattr(iris, "detect_workspace", lambda: None)
    assert iris.cmd_list(ns()) == 1


def test_build(ws, run, capsys):
    assert iris.cmd_build(ns(pristine=True)) == 0
    cmd, kw = run[0]
    assert cmd[:9] == ["west", "build", "-b", iris.DEFAULT_BOARD,
                       "mcuxsdk/examples/demo_apps/hello_world", "--toolchain", "armgcc", "--config", "debug"]
    assert cmd[9:11] == ["-p", "always"] and kw["env"]["ARMGCC_DIR"] == "/gcc"
    assert "Build complete" in capsys.readouterr().out


def test_build_failures(ws, monkeypatch, run):
    assert iris.cmd_build(ns(example=None)) == 1
    assert iris.cmd_build(ns(example="nope")) == 1
    run.rc = 3
    assert iris.cmd_build(ns()) == 3
    monkeypatch.setattr(iris, "armgcc_dir", lambda: (None, "not found"))
    assert iris.cmd_build(ns()) == 1
    monkeypatch.setattr(iris, "west_cmd", lambda: None)
    assert iris.cmd_build(ns()) == 1
    monkeypatch.setattr(iris, "detect_workspace", lambda: None)
    assert iris.cmd_build(ns()) == 1


def test_flash(ws, monkeypatch, capsys):
    import flash_helper
    seen = []
    monkeypatch.setattr(flash_helper, "HAS_PYLINK", True)
    monkeypatch.setattr(flash_helper, "pick_jlink", lambda prefer=None: "1060060281")
    monkeypatch.setattr(flash_helper, "flash_jlink_script",
                        lambda dev, commands, serial=None, speed=2000: seen.append((dev, commands, serial)) or 0)
    assert iris.cmd_flash(ns(example=None)) == 1
    assert iris.cmd_flash(ns(example="nope")) == 1
    assert iris.cmd_flash(ns()) == 1
    assert "Build directory not found" in capsys.readouterr().out
    # Current SDKs build straight into build/; .bin (at the flash base) wins over .elf.
    out = ws / "build"
    out.mkdir()
    assert iris.cmd_flash(ns()) == 1
    (out / "hello_world.elf").write_text("")
    assert iris.cmd_flash(ns()) == 0
    assert seen[-1] == ("RW612", ["r", "h", f'loadfile "{out / "hello_world.elf"}"', "r", "g"], "1060060281")
    (out / "hello_world.bin").write_text("")
    assert iris.cmd_flash(ns(serial="123")) == 0
    bin_path = out / "hello_world.bin"
    assert seen[-1] == ("RW612", ["r", "h", "erase 0x08000000 0x08000FFF", f'loadbin "{bin_path}" 0x08000000',
                                  f'verifybin "{bin_path}" 0x08000000', "r", "g"], "123")
    # Several probes and no way to tell which: stop before flashing.
    monkeypatch.setattr(flash_helper, "pick_jlink", lambda prefer=None: "")
    count = len(seen)
    assert iris.cmd_flash(ns()) == 1 and len(seen) == count
    # Older SDKs: build/<config>.
    release = out / "release"
    release.mkdir()
    (release / "hello_world.hex").write_text("")
    assert iris.cmd_flash(ns(config="release", serial="123")) == 0
    assert seen[-1][1][2] == f'loadfile "{release / "hello_world.hex"}"'
    monkeypatch.setattr(iris, "detect_workspace", lambda: None)
    assert iris.cmd_flash(ns()) == 1


def test_isp_steps(tmp_path):
    fw = tmp_path / "hello_world.bin"
    fw.write_bytes(b"\0" * 0x10001)
    fid = iris.isp_steps("fidelex-8mb", fw)
    assert fid[0][:2] == ["write-memory", "0x20001000"] and fid[0][2].endswith("FCB_FID.bin")
    assert fid[-2:] == [["flash-erase-region", "0x08000000", "0x20000"], ["write-memory", "0x08000000", str(fw)]]
    mx = iris.isp_steps("macronix-8mb", fw)
    assert mx[0] == ["fill-memory", "0x20001000", "0x4", "0xC0000008"] and mx[-1][0] == "write-memory"
    assert iris.is_serial_port("COM147") and iris.is_serial_port("/dev/ttyACM0") and not iris.is_serial_port("1060060281")


def test_flash_isp(ws, monkeypatch, capsys, tmp_path):
    fw = tmp_path / "hello_world.bin"
    fw.write_bytes(b"\0" * 16)
    monkeypatch.setattr(iris, "find_blhost", lambda: None)
    assert iris.flash_isp("COM147", fw) == 1
    assert "--install" in capsys.readouterr().out
    monkeypatch.setattr(iris, "find_blhost", lambda: "blhost")
    monkeypatch.setattr(iris, "flash_part", lambda: "fidelex-8mb")
    calls, codes = [], []

    def run(cmd, **kw):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, codes.pop(0) if codes else 0)
    monkeypatch.setattr(iris.subprocess, "run", run)
    codes[:] = [1]
    assert iris.flash_isp("COM147", fw) == 1
    assert "SW3 REQ=ON" in capsys.readouterr().out
    calls.clear()
    assert iris.flash_isp("COM147", fw) == 0
    assert calls[0][:3] == ["blhost", "-p", "COM147,115200"] and calls[-1][-3:] == ["write-memory", "0x08000000", str(fw)]
    assert "REQ=OFF" in capsys.readouterr().out
    codes[:] = [0, 0, 5]
    assert iris.flash_isp("COM147", fw) == 1


def test_flash_through_boot_rom(ws, monkeypatch, capsys):
    out = ws / "build"
    out.mkdir()
    (out / "hello_world.elf").write_text("")
    assert iris.cmd_flash(ns(serial="COM147")) == 1
    assert "needs a .bin" in capsys.readouterr().out
    (out / "hello_world.bin").write_text("")
    monkeypatch.setattr(iris, "flash_isp", lambda port, fw: (port, fw.name))
    assert iris.cmd_flash(ns(serial="COM147")) == ("COM147", "hello_world.bin")


def test_flash_part_from_rf_config(monkeypatch):
    import module_config
    monkeypatch.setattr(module_config, "load_state", lambda key: {})
    assert iris.flash_part() == "fidelex-8mb"
    monkeypatch.setattr(module_config, "load_state", lambda key: {"variables": {"flash_part": "macronix-8mb"}})
    assert iris.flash_part() == "macronix-8mb"


def test_find_blhost(monkeypatch, tmp_path):
    monkeypatch.setattr(iris.sys, "executable", str(tmp_path / "python"))
    monkeypatch.setattr(iris, "which", lambda name: None)
    assert iris.find_blhost() is None
    exe = tmp_path / ("blhost.exe" if iris.host_kind() == "windows" else "blhost")
    exe.write_text("")
    assert iris.find_blhost() == str(exe)


def test_log(monkeypatch):
    monkeypatch.setattr(iris.serial_logger, "open_serial_monitor", lambda port, baud: (port, baud))
    assert iris.cmd_log(ns(port="COM11")) == ("COM11", 115200)


def test_clean(ws, cfg, monkeypatch, capsys):
    (ws / "build").mkdir()
    assert iris.cmd_clean(ns()) == 0 and not (ws / "build").exists()
    assert iris.cmd_clean(ns()) == 0
    cfg["workspace"] = str(ws)
    assert iris.cmd_clean(ns(all=True)) == 0 and not ws.exists() and cfg == {}
    monkeypatch.setattr(iris, "detect_workspace", lambda: None)
    assert iris.cmd_clean(ns(all=True)) == 0
    assert iris.cmd_clean(ns()) == 1


def test_all_pipeline(monkeypatch, capsys):
    steps = []
    for name in ("cmd_install", "cmd_clone", "cmd_build"):
        monkeypatch.setattr(iris, name, lambda a, _n=name: steps.append(_n) or 0)
    assert iris.cmd_all(ns()) == 0 and steps == ["cmd_install", "cmd_clone", "cmd_build"]
    monkeypatch.setattr(iris, "cmd_clone", lambda a: 1)
    assert iris.cmd_all(ns()) == 1


@pytest.mark.parametrize("argv,command", [
    (["doctor"], "cmd_doctor"), (["clone", "--full"], "cmd_clone"), (["install"], "cmd_install"),
    (["list"], "cmd_list"), (["log", "COM3"], "cmd_log"), (["clean"], "cmd_clean"),
    (["build", "x", "-p"], "cmd_build"), (["flash", "x"], "cmd_flash"), (["all"], "cmd_all"),
])
def test_main_dispatch(monkeypatch, argv, command):
    monkeypatch.setattr(iris, command, lambda args: args)
    monkeypatch.setattr(iris, "is_venv_active", lambda: True)
    monkeypatch.setattr(sys, "argv", ["iris_w10_build.py", *argv])
    assert iris.main().command == argv[0]


def test_main_without_command(monkeypatch, capsys):
    monkeypatch.setattr(iris, "is_venv_active", lambda: False)
    monkeypatch.setattr(sys, "argv", ["iris_w10_build.py"])
    assert iris.main() == 0
    out = capsys.readouterr().out
    assert "[TIP]" in out and "usage" in out
