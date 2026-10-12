"""nora_w30_build.py commands on a fake Ameba-D tree (no make, toolchain or WSL2)."""

import argparse
import subprocess
import sys

import pytest

import nora_w30_build as w30

GCC = ("project", "realtek_amebaD_va0_example", "GCC-RELEASE")


def ns(**kw):
    return argparse.Namespace(**{"all": False, "project": None, "revision": None, **kw})


@pytest.fixture
def cfg(monkeypatch):
    data = {}
    monkeypatch.setattr(w30, "load_config", lambda: dict(data))
    monkeypatch.setattr(w30, "save_config", lambda c: data.clear() or data.update(c))
    return data


@pytest.fixture
def run(monkeypatch):
    class Recorder(list):
        rc = 0

        def __call__(self, cmd, **kw):
            self.append((cmd, kw))
            return subprocess.CompletedProcess(cmd, self.rc)
    rec = Recorder()
    monkeypatch.setattr(w30.subprocess, "run", rec)
    return rec


@pytest.fixture
def sdk(tmp_path, cfg):
    root = tmp_path / "ameba-rtos-d"
    for project in ("project_lp", "project_hp"):
        (root.joinpath(*GCC) / project).mkdir(parents=True)
    examples = root / "project" / "realtek_amebaD_va0_example" / "example_sources"
    (examples / "wifi_scan").mkdir(parents=True)
    (examples / "readme.txt").write_text("")
    cfg["sdk_path"] = str(root)
    return root


def test_config_round_trip(monkeypatch, tmp_path):
    path = tmp_path / "build.linux.json"
    monkeypatch.setattr(w30, "config_file", lambda: path)
    assert w30.load_config() == {}
    w30.save_config({"sdk_path": "/sdk"})
    assert w30.load_config() == {"sdk_path": "/sdk"}
    path.write_text("{")
    assert w30.load_config() == {}


def test_config_file_and_host(monkeypatch, tmp_path):
    monkeypatch.setattr(w30, "host_kind", lambda: "wsl")
    monkeypatch.setattr(w30.target_paths, "resolve_config", lambda t, h: tmp_path / t / h)
    assert w30.config_file() == tmp_path / "nora_w30" / "wsl"


@pytest.mark.parametrize("host,expected", [("linux", "/usr/bin/make"), ("windows", None)])
def test_tool_detection(monkeypatch, host, expected):
    monkeypatch.setattr(w30, "host_kind", lambda: host)
    monkeypatch.setattr(w30.shutil, "which", lambda name: f"/usr/bin/{name}")
    assert w30.detect_make() == expected
    assert w30.detect_arm_gcc() == (expected and "/usr/bin/arm-none-eabi-gcc")


def test_detect_python(monkeypatch, run):
    assert w30.detect_python() == sys.executable
    run.rc = 1
    assert w30.detect_python() is None


def test_doctor(monkeypatch, capsys):
    monkeypatch.setattr(w30, "config_file", lambda: "cfg.json")
    monkeypatch.setattr(w30, "host_kind", lambda: "windows")
    assert w30.cmd_doctor(ns()) == 1
    assert "WSL2" in capsys.readouterr().out
    monkeypatch.setattr(w30, "host_kind", lambda: "wsl")
    for name in ("detect_python", "detect_git", "detect_make", "detect_arm_gcc"):
        monkeypatch.setattr(w30, name, lambda: "/usr/bin/tool")
    assert w30.cmd_doctor(ns()) == 0
    monkeypatch.setattr(w30, "detect_make", lambda: None)
    assert w30.cmd_doctor(ns()) == 1
    assert "Some tools missing" in capsys.readouterr().out


def test_clone_failure_and_no_git(monkeypatch, cfg, run, capsys):
    monkeypatch.setattr(w30, "detect_git", lambda: None)
    assert w30.cmd_clone(ns()) == 1
    monkeypatch.setattr(w30, "detect_git", lambda: "git")
    monkeypatch.setattr(w30.target_paths, "check_space", lambda *a: False)
    assert w30.cmd_clone(ns(revision="v1")) == 1
    monkeypatch.setattr(w30.target_paths, "check_space", lambda *a: True)
    run.rc = 128
    assert w30.cmd_clone(ns(revision="v1")) == 128
    assert "Clone failed" in capsys.readouterr().out and cfg == {}


def test_install_prints_hints(capsys):
    assert w30.cmd_install(ns()) == 0
    assert "sudo apt install" in capsys.readouterr().out


def test_build(sdk, run, capsys):
    assert w30.cmd_build(ns()) == 0
    cmd, kw = run[0]
    assert cmd == ["make", "all"] and kw["cwd"] == sdk.joinpath(*GCC) / "project_hp"
    assert kw["env"]["SDK_ROOT"] == str(sdk)
    assert "Images at" in capsys.readouterr().out
    assert w30.cmd_build(ns(project="project_xx")) == 1


