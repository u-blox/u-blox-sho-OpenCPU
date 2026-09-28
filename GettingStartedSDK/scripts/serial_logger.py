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
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

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
        print("❌ pyserial not installed. Install with: pip install pyserial")
        return None
    
    ports = find_serial_ports()
    if not ports:
        print("❌ No serial ports found")
        return None
    
    # Look for u-blox specific ports
    ubx_keywords = ['ubx', 'u-blox', 'nordic', 'ti', 'uart', 'ttyusb', 'com']
    for port, desc in ports:
        desc_lower = desc.lower()
        if any(kw in desc_lower for kw in ubx_keywords):
            print(f"✅ Auto-detected: {port} - {desc}")
            return port
    
    # If no u-blox port found, use first available
    if ports:
        port, desc = ports[0]
        print(f"⚠️  Using first available: {port} - {desc}")
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
            print(f"❌ Cannot open port {port}: {e}")
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
            print("\n❌ Cannot auto-detect serial port")
            print("Available ports:")
            for p, desc in find_serial_ports():
                print(f"  {p}: {desc}")
            return 1
    
    # Validate port
    if not validate_port(port):
        return 1
    
    print(f"\n📡 Opening {port} at {baudrate} baud (Ctrl+C to exit)...")
    print("=" * 70)
    
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=1)
        print(f"✅ Connected to {port}\n")
        
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').rstrip()
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                print(f"[{timestamp}] {line}")
            else:
                time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("📴 Disconnected")
        return 0
    except serial.SerialException as e:
        print(f"\n❌ Serial error: {e}")
        return 1
    finally:
        try:
            ser.close()
        except:
            pass


def open_with_screen(port, baudrate=115200):
    """
    Fallback: Use 'screen' command (Unix/Linux/WSL only).
    """
    try:
        subprocess.run(['screen', port, str(baudrate)])
    except FileNotFoundError:
        print("❌ 'screen' command not found")
        return 1
    return 0


def open_with_putty(port, baudrate=115200):
    """
    Fallback: Use PuTTY (Windows).
    """
    try:
        # PuTTY uses different port format for COM ports
        putty_port = port.replace('COM', 'COM') if 'COM' in port else port
        subprocess.run(['putty', '-serial', putty_port, '-sercfg', f'{baudrate},8,1,N,N'])
    except FileNotFoundError:
        print("❌ PuTTY not found")
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
            print(f"❌ Invalid baudrate: {sys.argv[2]}")
            return 1
    
    if not HAS_PYSERIAL:
        print("⚠️  pyserial not available, trying fallback methods...")
        if not port:
            # Try to auto-detect with manual port listing
            print("Available serial ports (Windows):")
            os_name = sys.platform
            if os_name.startswith('win'):
                # Windows - list COM ports
                for i in range(1, 256):
                    try:
                        s = __import__('serial').Serial(f'COM{i}', timeout=0.1)
                        s.close()
                        print(f"  COM{i}")
                    except:
                        pass
            else:
                # Unix/Linux
                import glob
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
