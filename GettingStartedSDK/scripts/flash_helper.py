#!/usr/bin/env python3
"""
Common flash utility for u-blox modules.

Supports:
- J-Link (IRIS-W10, IRIS-W16x, NORA-W36x)
- XDS110 (NORA-W56x)
- ESP-IDF tools (NORA-W40)
- UART DFU (NORA-W30)

Usage:
    python flash_helper.py --device RW612 --file build/zephyr.hex --jlink
    python flash_helper.py --device CC3520SF --file build/app.bin --xds110
"""

import sys
import os
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
    
    try:
        from pylink import JLink
        # Get number of connected J-Link devices
        count = JLink.num_connected_emulators()
        devices = []
        for i in range(count):
            try:
                jlink = JLink()
                info = jlink.open(devnum=i)
                devices.append({
                    'index': i,
                    'serial': jlink.serial_number,
                    'product': f"J-Link (SN: {jlink.serial_number})"
                })
                jlink.close()
            except:
                pass
        return devices
    except:
        return []


def find_xds110_devices():
    """Find available XDS110 debuggers."""
    # XDS110 detection typically requires TI tools
    # For now, return placeholder
    try:
        result = subprocess.run(
            ['xdsiod', 'l'], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Parse XDS110 list
            devices = []
            for line in result.stdout.split('\n'):
                if 'XDS110' in line:
                    devices.append({'product': line.strip()})
            return devices
    except:
        pass
    return []


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
        print("❌ pylink not installed. Install with: pip install pylink-square")
        return 1
    
    fw_path = Path(firmware_file)
    if not fw_path.exists():
        print(f"❌ Firmware file not found: {firmware_file}")
        return 1
    
    try:
        with JLink(serial_no=serial) as jlink:
            jlink.set_tif(JLinkInterfaces.SWD)
            jlink.disable_dialog_boxes()
            
            print(f"\n🔗 Connecting to {device}...")
            jlink.connect(device)
            jlink.halt()
            
            print(f"📝 Flashing {fw_path.name}...")
            jlink.flash_file(str(fw_path), address)
            
            print("🔄 Resetting...")
            jlink.set_reset_pin_low()
            import time
            time.sleep(0.1)
            jlink.set_reset_pin_high()
            
            print("✅ Flash complete!\n")
            return 0
    except Exception as e:
        print(f"❌ Flash failed: {e}\n")
        return 1


def flash_xds110(firmware_file: str, device_serial: Optional[str] = None) -> int:
    """
    Flash firmware using XDS110 with TI tools.
    
    Args:
        firmware_file: Path to firmware (tool_settings.json location)
        device_serial: XDS110 serial number
    """
    try:
        # Use TI's simplelink-wifi-toolbox for flashing
        toolbox = os.environ.get('TI_TOOLBOX', 'simplelink-wifi-toolbox')
        
        cmd = [
            toolbox,
            'programmer',
            '-i', 'XDS110',
            'programming',
            '--tool_settings', firmware_file,
            '--verbose'
        ]
        
        if device_serial:
            cmd.insert(3, device_serial)
        
        print(f"\n🔗 Flashing with XDS110...")
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print("✅ Flash complete!\n")
        return result.returncode
    except Exception as e:
        print(f"❌ Flash failed: {e}\n")
        return 1


def flash_uart_dfu(port: str, firmware_file: str, baudrate: int = 115200) -> int:
    """
    Flash firmware using UART DFU protocol (NORA-W30 Realtek).
    
    Args:
        port: Serial port
        firmware_file: Path to firmware
        baudrate: Serial baud rate
    """
    if not HAS_PYSERIAL:
        print("❌ pyserial not installed. Install with: pip install pyserial")
        return 1
    
    print(f"⚠️  UART DFU flashing not yet implemented for {firmware_file}")
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
        import esptool
        
        if port is None:
            # Auto-detect port
            if HAS_PYSERIAL:
                ports = serial.tools.list_ports.comports()
                if ports:
                    port = ports[0].device
        
        if not port:
            print("❌ No serial port found for ESP32")
            return 1
        
        cmd = [
            'esptool.py',
            '--chip', 'esp32c6',
            '--port', port,
            '--baud', str(baudrate),
            'write_flash',
            '0x0', firmware_file
        ]
        
        print(f"\n🔗 Flashing ESP32-C6 via {port}...")
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print("✅ Flash complete!\n")
        return result.returncode
    except ImportError:
        print("❌ esptool not installed. Install with: pip install esptool")
        return 1
    except Exception as e:
        print(f"❌ Flash failed: {e}\n")
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
            print("❌ No debugger detected")
            return 1
        print(f"✅ Auto-detected: {debugger}")
        if devices:
            for dev in devices:
                print(f"   {dev}")
        args.jlink = (debugger == 'jlink')
        args.xds110 = (debugger == 'xds110')
    
    # Flash
    try:
        if args.jlink:
            if not args.device:
                print("❌ --device required for J-Link")
                return 1
            return flash_jlink(args.device, args.file, args.address, args.serial)
        elif args.xds110:
            return flash_xds110(args.file, args.serial)
        elif args.uart_dfu:
            if not args.port:
                print("❌ --port required for UART DFU")
                return 1
            return flash_uart_dfu(args.port, args.file, args.baudrate)
        elif args.esptool:
            return flash_esptool(args.file, args.port, args.baudrate)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
