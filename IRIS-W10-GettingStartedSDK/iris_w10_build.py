#!/usr/bin/env python3
"""
IRIS-W10 (NXP RW612/RW610) Build Driver
Automated cross-platform build orchestration for IRIS-W10 Open CPU modules using the
MCUXpresso SDK (west/CMake/Ninja flavour).

Supports: Windows, WSL2, Linux
"""

import os
import sys
import json
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, List, Optional

# Windows consoles default to cp1252 and raise UnicodeEncodeError on the status glyphs below.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

# ============================================================================
# CONSTANTS
# ============================================================================

MANIFEST_URL = "https://github.com/nxp-mcuxpresso/mcuxsdk-manifests.git"
WORKSPACE_NAME = "mcuxpresso-sdk"

# IRIS-W10 uses NXP RW612 (with Thread) or RW610 (BLE + Wi-Fi only); rdrw612bga is the matching MCUXpresso board target.
DEFAULT_BOARD = "rdrw612bga"
DEFAULT_TOOLCHAIN = "armgcc"
DEFAULT_EXAMPLE = "examples/demo_apps/hello_world"

# ============================================================================
# PLATFORM & ENVIRONMENT DETECTION
# ============================================================================

def is_venv_active() -> bool:
    """Check if running inside a virtual environment."""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

