#!/usr/bin/env python3
"""
Common flash utility for u-blox modules.

Supports:
- J-Link / MCU-Link (IRIS-W10)
- J-Link Commander scripts (NORA-W30)
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
import tempfile
import time
from pathlib import Path
from typing import Optional

import target_paths

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


def pick_jlink(prefer: Optional[str] = None) -> Optional[str]:
    """Serial of the probe to use when none was given; '' when the choice is ambiguous."""
    probes = []
    for emu in JLink().connected_emulators():
        product = emu.acProduct.decode(errors="replace") if isinstance(emu.acProduct, bytes) else str(emu.acProduct)
        probes.append((str(emu.SerialNumber), product))
    if len(probes) <= 1:
        return probes[0][0] if probes else None
    matches = [p for p in probes if prefer and prefer.lower() in p[1].lower()]
    if len(matches) == 1:
        print(f"[INFO] Several probes connected; using {matches[0][1]} {matches[0][0]}.")
        return matches[0][0]
    print("[FAIL] Several J-Link probes connected. Pick one with --flash <SN>:")
    for sn, product in probes:
        print(f"       {sn}  {product}")
    return ""


def flash_jlink(device: str, firmware_file: str, address: int = 0, serial: Optional[str] = None,
                prefer: Optional[str] = None) -> int:
    """
    Flash firmware using J-Link.

    Args:
        device: Target device (e.g., 'RW612', 'RTL8721D')
        firmware_file: Path to .hex or .bin file
        address: Flash address (for .bin files)
        serial: J-Link serial number (auto-detected if None)
        prefer: Probe product name to pick when several are connected (e.g. 'MCU-Link')
    """
    if not HAS_PYLINK:
        print("[FAIL] pylink not installed. Install with: pip install pylink-square")
        return 1

    fw_path = Path(firmware_file)
    if not fw_path.exists():
        print(f"[FAIL] Firmware file not found: {firmware_file}")
        return 1

    try:
        if not serial:
            serial = pick_jlink(prefer)
            if serial == "":
                return 1
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
            # Not every probe (e.g. the EVK-IRIS-W1 MCU-Link) drives nRESET; a core reset always runs.
            jlink.reset(halt=False)

            print("[OK] Flash complete!\n")
            return 0
    except (JLinkException, OSError, ValueError) as e:
        print(f"[FAIL] Flash failed: {e}\n")
        return 1


def find_jlink_commander() -> Optional[str]:
    """SEGGER J-Link Commander: JLinkExe on Linux/macOS, JLink.exe on Windows."""
    found = shutil.which("JLinkExe") or shutil.which("JLink")
    if found:
        return found
    found = target_paths.newest([
        "C:/Program Files/SEGGER/JLink*/JLink.exe",
        "C:/Program Files (x86)/SEGGER/JLink*/JLink.exe",
        "/opt/SEGGER/JLink*/JLinkExe",
    ])
    return str(found) if found else None


def flash_jlink_script(device: str, commands: list, serial: Optional[str] = None,
                       speed: int = 2000) -> int:
    """Run J-Link Commander commands (loadfile, r, ...) against device over SWD."""
    commander = find_jlink_commander()
    if not commander:
        print("[FAIL] SEGGER J-Link software not found. Install it from "
              "https://www.segger.com/downloads/jlink/")
        return 1

    fd, script = tempfile.mkstemp(suffix=".jlink", text=True)
    with os.fdopen(fd, "w") as f:
        f.write("\n".join([*commands, "qc"]) + "\n")
    cmd = [commander, "-device", device, "-if", "SWD", "-speed", str(speed),
           "-autoconnect", "1", "-NoGui", "1", "-ExitOnError", "1"]
    if serial:
        cmd += ["-USB", str(serial)]
    cmd += ["-CommandFile", script]
    print(f"\nFlashing {device} with {commander}...")
    try:
        result = subprocess.run(cmd)
    except OSError as e:
        print(f"[FAIL] Flash failed: {e}\n")
        return 1
    finally:
        os.unlink(script)

    if result.returncode == 0:
        print("[OK] Flash complete!\n")
    return result.returncode


def find_toolbox() -> Optional[str]:
    """The Wi-Fi Toolbox in TI's default install folders, which are not on PATH."""
    found = target_paths.newest([
        "C:/ti/simplelink_wifi_toolbox*/simplelink-wifi-toolbox.exe",
        "~/ti/simplelink_wifi_toolbox*/simplelink-wifi-toolbox",
        "/opt/ti/simplelink_wifi_toolbox*/simplelink-wifi-toolbox",
    ])
    return str(found) if found else None


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
        toolbox = shutil.which('simplelink-wifi-toolbox') or find_toolbox()
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
