"""Flash and serial helpers against fake pylink, pyserial and esptool modules."""

import subprocess
import sys
import types

import pytest

import flash_helper as fh
import serial_logger as sl


class SerialException(Exception):
    pass


def fake_serial(ports=(), opens=None, lines=()):
    """A stand-in for the pyserial package. `opens` raises on Serial() when set."""
    pending = list(lines)

    class Serial:
        def __init__(self, port, **kw):
            if opens:
                raise opens
            self.port = port

        @property
        def in_waiting(self):
            if not pending:
                raise KeyboardInterrupt
            return pending[0] is not None or pending.pop(0)

        def readline(self):
            return pending.pop(0)

        def close(self):
            pass

    listing = [types.SimpleNamespace(device=d, description=desc) for d, desc in ports]
    return types.SimpleNamespace(
        Serial=Serial, SerialException=SerialException,
        tools=types.SimpleNamespace(list_ports=types.SimpleNamespace(comports=lambda: listing)))


# ---------------------------------------------------------------------------
# flash_helper: J-Link
# ---------------------------------------------------------------------------

class FakeJLink:
    log: list = []
    fail = None

    def __init__(self, serial_no=None):
        self.serial_no = serial_no

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __getattr__(self, name):
        def record(*args):
            if name == self.fail:
                raise fh.JLinkException(f"{name} failed")
            FakeJLink.log.append((name, args))
        return record


@pytest.fixture
def jlink(monkeypatch):
    FakeJLink.log = []
    FakeJLink.fail = None
    monkeypatch.setattr(fh, "HAS_PYLINK", True)
    monkeypatch.setattr(fh, "JLink", FakeJLink, raising=False)
    monkeypatch.setattr(fh, "JLinkInterfaces", types.SimpleNamespace(SWD="swd"), raising=False)
    monkeypatch.setattr(fh.time, "sleep", lambda s: None)
    return FakeJLink


def test_flash_jlink_sequence(jlink, tmp_path):
    fw = tmp_path / "zephyr.hex"
    fw.write_text("")
    assert fh.flash_jlink("RW612", str(fw), 0x1000) == 0
    names = [name for name, _ in jlink.log]
    assert names == ["set_tif", "disable_dialog_boxes", "connect", "halt", "flash_file",
                     "set_reset_pin_low", "set_reset_pin_high"]
    assert ("flash_file", (str(fw), 0x1000)) in jlink.log


def test_flash_jlink_reports_failure(jlink, tmp_path, capsys):
    fw = tmp_path / "zephyr.hex"
    fw.write_text("")
    jlink.fail = "connect"
    assert fh.flash_jlink("RW612", str(fw)) == 1
    assert "connect failed" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# flash_helper: XDS110 and CLI
# ---------------------------------------------------------------------------

def test_xds110_failure_and_os_error(monkeypatch, tmp_path, capsys):
    toolbox = tmp_path / "toolbox"
    toolbox.write_text("")
    monkeypatch.setenv("TI_TOOLBOX", str(toolbox))
    seen = []
    monkeypatch.setattr(fh.subprocess, "run",
                        lambda cmd, **kw: seen.append(kw) or subprocess.CompletedProcess(cmd, 3))
    assert fh.flash_xds110("ts.json", cwd=tmp_path) == 3
    assert seen == [{"cwd": tmp_path}]

    def boom(cmd, **kw):
        raise OSError("denied")
    monkeypatch.setattr(fh.subprocess, "run", boom)
    assert fh.flash_xds110("ts.json") == 1
    assert "denied" in capsys.readouterr().out


def test_xds110_toolbox_on_path(monkeypatch):
    monkeypatch.delenv("TI_TOOLBOX", raising=False)
    monkeypatch.setattr(fh.shutil, "which", lambda name: "/opt/ti/toolbox")
    monkeypatch.setattr(fh.subprocess, "run", lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0))
    assert fh.flash_xds110("ts.json") == 0


def test_xds110_toolbox_in_ti_folder(monkeypatch):
    monkeypatch.delenv("TI_TOOLBOX", raising=False)
    monkeypatch.setattr(fh.shutil, "which", lambda name: None)
    exe = "C:/ti/simplelink_wifi_toolbox_win_4_3_23/simplelink-wifi-toolbox.exe"
    monkeypatch.setattr(fh.target_paths, "newest", lambda patterns: fh.Path(exe))
    seen = []
    monkeypatch.setattr(fh.subprocess, "run",
                        lambda cmd, **kw: seen.append(cmd) or subprocess.CompletedProcess(cmd, 0))
    assert fh.flash_xds110("ts.json") == 0
    assert seen[0][0] == str(fh.Path(exe))
    monkeypatch.setattr(fh.target_paths, "newest", lambda patterns: None)
    assert fh.find_toolbox() is None


@pytest.fixture
def cli(monkeypatch):
    seen = {}
    monkeypatch.setattr(fh, "flash_jlink", lambda *a: seen.setdefault("jlink", a) and 0)
    monkeypatch.setattr(fh, "flash_xds110", lambda *a, **kw: seen.setdefault("xds110", (a, kw)) and 0)

    def run(*argv):
        monkeypatch.setattr(sys, "argv", ["flash_helper.py", *argv])
        return fh.main(), seen
    return run


