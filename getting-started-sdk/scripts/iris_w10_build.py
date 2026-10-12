#!/usr/bin/env python3
"""
IRIS-W10 (NXP RW612/RW610) Build Driver
Automated cross-platform build orchestration for IRIS-W10 Open CPU modules using the
MCUXpresso SDK (west/CMake/Ninja flavour).

Supports: Windows, WSL2, Linux
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import serial logger
import serial_logger
import target_paths
from target_paths import host_kind, newest, short_path

TARGET = "iris_w10"

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

# IRIS-W10 uses NXP RW612 (with Thread) or RW610 (BLE + Wi-Fi only); rdrw612bga is the matching MCUXpresso board target.
DEFAULT_BOARD = "rdrw612bga"
# J-Link knows the SoC, not the board target.
JLINK_DEVICE = "RW612"
# RW612 FlexSPI flash (XIP) base; a raw .bin starts with the boot header here.
FLASH_BASE = 0x08000000
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

# ============================================================================
# TOOL DETECTION
# ============================================================================

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
    except (OSError, subprocess.SubprocessError):
        return False

def detect_git() -> Optional[str]:
    return which("git")

def detect_west() -> Optional[str]:
    """west as a printable command, for 'doctor'."""
    cmd = west_cmd()
    return " ".join(cmd) if cmd else None

def west_cmd() -> Optional[List[str]]:
    """Argv prefix for invoking west; a pip console script, else 'python -m west'."""
    found = which("west")
    if found:
        return [found]
    try:
        r = subprocess.run([sys.executable, "-m", "west", "--version"],
                           capture_output=True, text=True)
    except OSError:
        return None
    return [sys.executable, "-m", "west"] if r.returncode == 0 else None

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
    env_dir = os.environ.get("ARMGCC_DIR")
    if env_dir:
        exe = "arm-none-eabi-gcc" + (".exe" if host_kind() == "windows" else "")
        candidate = Path(env_dir) / "bin" / exe
        if candidate.exists():
            return short_path(str(candidate))

    if host_kind() == "windows":
        result = newest([
            "C:/Program Files/Arm/GNU Toolchain mingw-w64-x86_64-arm-none-eabi/bin/arm-none-eabi-gcc.exe",
            "C:/Program Files (x86)/Arm GNU Toolchain*/*/bin/arm-none-eabi-gcc.exe",
            "C:/Program Files/Arm GNU Toolchain*/*/bin/arm-none-eabi-gcc.exe",
            str(Path.home() / ".mcuxpressotools" / "arm-gnu-toolchain-*" / "bin" / "arm-none-eabi-gcc.exe"),
            "C:/armgcc/bin/arm-none-eabi-gcc.exe",
        ])
        if result:
            return short_path(result)
    return which("arm-none-eabi-gcc")

def armgcc_dir() -> Tuple[Optional[str], str]:
    """Toolchain root the MCUXpresso build needs as ARMGCC_DIR, and where it came from."""
    env = os.environ.get("ARMGCC_DIR")
    if env:
        return env, "ARMGCC_DIR"
    gcc = detect_arm_gcc()
    if gcc:
        # <root>/bin/arm-none-eabi-gcc -> <root>
        return str(Path(gcc).parent.parent), "auto-detected"
    return None, "not found"

def detect_workspace() -> Optional[str]:
    """Locate the west workspace (the directory holding .west/)."""
    cfg = load_config()
    if "workspace" in cfg and (Path(cfg["workspace"]) / ".west").exists():
        return cfg["workspace"]

    for candidate in target_paths.installed_sdks(TARGET):
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
    """Get per-platform config file path (modules/iris-w10/config)."""
    return target_paths.resolve_config(TARGET, host_kind())

def load_config() -> Dict:
    return target_paths.load_json(config_file())

def save_config(cfg: Dict) -> None:
    target_paths.save_json(config_file(), cfg)

# ============================================================================
# COMMANDS
# ============================================================================

def cmd_doctor(args) -> int:
    """Verify toolchain availability."""
    print("\nIRIS-W10 Build Environment Check\n")

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
        status = "[OK]" if path else "[FAIL]"
        print(f"  {status} {name:15} {path or 'NOT FOUND'}")
        if not path:
            all_ok = False

    workspace = detect_workspace()
    status = '[OK]' if workspace else '[FAIL]'
    print(f"  {status} {'SDK workspace':15} {workspace or 'NOT FOUND'}")
    if not workspace:
        all_ok = False

    toolchain, source = armgcc_dir()
    print(f"\nARMGCC_DIR: {toolchain or 'not found'} ({source})")
    print(f"Board:      {DEFAULT_BOARD} (NXP RW612)")
    print(f"Platform:   {host_kind()}")
    print(f"Config:     {config_file()}")

    if not toolchain:
        print("\n[WARNING] No Arm GNU toolchain found. Run 'install' for instructions,")
        print("    or set ARMGCC_DIR to the toolchain root (the folder containing bin/).")

    if all_ok and toolchain:
        print("\n[OK] All tools detected!\n")
        return 0
    print("\n[WARNING] Some tools missing. See README for setup instructions.\n")
    return 1

def cmd_clone(args) -> int:
    """Initialise the west workspace and fetch the RW612 repositories."""
    print("\nInitialising MCUXpresso SDK workspace...\n")

    west = west_cmd()
    if not west:
        print("[FAIL] west not found. Run 'python iris_w10_build.py install' first.")
        return 1

    if args.revision:
        workspace = target_paths.sdk_dir(TARGET, args.revision)
    else:
        workspace = Path(detect_workspace() or target_paths.sdk_dir(TARGET))
    # Approximate, including a first build: board-only ~2 GB, whole SDK ~7 GB.
    if not (workspace / ".west").exists() or args.full:
        needed = 8 if args.full else 3
        if not target_paths.check_space(workspace, needed, "the MCUXpresso SDK"):
            return 1
    if (workspace / ".west").exists():
        print(f"[INFO] {workspace} already initialised. Skipping west init.\n")
    else:
        target_paths.ensure(TARGET)
        workspace.parent.mkdir(parents=True, exist_ok=True)
        init = west + ["init", "-m", MANIFEST_URL, workspace.name]
        if args.revision:
            init += ["--mr", args.revision]
        print(f"Running: {' '.join(init)}\n")
        result = subprocess.run(init, cwd=workspace.parent)
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
            print("\n[WARNING] Targeted update failed. Retry with --full to fetch the whole SDK.")
        return result.returncode

    print("\n[OK] SDK workspace ready!\n")
    cfg = load_config()
    cfg["workspace"] = str(workspace)
    cfg["board"] = args.board
    save_config(cfg)
    return 0

def cmd_install(args) -> int:
    """Install west and report on the remaining toolchain prerequisites."""
    print("\nSetting up IRIS-W10 build environment...\n")

    python = detect_python()
    if not python:
        print("[FAIL] Python not found on PATH")
        return 1

    print("Installing/updating west...")
    result = subprocess.run(
        [python, "-m", "pip", "install", "-U", "west"],
    )
    if result.returncode != 0:
        print("\n[FAIL] Failed to install west.")
        return result.returncode
    print("[OK] west installed.\n")

    workspace = detect_workspace()
    reqs = Path(workspace) / "mcuxsdk" / "scripts" / "requirements-base.txt" if workspace else None
    if reqs and reqs.exists():
        print(f"Installing SDK Python requirements ({reqs.name})...")
        result = subprocess.run([python, "-m", "pip", "install", "-r", str(reqs)])
        if result.returncode != 0:
            print("\n[FAIL] Failed to install the SDK Python requirements.")
            return result.returncode
        print("[OK] SDK Python requirements installed.\n")
    else:
        print("[INFO] SDK not cloned yet; re-run install after clone for its Python requirements.\n")

    missing = []
    for name, path in (("CMake", detect_cmake()),
                       ("Ninja", detect_ninja()),
                       ("Arm GCC", detect_arm_gcc())):
        if not path:
            missing.append(name)

    if missing:
        print(f"[WARNING] Still missing: {', '.join(missing)}\n")
        print("These are not pip-installable. Install them as follows:\n")
        if host_kind() == "windows":
            print("  CMake    -> https://cmake.org/download (3.30+)")
            print("  Ninja    -> https://ninja-build.org (1.12.1+)")
            print("  Arm GCC  -> https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads")
            print("\n  Or install everything at once with the MCUXpresso Installer:")
            print("  -> https://github.com/nxp-mcuxpresso/vscode-for-mcux/wiki/Dependency-Installation")
        else:
            print("  sudo apt install cmake ninja-build gcc-arm-none-eabi")
    else:
        print("[OK] CMake, Ninja and Arm GCC already present.\n")

    print("\nNext: python iris_w10_build.py clone\n")
    return 0

def cmd_list(args) -> int:
    """List available examples."""
    workspace = detect_workspace()
    if not workspace:
        print("[FAIL] SDK workspace not found. Run 'python iris_w10_build.py clone' first.")
        return 1

    root = examples_root(workspace)
    if not root:
        print("[FAIL] Examples directory not found in the workspace.")
        return 1

    print(f"\nAvailable Examples (board: {args.board}):\n")

    found = False
    for cmake_file in sorted(root.rglob("CMakeLists.txt")):
        rel_path = cmake_file.parent.relative_to(root)
        depth = len(rel_path.parts)
        if depth <= 2:
            print(f"  - {rel_path.as_posix()}")
            found = True

    if not found:
        print("  (No examples found)")
    print("\nNot every example supports every board. Confirm with:")
    print(f"  west list_project -p examples/<path> -t {DEFAULT_TOOLCHAIN}\n")
    return 0

def cmd_log(args) -> int:
    """Open serial monitor for debugging output at 115200 baud."""
    port = getattr(args, 'port', None)

    print("\nIRIS-W10 Serial Monitor (115200 baud)")
    print("   Use Ctrl+C to exit\n")

    return serial_logger.open_serial_monitor(port, 115200)

def cmd_flash(args) -> int:
    """Flash firmware using J-Link debugger."""
    print("\nIRIS-W10 Flash Utility (J-Link/MCU-Link)\n")

    import flash_helper

    # Determine firmware file
    if not args.example:
        print("[FAIL] Please specify example to flash")
        return 1

    workspace = detect_workspace()
    if not workspace:
        print("[FAIL] SDK workspace not found. Run 'python iris_w10_build.py clone' first.")
        return 1

    example_path = resolve_example(workspace, args.example)
    if not example_path:
        return 1

    # Determine build directory: older SDKs use build/<config>, current ones build/ itself.
    build_config = "release" if args.config == "release" else "debug"
    build = Path(workspace) / "build"
    build_root = next((d for d in (build / build_config, build) if d.is_dir()), None)

    if not build_root:
        print(f"[FAIL] Build directory not found: {build}")
        print(f"   Build with: python iris_w10_build.py build {args.example}")
        return 1

    # Artefacts are named after the example; .hex and .elf carry their own load addresses.
    firmware_file = None
    for suffix in (".hex", ".elf", ".bin"):
        candidates = [build_root / f"{example_path.name}{suffix}"] + sorted(build_root.glob(f"*{suffix}"))
        firmware_file = next((c for c in candidates if c.is_file()), None)
        if firmware_file:
            break

    if not firmware_file:
        print(f"[FAIL] No firmware found in {build_root}")
        print(f"   Build with: python iris_w10_build.py build {args.example}")
        return 1

    print(f"Firmware: {firmware_file.name}")
    print(f"   Device: {JLINK_DEVICE}\n")

    address = FLASH_BASE if firmware_file.suffix == ".bin" else 0
    return flash_helper.flash_jlink(JLINK_DEVICE, str(firmware_file), address=address, serial=args.serial,
                                    prefer="MCU-Link")

def resolve_example(workspace: str, name: str) -> Optional[Path]:
    """Map a user-supplied example name to a directory in the workspace.

    Prints the reason on failure and returns None.
    """
    root = examples_root(workspace)
    if not root:
        print(f"[FAIL] No examples directory under {workspace}.")
        print("       Run 'python iris_w10_build.py clone' to populate the workspace.")
        return None

    candidate = root / name
    if candidate.is_dir():
        return candidate

    # Allow a bare name such as 'hello_world'.
    matches = [p.parent for p in root.rglob("CMakeLists.txt") if p.parent.name == name]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"[FAIL] '{name}' is ambiguous. Re-run with one of these paths:")
        for m in sorted(matches):
            print(f"     {m.relative_to(root).as_posix()}")
        return None
    print(f"[FAIL] Example '{name}' not found. Try 'list' to see what is available.")
    return None

def cmd_build(args) -> int:
    """Build an example application with west."""
    if not args.example:
        print("[FAIL] Please specify an example (e.g., 'demo_apps/hello_world')")
        return 1

    workspace = detect_workspace()
    if not workspace:
        print("[FAIL] SDK workspace not found. Run 'python iris_w10_build.py clone' first.")
        return 1

    west = west_cmd()
    if not west:
        print("[FAIL] west not found. Run 'python iris_w10_build.py install' first.")
        return 1

    example_path = resolve_example(workspace, args.example)
    if not example_path:
        return 1

    toolchain, source = armgcc_dir()
    if args.toolchain == "armgcc":
        if not toolchain:
            print("[FAIL] No Arm GNU toolchain found. Run 'python iris_w10_build.py install',")
            print("    or set ARMGCC_DIR to the toolchain root (the folder containing bin/).")
            return 1
        print(f"Toolchain: {toolchain} ({source})")

    rel = example_path.relative_to(workspace).as_posix()
    print(f"\nBuilding {rel} for {args.board}...\n")

    cmd = west + [
        "build",
        "-b", args.board,
        rel,
        "--toolchain", args.toolchain,
        "--config", args.config,
    ]
    # 'auto' wipes the shared build dir when it belongs to a different example.
    cmd += ["-p", "always" if args.pristine else "auto"]
    # CMake's own Python lookup can land on an unrelated interpreter (e.g. MSYS2)
    # missing the SDK's packages; pin it to the one running this driver.
    cmd += ["--", f"-DPython3_EXECUTABLE={Path(sys.executable).as_posix()}"]
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    if toolchain:
        env["ARMGCC_DIR"] = toolchain

    print(f"Running: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=workspace, env=env)

    if result.returncode == 0:
        print(f"\n[OK] Build complete. Artefacts under {workspace}/build\n")
        print("Flash with:  west flash -r linkserver     (or J-Link / J-Flash Lite)")
        print()
    return result.returncode

def cmd_clean(args) -> int:
    """Clean build artifacts."""
    print("\nCleaning build artifacts...\n")

    workspace = detect_workspace()

    if args.all:
        if workspace and Path(workspace).exists():
            print(f"Removing: {workspace}")
            shutil.rmtree(workspace)
            cfg = load_config()
            cfg.pop("workspace", None)
            save_config(cfg)
            print("[OK] SDK workspace removed.\n")
        else:
            print("[INFO] SDK workspace not found.\n")
        return 0

    if not workspace:
        print("[FAIL] SDK workspace not found.\n")
        return 1

    build_dir = Path(workspace) / "build"
    if build_dir.exists():
        print(f"Removing: {build_dir}")
        shutil.rmtree(build_dir)
        print("[OK] Build directory cleaned.\n")
    else:
        print(f"[INFO] Build directory not found: {build_dir}\n")
    return 0

def cmd_all(args) -> int:
    """Full pipeline: install -> clone -> build."""
    steps = [
        ("Install build environment", lambda: cmd_install(args)),
        ("Initialise SDK workspace", lambda: cmd_clone(args)),
        ("Build example", lambda: cmd_build(args)),
    ]

    for name, step in steps:
        print(f"\n{'='*50}\n{name}\n{'='*50}")
        if step() != 0:
            print(f"\n[FAIL] {name} failed!")
            return 1

    print("\n[OK] Pipeline complete!\n")
    return 0

# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse

    # Check if virtual environment is active (recommended but not required)
    if not is_venv_active():
        print("[TIP] Running outside virtual environment.")
        print("   Consider setting up the shared venv for better isolation:")
        print("   1. cd .. && python ../scripts/setup_venv.py")
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
  python iris_w10_build.py log                           # Open serial monitor (auto-detect port)
  python iris_w10_build.py log COM11                     # Open serial monitor on specific port
  python iris_w10_build.py flash demo_apps/hello_world   # Flash via J-Link (auto-detect)
  python iris_w10_build.py flash hello_world --serial 1234567
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

    log_parser = subparsers.add_parser("log", help="Open serial monitor for debugging output")
    log_parser.add_argument("port", nargs="?", default=None,
                           help="Serial port (auto-detected if not specified)")

    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    clean_parser.add_argument("--all", action="store_true", help="Remove entire workspace")

    build_parser = subparsers.add_parser("build", help="Build example")
    build_parser.add_argument("example", help="Example path or name")
    build_parser.add_argument("--config", default="debug", help="debug or release (default: debug)")
    build_parser.add_argument("--toolchain", default=DEFAULT_TOOLCHAIN,
                              help=f"toolchain (default: {DEFAULT_TOOLCHAIN})")
    build_parser.add_argument("-p", "--pristine", action="store_true", help="force a clean rebuild")

    flash_parser = subparsers.add_parser("flash", help="Flash example to device using J-Link")
    flash_parser.add_argument("example", help="Example path or name")
    flash_parser.add_argument("--config", default="debug", help="debug or release (default: debug)")
    flash_parser.add_argument("--serial", help="J-Link serial number (auto-detected if not specified)")

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
        "log": cmd_log,
        "clean": cmd_clean,
        "build": cmd_build,
        "flash": cmd_flash,
        "all": cmd_all,
    }

    if not args.command:
        parser.print_help()
        return 0

    return commands[args.command](args)

if __name__ == "__main__":
    sys.exit(target_paths.run_main(main))
