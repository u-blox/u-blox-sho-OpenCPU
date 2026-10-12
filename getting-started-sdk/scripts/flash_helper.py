#!/usr/bin/env python3
"""
Common flash utility for u-blox modules.

Supports:
- J-Link / MCU-Link (IRIS-W10)
- XDS110 through the TI SimpleLink Wi-Fi Toolbox (NORA-W50-W51)

The other targets flash through their vendor tools (west, idf.py).

Usage:
    python flash_helper.py --device RW612 --file build/zephyr.hex --jlink
    python flash_helper.py --file out/tool_settings.json --xds110
"""

import sys
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

# Windows consoles default to cp1252 and raise UnicodeEncodeError on the status glyphs below.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

try:
    from pylink import JLink
    from pylink.enums import JLinkInterfaces
    from pylink.errors import JLinkException
    HAS_PYLINK = True
except ImportError:
    HAS_PYLINK = False

    class JLinkException(Exception):
        """Stand-in so the except clause below works without pylink."""


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
            time.sleep(0.1)
            jlink.set_reset_pin_high()

            print("[OK] Flash complete!\n")
            return 0
    except (JLinkException, OSError, ValueError) as e:
        print(f"[FAIL] Flash failed: {e}\n")
        return 1


def flash_xds110(tool_settings: str, device_serial: Optional[str] = None,
                 cwd: Optional[Path] = None) -> int:
    """
    Flash through the SimpleLink Wi-Fi Toolbox programmer and an XDS110 probe.

    Args:
        tool_settings: The build's tool_settings.json, which names the images to program
        device_serial: XDS110 serial number
        cwd: Folder to run in; image paths in tool_settings.json are relative to it
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
        '--tool_settings', tool_settings,
        '--verbose'
    ]

    print("\nFlashing with XDS110...")
    try:
        result = subprocess.run(cmd, cwd=cwd)
    except (OSError, subprocess.SubprocessError) as e:
        print(f"[FAIL] Flash failed: {e}\n")
        return 1

    if result.returncode == 0:
        print("[OK] Flash complete!\n")
    return result.returncode


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Flash firmware to u-blox modules",
        epilog="""
Examples:
  python flash_helper.py --device RW612 --file build/zephyr.hex --jlink
  python flash_helper.py --file out/tool_settings.json --xds110
        """
    )

    parser.add_argument('--device', help='Target device (J-Link)')
    parser.add_argument('--file', required=True,
                        help='Firmware file (J-Link) or tool_settings.json (XDS110)')
    parser.add_argument('--address', type=lambda x: int(x, 0), default=0,
                       help='Flash address for .bin files (default: 0x0)')
    parser.add_argument('--serial', help='Debugger serial number')

    debug_group = parser.add_mutually_exclusive_group(required=True)
    debug_group.add_argument('--jlink', action='store_true', help='Use J-Link debugger')
    debug_group.add_argument('--xds110', action='store_true', help='Use XDS110 debugger')

    args = parser.parse_args()

    if args.xds110:
        return flash_xds110(args.file, args.serial, cwd=Path(args.file).parent)
    if not args.device:
        print("[FAIL] --device required for J-Link")
        return 1
    return flash_jlink(args.device, args.file, args.address, args.serial)


if __name__ == '__main__':
    sys.exit(main())
