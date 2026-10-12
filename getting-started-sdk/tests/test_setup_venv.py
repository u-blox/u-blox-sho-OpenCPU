"""Shared venv setup (scripts/setup_venv.py)."""

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
