#!/usr/bin/env python3
"""
NORA-W40 (ESP32-S3) Build Driver
Automated cross-platform build orchestration for NORA-W40 Open CPU modules using ESP-IDF.

Supports: Windows, WSL2, Linux
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================================
# PLATFORM & ENVIRONMENT DETECTION
# ============================================================================

def host_kind() -> str:
    """Detect platform type: 'windows', 'wsl', or 'linux'."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Linux":
        # Check if running under WSL
        try:
            with open("/proc/version") as f:
                if "WSL" in f.read().upper() or "microsoft" in f.read().lower():
                    return "wsl"
        except:
            pass
        return "linux"
    return "linux"

def short_path(value: str) -> str:
    """Convert Windows path to 8.3 short form (no spaces)."""
    if host_kind() != "windows":
        return value
    try:
        import ctypes
        GetShortPathName = ctypes.windll.kernel32.GetShortPathNameW
        length = GetShortPathName(value, None, 0)
        buf = ctypes.create_unicode_buffer(length)
        GetShortPathName(value, buf, length)
        return buf.value
    except:
        return value

def mak_path(p: str) -> str:
    """Convert path to forward slashes."""
    return str(p).replace("\\", "/")

# ============================================================================
# TOOL DETECTION
# ============================================================================

def newest(patterns: List[str], exists_check: bool = True) -> Optional[str]:
    """Find newest matching path from glob patterns."""
    candidates = []
    for pattern in patterns:
        candidates.extend(Path().glob(pattern))
    if not candidates:
        return None
    candidates.sort(key=lambda p: str(p), reverse=True)
    for c in candidates:
        if not exists_check or c.exists():
            return str(c.resolve())
    return None

def detect_idf() -> Optional[str]:
    """Detect ESP-IDF installation."""
    patterns = [
        str(Path.home() / "esp" / "esp-idf"),
        "/opt/esp/esp-idf",
        "C:/esp/esp-idf",
        "C:/Users/*/esp/esp-idf",
    ]
    for p in patterns:
        expanded = os.path.expanduser(p)
        if Path(expanded).exists():
            return expanded
    return None

