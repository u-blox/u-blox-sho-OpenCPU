#!/usr/bin/env python3
"""
Common flash utility for u-blox modules.

Supports:
- J-Link / MCU-Link (IRIS-W10)
- J-Link OB (NORA-B20-B21-B22, ALMA-B20-B21)
- XDS110 (NORA-W50-W51)
- ESP-IDF tools (NORA-W40)
- UART DFU (NORA-W30)

Usage:
    python flash_helper.py --device RW612 --file build/zephyr.hex --jlink
    python flash_helper.py --device CC3551E --file build/app.bin --xds110
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

# Windows consoles default to cp1252 and raise UnicodeEncodeError on the status glyphs below.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

try:
    import serial
    import serial.tools.list_ports
    HAS_PYSERIAL = True
except ImportError:
    HAS_PYSERIAL = False

try:
    from pylink import JLink
    from pylink.enums import JLinkInterfaces
    HAS_PYLINK = True
except ImportError:
    HAS_PYLINK = False


class FlashError(Exception):
    """Flash operation error."""
    pass


def find_jlink_devices():
    """Find available J-Link debuggers."""
    if not HAS_PYLINK:
        return []

    devices = []
    try:
        count = JLink.num_connected_emulators()
    except Exception as e:
        print(f"[WARNING] Could not enumerate J-Link probes: {e}")
        return []

    for i in range(count):
        try:
            jlink = JLink()
            jlink.open(devnum=i)
            devices.append({
                'index': i,
                'serial': jlink.serial_number,
                'product': f"J-Link (SN: {jlink.serial_number})"
            })
            jlink.close()
        except Exception as e:
            print(f"[WARNING] J-Link probe {i} could not be opened: {e}")
    return devices


def _find_xdsiod() -> Optional[str]:
    """Locate xdsiod, which ships inside CCS rather than on PATH."""
    found = shutil.which('xdsiod')
    if found:
        return found

    roots = [os.environ.get('CCS_INSTALL_ROOT'), 'C:/ti', '/opt/ti',
             str(Path.home() / 'ti')]
    exe = 'xdsiod.exe' if os.name == 'nt' else 'xdsiod'
    for root in roots:
        if not root or not Path(root).is_dir():
            continue
        for candidate in sorted(Path(root).glob(f"**/ccs_base/common/uscif/{exe}")):
            return str(candidate)
    return None


def find_xds110_devices():
    """Find available XDS110 debuggers."""
    xdsiod = _find_xdsiod()
    if not xdsiod:
        return []

    try:
        result = subprocess.run(
            [xdsiod, 'l'],
            capture_output=True,
            text=True,
            timeout=5
        )
    except (OSError, subprocess.SubprocessError) as e:
        print(f"[WARNING] xdsiod failed: {e}")
        return []

    if result.returncode != 0:
        return []
    return [{'product': line.strip()}
            for line in result.stdout.splitlines() if 'XDS110' in line]


def flash_jlink(device: str, firmware_file: str, address: int = 0, serial: Optional[str] = None) -> int:
    """
    Flash firmware using J-Link.

    Args:
        device: Target device (e.g., 'RW612', 'RTL8721D')
        firmware_file: Path to .hex or .bin file
        address: Flash address (for .bin files)
        serial: J-Link serial number (auto-detected if None)
    """
    if not HAS_PYLINK:
        print("[FAIL] pylink not installed. Install with: pip install pylink-square")
        return 1

    fw_path = Path(firmware_file)
    if not fw_path.exists():
        print(f"[FAIL] Firmware file not found: {firmware_file}")
        return 1

    try:
        with JLink(serial_no=serial) as jlink:
            jlink.set_tif(JLinkInterfaces.SWD)
            jlink.disable_dialog_boxes()

            print(f"\nConnecting to {device}...")
            jlink.connect(device)
            jlink.halt()

            print(f"Flashing {fw_path.name}...")
            jlink.flash_file(str(fw_path), address)

            print("Resetting...")
            jlink.set_reset_pin_low()
            import time
            time.sleep(0.1)
            jlink.set_reset_pin_high()

            print("[OK] Flash complete!\n")
            return 0
    except Exception as e:
        print(f"[FAIL] Flash failed: {e}\n")
        return 1


def flash_xds110(firmware_file: str, device_serial: Optional[str] = None) -> int:
    """
    Flash firmware using XDS110 with TI tools.

    Args:
        firmware_file: Path to firmware (tool_settings.json location)
        device_serial: XDS110 serial number
    """
    toolbox = os.environ.get('TI_TOOLBOX')
    if toolbox:
        if not Path(toolbox).exists() and not shutil.which(toolbox):
            print(f"[FAIL] TI_TOOLBOX does not point at an executable: {toolbox}")
            return 1
    else:
        toolbox = shutil.which('simplelink-wifi-toolbox')
        if not toolbox:
            print("[FAIL] SimpleLink Wi-Fi Toolbox not found.")
            print("       Install it, then set TI_TOOLBOX to its executable path.")
            return 1

    cmd = [
        toolbox,
        'programmer',
        '-i', 'XDS110',
        '-param1', device_serial or 'auto',
        'programming',
        '--tool_settings', firmware_file,
        '--verbose'
    ]

    print("\nFlashing with XDS110...")
    try:
        result = subprocess.run(cmd)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"[FAIL] Flash failed: {e}\n")
        return 1

    if result.returncode == 0:
        print("[OK] Flash complete!\n")
    return result.returncode


def flash_uart_dfu(port: str, firmware_file: str, baudrate: int = 115200) -> int:
    """
    Flash firmware using UART DFU protocol (NORA-W30 Realtek).

    Args:
        port: Serial port
        firmware_file: Path to firmware
        baudrate: Serial baud rate
    """
    if not HAS_PYSERIAL:
        print("[FAIL] pyserial not installed. Install with: pip install pyserial")
        return 1

    print(f"[WARNING] UART DFU flashing not yet implemented for {firmware_file}")
    print("   Use Realtek's flash tools directly")
    return 1


def flash_esptool(firmware_file: str, port: Optional[str] = None, baudrate: int = 460800) -> int:
    """
    Flash firmware using esptool (NORA-W40 ESP32).

    Args:
        firmware_file: Path to firmware or app.bin
        port: Serial port (auto-detected if None)
        baudrate: Flash baud rate
    """
    try:
        import esptool  # noqa: F401  availability check; esptool.py runs as a subprocess

        if port is None:
            # Auto-detect port
            if HAS_PYSERIAL:
                ports = serial.tools.list_ports.comports()
                if ports:
                    port = ports[0].device

        if not port:
            print("[FAIL] No serial port found for ESP32")
            return 1

        cmd = [
            'esptool.py',
            '--chip', 'esp32c6',
            '--port', port,
            '--baud', str(baudrate),
            'write_flash',
            '0x0', firmware_file
        ]

        print(f"\nFlashing ESP32-C6 via {port}...")
        result = subprocess.run(cmd)

        if result.returncode == 0:
            print("[OK] Flash complete!\n")
        return result.returncode
    except ImportError:
        print("[FAIL] esptool not installed. Install with: pip install esptool")
        return 1
    except Exception as e:
        print(f"[FAIL] Flash failed: {e}\n")
        return 1


def auto_detect_debugger():
    """
    Auto-detect available debugger and return type + devices.

    Returns:
        (debugger_type, devices) tuple
        debugger_type: 'jlink', 'xds110', or None
        devices: list of available devices
    """
    # Check for J-Link first
    jlink_devices = find_jlink_devices()
    if jlink_devices:
        return 'jlink', jlink_devices

    # Check for XDS110
    xds110_devices = find_xds110_devices()
    if xds110_devices:
        return 'xds110', xds110_devices

    return None, []


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Flash firmware to u-blox modules",
        epilog="""
