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
        try:
            if pattern.startswith(("C:/", "C:\\", "/")):
                # Absolute path - check directly
                p = Path(pattern)
                if p.exists():
                    candidates.append(p)
            else:
                # Relative path - use glob
                candidates.extend(Path().glob(pattern))
        except:
            pass
    
    if not candidates:
        return None
    candidates.sort(key=lambda p: str(p), reverse=True)
    for c in candidates:
        if not exists_check or c.exists():
            return str(c.resolve())
    return None

def detect_idf() -> Optional[str]:
    """Detect ESP-IDF installation."""
    # Check config first
    cfg = load_config()
    if "idf_path" in cfg:
        idf_path = cfg["idf_path"]
        if Path(idf_path).exists():
            return idf_path
    
    # Check common locations
    patterns = [
        str(Path.cwd() / "esp-idf"),
        str(Path.home() / "esp" / "esp-idf"),
        "/opt/esp/esp-idf",
        "C:/esp/esp-idf",
    ]
    for p in patterns:
        if Path(p).exists():
            return p
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
    if host_kind() == "windows":
        patterns = [
            "C:/Program Files/make/bin/make.EXE",
            "C:/Program Files (x86)/GnuWin32/bin/make.EXE",
        ]
        result = newest(patterns)
        if result:
            return short_path(result)
    
    result = subprocess.run(["which", "make"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def detect_cmake() -> Optional[str]:
    """Detect CMake."""
    if host_kind() == "windows":
        patterns = [
            "C:/Program Files/CMake/bin/cmake.EXE",
            "C:/Program Files (x86)/CMake/bin/cmake.EXE",
        ]
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
    
    # Try git command directly (should be in PATH)
    try:
        git_cmd = ["git", "--version"]
        subprocess.run(git_cmd, capture_output=True, check=True)
    except:
        print("❌ Git not found or not in PATH!")
        return 1
    
    idf_dir = Path.cwd() / "esp-idf"
    if idf_dir.exists():
        print(f"ℹ️  {idf_dir} already exists. Skipping clone.\n")
        cfg = load_config()
        cfg["idf_path"] = str(idf_dir)
        save_config(cfg)
        return 0
    
    result = subprocess.run(
        ["git", "clone", "--depth", "1", "https://github.com/espressif/esp-idf.git"],
        cwd=Path.cwd()
    )
    
    if result.returncode == 0:
        print("\n✅ ESP-IDF cloned successfully!\n")
        cfg = load_config()
        cfg["idf_path"] = str(idf_dir)
        save_config(cfg)
    return result.returncode

def cmd_install(args) -> int:
    """Install ESP-IDF environment and dependencies."""
    print("\n🔧 Installing ESP-IDF environment...\n")
    
    idf_dir = detect_idf()
    if not idf_dir:
        print("❌ ESP-IDF not found. Run 'python nora_w40_build.py clone' first.")
        return 1
    
    idf_path = Path(idf_dir)
    platform_type = host_kind()
    
    # Determine install script based on platform
    if platform_type == "windows":
        install_script = idf_path / "install.bat"
        if not install_script.exists():
            print(f"❌ Install script not found: {install_script}")
            return 1
        print(f"Running: {install_script}\n")
        result = subprocess.run(
            [str(install_script)],
            cwd=idf_path,
            shell=True
        )
    else:  # WSL2 or Linux
        install_script = idf_path / "install.sh"
        if not install_script.exists():
            print(f"❌ Install script not found: {install_script}")
            return 1
        print(f"Running: {install_script}\n")
        # Make script executable
        os.chmod(install_script, 0o755)
        result = subprocess.run(
            [str(install_script)],
            cwd=idf_path
        )
    
    if result.returncode == 0:
        print("\n✅ ESP-IDF environment installed successfully!")
        print("\n📝 Next steps:")
        if platform_type == "windows":
            print("   • Open PowerShell in the ESP-IDF directory")
            print("   • Run: .\\export.ps1")
            print("   • Then you can build examples")
        else:
            print("   • Run: source .\\export.sh")
            print("   • Then you can build examples")
        print()
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
    
    # Use full path to idf.py
    idf_py = Path(idf_dir) / "tools" / "idf.py"
    if not idf_py.exists():
        print(f"❌ idf.py not found at {idf_py}")
        return 1
    
    result = subprocess.run(
        [sys.executable, str(idf_py), "build"],
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
    
    # Search recursively for CMakeLists.txt files
    found = False
    for cmake_file in sorted(examples_path.rglob("CMakeLists.txt")):
        example_dir = cmake_file.parent
        # Calculate relative path from examples folder
        rel_path = example_dir.relative_to(examples_path)
        # Only show directories with CMakeLists.txt (not nested cmake from components, etc)
        depth = len(rel_path.parts)
        if depth <= 2:  # Limit to /category/example level
            print(f"  • {rel_path}")
            found = True
    
    if not found:
        print("  (No examples found)")
    print()
    return 0

def cmd_all(args) -> int:
    """Full pipeline: clone → install → build."""
    steps = [
        ("Clone ESP-IDF", lambda: cmd_clone(args)),
        ("Install ESP-IDF Environment", lambda: cmd_install(args)),
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
  python nora_w40_build.py install             # Install ESP-IDF environment
  python nora_w40_build.py list                # List examples
  python nora_w40_build.py build hello_world   # Build example
  python nora_w40_build.py all hello_world     # Full pipeline
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    subparsers.add_parser("doctor", help="Verify toolchain")
    subparsers.add_parser("clone", help="Clone ESP-IDF")
    subparsers.add_parser("install", help="Install ESP-IDF environment")
    subparsers.add_parser("list", help="List examples")
    
    build_parser = subparsers.add_parser("build", help="Build example")
    build_parser.add_argument("example", help="Example name")
    
    all_parser = subparsers.add_parser("all", help="Full pipeline")
    all_parser.add_argument("example", help="Example name")
    
    args = parser.parse_args()
    
    commands = {
        "doctor": cmd_doctor,
        "clone": cmd_clone,
        "install": cmd_install,
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
