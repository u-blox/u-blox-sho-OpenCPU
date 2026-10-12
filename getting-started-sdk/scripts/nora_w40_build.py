#!/usr/bin/env python3
"""
NORA-W40 (ESP32-C6) Build Driver
Automated cross-platform build orchestration for NORA-W40 Open CPU modules using ESP-IDF.

Supports: Windows, WSL2, Linux
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional

import target_paths
from target_paths import host_kind, newest, short_path

TARGET = "nora_w40"

# NORA-W40 is an ESP32-C6 (RISC-V), not the Xtensa ESP32 that idf.py assumes by default.
IDF_TARGET = "esp32c6"

NO_IDF = "[FAIL] ESP-IDF not found. Run: ubx-sdk nora-w40 --clone"
NO_IDF_PYTHON = ("[FAIL] ESP-IDF Python environment not found or incomplete.\n"
                 "       Run: ubx-sdk nora-w40 --install")

# Windows consoles default to cp1252 and raise UnicodeEncodeError on the status glyphs below.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

# ============================================================================
# TOOL DETECTION
# ============================================================================

def detect_idf() -> Optional[str]:
    """Detect ESP-IDF installation."""
    # Check config first
    cfg = load_config()
    if "idf_path" in cfg:
        idf_path = cfg["idf_path"]
        if Path(idf_path).exists():
            return idf_path

    # Check common locations
    patterns = [str(p) for p in target_paths.installed_sdks(TARGET)] + [
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

    return shutil.which("git")

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

    return shutil.which("make")

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

    return shutil.which("cmake")

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
    """Get per-platform config file path (modules/nora-w40/config)."""
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
    print("\nNORA-W40 Build Environment Check\n")

    tools = {
        "Python": detect_python(),
        "Git": detect_git(),
        "CMake": detect_cmake(),
        "Make": detect_make(),
        "ESP-IDF": detect_idf(),
    }

    all_ok = True
    for name, path in tools.items():
        status = "[OK]" if path else "[FAIL]"
        print(f"  {status} {name:15} {path or 'NOT FOUND'}")
        if not path:
            all_ok = False

    print(f"\nPlatform: {host_kind()}")
    print(f"Config: {config_file()}")

    if all_ok:
        print("\n[OK] All tools detected!\n")
        return 0
    else:
        print("\n[WARNING] Some tools missing. See docs/nora_w40_README.md.\n")
        return 1

def cmd_clone(args) -> int:
    """Clone ESP-IDF repository."""
    print("\nCloning ESP-IDF...\n")

    # Try git command directly (should be in PATH)
    try:
        git_cmd = ["git", "--version"]
        subprocess.run(git_cmd, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        print("[FAIL] Git not found or not in PATH!")
        return 1

    revision = getattr(args, "revision", None)
    if revision:
        idf_dir = target_paths.sdk_dir(TARGET, revision)
    else:
        # Without a version, keep the ESP-IDF already in use.
        idf_dir = Path(detect_idf() or target_paths.sdk_dir(TARGET))
    if idf_dir.exists():
        print(f"[INFO] {idf_dir} already exists. Skipping clone.\n")
        cfg = load_config()
        cfg["idf_path"] = str(idf_dir)
        save_config(cfg)
        return 0
    target_paths.ensure(TARGET)
    idf_dir.parent.mkdir(parents=True, exist_ok=True)
    # Approximate: shallow ESP-IDF with submodules plus a first build.
    if not target_paths.check_space(idf_dir, 3, "ESP-IDF"):
        return 1

    result = subprocess.run(
        ["git", "clone", "--depth", "1", *(["--branch", revision] if revision else []),
         "https://github.com/espressif/esp-idf.git", str(idf_dir)],
        cwd=idf_dir.parent
    )

    if result.returncode == 0:
        print("\n[OK] ESP-IDF cloned successfully!\n")
        cfg = load_config()
        cfg["idf_path"] = str(idf_dir)
        save_config(cfg)
    return result.returncode

def cmd_install(args) -> int:
    """Install ESP-IDF environment and dependencies."""
    print("\nInstalling ESP-IDF environment...\n")

    idf_dir = detect_idf()
    if not idf_dir:
        print(NO_IDF)
        return 1

    idf_path = Path(idf_dir)
    platform_type = host_kind()

    # The installer calls idf_tools.py, which refuses to run when MSYSTEM is set.
    env = os.environ.copy()
    env.pop("MSYSTEM", None)

    # Determine install script based on platform
    if platform_type == "windows":
        install_script = idf_path / "install.bat"
        if not install_script.exists():
            print(f"[FAIL] Install script not found: {install_script}")
            return 1
        print(f"Running: {install_script}\n")
        result = subprocess.run(
            ["cmd", "/c", str(install_script)],
            cwd=idf_path,
            env=env
        )
    else:  # WSL2 or Linux
        install_script = idf_path / "install.sh"
        if not install_script.exists():
            print(f"[FAIL] Install script not found: {install_script}")
            return 1
        print(f"Running: {install_script}\n")
        # Make script executable
        os.chmod(install_script, 0o755)
        result = subprocess.run(
            [str(install_script)],
            cwd=idf_path,
            env=env
        )

    if result.returncode == 0:
        print("\n[OK] ESP-IDF environment installed successfully!")
        print("\nNext: ubx-sdk nora-w40 --build hello_world   (the launcher sets up the ESP-IDF environment)\n")
    return result.returncode

def detect_idf_python(idf_dir):
    """Find ESP-IDF's own Python env; idf.py cannot run from the repo venv.

    Installs vary between a Scripts/ and a bin/ layout, and a stale env may sit
    beside a good one, so candidates are validated with ESP-IDF's own checker.
    """
    bases = []
    explicit = os.environ.get("IDF_PYTHON_ENV_PATH")
    if explicit:
        bases.append(Path(explicit))
    tools_path = os.environ.get("IDF_TOOLS_PATH")
    root = Path(tools_path) if tools_path else Path.home() / ".espressif"
    bases.extend(sorted((root / "python_env").glob("*_env"), reverse=True))

    checker = Path(idf_dir) / "tools" / "idf_tools.py"
    probe_env = os.environ.copy()
    probe_env["IDF_PATH"] = idf_dir
    probe_env.pop("MSYSTEM", None)

    for base in bases:
        for rel in ("Scripts/python.exe", "bin/python.exe", "bin/python3", "bin/python"):
            exe = base / rel
            if not exe.is_file():
                continue
            if not checker.is_file():
                return str(exe)
            probe = subprocess.run(
                [str(exe), str(checker), "check-python-dependencies"],
                capture_output=True, env=probe_env,
            )
            if probe.returncode == 0:
                return str(exe)
    return None


def idf_environment(idf_dir, idf_python):
    """Build the environment export.sh would set up, so the toolchain is on PATH."""
    env = os.environ.copy()
    env["IDF_PATH"] = idf_dir
    # idf.py and idf_tools.py hard-refuse to run when MSYSTEM is set. Git Bash
    # re-injects it into native child processes, but an explicit env block wins.
    env.pop("MSYSTEM", None)
    idf_tools = Path(idf_dir) / "tools" / "idf_tools.py"
    if not idf_tools.is_file():
        return env

    result = subprocess.run(
        [idf_python, str(idf_tools), "export", "--format", "key-value"],
        capture_output=True, text=True, env=env,
    )
    if result.returncode != 0:
        return env

    for line in result.stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.replace("%PATH%", env.get("PATH", ""))
        value = value.replace("$PATH", env.get("PATH", ""))
        env[key] = value
    return env


def current_target(example_path):
    """Read CONFIG_IDF_TARGET out of an example's generated sdkconfig."""
    sdkconfig = example_path / "sdkconfig"
    if not sdkconfig.is_file():
        return None
    for line in sdkconfig.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("CONFIG_IDF_TARGET="):
            return line.split("=", 1)[1].strip().strip('"')
    return None


