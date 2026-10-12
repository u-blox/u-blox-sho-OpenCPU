#!/usr/bin/env python3
"""
Serial port logger utility for u-blox modules.

Usage:
    python serial_logger.py [PORT] [BAUDRATE]

Examples:
    python serial_logger.py                  # Auto-detect at 115200
    python serial_logger.py COM11            # Windows specific port
    python serial_logger.py /dev/ttyUSB0     # Linux/WSL specific port
    python serial_logger.py COM11 9600       # Specific port and baudrate
"""

import sys
import time
import subprocess
from datetime import datetime

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


def find_serial_ports():
    """
    Find available serial ports.
    Returns list of (port, description) tuples.
    """
    if not HAS_PYSERIAL:
        return []

    ports = []
    for port in serial.tools.list_ports.comports():
        ports.append((port.device, port.description))
    return ports


def auto_detect_port():
    """
    Auto-detect u-blox module serial port.
    Looks for common patterns in port names and descriptions.
    """
    if not HAS_PYSERIAL:
        print("[FAIL] pyserial not installed. Install with: pip install pyserial")
        return None

    ports = find_serial_ports()
    if not ports:
        print("[FAIL] No serial ports found")
        return None

    # Debug-probe and USB-UART bridges used on u-blox EVKs, most specific first.
    # Generic words like 'com' or 'ti' would match every Windows port.
    ubx_keywords = ['u-blox', 'ubx', 'j-link', 'jlink', 'mcu-link', 'xds110', 'nordic',
                    'cp210', 'ftdi', 'ch340', 'usb serial', 'usb-serial', 'ttyusb', 'ttyacm']
    for kw in ubx_keywords:
        for port, desc in ports:
            if kw in f"{port} {desc}".lower():
                print(f"[OK] Auto-detected: {port} - {desc}")
                return port

    # If no u-blox port found, use first available
    if ports:
        port, desc = ports[0]
        print(f"[WARNING] Using first available: {port} - {desc}")
        return port

    return None


def validate_port(port):
    """Validate that port exists and is accessible."""
    if HAS_PYSERIAL:
        try:
            s = serial.Serial(port, timeout=0.1)
            s.close()
            return True
        except (serial.SerialException, OSError) as e:
            print(f"[FAIL] Cannot open port {port}: {e}")
            return False
    return False


def open_serial_monitor(port=None, baudrate=115200):
    """
    Open serial monitor with auto-detection and platform support.

    Args:
        port: Serial port (auto-detected if None)
        baudrate: Baud rate (default 115200)
    """
    # Auto-detect port if not specified
    if port is None:
        port = auto_detect_port()
        if port is None:
            print("\n[FAIL] Cannot auto-detect serial port")
            print("Available ports:")
            for p, desc in find_serial_ports():
                print(f"  {p}: {desc}")
            return 1

    # Validate port
    if not validate_port(port):
        return 1

    print(f"\nOpening {port} at {baudrate} baud (Ctrl+C to exit)...")
    print("=" * 70)

    ser = None
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        print(f"[OK] Connected to {port}\n")

        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').rstrip()
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                print(f"[{timestamp}] {line}")
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Disconnected")
        return 0
    except serial.SerialException as e:
        print(f"\n[FAIL] Serial error: {e}")
        return 1
    finally:
        if ser is not None:
            ser.close()


def open_with_screen(port, baudrate=115200):
    """
    Fallback: Use 'screen' command (Unix/Linux/WSL only).
    """
    try:
        subprocess.run(['screen', port, str(baudrate)])
    except FileNotFoundError:
        print("[FAIL] 'screen' command not found")
        return 1
    return 0


def open_with_putty(port, baudrate=115200):
    """
    Fallback: Use PuTTY (Windows).
    """
    try:
        subprocess.run(['putty', '-serial', port, '-sercfg', f'{baudrate},8,1,N,N'])
    except FileNotFoundError:
        print("[FAIL] PuTTY not found")
        return 1
    return 0


def main():
    """Main entry point."""
    port = None
    baudrate = 115200

    # Parse arguments
    if len(sys.argv) > 1:
        port = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            baudrate = int(sys.argv[2])
        except ValueError:
            print(f"[FAIL] Invalid baudrate: {sys.argv[2]}")
            return 1

    if not HAS_PYSERIAL:
        print("[WARNING] pyserial not available, trying fallback methods...")
        if not port:
            if sys.platform.startswith('win'):
                print("Pass the COM port (see Device Manager), or install pyserial for auto-detection.")
            else:
                import glob
                print("Available serial ports:")
                for port_path in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'):
                    print(f"  {port_path}")
            return 1

        # Try screen (Unix)
        if sys.platform != 'win32':
            return open_with_screen(port, baudrate)
        else:
            return open_with_putty(port, baudrate)

    # Use pyserial
    return open_serial_monitor(port, baudrate)


if __name__ == '__main__':
    sys.exit(main())