def detect_git() -> Optional[str]:
    """Detect git executable."""
    if host_kind() == "windows":
        patterns = [
            "C:/Program Files/Git/bin/git.EXE",
            "C:/Program Files (x86)/Git/bin/git.EXE",
        ]
        result = newest(patterns)
        if result:
            return short_path(result)
    
    result = subprocess.run(["which", "git"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def detect_make() -> Optional[str]:
    """Detect make/gmake."""
    result = subprocess.run(["which", "make"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    
    if host_kind() == "windows":
        patterns = ["C:/Program Files/make/bin/make.EXE"]
        return newest(patterns)
    return None

def detect_cmake() -> Optional[str]:
    """Detect CMake."""
    if host_kind() == "windows":
        patterns = ["C:/Program Files/CMake/bin/cmake.EXE"]
        result = newest(patterns)
        if result:
            return short_path(result)
    
    result = subprocess.run(["which", "cmake"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def detect_python() -> Optional[str]:
    """Detect Python 3."""
    result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        return sys.executable
    return None

# ============================================================================
# CONFIGURATION CACHE
# ============================================================================

def config_file() -> Path:
    """Get per-platform config file path."""
    return Path.cwd() / f".nora_w40_build.{host_kind()}.json"

def load_config() -> Dict:
    """Load cached configuration."""
    cfg_path = config_file()
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text())
        except:
            pass
    return {}

def save_config(cfg: Dict) -> None:
    """Save configuration to cache."""
    config_file().write_text(json.dumps(cfg, indent=2))

# ============================================================================
# COMMANDS
# ============================================================================

def cmd_doctor(args) -> int:
    """Verify toolchain availability."""
    print("\n🔍 NORA-W40 Build Environment Check\n")
    
    tools = {
        "Python": detect_python(),
        "Git": detect_git(),
        "CMake": detect_cmake(),
        "Make": detect_make(),
        "ESP-IDF": detect_idf(),
    }
    
    all_ok = True
    for name, path in tools.items():
        status = "✅" if path else "❌"
        print(f"  {status} {name:15} {path or 'NOT FOUND'}")
        if not path:
            all_ok = False
    
    print(f"\nPlatform: {host_kind()}")
    print(f"Config: {config_file()}")
    
    if all_ok:
        print("\n✅ All tools detected!\n")
        return 0
    else:
        print("\n⚠️  Some tools missing. See README for setup instructions.\n")
        return 1

def cmd_clone(args) -> int:
    """Clone ESP-IDF repository."""
    print("\n📥 Cloning ESP-IDF...\n")
    
    git = detect_git()
    if not git:
        print("❌ Git not found!")
        return 1
    
    idf_dir = Path.cwd() / "esp-idf"
    if idf_dir.exists():
        print(f"ℹ️  {idf_dir} already exists. Skipping clone.\n")
        return 0
    
    result = subprocess.run(
        [git, "clone", "--depth", "1", "https://github.com/espressif/esp-idf.git"],
        cwd=Path.cwd()
    )
    
    if result.returncode == 0:
        print("\n✅ ESP-IDF cloned successfully!\n")
        cfg = load_config()
        cfg["idf_path"] = str(idf_dir)
        save_config(cfg)
    return result.returncode

def cmd_build(args) -> int:
    """Build example application."""
    if not args.example:
        print("❌ Please specify an example name (e.g., 'hello_world')")
        return 1
    
    idf_dir = detect_idf()
    if not idf_dir:
        print("❌ ESP-IDF not found. Run 'python nora_w40_build.py clone' first.")
        return 1
    
    example_path = Path(idf_dir) / "examples" / args.example
    if not example_path.exists():
        print(f"❌ Example '{args.example}' not found at {example_path}")
        return 1
    
    print(f"\n🔨 Building example: {args.example}\n")
    
    # Set IDF_PATH and call idf.py
    env = os.environ.copy()
    env["IDF_PATH"] = idf_dir
    
    result = subprocess.run(
        [sys.executable, "idf.py", "build"],
        cwd=example_path,
        env=env
    )
    
    return result.returncode

def cmd_list(args) -> int:
    """List available examples."""
    idf_dir = detect_idf()
    if not idf_dir:
        print("❌ ESP-IDF not found.")
        return 1
    
    examples_path = Path(idf_dir) / "examples"
    if not examples_path.exists():
        print("❌ Examples directory not found.")
        return 1
    
    print("\n📚 Available Examples:\n")
    for ex in sorted(examples_path.iterdir()):
        if ex.is_dir():
            cmakelists = ex / "CMakeLists.txt"
            if cmakelists.exists():
                print(f"  • {ex.name}")
    print()
    return 0

def cmd_all(args) -> int:
    """Full pipeline: clone → build."""
    steps = [
        ("Clone ESP-IDF", lambda: cmd_clone(args)),
        ("Build Example", lambda: cmd_build(args)),
    ]
    
    for name, step in steps:
        print(f"\n{'='*50}\n{name}\n{'='*50}")
        if step() != 0:
            print(f"\n❌ {name} failed!")
            return 1
    
    print("\n✅ Pipeline complete!\n")
    return 0

# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="NORA-W40 (ESP32-S3) Build Driver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python nora_w40_build.py doctor              # Check environment
  python nora_w40_build.py clone               # Clone ESP-IDF
  python nora_w40_build.py list                # List examples
  python nora_w40_build.py build hello_world   # Build example
  python nora_w40_build.py all hello_world     # Full pipeline
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    subparsers.add_parser("doctor", help="Verify toolchain")
    subparsers.add_parser("clone", help="Clone ESP-IDF")
    subparsers.add_parser("list", help="List examples")
    
    build_parser = subparsers.add_parser("build", help="Build example")
    build_parser.add_argument("example", help="Example name")
    
    all_parser = subparsers.add_parser("all", help="Full pipeline")
    all_parser.add_argument("example", help="Example name")
    
    args = parser.parse_args()
    
    commands = {
        "doctor": cmd_doctor,
        "clone": cmd_clone,
        "list": cmd_list,
        "build": cmd_build,
        "all": cmd_all,
    }
    
    if not args.command:
        parser.print_help()
        return 0
    
    return commands[args.command](args)

if __name__ == "__main__":
    sys.exit(main())
