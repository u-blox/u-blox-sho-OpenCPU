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
    connected = 2
    broken: set = set()
    fail = None

    def __init__(self, serial_no=None):
        self.serial_number = 1000

    @classmethod
    def num_connected_emulators(cls):
        if isinstance(cls.connected, Exception):
            raise cls.connected
        return cls.connected

    def open(self, devnum):
        if devnum in self.broken:
            raise RuntimeError("busy")
        self.serial_number = 1000 + devnum

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __getattr__(self, name):
        def record(*args):
            if name == self.fail:
                raise RuntimeError(f"{name} failed")
            FakeJLink.log.append((name, args))
        return record


@pytest.fixture
def jlink(monkeypatch):
    FakeJLink.log = []
    FakeJLink.connected = 2
    FakeJLink.broken = set()
    FakeJLink.fail = None
    monkeypatch.setattr(fh, "HAS_PYLINK", True)
    monkeypatch.setattr(fh, "JLink", FakeJLink, raising=False)
    monkeypatch.setattr(fh, "JLinkInterfaces", types.SimpleNamespace(SWD="swd"), raising=False)
    monkeypatch.setattr("time.sleep", lambda s: None)
    return FakeJLink


def test_find_jlink_devices_lists_every_probe(jlink, capsys):
    jlink.broken = {1}
    assert fh.find_jlink_devices() == [{"index": 0, "serial": 1000, "product": "J-Link (SN: 1000)"}]
    assert "probe 1 could not be opened" in capsys.readouterr().out


def test_find_jlink_devices_enumeration_error(jlink, capsys):
    jlink.connected = RuntimeError("no DLL")
    assert fh.find_jlink_devices() == []
    assert "no DLL" in capsys.readouterr().out


def test_find_jlink_devices_without_pylink(monkeypatch):
    monkeypatch.setattr(fh, "HAS_PYLINK", False)
    assert fh.find_jlink_devices() == []


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
# flash_helper: XDS110, UART, esptool, auto-detect, CLI
# ---------------------------------------------------------------------------

def test_xds110_failure_and_os_error(monkeypatch, tmp_path, capsys):
    toolbox = tmp_path / "toolbox"
    toolbox.write_text("")
    monkeypatch.setenv("TI_TOOLBOX", str(toolbox))
    monkeypatch.setattr(fh.subprocess, "run", lambda cmd, **kw: subprocess.CompletedProcess(cmd, 3))
    assert fh.flash_xds110("ts.json") == 3

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


def test_find_xdsiod_on_path_and_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(fh.shutil, "which", lambda name: "/usr/bin/xdsiod")
    assert fh._find_xdsiod() == "/usr/bin/xdsiod"
    monkeypatch.setattr(fh.shutil, "which", lambda name: None)
    monkeypatch.setenv("CCS_INSTALL_ROOT", str(tmp_path))
    monkeypatch.setattr(fh.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(fh.Path, "is_dir", lambda self: self == tmp_path)
    assert fh._find_xdsiod() is None


def test_xds110_device_listing_errors(monkeypatch, capsys):
    monkeypatch.setattr(fh, "_find_xdsiod", lambda: None)
    assert fh.find_xds110_devices() == []
    monkeypatch.setattr(fh, "_find_xdsiod", lambda: "xdsiod")
    monkeypatch.setattr(fh.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1, "", ""))
    assert fh.find_xds110_devices() == []

    def timeout(*a, **k):
        raise subprocess.TimeoutExpired("xdsiod", 5)
    monkeypatch.setattr(fh.subprocess, "run", timeout)
    assert fh.find_xds110_devices() == []
    assert "xdsiod failed" in capsys.readouterr().out


def test_uart_dfu_needs_pyserial(monkeypatch):
    monkeypatch.setattr(fh, "HAS_PYSERIAL", False)
    assert fh.flash_uart_dfu("COM3", "image.bin") == 1


@pytest.fixture
def esptool(monkeypatch):
    monkeypatch.setitem(sys.modules, "esptool", types.ModuleType("esptool"))
    seen = []
    monkeypatch.setattr(fh.subprocess, "run",
                        lambda cmd, **kw: seen.append(cmd) or subprocess.CompletedProcess(cmd, 0))
    return seen