def resolve_example(idf_dir, name):
    """Map an example name to its directory.

    ESP-IDF nests examples under a category ('get-started/hello_world'), so a
    bare leaf name is also searched for recursively.
    Returns (path, None) on success or (None, message) on failure.
    """
    examples_root = Path(idf_dir) / "examples"
    if not examples_root.is_dir():
        return None, f"Examples directory not found at {examples_root}"

    direct = examples_root / name
    if (direct / "CMakeLists.txt").is_file():
        return direct, None

    leaf = Path(name).name
    matches = sorted(
        p.parent for p in examples_root.rglob(f"{leaf}/CMakeLists.txt")
    )
    if len(matches) == 1:
        return matches[0], None
    if not matches:
        return None, (
            f"Example '{name}' not found under {examples_root}.\n"
            "       Run 'ubx-sdk nora-w40 --list' to see what is available."
        )

    # Real examples live near the top; deeper hits are build-system fixtures.
    def depth(p):
        return len(p.relative_to(examples_root).parts)

    best = min(depth(m) for m in matches)
    top = [m for m in matches if depth(m) == best]
    if len(top) == 1:
        return top[0], None

    listing = "\n".join(
        f"         {m.relative_to(examples_root).as_posix()}" for m in top
    )
    return None, (
        f"Example '{name}' is ambiguous, {len(top)} matches:\n{listing}\n"
        "       Re-run with the full path shown above."
    )