def test_build_without_sdk(cfg):
    assert w30.cmd_build(ns()) == 1
    assert w30.cmd_list(ns()) == 1
    assert w30.cmd_clean(ns()) == 1


def test_list(sdk, capsys):
    assert w30.cmd_list(ns()) == 0
    out = capsys.readouterr().out
    assert "- wifi_scan" in out and "readme" not in out


def test_list_without_examples(sdk, capsys):
    import shutil
    shutil.rmtree(sdk / "project" / "realtek_amebaD_va0_example" / "example_sources")
    assert w30.cmd_list(ns()) == 1


def test_clean_projects(sdk, run, capsys):
    assert w30.cmd_clean(ns()) == 0
    assert [kw["cwd"].name for _, kw in run] == ["project_lp", "project_hp"]
    assert w30.cmd_clean(ns(project="project_xx")) == 0
    assert "Project not found" in capsys.readouterr().out
    run.rc = 2
    assert w30.cmd_clean(ns(project="project_hp")) == 1


def test_clean_all(sdk, cfg, capsys):
    assert w30.cmd_clean(ns(all=True)) == 0
    assert not sdk.exists() and cfg == {}
    assert w30.cmd_clean(ns(all=True)) == 0
    assert "not found" in capsys.readouterr().out


def test_all_pipeline(monkeypatch, capsys):
    steps = []
    monkeypatch.setattr(w30, "cmd_clone", lambda a: steps.append("clone") or 0)
    monkeypatch.setattr(w30, "cmd_build", lambda a: steps.append("build") or 0)
    assert w30.cmd_all(ns()) == 0 and steps == ["clone", "build"]
    monkeypatch.setattr(w30, "cmd_clone", lambda a: 1)
    assert w30.cmd_all(ns()) == 1
    assert "Clone Realtek SDK failed" in capsys.readouterr().out


def test_flash_programs_the_three_images(sdk, monkeypatch, capsys):
    import flash_helper
    seen = {}
    monkeypatch.setattr(flash_helper, "flash_jlink_script",
                        lambda device, commands, serial: seen.update(device=device, commands=commands,
                                                                     serial=serial) or 0)
    hp = sdk.joinpath(*GCC) / "project_hp" / "asdk" / "image"
    lp = sdk.joinpath(*GCC) / "project_lp" / "asdk" / "image"
    hp.mkdir(parents=True)
    lp.mkdir(parents=True)
    assert w30.cmd_flash(ns(serial=None)) == 1
    assert "Build both cores first" in capsys.readouterr().out
    (lp / "km0_boot_all.bin").write_bytes(b"0")
    for name in ("km4_boot_all.bin", "km0_km4_image2.bin"):
        (hp / name).write_bytes(b"0")
    assert w30.cmd_flash(ns(serial="1100005639")) == 0
    assert seen["device"] == "RTL872xCS" and seen["serial"] == "1100005639"
    loads = [c for c in seen["commands"] if c.startswith("loadfile")]
    assert loads == [f'loadfile "{lp / "km0_boot_all.bin"}" 0x08000000',
                     f'loadfile "{hp / "km4_boot_all.bin"}" 0x08004000',
                     f'loadfile "{hp / "km0_km4_image2.bin"}" 0x08006000']


def test_flash_finds_the_sdk_without_cached_path(cfg, monkeypatch, tmp_path, capsys):
    sdk = tmp_path / "main"
    (sdk / "project").mkdir(parents=True)
    monkeypatch.setattr(w30.target_paths, "installed_sdks", lambda t: [sdk])
    cfg["sdk_path"] = "/mnt/e/not/on/windows"
    assert w30.find_sdk() == sdk
    monkeypatch.setattr(w30.target_paths, "installed_sdks", lambda t: [])
    assert w30.cmd_flash(ns(serial=None)) == 1
    assert "Realtek SDK not found" in capsys.readouterr().out


def test_log(monkeypatch):
    import serial_logger
    monkeypatch.setattr(serial_logger, "open_serial_monitor", lambda port, baud: (port, baud))
    assert w30.cmd_log(ns(port="COM191")) == ("COM191", 115200)


@pytest.mark.parametrize("argv,command", [
    (["flash", "project_hp", "--serial", "1"], "cmd_flash"), (["log", "COM3"], "cmd_log"),
    (["doctor"], "cmd_doctor"), (["clone", "--revision", "v1"], "cmd_clone"),
    (["install"], "cmd_install"), (["list"], "cmd_list"), (["clean", "--all"], "cmd_clean"),
    (["build", "project_lp"], "cmd_build"), (["all"], "cmd_all"),
])
def test_main_dispatch(monkeypatch, argv, command):
    monkeypatch.setattr(w30, command, lambda args: args)
    monkeypatch.setattr(sys, "argv", ["nora_w30_build.py", *argv])
    assert w30.main().command == argv[0]


def test_main_without_command(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["nora_w30_build.py"])
    assert w30.main() == 0
    assert "usage" in capsys.readouterr().out
