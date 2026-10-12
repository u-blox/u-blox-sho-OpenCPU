"""nora_w40_build.py commands on a fake ESP-IDF tree (no idf.py, toolchain or board)."""

import argparse
import subprocess
import sys

import pytest

import nora_w40_build as w40


def ns(**kw):
    return argparse.Namespace(**{"all": False, "example": "hello_world", "revision": None,
                                 "serial": None, **kw})


class Recorder(list):
    """subprocess.run stand-in: records (cmd, kwargs), returns rc and stdout."""
    rc = 0
    out = ""

    def __call__(self, cmd, **kw):
        self.append((cmd, kw))
        if kw.get("check") and self.rc:
            raise subprocess.CalledProcessError(self.rc, cmd)
        return subprocess.CompletedProcess(cmd, self.rc, self.out, "")

    @property
    def cmds(self):
        return [c for c, _ in self]


@pytest.fixture
def run(monkeypatch):
    rec = Recorder()
    monkeypatch.setattr(w40.subprocess, "run", rec)
    return rec


@pytest.fixture
def cfg(monkeypatch):
    data = {}
    monkeypatch.setattr(w40, "load_config", lambda: dict(data))
    monkeypatch.setattr(w40, "save_config", lambda c: data.clear() or data.update(c))
    return data


def example(root, rel):
    path = root / "examples" / rel
    path.mkdir(parents=True)
    (path / "CMakeLists.txt").write_text("")
    return path


@pytest.fixture
def idf(tmp_path, monkeypatch, cfg):
    root = tmp_path / "esp-idf"
    example(root, "get-started/hello_world")
    example(root, "wifi/scan")
    (root / "tools").mkdir()
    (root / "tools" / "idf.py").write_text("")
    monkeypatch.setattr(w40, "detect_idf", lambda: str(root))
    monkeypatch.setattr(w40, "detect_idf_python", lambda d: "idfpy")
    monkeypatch.setattr(w40, "idf_environment", lambda d, p: {"IDF_PATH": d})
    return root


# ---------------------------------------------------------------------------
# detection and environment
# ---------------------------------------------------------------------------

def test_config_round_trip(monkeypatch, tmp_path):
    path = tmp_path / "build.json"
    monkeypatch.setattr(w40, "config_file", lambda: path)
    assert w40.load_config() == {}
    w40.save_config({"idf_path": "/idf"})
    assert w40.load_config() == {"idf_path": "/idf"}
    path.write_text("{")
    assert w40.load_config() == {}


def test_config_file_and_host(monkeypatch, tmp_path):
    monkeypatch.setattr(w40.target_paths, "host_kind", lambda: "linux")
    monkeypatch.setattr(w40.target_paths, "resolve_config", lambda t, h: tmp_path / t / h)
    assert w40.config_file() == tmp_path / "nora_w40" / "linux"


