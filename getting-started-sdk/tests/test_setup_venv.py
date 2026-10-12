"""Shared venv setup (scripts/setup_venv.py) and the launcher entry points."""

import subprocess
from pathlib import Path

import pytest

import setup_venv as sv


@pytest.mark.parametrize("tag,expected", [
    ("mingw_x86_64_ucrt", True),
    ("mingw_x86_64", True),
    ("win-amd64", False),
    ("linux-x86_64", False),
])
def test_is_mingw_python(tag, expected):
    assert sv.is_mingw_python(tag) is expected


def test_base_python_off_windows(monkeypatch):
    monkeypatch.setattr(sv.platform, "system", lambda: "Linux")
    assert sv.select_base_python() == sv.sys.executable


def test_base_python_native_windows(monkeypatch):
    monkeypatch.setattr(sv.platform, "system", lambda: "Windows")
    monkeypatch.setattr(sv, "is_mingw_python", lambda tag=None: False)
    assert sv.select_base_python() == sv.sys.executable


def test_base_python_mingw_switches_to_native(monkeypatch, capsys):
    monkeypatch.setattr(sv.platform, "system", lambda: "Windows")
    monkeypatch.setattr(sv, "is_mingw_python", lambda tag=None: True)
    monkeypatch.setattr(sv, "find_native_python", lambda: r"C:\Python312\python.exe")
    assert sv.select_base_python() == r"C:\Python312\python.exe"
    assert "MSYS2/MinGW" in capsys.readouterr().out


def test_base_python_mingw_without_native_fails(monkeypatch):
    monkeypatch.setattr(sv.platform, "system", lambda: "Windows")
    monkeypatch.setattr(sv, "is_mingw_python", lambda tag=None: True)
    monkeypatch.setattr(sv, "find_native_python", lambda: None)
    with pytest.raises(SystemExit):
        sv.select_base_python()


def test_find_native_python_without_py_launcher(monkeypatch):
    monkeypatch.setattr(sv.shutil, "which", lambda name: None)
    assert sv.find_native_python() is None


def test_existing_unix_layout_venv_rejected_on_windows(monkeypatch, tmp_path):
    (tmp_path / ".venv" / "bin").mkdir(parents=True)
    monkeypatch.setattr(sv, "get_sdk_root", lambda: str(tmp_path))
    monkeypatch.setattr(sv.platform, "system", lambda: "Windows")
    with pytest.raises(SystemExit):
        sv.create_venv()


def test_find_native_python_probe(monkeypatch):
    monkeypatch.setattr(sv.shutil, "which", lambda name: "py")
    monkeypatch.setattr(sv.subprocess, "run",
                        lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "C:\\Py\\python.exe\n", ""))
    assert sv.find_native_python() == "C:\\Py\\python.exe"
    monkeypatch.setattr(sv.subprocess, "run",
                        lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "\n", ""))
    assert sv.find_native_python() is None

    def boom(cmd, **kw):
        raise OSError("py broken")
    monkeypatch.setattr(sv.subprocess, "run", boom)
    assert sv.find_native_python() is None


@pytest.fixture
def sdk(monkeypatch, tmp_path):
    monkeypatch.setattr(sv, "get_sdk_root", lambda: str(tmp_path))
    monkeypatch.setattr(sv.platform, "system", lambda: "Linux")
    return tmp_path


def make_pip(venv, *parts):
    pip = venv.joinpath(*parts)
    pip.parent.mkdir(parents=True, exist_ok=True)
    pip.write_text("")
    return str(pip)


def test_create_venv(sdk, monkeypatch):
    seen = []
    monkeypatch.setattr(sv.subprocess, "check_call", seen.append)
    assert sv.create_venv() == str(sdk / ".venv")
    assert seen == [[sv.sys.executable, "-m", "venv", str(sdk / ".venv")]]
    (sdk / ".venv").mkdir()
    assert sv.create_venv() == str(sdk / ".venv")
    assert len(seen) == 1


@pytest.mark.parametrize("parts", [("bin", "pip"), ("bin", "pip.exe"), ("Scripts", "pip.exe")])
def test_get_pip_executable(tmp_path, parts):
    pip = make_pip(tmp_path, *parts)
    assert sv.get_pip_executable(str(tmp_path)) == pip


@pytest.mark.parametrize("system,expected", [("Windows", ("Scripts", "pip.exe")), ("Linux", ("bin", "pip"))])
def test_get_pip_executable_missing(monkeypatch, tmp_path, system, expected):
    monkeypatch.setattr(sv.platform, "system", lambda: system)
    assert sv.get_pip_executable(str(tmp_path)) == str(tmp_path.joinpath(*expected))


def test_install_west(sdk, monkeypatch):
    seen = []
    monkeypatch.setattr(sv.subprocess, "check_call", seen.append)
    with pytest.raises(SystemExit):
        sv.install_west(str(sdk))
    pip = make_pip(sdk, "bin", "pip")
    sv.install_west(str(sdk))
    assert seen == [[pip, "install", "-U", "west"]]


def test_install_optional_dependencies(sdk, monkeypatch, capsys):
    assert sv.install_optional_dependencies(str(sdk)) == ["pyserial", "pylink-square"]
    make_pip(sdk, "bin", "pip")

    def run(cmd, **kw):
        if cmd[-1] == "pylink-square":
            raise subprocess.CalledProcessError(1, cmd, stderr=b"ERROR: no wheel for psutil\n")
    monkeypatch.setattr(sv.subprocess, "run", run)
    assert sv.install_optional_dependencies(str(sdk)) == ["pylink-square"]
    assert "no wheel for psutil" in capsys.readouterr().out


@pytest.mark.parametrize("system,msystem,expected", [
    ("Windows", "UCRT64", "source .venv/Scripts/activate"),
    ("Windows", None, ".venv\\Scripts\\activate.bat"),
    ("Linux", None, "source .venv/bin/activate"),
])
def test_activation_command(monkeypatch, system, msystem, expected):
    monkeypatch.setattr(sv.platform, "system", lambda: system)
    if msystem:
        monkeypatch.setenv("MSYSTEM", msystem)
    else:
        monkeypatch.delenv("MSYSTEM", raising=False)
    assert sv.get_activation_command().startswith(expected)


def test_main_reports_missing_packages(sdk, monkeypatch, capsys):
    monkeypatch.setattr(sv, "create_venv", lambda: str(sdk))
    monkeypatch.setattr(sv, "install_west", lambda venv: None)
    monkeypatch.setattr(sv, "install_optional_dependencies", lambda venv: ["pyserial"])
    sv.main()
    out = capsys.readouterr().out
    assert "Setup complete" in out and "missing: pyserial" in out and "./ubx-sdk.sh" in out


@pytest.mark.parametrize("error", [subprocess.CalledProcessError(1, "pip"), OSError("disk full")])
def test_main_fails_cleanly(monkeypatch, error):
    def boom():
        raise error
    monkeypatch.setattr(sv, "create_venv", boom)
    with pytest.raises(SystemExit) as exc:
        sv.main()
    assert exc.value.code == 1


@pytest.mark.parametrize("script,matter", [("ubx_sdk.py", False), ("ubx_matter.py", True)])
def test_entry_points_call_the_launcher(monkeypatch, script, matter):
    import runpy
    import ubx
    seen = []
    monkeypatch.setattr(ubx, "main", lambda matter=False: seen.append(matter) or 0)
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(Path(sv.get_sdk_root()) / "scripts" / script), run_name="__main__")
    assert exc.value.code == 0 and seen == [matter]