def host_kind() -> str:
    """Detect platform type: 'windows', 'wsl', or 'linux'."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Linux":
        try:
            text = Path("/proc/version").read_text(encoding="utf-8", errors="replace")
            if "microsoft" in text.lower():
                return "wsl"
        except OSError:
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
        return buf.value or value
    except Exception:
        return value

# ============================================================================
# TOOL DETECTION
# ============================================================================

def newest(patterns: List[str]) -> Optional[str]:
    """Find newest matching path from glob patterns."""
    candidates = []
    for pattern in patterns:
        try:
            if pattern.startswith(("C:/", "C:\\", "/")):
                p = Path(pattern)
                if p.exists():
                    candidates.append(p)
            else:
                candidates.extend(Path().glob(pattern))
        except Exception:
            pass

    if not candidates:
        return None
    candidates.sort(key=lambda p: str(p), reverse=True)
    for c in candidates:
        if c.exists():
            return str(c.resolve())
    return None

def which(name: str) -> Optional[str]:
    """Locate an executable on PATH."""
    return shutil.which(name)

def detect_python() -> Optional[str]:
    """Detect Python, preferring one that has pip installed."""
    # Check current interpreter first
    if _python_has_pip(sys.executable):
        return sys.executable
    
    # On Windows with msys64, fall back to AppData Python or system Python
    if host_kind() == "windows":
        candidates = [
            "C:/Users/" + os.environ.get("USERNAME", "").split("/")[-1] + "/AppData/Local/Python/bin/python.exe",
            "C:/Program Files/Python3*/python.exe",
            which("python3") or "",
            which("python") or "",
        ]
        for candidate in candidates:
            if candidate and Path(candidate).exists():
                exe = str(Path(candidate).resolve())
                if _python_has_pip(exe):
                    return exe
    
    # Fallback: return current interpreter
    return sys.executable

def _python_has_pip(python_exe: str) -> bool:
    """Check if a Python executable has pip."""
    try:
        result = subprocess.run(
            [python_exe, "-m", "pip", "--version"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False

def detect_git() -> Optional[str]:
    return which("git")

def detect_west() -> Optional[str]:
    """west is a pip console script; fall back to 'python -m west'."""
    found = which("west")
    if found:
        return found
    try:
        r = subprocess.run([sys.executable, "-m", "west", "--version"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return f"{sys.executable} -m west"
    except Exception:
        pass
    return None

def west_cmd() -> Optional[List[str]]:
    """Argv prefix for invoking west."""
    found = which("west")
    if found:
        return [found]
    try:
        r = subprocess.run([sys.executable, "-m", "west", "--version"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return [sys.executable, "-m", "west"]
    except Exception:
        pass
    return None

def detect_cmake() -> Optional[str]:
    if host_kind() == "windows":
        result = newest([
            "C:/Program Files/CMake/bin/cmake.EXE",
            "C:/Program Files (x86)/CMake/bin/cmake.EXE",
        ])
        if result:
            return short_path(result)
    return which("cmake")

def detect_ninja() -> Optional[str]:
    if host_kind() == "windows":
        result = newest([
            "C:/Program Files/Ninja/ninja.EXE",
            "C:/ninja/ninja.EXE",
        ])
        if result:
            return short_path(result)
    return which("ninja")

def detect_arm_gcc() -> Optional[str]:
    """Locate arm-none-eabi-gcc, preferring the ARMGCC_DIR the SDK build system uses."""
    armgcc_dir = os.environ.get("ARMGCC_DIR")
    if armgcc_dir:
        exe = "arm-none-eabi-gcc" + (".exe" if host_kind() == "windows" else "")
        candidate = Path(armgcc_dir) / "bin" / exe
        if candidate.exists():
            return short_path(str(candidate))

    if host_kind() == "windows":
        result = newest([
            "C:/Program Files (x86)/Arm GNU Toolchain*/*/bin/arm-none-eabi-gcc.exe",
            "C:/Program Files/Arm GNU Toolchain*/*/bin/arm-none-eabi-gcc.exe",
            "C:/armgcc/bin/arm-none-eabi-gcc.exe",
        ])
        if result:
            return short_path(result)
    return which("arm-none-eabi-gcc")

def detect_workspace() -> Optional[str]:
    """Locate the west workspace (the directory holding .west/)."""
    cfg = load_config()
    if "workspace" in cfg and (Path(cfg["workspace"]) / ".west").exists():
        return cfg["workspace"]

    for candidate in (Path.cwd() / WORKSPACE_NAME, Path.cwd()):
        if (candidate / ".west").exists():
            return str(candidate)
    return None

def examples_root(workspace: str) -> Optional[Path]:
    """Examples live under mcuxsdk/examples in the multi-repo layout."""
    for rel in ("mcuxsdk/examples", "examples"):
        p = Path(workspace) / rel
        if p.is_dir():
            return p
    return None

# ============================================================================
# CONFIGURATION CACHE
# ============================================================================

def config_file() -> Path:
    """Get per-platform config file path."""
    return Path.cwd() / f".iris_w10_build.{host_kind()}.json"

def load_config() -> Dict:
    cfg_path = config_file()
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}

def save_config(cfg: Dict) -> None:
    config_file().write_text(json.dumps(cfg, indent=2), encoding="utf-8")

# ============================================================================
# COMMANDS
# ============================================================================

def cmd_doctor(args) -> int:
    """Verify toolchain availability."""
    print("\n🔍 IRIS-W10 Build Environment Check\n")

    tools = {
        "Python": detect_python(),
        "Git": detect_git(),
        "West": detect_west(),
        "CMake": detect_cmake(),
        "Ninja": detect_ninja(),
        "Arm GCC": detect_arm_gcc(),
    }

    all_ok = True
    for name, path in tools.items():
        status = "✅" if path else "❌"
        print(f"  {status} {name:15} {path or 'NOT FOUND'}")
        if not path:
            all_ok = False

    workspace = detect_workspace()
    print(f"  {'✅' if workspace else '❌'} {'SDK workspace':15} {workspace or 'NOT FOUND'}")
    if not workspace:
        all_ok = False

    armgcc_dir = os.environ.get("ARMGCC_DIR")
    print(f"\nARMGCC_DIR: {armgcc_dir or 'not set'}")
    print(f"Board:      {DEFAULT_BOARD} (NXP RW612)")
    print(f"Platform:   {host_kind()}")
    print(f"Config:     {config_file()}")

    if not armgcc_dir:
        print("\n⚠️  ARMGCC_DIR is not set. The MCUXpresso build system needs it to")
        print("    locate the Arm GNU toolchain. Run 'install' for instructions.")

    if all_ok and armgcc_dir:
        print("\n✅ All tools detected!\n")
        return 0
    print("\n⚠️  Some tools missing. See README for setup instructions.\n")
    return 1

def cmd_clone(args) -> int:
    """Initialise the west workspace and fetch the RW612 repositories."""
    print("\n📥 Initialising MCUXpresso SDK workspace...\n")

    west = west_cmd()
    if not west:
        print("❌ west not found. Run 'python iris_w10_build.py install' first.")
        return 1

    workspace = Path.cwd() / WORKSPACE_NAME
    if (workspace / ".west").exists():
        print(f"ℹ️  {workspace} already initialised. Skipping west init.\n")
    else:
        init = west + ["init", "-m", MANIFEST_URL, WORKSPACE_NAME]
        if args.revision:
            init += ["--mr", args.revision]
        print(f"Running: {' '.join(init)}\n")
        result = subprocess.run(init, cwd=Path.cwd())
        if result.returncode != 0:
            return result.returncode

    # Targeted fetch keeps the workspace near 2 GB instead of the full ~7 GB.
    if args.full:
        update = west + ["update"]
    else:
        update = west + ["update_board", "--set", "board", args.board]
    print(f"\nRunning: {' '.join(update)}\n")
    result = subprocess.run(update, cwd=workspace)

    if result.returncode != 0:
        if not args.full:
            print("\n⚠️  Targeted update failed. Retry with --full to fetch the whole SDK.")
        return result.returncode

    print("\n✅ SDK workspace ready!\n")
    cfg = load_config()
    cfg["workspace"] = str(workspace)
    cfg["board"] = args.board
    save_config(cfg)
    return 0

def cmd_install(args) -> int:
    """Install west and report on the remaining toolchain prerequisites."""
    print("\n🔧 Setting up IRIS-W10 build environment...\n")

    python = detect_python()
    if not python:
        print("❌ Python not found on PATH")
        return 1

    print("Installing/updating west...")
    result = subprocess.run(
        [python, "-m", "pip", "install", "-U", "west"],
    )
    if result.returncode != 0:
        print("\n❌ Failed to install west.")
        return result.returncode
    print("✅ west installed.\n")

    missing = []
    for name, path in (("CMake", detect_cmake()),
                       ("Ninja", detect_ninja()),
                       ("Arm GCC", detect_arm_gcc())):
        if not path:
            missing.append(name)

    if missing:
        print(f"⚠️  Still missing: {', '.join(missing)}\n")
        print("These are not pip-installable. Install them as follows:\n")
        if host_kind() == "windows":
            print("  CMake    → https://cmake.org/download (3.30+)")
            print("  Ninja    → https://ninja-build.org (1.12.1+)")
            print("  Arm GCC  → https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads")
            print("\n  Or install everything at once with the MCUXpresso Installer:")
            print("  → https://github.com/nxp-mcuxpresso/vscode-for-mcux/wiki/Dependency-Installation")
        else:
            print("  sudo apt install cmake ninja-build gcc-arm-none-eabi")
    else:
        print("✅ CMake, Ninja and Arm GCC already present.\n")

    if not os.environ.get("ARMGCC_DIR"):
        print("\n📝 Set ARMGCC_DIR so the SDK build system finds the toolchain:\n")
        if host_kind() == "windows":
            print('   setx ARMGCC_DIR "C:\\Program Files (x86)\\Arm GNU Toolchain arm-none-eabi\\<version>"')
            print("   (then open a new terminal)")
        else:
            print('   export ARMGCC_DIR="/usr"   # add to ~/.bashrc')

    print("\nNext: python iris_w10_build.py clone\n")
    return 0

def cmd_list(args) -> int:
    """List available examples."""
    workspace = detect_workspace()
    if not workspace:
        print("❌ SDK workspace not found. Run 'python iris_w10_build.py clone' first.")
        return 1

    root = examples_root(workspace)
    if not root:
        print("❌ Examples directory not found in the workspace.")
        return 1

    print(f"\n📚 Available Examples (board: {args.board}):\n")

    found = False
    for cmake_file in sorted(root.rglob("CMakeLists.txt")):
        rel_path = cmake_file.parent.relative_to(root)
        depth = len(rel_path.parts)
        if depth <= 2:
            print(f"  • {rel_path.as_posix()}")
            found = True

    if not found:
        print("  (No examples found)")
    print("\nNot every example supports every board. Confirm with:")
    print(f"  west list_project -p examples/<path> -t {DEFAULT_TOOLCHAIN}\n")
    return 0

def resolve_example(workspace: str, name: str) -> Optional[Path]:
    """Map a user-supplied example name to a directory in the workspace."""
    root = examples_root(workspace)
    if not root:
        return None

    candidate = root / name
    if candidate.is_dir():
        return candidate

    # Allow a bare name such as 'hello_world'.
    matches = [p.parent for p in root.rglob("CMakeLists.txt") if p.parent.name == name]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"⚠️  '{name}' is ambiguous. Matches:")
        for m in sorted(matches):
            print(f"     {m.relative_to(root).as_posix()}")
        return None
    return None

def cmd_build(args) -> int:
    """Build an example application with west."""
    if not args.example:
        print("❌ Please specify an example (e.g., 'demo_apps/hello_world')")
        return 1

    workspace = detect_workspace()
    if not workspace:
        print("❌ SDK workspace not found. Run 'python iris_w10_build.py clone' first.")
        return 1

    west = west_cmd()
    if not west:
        print("❌ west not found. Run 'python iris_w10_build.py install' first.")
        return 1

    example_path = resolve_example(workspace, args.example)
    if not example_path:
        print(f"❌ Example '{args.example}' not found. Try 'list' to see what is available.")
        return 1

    if not os.environ.get("ARMGCC_DIR") and args.toolchain == "armgcc":
        print("⚠️  ARMGCC_DIR is not set; the build will likely fail.")
        print("    Run 'python iris_w10_build.py install' for instructions.\n")

    rel = example_path.relative_to(workspace).as_posix()
    print(f"\n🔨 Building {rel} for {args.board}...\n")

    cmd = west + [
        "build",
        "-b", args.board,
        rel,
        "--toolchain", args.toolchain,
        "--config", args.config,
    ]
    if args.pristine:
        cmd += ["-p", "always"]

    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=workspace)

    if result.returncode == 0:
        print(f"\n✅ Build complete. Artefacts under {workspace}/build\n")
        print("Flash with:  west flash -r linkserver     (or J-Link / J-Flash Lite)")
        print()
    return result.returncode

def cmd_clean(args) -> int:
    """Clean build artifacts."""
    print("\n🧹 Cleaning build artifacts...\n")

    workspace = detect_workspace()

    if args.all:
        if workspace and Path(workspace).exists():
            print(f"Removing: {workspace}")
            shutil.rmtree(workspace)
            cfg = load_config()
            cfg.pop("workspace", None)
            save_config(cfg)
            print("✅ SDK workspace removed.\n")
        else:
            print("ℹ️  SDK workspace not found.\n")
        return 0

    if not workspace:
        print("❌ SDK workspace not found.\n")
        return 1

    build_dir = Path(workspace) / "build"
    if build_dir.exists():
        print(f"Removing: {build_dir}")
        shutil.rmtree(build_dir)
        print("✅ Build directory cleaned.\n")
    else:
        print(f"ℹ️  Build directory not found: {build_dir}\n")
    return 0

def cmd_all(args) -> int:
    """Full pipeline: install → clone → build."""
    steps = [
        ("Install build environment", lambda: cmd_install(args)),
        ("Initialise SDK workspace", lambda: cmd_clone(args)),
        ("Build example", lambda: cmd_build(args)),
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

    # Check if virtual environment is active (recommended but not required)
    if not is_venv_active():
        print("⚠️  Tip: Running outside virtual environment.")
        print("   Consider setting up the shared venv for better isolation:")
        print("   1. cd .. && python ../setup_venv.py")
        print("   2. Then activate: .venv\\Scripts\\activate (Windows) or source .venv/bin/activate (Linux/macOS)")
        print()

    parser = argparse.ArgumentParser(
        prog="iris_w10_build.py",
        description="IRIS-W10 (NXP RW612/RW610) Build Driver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python iris_w10_build.py doctor                        # Check environment
  python iris_w10_build.py install                       # Install west + toolchain info
  python iris_w10_build.py clone                         # Init west workspace (RW612 only)
  python iris_w10_build.py clone --full                  # Fetch the complete SDK (~7 GB)
  python iris_w10_build.py list                          # List examples
  python iris_w10_build.py build demo_apps/hello_world   # Build example
  python iris_w10_build.py build hello_world --config release
  python iris_w10_build.py clean                         # Remove build directory
  python iris_w10_build.py clean --all                   # Remove entire workspace
  python iris_w10_build.py all demo_apps/hello_world     # Full pipeline
        """
    )
    parser.add_argument("--board", default=DEFAULT_BOARD,
                        help=f"MCUXpresso board target (default: {DEFAULT_BOARD})")

    subparsers = parser.add_subparsers(dest="command", help="Command")

    subparsers.add_parser("doctor", help="Verify toolchain")

    clone_parser = subparsers.add_parser("clone", help="Initialise west workspace")
    clone_parser.add_argument("--full", action="store_true",
                              help="fetch the complete SDK instead of RW612 only")
    clone_parser.add_argument("--revision", help="manifest tag, e.g. v25.09.00")

    subparsers.add_parser("install", help="Install west and report toolchain status")
    subparsers.add_parser("list", help="List examples")

    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    clean_parser.add_argument("--all", action="store_true", help="Remove entire workspace")

    build_parser = subparsers.add_parser("build", help="Build example")
    build_parser.add_argument("example", help="Example path or name")
    build_parser.add_argument("--config", default="debug", help="debug or release (default: debug)")
    build_parser.add_argument("--toolchain", default=DEFAULT_TOOLCHAIN,
                              help=f"toolchain (default: {DEFAULT_TOOLCHAIN})")
    build_parser.add_argument("-p", "--pristine", action="store_true", help="force a clean rebuild")

    all_parser = subparsers.add_parser("all", help="Full pipeline")
    all_parser.add_argument("example", nargs="?", default=DEFAULT_EXAMPLE, help="Example path or name")
    all_parser.add_argument("--config", default="debug", help="debug or release (default: debug)")
    all_parser.add_argument("--toolchain", default=DEFAULT_TOOLCHAIN, help="toolchain")
    all_parser.add_argument("-p", "--pristine", action="store_true", help="force a clean rebuild")
    all_parser.add_argument("--full", action="store_true", help="fetch the complete SDK")
    all_parser.add_argument("--revision", help="manifest tag, e.g. v25.09.00")

    args = parser.parse_args()

    commands = {
        "doctor": cmd_doctor,
        "clone": cmd_clone,
        "install": cmd_install,
        "list": cmd_list,
        "clean": cmd_clean,
        "build": cmd_build,
        "all": cmd_all,
    }

    if not args.command:
        parser.print_help()
        return 0

    return commands[args.command](args)

if __name__ == "__main__":
    sys.exit(main())