def test_detect_idf(monkeypatch, tmp_path):
    saved = tmp_path / "saved"
    saved.mkdir()
    monkeypatch.setattr(w40, "load_config", lambda: {"idf_path": str(saved)})
    assert w40.detect_idf() == str(saved)
    installed = tmp_path / "sdks" / "master"
    installed.mkdir(parents=True)
    monkeypatch.setattr(w40, "load_config", lambda: {"idf_path": str(tmp_path / "gone")})
    monkeypatch.setattr(w40.target_paths, "installed_sdks", lambda t: [installed])
    assert w40.detect_idf() == str(installed)
    monkeypatch.setattr(w40.target_paths, "installed_sdks", lambda t: [])
    monkeypatch.setattr(w40.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(w40.Path, "exists", lambda self: False)
    assert w40.detect_idf() is None


@pytest.mark.parametrize("name", ["detect_git", "detect_make", "detect_cmake"])
def test_tool_detection(monkeypatch, tmp_path, name):
    monkeypatch.setattr(w40.shutil, "which", lambda tool: f"/usr/bin/{tool}")
    monkeypatch.setattr(w40, "host_kind", lambda: "linux")
    assert getattr(w40, name)().startswith("/usr/bin/")
    monkeypatch.setattr(w40, "host_kind", lambda: "windows")
    monkeypatch.setattr(w40, "newest", lambda patterns: "C:/Program Files/tool.EXE")
    monkeypatch.setattr(w40, "short_path", lambda p: "C:/PROGRA~1/tool.EXE")
    assert getattr(w40, name)() == "C:/PROGRA~1/tool.EXE"


def test_newest(tmp_path, monkeypatch):
    for v in ("1.0", "2.0"):
        (tmp_path / f"tool-{v}").mkdir()
    monkeypatch.chdir(tmp_path)
    assert w40.newest(["tool-*"]).endswith("tool-2.0")
    assert w40.newest([str(tmp_path / "tool-1.0").replace("\\", "/")]).endswith("tool-1.0")
    assert w40.newest(["/does/not/exist"]) is None


def test_short_path_off_windows(monkeypatch):
    monkeypatch.setattr(w40, "host_kind", lambda: "linux")
    assert w40.short_path("/a b") == "/a b"


@pytest.mark.skipif(sys.platform != "win32", reason="GetShortPathNameW is Windows-only")
def test_short_path_on_windows(monkeypatch, tmp_path):
    monkeypatch.setattr(w40, "host_kind", lambda: "windows")
    assert w40.short_path(str(tmp_path))


def test_detect_python(run):
    assert w40.detect_python() == sys.executable
    run.rc = 1
    assert w40.detect_python() is None


def make_env(root, name, layout):
    exe = root / "python_env" / name / layout
    exe.parent.mkdir(parents=True)
    exe.write_text("")
    return exe


def test_detect_idf_python(monkeypatch, tmp_path, run):
    tools = tmp_path / "tools"
    monkeypatch.setenv("IDF_TOOLS_PATH", str(tools))
    monkeypatch.delenv("IDF_PYTHON_ENV_PATH", raising=False)
    idf = tmp_path / "idf"
    assert w40.detect_idf_python(str(idf)) is None
    exe = make_env(tools, "idf6.0_py3.12_env", "bin/python3")
    assert w40.detect_idf_python(str(idf)) == str(exe)
    (idf / "tools").mkdir(parents=True)
    (idf / "tools" / "idf_tools.py").write_text("")
    run.rc = 1
    assert w40.detect_idf_python(str(idf)) is None
    run.rc = 0
    monkeypatch.setenv("IDF_PYTHON_ENV_PATH", str(tools / "python_env" / "idf6.0_py3.12_env"))
    assert w40.detect_idf_python(str(idf)) == str(exe)
    assert run.cmds[-1][1:] == [str(idf / "tools" / "idf_tools.py"), "check-python-dependencies"]


def test_idf_environment(monkeypatch, tmp_path, run):
    monkeypatch.setenv("PATH", "/usr/bin")
    monkeypatch.setenv("MSYSTEM", "UCRT64")
    env = w40.idf_environment(str(tmp_path), "py")
    assert env["IDF_PATH"] == str(tmp_path) and "MSYSTEM" not in env and not run
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "idf_tools.py").write_text("")
    run.out = "PATH=/idf/bin:$PATH\nIDF_TOOLS=1\nnoise\n"
    env = w40.idf_environment(str(tmp_path), "py")
    assert env["PATH"] == "/idf/bin:/usr/bin" and env["IDF_TOOLS"] == "1"
    run.rc = 1
    assert "IDF_TOOLS" not in w40.idf_environment(str(tmp_path), "py")


def test_current_target(tmp_path):
    assert w40.current_target(tmp_path) is None
    (tmp_path / "sdkconfig").write_text('# x\nCONFIG_IDF_TARGET="esp32c6"\n')
    assert w40.current_target(tmp_path) == "esp32c6"
    (tmp_path / "sdkconfig").write_text("# empty\n")
    assert w40.current_target(tmp_path) is None


def test_resolve_example(idf):
    assert w40.resolve_example(str(idf), "wifi/scan") == (idf / "examples/wifi/scan", None)
    assert w40.resolve_example(str(idf), "scan") == (idf / "examples/wifi/scan", None)
    example(idf, "build_system/fixtures/deep/scan")
    assert w40.resolve_example(str(idf), "scan")[0] == idf / "examples/wifi/scan"
    example(idf, "bluetooth/scan")
    path, error = w40.resolve_example(str(idf), "scan")
    assert path is None and "ambiguous, 2 matches" in error
    assert "not found" in w40.resolve_example(str(idf), "nope")[1]
    assert "Examples directory" in w40.resolve_example(str(idf / "x"), "scan")[1]


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def test_doctor(monkeypatch, capsys):
    monkeypatch.setattr(w40, "config_file", lambda: "cfg.json")
    monkeypatch.setattr(w40, "host_kind", lambda: "linux")
    for name in ("detect_python", "detect_git", "detect_cmake", "detect_make", "detect_idf"):
        monkeypatch.setattr(w40, name, lambda: "/tool")
    assert w40.cmd_doctor(ns()) == 0
    monkeypatch.setattr(w40, "detect_idf", lambda: None)
    assert w40.cmd_doctor(ns()) == 1
    assert "Some tools missing" in capsys.readouterr().out


def test_clone_paths(monkeypatch, tmp_path, run, cfg):
    monkeypatch.setattr(w40.target_paths, "check_space", lambda *a: False)
    assert w40.cmd_clone(ns(revision="v6.0")) == 1
    monkeypatch.setattr(w40.target_paths, "check_space", lambda *a: True)
    run.rc = 1
    assert w40.cmd_clone(ns()) == 1  # git --version fails


def test_install(idf, monkeypatch, run, capsys):
    monkeypatch.setenv("MSYSTEM", "UCRT64")
    for host, script in (("linux", "install.sh"), ("windows", "install.bat")):
        monkeypatch.setattr(w40, "host_kind", lambda h=host: h)
        assert w40.cmd_install(ns()) == 1
        (idf / script).write_text("")
        assert w40.cmd_install(ns()) == 0
        assert run[-1][0][-1] == str(idf / script) and "MSYSTEM" not in run[-1][1]["env"]
    assert "export.ps1" in capsys.readouterr().out