def cmd_build(args) -> int:
    """Build example application."""
    if not args.example:
        print("[FAIL] Please specify an example name (e.g., 'hello_world')")
        return 1

    idf_dir = detect_idf()
    if not idf_dir:
        print(NO_IDF)
        return 1

    example_path, error = resolve_example(idf_dir, args.example)
    if error:
        print(f"[FAIL] {error}")
        return 1

    print(f"\nBuilding example: {args.example}\n")

    idf_python = detect_idf_python(idf_dir)
    if not idf_python:
        print(NO_IDF_PYTHON)
        return 1

    env = idf_environment(idf_dir, idf_python)

    # Use full path to idf.py
    idf_py = Path(idf_dir) / "tools" / "idf.py"
    if not idf_py.exists():
        print(f"[FAIL] idf.py not found at {idf_py}")
        return 1

    # Without this idf.py would silently default to the original ESP32.
    if current_target(example_path) != IDF_TARGET:
        print(f"Setting target to {IDF_TARGET}...")
        result = subprocess.run(
            [idf_python, str(idf_py), "set-target", IDF_TARGET],
            cwd=example_path,
            env=env
        )
        if result.returncode != 0:
            print(f"[FAIL] Could not set target to {IDF_TARGET}.")
            return result.returncode

    result = subprocess.run(
        [idf_python, str(idf_py), "build"],
        cwd=example_path,
        env=env
    )

    return result.returncode

def cmd_clean(args) -> int:
    """Clean build artifacts."""
    print("\nCleaning build artifacts...\n")

    if args.all:
        # Remove entire ESP-IDF directory
        idf_dir = detect_idf()
        if idf_dir and Path(idf_dir).exists():
            if not target_paths.is_fetched(idf_dir):
                print(f"[FAIL] {idf_dir} is your own ESP-IDF, not one fetched by --clone; not removing it.\n")
                return 1
            print(f"Removing: {idf_dir}")
            shutil.rmtree(idf_dir)
            # Clear config
            cfg = load_config()
            cfg.pop("idf_path", None)
            save_config(cfg)
            print("[OK] ESP-IDF removed.\n")
        else:
            print("[INFO] ESP-IDF not found.\n")
        return 0

    # Clean build directory for current example
    if not args.example:
        print("[INFO] Specify example to clean, or use --all to remove ESP-IDF.\n")
        return 0

    idf_dir = detect_idf()
    if not idf_dir:
        print("[FAIL] ESP-IDF not found.\n")
        return 1

    example_path, error = resolve_example(idf_dir, args.example)
    if error:
        print(f"[FAIL] {error}")
        return 1

    build_dir = example_path / "build"

    if build_dir.exists():
        print(f"Removing: {build_dir}")
        shutil.rmtree(build_dir)
        print("[OK] Build directory cleaned.\n")
    else:
        print(f"[INFO] Build directory not found: {build_dir}\n")

    return 0

def cmd_list(args) -> int:
    """List available examples."""
    idf_dir = detect_idf()
    if not idf_dir:
        print("[FAIL] ESP-IDF not found.")
        return 1

    examples_path = Path(idf_dir) / "examples"
    if not examples_path.exists():
        print("[FAIL] Examples directory not found.")
        return 1

    print("\nAvailable Examples:\n")

    # Search recursively for CMakeLists.txt files
    found = False
    for cmake_file in sorted(examples_path.rglob("CMakeLists.txt")):
        example_dir = cmake_file.parent
        # Calculate relative path from examples folder
        rel_path = example_dir.relative_to(examples_path)
        # Only show directories with CMakeLists.txt (not nested cmake from components, etc)
        depth = len(rel_path.parts)
        if depth <= 2:  # Limit to /category/example level
            print(f"  - {rel_path}")
            found = True

    if not found:
        print("  (No examples found)")
    print()
    return 0