Examples:
  python flash_helper.py --device RW612 --file build/zephyr.hex --jlink
  python flash_helper.py --device RTL8721D --file image.bin --jlink
  python flash_helper.py --file tool_settings.json --xds110
  python flash_helper.py --device esp32c6 --file app.bin --esptool
        """
    )

    parser.add_argument('--device', help='Target device')
    parser.add_argument('--file', required=True, help='Firmware file path')
    parser.add_argument('--address', type=lambda x: int(x, 0), default=0,
                       help='Flash address for .bin files (default: 0x0)')
    parser.add_argument('--serial', help='Debugger serial number')
    parser.add_argument('--port', help='Serial port for UART/esptool')
    parser.add_argument('--baudrate', type=int, default=460800,
                       help='Baud rate for UART (default: 460800)')

    # Debugger selection
    debug_group = parser.add_mutually_exclusive_group(required=True)
    debug_group.add_argument('--jlink', action='store_true', help='Use J-Link debugger')
    debug_group.add_argument('--xds110', action='store_true', help='Use XDS110 debugger')
    debug_group.add_argument('--uart-dfu', action='store_true', help='Use UART DFU (Realtek)')
    debug_group.add_argument('--esptool', action='store_true', help='Use esptool (ESP32)')
    debug_group.add_argument('--auto', action='store_true', help='Auto-detect debugger')

    args = parser.parse_args()

    # Auto-detect if requested
    if args.auto:
        debugger, devices = auto_detect_debugger()
        if not debugger:
            print("[FAIL] No debugger detected")
            return 1
        print(f"[OK] Auto-detected: {debugger}")
        if devices:
            for dev in devices:
                print(f"   {dev}")
        args.jlink = (debugger == 'jlink')
        args.xds110 = (debugger == 'xds110')

    # Flash
    try:
        if args.jlink:
            if not args.device:
                print("[FAIL] --device required for J-Link")
                return 1
            return flash_jlink(args.device, args.file, args.address, args.serial)
        elif args.xds110:
            return flash_xds110(args.file, args.serial)
        elif args.uart_dfu:
            if not args.port:
                print("[FAIL] --port required for UART DFU")
                return 1
            return flash_uart_dfu(args.port, args.file, args.baudrate)
        elif args.esptool:
            return flash_esptool(args.file, args.port, args.baudrate)
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