def test_cli_dispatch(cli, tmp_path):
    assert cli("--file", "fw.bin", "--jlink", "--device", "RW612", "--address", "0x1000")[1]["jlink"] == \
        ("RW612", "fw.bin", 0x1000, None)
    settings = str(tmp_path / "tool_settings.json")
    assert cli("--file", settings, "--xds110", "--serial", "L41")[1]["xds110"] == \
        ((settings, "L41"), {"cwd": tmp_path})


# ---------------------------------------------------------------------------
# serial_logger
# ---------------------------------------------------------------------------

@pytest.fixture
def pyserial(monkeypatch):
    def use(**kw):
        fake = fake_serial(**kw)
        monkeypatch.setattr(sl, "HAS_PYSERIAL", True)
        monkeypatch.setattr(sl, "serial", fake, raising=False)
        return fake
    return use


def test_find_serial_ports(pyserial, monkeypatch):
    pyserial(ports=[("COM3", "XDS110")])
    assert sl.find_serial_ports() == [("COM3", "XDS110")]
    monkeypatch.setattr(sl, "HAS_PYSERIAL", False)
    assert sl.find_serial_ports() == []


def test_validate_port(pyserial, monkeypatch, capsys):
    pyserial()
    assert sl.validate_port("COM3")
    pyserial(opens=SerialException("access denied"))
    assert not sl.validate_port("COM3")
    assert "access denied" in capsys.readouterr().out
    monkeypatch.setattr(sl, "HAS_PYSERIAL", False)
    assert not sl.validate_port("COM3")


def test_monitor_prints_lines_until_ctrl_c(pyserial, capsys):
    pyserial(lines=[b"*** Booting ***\r\n", None, b"hello\n"])
    assert sl.open_serial_monitor("COM3", 115200) == 0
    out = capsys.readouterr().out
    assert "] *** Booting ***" in out and "] hello" in out and "Disconnected" in out


def test_monitor_without_ports(pyserial, capsys):
    pyserial()
    assert sl.open_serial_monitor() == 1
    assert "Cannot auto-detect" in capsys.readouterr().out


def test_monitor_autodetects_and_handles_open_error(pyserial, monkeypatch):
    pyserial(ports=[("COM7", "XDS110 UART")], lines=[])
    assert sl.open_serial_monitor() == 0
    pyserial(opens=SerialException("gone"))
    assert sl.open_serial_monitor("COM7") == 1


def test_monitor_serial_error_while_reading(pyserial, monkeypatch, capsys):
    fake = pyserial()
    monkeypatch.setattr(sl, "validate_port", lambda port: True)

    class Broken(fake.Serial):
        @property
        def in_waiting(self):
            raise SerialException("unplugged")
    fake.Serial = Broken
    assert sl.open_serial_monitor("COM3") == 1
    assert "unplugged" in capsys.readouterr().out


@pytest.mark.parametrize("tool,func", [("screen", sl.open_with_screen), ("putty", sl.open_with_putty)])
def test_terminal_fallbacks(monkeypatch, tool, func):
    seen = []
    monkeypatch.setattr(sl.subprocess, "run", lambda cmd: seen.append(cmd))
    assert func("COM3", 9600) == 0
    assert seen[0][0] == tool

    def missing(cmd):
        raise FileNotFoundError(cmd[0])
    monkeypatch.setattr(sl.subprocess, "run", missing)
    assert func("COM3") == 1


def test_main_uses_pyserial(monkeypatch):
    monkeypatch.setattr(sl, "HAS_PYSERIAL", True)
    monkeypatch.setattr(sl, "open_serial_monitor", lambda port, baud: (port, baud))
    monkeypatch.setattr(sys, "argv", ["serial_logger.py", "COM3", "9600"])
    assert sl.main() == ("COM3", 9600)


@pytest.mark.parametrize("platform,expected", [("linux", "screen"), ("win32", "putty")])
def test_main_without_pyserial_uses_terminal(monkeypatch, platform, expected):
    monkeypatch.setattr(sl, "HAS_PYSERIAL", False)
    monkeypatch.setattr(sl.sys, "platform", platform)
    monkeypatch.setattr(sl, "open_with_screen", lambda port, baud: "screen")
    monkeypatch.setattr(sl, "open_with_putty", lambda port, baud: "putty")
    monkeypatch.setattr(sys, "argv", ["serial_logger.py", "COM3"])
    assert sl.main() == expected


def test_main_without_pyserial_lists_ports(monkeypatch, capsys):
    monkeypatch.setattr(sl, "HAS_PYSERIAL", False)
    monkeypatch.setattr(sl.sys, "platform", "linux")
    monkeypatch.setattr("glob.glob", lambda pattern: [pattern.replace("*", "0")])
    monkeypatch.setattr(sys, "argv", ["serial_logger.py"])
    assert sl.main() == 1
    out = capsys.readouterr().out
    assert "/dev/ttyUSB0" in out and "/dev/ttyACM0" in out


def test_main_without_pyserial_hints_on_windows(monkeypatch, capsys):
    monkeypatch.setattr(sl, "HAS_PYSERIAL", False)
    monkeypatch.setattr(sl.sys, "platform", "win32")
    monkeypatch.setattr(sys, "argv", ["serial_logger.py"])
    assert sl.main() == 1
    assert "Device Manager" in capsys.readouterr().out