def test_install_without_idf(monkeypatch):
    monkeypatch.setattr(w40, "detect_idf", lambda: None)
    assert w40.cmd_install(ns()) == 1
    assert w40.cmd_build(ns()) == 1
    assert w40.cmd_list(ns()) == 1
    assert w40.cmd_clean(ns()) == 1
    assert w40.cmd_flash(ns()) == 1


def test_build_sets_target_then_builds(idf, run):
    assert w40.cmd_build(ns()) == 0
    hello = idf / "examples/get-started/hello_world"
    assert run.cmds == [["idfpy", str(idf / "tools/idf.py"), "set-target", "esp32c6"],
                        ["idfpy", str(idf / "tools/idf.py"), "build"]]
    assert run[0][1]["cwd"] == hello
    (hello / "sdkconfig").write_text('CONFIG_IDF_TARGET="esp32c6"\n')
    run.clear()
    assert w40.cmd_build(ns()) == 0 and len(run) == 1


def test_build_failures(idf, run, monkeypatch, capsys):
    assert w40.cmd_build(ns(example=None)) == 1
    assert w40.cmd_build(ns(example="nope")) == 1
    run.rc = 2
    assert w40.cmd_build(ns()) == 2
    assert "Could not set target" in capsys.readouterr().out
    (idf / "tools" / "idf.py").unlink()
    assert w40.cmd_build(ns()) == 1
    assert w40.cmd_flash(ns()) == 1
    monkeypatch.setattr(w40, "detect_idf_python", lambda d: None)
    assert w40.cmd_build(ns()) == 1
    assert w40.cmd_flash(ns()) == 1


def test_flash_and_log(idf, run):
    assert w40.cmd_flash(ns(serial="COM9")) == 0
    assert run.cmds[-1] == ["idfpy", str(idf / "tools/idf.py"), "-p", "COM9", "flash"]
    assert w40.cmd_log(ns()) == 0
    assert run.cmds[-1] == ["idfpy", str(idf / "tools/idf.py"), "monitor"]
    assert w40.cmd_flash(ns(example="nope")) == 1


def test_list(idf, capsys):
    example(idf, "a/b/c/too_deep")
    assert w40.cmd_list(ns()) == 0
    out = capsys.readouterr().out
    assert "hello_world" in out and "too_deep" not in out


def test_list_empty_and_missing(idf, capsys):
    import shutil
    shutil.rmtree(idf / "examples")
    assert w40.cmd_list(ns()) == 1
    (idf / "examples").mkdir()
    assert w40.cmd_list(ns()) == 0
    assert "No examples found" in capsys.readouterr().out


def test_clean(idf, capsys):
    build = idf / "examples/get-started/hello_world/build"
    build.mkdir()
    assert w40.cmd_clean(ns()) == 0 and not build.exists()
    assert w40.cmd_clean(ns()) == 0
    assert w40.cmd_clean(ns(example=None)) == 0
    assert w40.cmd_clean(ns(example="nope")) == 1
    assert "Build directory not found" in capsys.readouterr().out


def test_clean_all(idf, cfg, monkeypatch, capsys):
    cfg["idf_path"] = str(idf)
    assert w40.cmd_clean(ns(all=True)) == 0
    assert not idf.exists() and cfg == {}
    monkeypatch.setattr(w40, "detect_idf", lambda: None)
    assert w40.cmd_clean(ns(all=True)) == 0
    assert "ESP-IDF not found" in capsys.readouterr().out


def test_all_pipeline(monkeypatch, capsys):
    steps = []
    for name in ("cmd_clone", "cmd_install", "cmd_build"):
        monkeypatch.setattr(w40, name, lambda a, _n=name: steps.append(_n) or 0)
    assert w40.cmd_all(ns()) == 0 and len(steps) == 3
    monkeypatch.setattr(w40, "cmd_install", lambda a: 1)
    assert w40.cmd_all(ns()) == 1
    assert "Install ESP-IDF Environment failed" in capsys.readouterr().out


@pytest.mark.parametrize("argv,command", [
    (["doctor"], "cmd_doctor"), (["clone"], "cmd_clone"), (["install"], "cmd_install"),
    (["list"], "cmd_list"), (["clean", "--all"], "cmd_clean"), (["build", "x"], "cmd_build"),
    (["flash", "x", "--serial", "COM3"], "cmd_flash"), (["log"], "cmd_log"), (["all", "x"], "cmd_all"),
])
def test_main_dispatch(monkeypatch, argv, command):
    monkeypatch.setattr(w40, command, lambda args: args)
    monkeypatch.setattr(sys, "argv", ["nora_w40_build.py", *argv])
    assert w40.main().command == argv[0]


def test_main_without_command(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["nora_w40_build.py"])
    assert w40.main() == 0
    assert "usage" in capsys.readouterr().out
