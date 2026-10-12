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
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import target_paths

TARGET = "nora_w30"

# Windows consoles default to cp1252 and raise UnicodeEncodeError on the status glyphs below.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

# ============================================================================
# PLATFORM & ENVIRONMENT DETECTION
# ============================================================================

def host_kind() -> str:
    """Detect platform type: 'wsl', 'linux', or 'windows'."""
    return target_paths.host_kind()

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
    return str(candidates[0].resolve()) if candidates else None

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
    """Get per-platform config file path (targets/nora-w30/config)."""
    return target_paths.resolve_config(TARGET, host_kind())

def load_config() -> Dict:
    """Load cached configuration."""
    cfg_path = config_file()
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except:
            pass
    return {}

def save_config(cfg: Dict) -> None:
    """Save configuration to cache."""
    config_file().write_text(json.dumps(cfg, indent=2), encoding="utf-8")

# ============================================================================
# COMMANDS
# ============================================================================

def cmd_doctor(args) -> int:
    """Verify toolchain availability."""
    current_host = host_kind()
    print(f"\nNORA-W3 Build Environment Check ({current_host})\n")

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

    for existing in target_paths.sdk_candidates(TARGET) + [target_paths.sdk_dir(TARGET) / "realtek-rtos-sdk"]:
        if (existing / "project").is_dir():
            print(f"[INFO] {existing} already exists. Skipping clone.\n")
            cfg = load_config()
            cfg["sdk_path"] = str(existing)
            save_config(cfg)
            return 0

    sdk_dir = target_paths.vendor_sdk(TARGET)
    target_paths.ensure(TARGET)
    # Approximate: shallow Ameba-D SDK, its bundled toolchain and a first build.
    if not target_paths.check_space(sdk_dir, 2, "the Realtek Ameba-D SDK"):
        return 1

    # Note: NORA-W30 uses Realtek RTL8720DF which requires Ameba-D SDK (not main ameba-rtos)
    repo_url = "https://github.com/Ameba-AIoT/ameba-rtos-d.git"  # Ameba-D SDK (specifically for RTL8720DF used in NORA-W30)

    print(f"Cloning from: {repo_url}\n")

    result = subprocess.run(
        [git, "clone", "--depth", "1", repo_url, str(sdk_dir)],
        cwd=sdk_dir.parent
    )

    if result.returncode == 0:
        print("\n[OK] Realtek SDK cloned successfully!\n")
        cfg = load_config()
        cfg["sdk_path"] = str(sdk_dir)
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

    sdk_path = load_config().get("sdk_path")
    if not sdk_path:
        print("[FAIL] Realtek SDK not found.\n")
        return 1

    sdk_path = Path(sdk_path)

    # Try Ameba-D structure first
    example_sources = sdk_path / "project" / "realtek_amebaD_va0_example" / "example_sources"
    if example_sources.exists():
        example_dir = example_sources / args.example
        if example_dir.exists():
            print(f"Running make clean for: {args.example}\n")
            result = subprocess.run(
                ["make", "-C", str(example_sources), "clean"],
                cwd=example_sources
            )
            if result.returncode == 0:
                print("\n[OK] Build directory cleaned.\n")
            return result.returncode
        else:
            print(f"[INFO] Example directory not found: {example_dir}\n")
            return 0

    # Fall back to alternative paths
    example_dir = sdk_path / "examples" / args.example
    if not example_dir.exists():
        example_dir = sdk_path / "project" / "realtek_amebaZ" / args.example

    # Try to clean using make
    if example_dir.exists():
        print(f"Running make clean in: {example_dir}\n")
        result = subprocess.run(
            ["make", "clean"],
            cwd=example_dir
        )
        if result.returncode == 0:
            print("\n[OK] Build directory cleaned.\n")
        return result.returncode
    else:
        print(f"[INFO] Example directory not found: {example_dir}\n")

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
        print(f"Available projects: project_lp (KM0), project_hp (KM4)")
        return 1

    print(f"\nBuilding {project} (Ameba-D Firmware)...\n")

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
    subparsers.add_parser("clone", help="Clone Realtek SDK")
    subparsers.add_parser("install", help="Show tool installation info")
    subparsers.add_parser("list", help="List example sources")

    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    clean_parser.add_argument("project", nargs="?", help="Project name (project_lp, project_hp; optional)")
    clean_parser.add_argument("--all", action="store_true", help="Remove entire SDK")

    build_parser = subparsers.add_parser("build", help="Build firmware")
    build_parser.add_argument("project", nargs="?", help="Project name (project_lp, project_hp; default: project_hp)")

    all_parser = subparsers.add_parser("all", help="Full pipeline")
    all_parser.add_argument("project", nargs="?", help="Project name (project_lp or project_hp; default: project_hp)")

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
