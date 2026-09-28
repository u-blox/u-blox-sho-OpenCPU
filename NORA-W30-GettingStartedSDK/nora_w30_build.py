#!/usr/bin/env python3
"""
NORA-W30 (Realtek RTL872x) Build Driver
Automated cross-platform build orchestration for NORA-W30 Open CPU modules using Realtek RTOS SDK.

Supports: Linux (native & WSL2) | Windows (WSL2 recommended)
Note: Cygwin on Windows is complex; native Windows build not fully supported.
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional

# ============================================================================
# PLATFORM & ENVIRONMENT DETECTION
# ============================================================================

def host_kind() -> str:
    """Detect platform type: 'wsl', 'linux', or 'windows'."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Linux":
        try:
            with open("/proc/version") as f:
                content = f.read().upper()
                if "WSL" in content or "MICROSOFT" in content:
                    return "wsl"
        except:
            pass
        return "linux"
    return "linux"

def mak_path(p: str) -> str:
    """Convert path to forward slashes."""
    return str(p).replace("\\", "/")

# ============================================================================
# TOOL DETECTION
# ============================================================================

def newest(patterns: List[str]) -> Optional[str]:
    """Find newest matching path from glob patterns."""
    candidates = []
    for pattern in patterns:
        candidates.extend(Path().glob(pattern))
    if not candidates:
        return None
    candidates.sort(key=lambda p: str(p), reverse=True)
    return str(candidates[0].resolve()) if candidates else None

def detect_git() -> Optional[str]:
    """Detect git executable."""
    result = subprocess.run(["which", "git"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def detect_make() -> Optional[str]:
    """Detect make."""
    result = subprocess.run(["which", "make"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None

def detect_arm_gcc() -> Optional[str]:
    """Detect arm-none-eabi-gcc."""
    result = subprocess.run(["which", "arm-none-eabi-gcc"], capture_output=True, text=True)
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
    return Path.cwd() / f".nora_w30_build.{host_kind()}.json"

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
    current_host = host_kind()
    print(f"\n🔍 NORA-W30 Build Environment Check ({current_host})\n")
    
    if current_host == "windows":
        print("⚠️  Windows detected.")
        print("    Realtek SDK build on Windows requires WSL2 or Cygwin.")
        print("    Recommend: Use WSL2 with Ubuntu instead.\n")
        return 1
    
    tools = {
        "Python": detect_python(),
        "Git": detect_git(),
        "Make": detect_make(),
        "Arm GCC": detect_arm_gcc(),
    }
    
    all_ok = True
    for name, path in tools.items():
        status = "✅" if path else "❌"
        print(f"  {status} {name:15} {path or 'NOT FOUND'}")
        if not path:
            all_ok = False
    
    print(f"\nPlatform: {current_host}")
    print(f"Config: {config_file()}")
    
    if all_ok:
        print("\n✅ All tools detected!\n")
        return 0
    else:
        print("\n⚠️  Some tools missing. See README for setup instructions.\n")
        return 1

def cmd_clone(args) -> int:
    """Clone Realtek SDK repository."""
    print("\n📥 Cloning Realtek RTOS SDK...\n")
    
    git = detect_git()
    if not git:
        print("❌ Git not found!")
        return 1
    
    sdk_dir = Path.cwd() / "realtek-rtos-sdk"
    if sdk_dir.exists():
        print(f"ℹ️  {sdk_dir} already exists. Skipping clone.\n")
        cfg = load_config()
        cfg["sdk_path"] = str(sdk_dir)
        save_config(cfg)
        return 0
    
    # Note: URL is placeholder; adjust to actual Realtek SDK repo
    repo_url = "https://github.com/ambiot/ameba-rtos.git"  # Ameba (Realtek IoT) official repo
    
    print(f"Cloning from: {repo_url}\n")
    
    result = subprocess.run(
        [git, "clone", "--depth", "1", repo_url, str(sdk_dir)],
        cwd=Path.cwd()
    )
    
    if result.returncode == 0:
        print("\n✅ Realtek SDK cloned successfully!\n")
        cfg = load_config()
        cfg["sdk_path"] = str(sdk_dir)
        save_config(cfg)
    else:
        print("\n❌ Clone failed. Check URL and network connection.\n")
    
    return result.returncode

def cmd_build(args) -> int:
    """Build example application."""
    if not args.example:
        print("❌ Please specify an example name (e.g., 'ota')")
        return 1
    
    sdk_path = load_config().get("sdk_path")
    if not sdk_path or not Path(sdk_path).exists():
        print("❌ Realtek SDK not found. Run 'python nora_w30_build.py clone' first.")
        return 1
    
    # Realtek SDK structure varies; adjust paths as needed
    example_dir = Path(sdk_path) / "examples" / args.example
    if not example_dir.exists():
        # Try alternative structure
        example_dir = Path(sdk_path) / "project" / "realtek_amebaZ" / args.example
    
    if not example_dir.exists():
        print(f"❌ Example '{args.example}' not found.")
        return 1
    
    print(f"\n🔨 Building example: {args.example}\n")
    
    env = os.environ.copy()
    env["SDK_ROOT"] = str(sdk_path)
    
    # Typical Realtek build command
    result = subprocess.run(
        ["make", "-j"],
        cwd=example_dir,
        env=env
    )
    
    return result.returncode

def cmd_list(args) -> int:
    """List available examples."""
    sdk_path = load_config().get("sdk_path")
    if not sdk_path or not Path(sdk_path).exists():
        print("❌ Realtek SDK not found.")
        return 1
    
    examples_path = Path(sdk_path) / "examples"
    if not examples_path.exists():
        examples_path = Path(sdk_path) / "project" / "realtek_amebaZ"
    
    if not examples_path.exists():
        print("❌ Examples directory not found.")
        return 1
    
    print("\n📚 Available Examples:\n")
    for ex in sorted(examples_path.iterdir()):
        if ex.is_dir():
            makefile = ex / "Makefile"
            if makefile.exists():
                print(f"  • {ex.name}")
    print()
    return 0

def cmd_all(args) -> int:
    """Full pipeline: clone → build."""
    steps = [
        ("Clone Realtek SDK", lambda: cmd_clone(args)),
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
        description="NORA-W30 (Realtek RTL872x) Build Driver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python nora_w30_build.py doctor              # Check environment
  python nora_w30_build.py clone               # Clone Realtek SDK
  python nora_w30_build.py list                # List examples
  python nora_w30_build.py build ota           # Build example
  python nora_w30_build.py all ota             # Full pipeline

Note: Best on Linux or WSL2. Windows Cygwin is complex.
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    subparsers.add_parser("doctor", help="Verify toolchain")
    subparsers.add_parser("clone", help="Clone Realtek SDK")
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
