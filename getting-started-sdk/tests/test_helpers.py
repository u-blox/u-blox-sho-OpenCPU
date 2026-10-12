"""Flash and serial helpers (scripts/flash_helper.py, scripts/serial_logger.py)."""

import subprocess
import sys

import pytest

import flash_helper as fh
import serial_logger as sl


# ---------------------------------------------------------------------------
# flash_helper
# ---------------------------------------------------------------------------

def test_jlink_needs_pylink(monkeypatch, capsys):
    monkeypatch.setattr(fh, "HAS_PYLINK", False)
    assert fh.flash_jlink("RW612", "x.hex") == 1
    assert "pylink not installed" in capsys.readouterr().out


def test_jlink_missing_file(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(fh, "HAS_PYLINK", True)
    assert fh.flash_jlink("RW612", str(tmp_path / "missing.hex")) == 1
    assert "not found" in capsys.readouterr().out


def test_xds110_without_toolbox(monkeypatch, capsys):
    monkeypatch.delenv("TI_TOOLBOX", raising=False)
    monkeypatch.setattr(fh.shutil, "which", lambda name: None)
    assert fh.flash_xds110("tool_settings.json") == 1
    assert "Toolbox not found" in capsys.readouterr().out


def test_xds110_bad_toolbox_env(monkeypatch, tmp_path):
    monkeypatch.setenv("TI_TOOLBOX", str(tmp_path / "nope"))
    monkeypatch.setattr(fh.shutil, "which", lambda name: None)
    assert fh.flash_xds110("tool_settings.json") == 1


@pytest.mark.parametrize("serial,param", [(None, "auto"), ("L4100123", "L4100123")])
def test_xds110_command(monkeypatch, tmp_path, serial, param):
    toolbox = tmp_path / "simplelink-wifi-toolbox"
    toolbox.write_text("")
    monkeypatch.setenv("TI_TOOLBOX", str(toolbox))
    seen = {}
    monkeypatch.setattr(fh.subprocess, "run",
                        lambda cmd, **kw: seen.setdefault("cmd", cmd) and subprocess.CompletedProcess(cmd, 0))
    assert fh.flash_xds110("out/tool_settings.json", serial) == 0
    assert seen["cmd"] == [str(toolbox), "programmer", "-i", "XDS110", "-param1", param,
                           "programming", "--tool_settings", "out/tool_settings.json", "--verbose"]


def test_cli_requires_a_debugger(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["flash_helper.py", "--file", "x.bin"])
    with pytest.raises(SystemExit) as exc:
        fh.main()
    assert exc.value.code == 2


def test_cli_jlink_needs_device(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["flash_helper.py", "--file", "x.bin", "--jlink"])
    assert fh.main() == 1
    assert "--device required" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# serial_logger
# ---------------------------------------------------------------------------

@pytest.fixture
def ports(monkeypatch):
    def use(listing):
        monkeypatch.setattr(sl, "HAS_PYSERIAL", True)
        monkeypatch.setattr(sl, "find_serial_ports", lambda: listing)
    return use


def test_auto_detect_prefers_debug_probe(ports):
    ports([("COM3", "Intel(R) Active Management Technology - SOL (COM3)"),
           ("COM7", "XDS110 Class Application/User UART (COM7)")])
    assert sl.auto_detect_port() == "COM7"


def test_auto_detect_jlink_over_generic(ports):
    ports([("COM1", "Communications Port (COM1)"), ("COM9", "JLink CDC UART Port (COM9)")])
    assert sl.auto_detect_port() == "COM9"


def test_auto_detect_linux_usb(ports):
    ports([("/dev/ttyS0", "ttyS0"), ("/dev/ttyACM0", "J-Link - CDC")])
    assert sl.auto_detect_port() == "/dev/ttyACM0"


def test_auto_detect_falls_back_to_first(ports, capsys):
    ports([("COM1", "Communications Port (COM1)")])
    assert sl.auto_detect_port() == "COM1"
    assert "[WARNING]" in capsys.readouterr().out


def test_auto_detect_no_ports(ports):
    ports([])
    assert sl.auto_detect_port() is None


def test_auto_detect_without_pyserial(monkeypatch):
    monkeypatch.setattr(sl, "HAS_PYSERIAL", False)
    assert sl.auto_detect_port() is None


def test_invalid_baudrate(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["serial_logger.py", "COM3", "fast"])
    assert sl.main() == 1
    assert "Invalid baudrate" in capsys.readouterr().out
