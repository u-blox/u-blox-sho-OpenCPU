#!/usr/bin/env python3
"""
NORA-W30 (Realtek RTL872x) Build Driver
Automated cross-platform build orchestration for NORA-W30 Open CPU modules using Realtek RTOS SDK.

Supports: Linux (native & WSL2) | Windows (WSL2 recommended)
Note: Cygwin on Windows is complex; native Windows build not fully supported.
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional

import target_paths
from target_paths import host_kind

TARGET = "nora_w30"

# J-Link's name for the RTL8720DF KM0 core, as used by u-blox's own Realtek tooling.
JLINK_DEVICE = "RTL872xCS"

# Ameba-D flash layout (rlx8721d_layout*.ld, LS_IMG2_OTA1_ADDR in rtl8721d_ota.h).
FLASH_IMAGES = (
    ("km0_boot_all.bin", 0x08000000),
    ("km4_boot_all.bin", 0x08004000),
    ("km0_km4_image2.bin", 0x08006000),
)

# Windows consoles default to cp1252 and raise UnicodeEncodeError on the status glyphs below.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

# ============================================================================
# TOOL DETECTION
# ============================================================================

def detect_git() -> Optional[str]:
    """Detect git executable."""
    return shutil.which("git")

def detect_make() -> Optional[str]:
    """Detect make."""
    return shutil.which("make") if host_kind() != "windows" else None

def detect_arm_gcc() -> Optional[str]:
    """Detect arm-none-eabi-gcc."""
    return shutil.which("arm-none-eabi-gcc") if host_kind() != "windows" else None

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
    """Get per-platform config file path (modules/nora-w30/config)."""
    return target_paths.resolve_config(TARGET, host_kind())

def load_config() -> Dict:
    """Load cached configuration."""
    return target_paths.load_json(config_file())

def save_config(cfg: Dict) -> None:
    """Save configuration to cache."""
    target_paths.save_json(config_file(), cfg)

# ============================================================================
# COMMANDS
# ============================================================================

def cmd_doctor(args) -> int:
    """Verify toolchain availability."""
    current_host = host_kind()
    print(f"\nNORA-W30 Build Environment Check ({current_host})\n")

    if current_host == "windows":
        print("[NOTE] Windows detected.")
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
        status = "[OK]" if path else "[FAIL]"
        print(f"  {status} {name:15} {path or 'NOT FOUND'}")
        if not path:
            all_ok = False

    print(f"\nPlatform: {current_host}")
    print(f"Config: {config_file()}")

    if all_ok:
        print("\n[OK] All tools detected!\n")
        return 0
    else:
        print("\n[WARNING] Some tools missing. See README for setup instructions.\n")
        return 1

def cmd_clone(args) -> int:
    """Clone Realtek SDK repository."""
    print("\nCloning Realtek RTOS SDK...\n")

    git = detect_git()
    if not git:
        print("[FAIL] Git not found!")
        return 1

    revision = getattr(args, "revision", None)
    if revision:
        candidates = [target_paths.sdk_dir(TARGET, revision)]
    else:
        # Without a version, keep the SDK already in use.
        cached = load_config().get("sdk_path")
        candidates = ([Path(cached)] if cached else []) + target_paths.installed_sdks(TARGET)
    for existing in candidates:
        if (existing / "project").is_dir():
            print(f"[INFO] {existing} already exists. Skipping clone.\n")
            cfg = load_config()
            cfg["sdk_path"] = str(existing)
            save_config(cfg)
            return 0

    sdk_dir = target_paths.sdk_dir(TARGET, revision)
    target_paths.ensure(TARGET)
    sdk_dir.parent.mkdir(parents=True, exist_ok=True)
    # Approximate: shallow Ameba-D SDK, its bundled toolchain and a first build.
    if not target_paths.check_space(sdk_dir, 2, "the Realtek Ameba-D SDK"):
        return 1

    # Note: NORA-W30 uses Realtek RTL8720DF which requires Ameba-D SDK (not main ameba-rtos)
    repo_url = "https://github.com/Ameba-AIoT/ameba-rtos-d.git"  # Ameba-D SDK (specifically for RTL8720DF used in NORA-W30)

    print(f"Cloning from: {repo_url}\n")

    result = subprocess.run(
        [git, "clone", "--depth", "1", *(["--branch", revision] if revision else []), repo_url, str(sdk_dir)],
        cwd=sdk_dir.parent
    )

    if result.returncode == 0:
        print("\n[OK] Realtek SDK cloned successfully!\n")
        cfg = load_config()
        cfg["sdk_path"] = str(sdk_dir)
        remember_distro(cfg)
        save_config(cfg)
    else:
        print("\n[FAIL] Clone failed. Check URL and network connection.\n")

    return result.returncode

def cmd_install(args) -> int:
    """Verify Realtek SDK environment (tools already installed via system package manager)."""
    print("\n[OK] Environment Check for NORA-W30 (Realtek RTOS)\n")
    print("Realtek SDK uses standard Linux tools (arm-none-eabi-gcc, make, git).")
    print("These are installed via your system package manager (apt, yum, etc.).")
    print("\nTo install missing tools, run:")
    print("  Ubuntu/Debian: sudo apt install arm-none-eabi-gcc make git python3")
    print("  Other Linux:   Use your package manager to install the above tools")
    print("\nTo verify your installation, run:")
    print("  python3 nora_w30_build.py doctor")
    print()
    return 0

def cmd_clean(args) -> int:
    """Clean build artifacts."""
    print("\nCleaning build artifacts...\n")

    if args.all:
        # Remove entire SDK directory
        sdk_path = load_config().get("sdk_path")
        if sdk_path and Path(sdk_path).exists():
            print(f"Removing: {sdk_path}")
            shutil.rmtree(sdk_path)
            # Clear config
            cfg = load_config()
            cfg.pop("sdk_path", None)
            save_config(cfg)
            print("[OK] Realtek SDK removed.\n")
        else:
            print("[INFO] Realtek SDK not found.\n")
        return 0

    # Clean project (not example-based)
    sdk_path = load_config().get("sdk_path")
    if not sdk_path or not Path(sdk_path).exists():
        print("[FAIL] Realtek SDK not found.\n")
        return 1

    sdk_path = Path(sdk_path)

    # Clean specified project or both
    projects = ["project_lp", "project_hp"]
    if hasattr(args, 'project') and args.project:
        projects = [args.project]

    for project in projects:
        project_dir = sdk_path / "project" / "realtek_amebaD_va0_example" / "GCC-RELEASE" / project
        if not project_dir.exists():
            print(f"[WARN] Project not found: {project}\n")
            continue

        print(f"Running make clean for: {project}\n")
        result = subprocess.run(
            ["make", "clean"],
            cwd=project_dir
        )
        if result.returncode != 0:
            return 1

    print("[OK] Clean complete.\n")
    return 0

def cmd_build(args) -> int:
    """Build Ameba-D firmware image."""

    sdk_path = load_config().get("sdk_path")
    if not sdk_path or not Path(sdk_path).exists():
        print("[FAIL] Realtek SDK not found. Run 'python nora_w30_build.py clone' first.")
        return 1

    sdk_path = Path(sdk_path)

    # Determine which project to build (project_lp = KM0, project_hp = KM4)
    project = getattr(args, 'project', None) or 'project_hp'  # Default to project_hp (KM4)
    project_dir = sdk_path / "project" / "realtek_amebaD_va0_example" / "GCC-RELEASE" / project

    if not project_dir.exists():
        print(f"[FAIL] Project directory not found: {project_dir}")
        print("Available projects: project_lp (KM0), project_hp (KM4)")
        return 1

    print(f"\nBuilding {project} (Ameba-D Firmware)...\n")
    if on_windows_drive(sdk_path):
        print(f"[WARNING] The SDK is on the Windows drive ({sdk_path}); WSL2 builds there are very slow.")
        print("          '--clone main' fetches a copy into the WSL2 file system and uses it from then on.\n")
    cfg = load_config()
    if remember_distro(cfg):
        save_config(cfg)

    env = os.environ.copy()
    env["SDK_ROOT"] = str(sdk_path)

    # Run make all from the project directory
    result = subprocess.run(
        ["make", "all"],
        cwd=project_dir,
        env=env
    )

    if result.returncode == 0:
        image_dir = project_dir / "asdk" / "image"
        print(f"\n[OK] Build complete. Images at: {image_dir}\n")

    return result.returncode

def cmd_list(args) -> int:
    """List available example source files in SDK."""
    sdk_path = load_config().get("sdk_path")
    if not sdk_path or not Path(sdk_path).exists():
        print("[FAIL] Realtek SDK not found.")
        return 1

    sdk_path = Path(sdk_path)

    # Show Ameba-D example sources (included in build, not separate targets)
    example_sources = sdk_path / "project" / "realtek_amebaD_va0_example" / "example_sources"
    if example_sources.exists():
        print("\nAmeba-D Example Sources (included in firmware build):\n")
        for ex in sorted(example_sources.iterdir()):
            if ex.is_dir():
                print(f"  - {ex.name}")
        print("\nNote: These are example source files, not separate build targets.")
        print("Modify build configuration to include different examples in the firmware.\n")
        return 0

    print("[FAIL] Example sources directory not found.")
    return 1

def on_windows_drive(path: Path) -> bool:
    return host_kind() == "wsl" and Path(path).as_posix().startswith("/mnt/")

def remember_distro(cfg: Dict) -> bool:
    """Store the WSL2 distro so Windows can reach the SDK for flashing; True when cfg changed."""
    distro = os.environ.get("WSL_DISTRO_NAME")
    if host_kind() != "wsl" or not distro or cfg.get("wsl_distro") == distro:
        return False
    cfg["wsl_distro"] = distro
    return True

def wsl_sdk_from_windows() -> Optional[Path]:
    """The SDK the WSL2 build uses, as a Windows path."""
    cfg = target_paths.load_json(target_paths.config_file(TARGET, "wsl"))
    path = cfg.get("sdk_path", "")
    if path.startswith("/mnt/") and len(path) > 6:
        return Path(f"{path[5].upper()}:" + path[6:].replace("/", "\\"))
    if path.startswith("/") and cfg.get("wsl_distro"):
        return Path(f"\\\\wsl$\\{cfg['wsl_distro']}" + path.replace("/", "\\"))
    return None

def find_sdk() -> Optional[Path]:
    """The SDK in use; from Windows that is the one the WSL2 build cached."""
    cached = load_config().get("sdk_path")
    candidates = [Path(cached)] if cached else []
    if host_kind() == "windows":
        candidates.append(wsl_sdk_from_windows())
    candidates += target_paths.installed_sdks(TARGET)
    return next((p for p in candidates if p and (p / "project").is_dir()), None)

def cmd_flash(args) -> int:
    """Program the Ameba-D images over SWD with SEGGER J-Link Commander."""
    import flash_helper

    sdk_path = find_sdk()
    if not sdk_path:
        print("[FAIL] Realtek SDK not found. Run 'python nora_w30_build.py clone' first.")
        return 1

    gcc_release = sdk_path / "project" / "realtek_amebaD_va0_example" / "GCC-RELEASE"
    image_dirs = [gcc_release / p / "asdk" / "image" for p in ("project_hp", "project_lp")]
    images = []
    for name, address in FLASH_IMAGES:
        found = next((d / name for d in image_dirs if (d / name).is_file()), None)
        if not found:
            print(f"[FAIL] {name} not found in {image_dirs[0]}")
            print("       Build both cores first: --build project_lp, then --build project_hp")
            return 1
        images.append((found, address))

    print("\nNORA-W30 Flash Utility (J-Link, SWD)\n")
    for path, address in images:
        print(f"  0x{address:08X}  {path.name}")
    # J-Link Commander may not open \\wsl$ paths; give it local copies.
    with tempfile.TemporaryDirectory(prefix="ubx-w30-") as tmp:
        local = [(Path(shutil.copy(path, tmp)), address) for path, address in images]
        commands = ["RSetType 4", "r", "Sleep 500",
                    *[f'loadfile "{path}" 0x{address:08X}' for path, address in local],
                    "RSetType 2", "r", "g"]
        return flash_helper.flash_jlink_script(JLINK_DEVICE, commands, args.serial)

def cmd_log(args) -> int:
    """Open the serial console (115200 8N1)."""
    import serial_logger

    print("\nNORA-W30 Serial Monitor (115200 baud)")
    print("   Use Ctrl+C to exit\n")
    return serial_logger.open_serial_monitor(args.port, 115200)

def cmd_all(args) -> int:
    """Full pipeline: clone -> build."""
    steps = [
        ("Clone Realtek SDK", lambda: cmd_clone(args)),
        ("Build Example", lambda: cmd_build(args)),
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

    parser = argparse.ArgumentParser(
        description="NORA-W30 (Realtek RTL872x) Build Driver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python nora_w30_build.py doctor              # Check environment
  python nora_w30_build.py clone               # Clone Realtek SDK
  python nora_w30_build.py install             # Show tool installation info
  python nora_w30_build.py list                # List example sources
  python nora_w30_build.py build               # Build firmware (project_hp default)
  python nora_w30_build.py build project_lp   # Build KM0 project
  python nora_w30_build.py clean               # Clean firmware artifacts
  python nora_w30_build.py clean --all         # Remove Realtek SDK entirely

Note: Best on Linux or WSL2. Windows Cygwin is complex.
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    subparsers.add_parser("doctor", help="Verify toolchain")
    clone_parser = subparsers.add_parser("clone", help="Clone Realtek SDK")
    clone_parser.add_argument("--revision", help="branch or tag (default: main), fetched into sdks/ameba-rtos-d/<revision>")
    subparsers.add_parser("install", help="Show tool installation info")
    subparsers.add_parser("list", help="List example sources")

    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    clean_parser.add_argument("project", nargs="?", help="Project name (project_lp, project_hp; optional)")
    clean_parser.add_argument("--all", action="store_true", help="Remove entire SDK")

    build_parser = subparsers.add_parser("build", help="Build firmware")
    build_parser.add_argument("project", nargs="?", help="Project name (project_lp, project_hp; default: project_hp)")

    all_parser = subparsers.add_parser("all", help="Full pipeline")
    all_parser.add_argument("project", nargs="?", help="Project name (project_lp or project_hp; default: project_hp)")

    flash_parser = subparsers.add_parser("flash", help="Flash both cores over SWD (J-Link)")
    flash_parser.add_argument("project", nargs="?", help="Ignored; both cores are always flashed")
    flash_parser.add_argument("--serial", help="J-Link serial number (when several are connected)")

    log_parser = subparsers.add_parser("log", help="Open the serial console")
    log_parser.add_argument("port", nargs="?", default=None, help="Serial port (auto-detected if omitted)")

    args = parser.parse_args()

    commands = {
        "doctor": cmd_doctor,
        "clone": cmd_clone,
        "install": cmd_install,
        "list": cmd_list,
        "clean": cmd_clean,
        "build": cmd_build,
        "all": cmd_all,
        "flash": cmd_flash,
        "log": cmd_log,
    }

    if not args.command:
        parser.print_help()
        return 0

    return commands[args.command](args)

if __name__ == "__main__":
    sys.exit(main())