def test_esptool_autodetects_port(monkeypatch, esptool):
    monkeypatch.setattr(fh, "HAS_PYSERIAL", True)
    monkeypatch.setattr(fh, "serial", fake_serial([("COM5", "CP210x")]), raising=False)
    assert fh.flash_esptool("app.bin") == 0
    assert esptool[0] == ["esptool.py", "--chip", "esp32c6", "--port", "COM5", "--baud", "460800",
                          "write_flash", "0x0", "app.bin"]


def test_esptool_without_port(monkeypatch, esptool, capsys):
    monkeypatch.setattr(fh, "HAS_PYSERIAL", False)
    assert fh.flash_esptool("app.bin") == 1
    assert "No serial port" in capsys.readouterr().out


def test_esptool_run_error(monkeypatch, esptool, capsys):
    def boom(cmd, **kw):
        raise OSError("no esptool.py")
    monkeypatch.setattr(fh.subprocess, "run", boom)
    assert fh.flash_esptool("app.bin", "COM5") == 1
    assert "no esptool.py" in capsys.readouterr().out


def test_esptool_not_installed(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "esptool", None)
    assert fh.flash_esptool("app.bin", "COM5") == 1
    assert "esptool not installed" in capsys.readouterr().out


@pytest.mark.parametrize("jlink_devs,xds_devs,expected", [
    ([{"index": 0}], [], "jlink"),
    ([], [{"product": "XDS110"}], "xds110"),
])
def test_auto_detect_debugger(monkeypatch, jlink_devs, xds_devs, expected):
    monkeypatch.setattr(fh, "find_jlink_devices", lambda: jlink_devs)
    monkeypatch.setattr(fh, "find_xds110_devices", lambda: xds_devs)
    assert fh.auto_detect_debugger()[0] == expected


@pytest.fixture
def cli(monkeypatch):
    seen = {}
    for name in ("flash_jlink", "flash_xds110", "flash_uart_dfu", "flash_esptool"):
        monkeypatch.setattr(fh, name, lambda *a, _n=name: seen.setdefault(_n, a) and 0)

    def run(*argv):
        monkeypatch.setattr(sys, "argv", ["flash_helper.py", "--file", "fw.bin", *argv])
        return fh.main(), seen
    return run


def test_cli_dispatch(cli):
    assert cli("--jlink", "--device", "RW612", "--address", "0x1000")[1]["flash_jlink"] == \
        ("RW612", "fw.bin", 0x1000, None)
    assert cli("--xds110", "--serial", "L41")[1]["flash_xds110"] == ("fw.bin", "L41")
    assert cli("--uart-dfu", "--port", "COM3")[1]["flash_uart_dfu"] == ("COM3", "fw.bin", 460800)
    assert cli("--esptool", "--port", "COM4")[1]["flash_esptool"] == ("fw.bin", "COM4", 460800)


def test_cli_uart_dfu_needs_port(cli, capsys):
    assert cli("--uart-dfu")[0] == 1
    assert "--port required" in capsys.readouterr().out


def test_cli_auto(cli, monkeypatch, capsys):
    monkeypatch.setattr(fh, "auto_detect_debugger", lambda: (None, []))
    assert cli("--auto")[0] == 1
    monkeypatch.setattr(fh, "auto_detect_debugger", lambda: ("xds110", [{"product": "XDS110"}]))
    rc, seen = cli("--auto")
    assert rc == 0 and "flash_xds110" in seen
    assert "Auto-detected: xds110" in capsys.readouterr().out


def test_cli_reports_unexpected_errors(monkeypatch, capsys):
    def boom(*a):
        raise ValueError("bad file")
    monkeypatch.setattr(fh, "flash_xds110", boom)
    monkeypatch.setattr(sys, "argv", ["flash_helper.py", "--file", "fw.bin", "--xds110"])
    assert fh.main() == 1
    assert "bad file" in capsys.readouterr().out


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


def test_main_without_pyserial_probes_com_ports(monkeypatch, capsys):
    monkeypatch.setattr(sl, "HAS_PYSERIAL", False)
    monkeypatch.setattr(sl.sys, "platform", "win32")
    probe = types.ModuleType("serial")

    def Serial(port, timeout):
        if port != "COM4":
            raise OSError(port)
        return types.SimpleNamespace(close=lambda: None)
    probe.Serial = Serial
    monkeypatch.setitem(sys.modules, "serial", probe)
    monkeypatch.setattr(sys, "argv", ["serial_logger.py"])
    assert sl.main() == 1
    assert "  COM4\n" in capsys.readouterr().out