def _idf_invoke(args, verb: str, extra: list) -> int:
    """Run an idf.py verb inside an example directory."""
    idf_dir = detect_idf()
    if not idf_dir:
        print(NO_IDF)
        return 1

    example_path, error = resolve_example(idf_dir, args.example)
    if error:
        print(f"[FAIL] {error}")
        return 1

    idf_python = detect_idf_python(idf_dir)
    if not idf_python:
        print(NO_IDF_PYTHON)
        return 1

    idf_py = Path(idf_dir) / "tools" / "idf.py"
    if not idf_py.exists():
        print(f"[FAIL] idf.py not found at {idf_py}")
        return 1

    cmd = [idf_python, str(idf_py)]
    if args.serial:
        cmd += ["-p", args.serial]
    cmd += [verb, *extra]
    return subprocess.run(cmd, cwd=example_path, env=idf_environment(idf_dir, idf_python)).returncode


def cmd_flash(args) -> int:
    """Flash a built example over the ESP32-C6 USB/UART bootloader."""
    print(f"\nNORA-W40 Flash Utility: {args.example}\n")
    return _idf_invoke(args, "flash", [])


def cmd_log(args) -> int:
    """Open the ESP-IDF serial monitor."""
    print("\nNORA-W40 Serial Monitor (Ctrl+] to exit)\n")
    return _idf_invoke(args, "monitor", [])


def cmd_all(args) -> int:
    """Full pipeline: clone -> install -> build."""
    steps = [
        ("Clone ESP-IDF", lambda: cmd_clone(args)),
        ("Install ESP-IDF Environment", lambda: cmd_install(args)),
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
        description="NORA-W40 (ESP32-C6) Build Driver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python nora_w40_build.py doctor              # Check environment
  python nora_w40_build.py clone               # Clone ESP-IDF
  python nora_w40_build.py install             # Install ESP-IDF environment
  python nora_w40_build.py list                # List examples
  python nora_w40_build.py build hello_world   # Build example
  python nora_w40_build.py flash hello_world   # Flash over USB/UART
  python nora_w40_build.py log hello_world     # Open serial monitor
  python nora_w40_build.py clean hello_world   # Clean example build
  python nora_w40_build.py clean --all         # Remove ESP-IDF entirely
  python nora_w40_build.py all hello_world     # Full pipeline
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    subparsers.add_parser("doctor", help="Verify toolchain")
    clone_parser = subparsers.add_parser("clone", help="Clone ESP-IDF")
    clone_parser.add_argument("--revision", help="branch or tag, e.g. v5.5.1 (default: master), fetched into sdks/esp-idf/<revision>")
    subparsers.add_parser("install", help="Install ESP-IDF environment")
    subparsers.add_parser("list", help="List examples")

    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    clean_parser.add_argument("example", nargs="?", help="Example name (optional)")
    clean_parser.add_argument("--all", action="store_true", help="Remove entire ESP-IDF")

    build_parser = subparsers.add_parser("build", help="Build example")
    build_parser.add_argument("example", help="Example name")

    flash_parser = subparsers.add_parser("flash", help="Flash example to the board")
    flash_parser.add_argument("example", help="Example name")
    flash_parser.add_argument("--serial", help="Serial port (auto-detected if omitted)")

    log_parser = subparsers.add_parser("log", help="Open the ESP-IDF serial monitor")
    log_parser.add_argument("example", nargs="?", default="hello_world", help="Example name")
    log_parser.add_argument("--serial", help="Serial port (auto-detected if omitted)")

    all_parser = subparsers.add_parser("all", help="Full pipeline")
    all_parser.add_argument("example", help="Example name")

    args = parser.parse_args()

    commands = {
        "doctor": cmd_doctor,
        "clone": cmd_clone,
        "install": cmd_install,
        "list": cmd_list,
        "clean": cmd_clean,
        "build": cmd_build,
        "flash": cmd_flash,
        "log": cmd_log,
        "all": cmd_all,
    }

    if not args.command:
        parser.print_help()
        return 0

    return commands[args.command](args)

if __name__ == "__main__":
    sys.exit(target_paths.run_main(main))
