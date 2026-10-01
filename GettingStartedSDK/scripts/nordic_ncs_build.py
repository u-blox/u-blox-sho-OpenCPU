#!/usr/bin/env python3
"""
nRF Connect SDK (NCS) build driver for u-blox Nordic-based Open CPU modules.

One driver serves every NCS target because they differ only in board target and
J-Link device; the toolchain, west workspace layout and build verbs are
identical. The target key is the first positional argument, matching the way
matter_build.py is invoked by the launcher:

    python scripts/nordic_ncs_build.py nora-b2 build hello_world

Supports: Windows, WSL2, Linux, macOS
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import target_paths

# Latest NCS general-availability release. Pinned rather than tracking main so a
# clone is reproducible.
NCS_REVISION = "v3.4.1"
NCS_MANIFEST_URL = "https://github.com/nrfconnect/sdk-nrf"
WORKSPACE_NAME = "ncs"


@dataclass(frozen=True)
class NcsTarget:
    key: str
    slug: str
    label: str
    soc: str
    board: str
    jlink_device: str
    default_example: str
    variants: tuple
    note: str = ""


TARGETS: Dict[str, NcsTarget] = {
    "nora-b2": NcsTarget(
        key="nora-b2",
        slug="nora_b2",
        label="NORA-B2 (Nordic nRF54L15/L10/L05)",
        soc="nRF54L15",
        board="ubx_evknorab2/nrf54l15/cpuapp",
        jlink_device="nRF54L15_M33",
        default_example="hello_world",
        # NORA-B20x -> nRF54L15, B21x -> nRF54L10, B22x -> nRF54L05.
        variants=(
            "ubx_evknorab2/nrf54l15/cpuapp",
            "ubx_evknorab2/nrf54l15/cpuapp/ns",
            "ubx_evknorab2/nrf54l10/cpuapp",
            "ubx_evknorab2/nrf54l10/cpuapp/ns",
            "ubx_evknorab2/nrf54l05/cpuapp",
            "ubx_evknorab2/nrf54l15/cpuflpr",
            "ubx_evknorab2/nrf54l10/cpuflpr",
            "ubx_evknorab2/nrf54l05/cpuflpr",
        ),
        note="EVK-NORA-B201 / EVK-NORA-B206. Board is upstream in Zephyr and NCS.",
    ),
    "alma-b2": NcsTarget(
        key="alma-b2",
        slug="alma_b2",
        label="ALMA-B2 (Nordic nRF54LM20A/B)",
        soc="nRF54LM20",
        # u-blox has not published ubx_evkalmab2 yet; Nordic's DK is the
        # documented stand-in and is pin-compatible enough to bring code up.
        board="nrf54lm20dk/nrf54lm20a/cpuapp",
        jlink_device="nRF54LM20A_M33",
        default_example="hello_world",
        variants=(
            "nrf54lm20dk/nrf54lm20a/cpuapp",
            "nrf54lm20dk/nrf54lm20a/cpuapp/ns",
            "nrf54lm20dk/nrf54lm20b/cpuapp",
            "nrf54lm20dk/nrf54lm20b/cpuapp/ns",
            "nrf54lm20dk/nrf54lm20a/cpuflpr",
            "nrf54lm20dk/nrf54lm20b/cpuflpr",
        ),
        note="Module is under development. No ubx_evkalmab2 board yet - "
             "builds fall back to Nordic's nRF54LM20 DK board target.",
    ),
}

ALIASES = {
    "norab2": "nora-b2", "nora_b2": "nora-b2",
    "almab2": "alma-b2", "alma_b2": "alma-b2",
}

# Where samples are searched for, in priority order, relative to the workspace.
SAMPLE_ROOTS = ("nrf/samples", "nrf/applications", "zephyr/samples")


def resolve_target(name: str) -> Optional[NcsTarget]:
    key = name.lower().replace("_", "-")
    key = ALIASES.get(key.replace("-", ""), ALIASES.get(key, key))
    return TARGETS.get(key)


# ============================================================================
# PLATFORM & ENVIRONMENT DETECTION
# ============================================================================

def host_kind() -> str:
    """Detect platform type: 'windows', 'wsl', 'linux' or 'macos'."""
    system = platform.system()
    if system == "Windows":
        return "windows"
    if system == "Darwin":
        return "macos"
    try:
        content = Path("/proc/version").read_text(encoding="utf-8", errors="replace").upper()
        if "WSL" in content or "MICROSOFT" in content:
            return "wsl"
    except OSError:
        pass
    return "linux"


def which(name: str) -> Optional[str]:
    return shutil.which(name)


def detect_git() -> Optional[str]:
    return which("git")


def detect_cmake() -> Optional[str]:
    return which("cmake")


def detect_ninja() -> Optional[str]:
    return which("ninja")


def detect_west() -> Optional[List[str]]:
    """west as an executable, or via the active interpreter as a fallback."""
    found = which("west")
    if found:
        return [found]
    probe = subprocess.run([sys.executable, "-m", "west", "--version"],
                           capture_output=True, text=True)
    if probe.returncode == 0:
        return [sys.executable, "-m", "west"]
    return None


def detect_nrfutil() -> Optional[str]:
    return which("nrfutil")


def detect_toolchain() -> Optional[str]:
    """Zephyr SDK or an Arm GNU toolchain, whichever the host has."""
    sdk = os.environ.get("ZEPHYR_SDK_INSTALL_DIR")
    if sdk and Path(sdk).is_dir():
        return f"Zephyr SDK at {sdk}"
    gnuarm = os.environ.get("GNUARMEMB_TOOLCHAIN_PATH")
    if gnuarm and Path(gnuarm).is_dir():
        return f"Arm GNU toolchain at {gnuarm}"
    gcc = which("arm-zephyr-eabi-gcc") or which("arm-none-eabi-gcc")
    if gcc:
        return gcc
    for root in (Path.home() / "zephyr-sdk", Path.home() / "ncs" / "toolchains",
                 Path("/opt/zephyr-sdk")):
        if root.is_dir():
            return str(root)
    return None


def detect_workspace(target: NcsTarget) -> Optional[str]:
    """Locate the west workspace (the directory holding .west/)."""
    cfg = load_config(target)
    if "workspace" in cfg and (Path(cfg["workspace"]) / ".west").exists():
        return cfg["workspace"]

    candidates = (
        target_paths.sdk_dir(target.slug) / WORKSPACE_NAME,
        target_paths.SDK_ROOT / WORKSPACE_NAME,
        Path.home() / "ncs",
    )
    for candidate in candidates:
        if (candidate / ".west").exists():
            return str(candidate)
    return None


# ============================================================================
# CONFIGURATION CACHE
# ============================================================================

def config_file(target: NcsTarget) -> Path:
    return target_paths.resolve_config(target.slug, host_kind())


def load_config(target: NcsTarget) -> Dict:
    path = config_file(target)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def save_config(target: NcsTarget, cfg: Dict) -> None:
    path = config_file(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


# ============================================================================
# EXAMPLES
# ============================================================================

def is_sample(path: Path) -> bool:
    return (path / "CMakeLists.txt").exists() and (path / "prj.conf").exists()


def resolve_example(workspace: str, name: str) -> Optional[Path]:
    """Map a sample name or relative path to a directory in the workspace.

    Prints the reason on failure and returns None.
    """
    root = Path(workspace)

    direct = root / name
    if is_sample(direct):
        return direct

    for rel in SAMPLE_ROOTS:
        candidate = root / rel / name
        if is_sample(candidate):
            return candidate

    matches = []
    for rel in SAMPLE_ROOTS:
        base = root / rel
        if not base.is_dir():
            continue
        matches += [p for p in base.rglob(name) if p.is_dir() and is_sample(p)]

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"[FAIL] '{name}' is ambiguous. Re-run with one of these paths:")
        for m in sorted(matches):
            print(f"     {m.relative_to(root).as_posix()}")
        return None

    print(f"[FAIL] Sample '{name}' not found. Try 'list' to see what is available.")
    return None


def build_dir(workspace: str, example_path: Path) -> Path:
    return Path(workspace) / "build" / example_path.name


# ============================================================================
# COMMANDS
# ============================================================================

def cmd_doctor(target: NcsTarget, args) -> int:
    print(f"\n=== {target.label} ===")
    print(f"Host:        {host_kind()}")
    print(f"SoC:         {target.soc}")
    print(f"Board:       {target.board}")
    print(f"NCS:         {NCS_REVISION}")
    if target.note:
        print(f"Note:        {target.note}")
    print()

    checks = [
        ("git", detect_git()),
        ("cmake", detect_cmake()),
        ("ninja", detect_ninja()),
        ("west", " ".join(detect_west() or []) or None),
        ("toolchain", detect_toolchain()),
    ]
    missing = []
    for name, value in checks:
        if value:
            print(f"[OK] {name:<12} {value}")
        else:
            print(f"[FAIL] {name:<12} not found")
            missing.append(name)

    nrfutil = detect_nrfutil()
    print(f"[{'OK' if nrfutil else 'WARNING'}] {'nrfutil':<12} "
          f"{nrfutil or 'not found (needed only for --flash)'}")

    workspace = detect_workspace(target)
    if workspace:
        print(f"\n[OK] NCS workspace   {workspace}")
    else:
        print(f"\n[FAIL] NCS workspace not found. "
              f"Run: python nordic_ncs_build.py {target.key} clone")
        missing.append("workspace")

    if missing:
        print(f"\n[WARNING] Missing: {', '.join(missing)}")
        print("          Install the nRF Connect SDK toolchain via nRF Connect for "
              "Desktop (Toolchain Manager),")
        print("          or see docs/nora_b2_README.md for a manual setup.\n")
        return 1

    print("\n[OK] Ready to build.\n")
    return 0


def cmd_clone(target: NcsTarget, args) -> int:
    west = detect_west()
    if not west:
        print("[FAIL] west not found. Run: python scripts/setup_venv.py")
        return 1

    workspace = Path(args.workspace) if args.workspace else \
        target_paths.sdk_dir(target.slug) / WORKSPACE_NAME

    if (workspace / ".west").exists():
        print(f"[INFO] {workspace} already initialised. Skipping west init.\n")
    else:
        workspace.mkdir(parents=True, exist_ok=True)
        print(f"Initialising nRF Connect SDK {args.revision} in {workspace}")
        print("This downloads several GB and takes a while.\n")
        rc = subprocess.call(
            [*west, "init", "-m", NCS_MANIFEST_URL, "--mr", args.revision, str(workspace)]
        )
        if rc != 0:
            print("[FAIL] west init failed.")
            return rc

    print("\nRunning west update...\n")
    rc = subprocess.call([*west, "update"], cwd=str(workspace))
    if rc != 0:
        print("[FAIL] west update failed.")
        return rc

    subprocess.call([*west, "zephyr-export"], cwd=str(workspace))

    cfg = load_config(target)
    cfg["workspace"] = str(workspace)
    cfg["revision"] = args.revision
    save_config(target, cfg)

    print(f"\n[OK] nRF Connect SDK {args.revision} ready at {workspace}\n")
    return 0


def cmd_install(target: NcsTarget, args) -> int:
    """Install the Python requirements the NCS workspace declares."""
    workspace = detect_workspace(target)
    if not workspace:
        print(f"[FAIL] NCS workspace not found. "
              f"Run: python nordic_ncs_build.py {target.key} clone")
        return 1

    requirements = Path(workspace) / "zephyr" / "scripts" / "requirements.txt"
    if not requirements.exists():
        print(f"[FAIL] Requirements file not found: {requirements}")
        return 1

    print(f"Installing Zephyr Python requirements from {requirements}\n")
    rc = subprocess.call([sys.executable, "-m", "pip", "install", "-r", str(requirements)])
    if rc != 0:
        print("[FAIL] pip install failed.")
        return rc

    if not detect_toolchain():
        print("\n[WARNING] No Arm toolchain detected.")
        print("          Install the Zephyr SDK, or the nRF Connect SDK toolchain")
        print("          bundle via nRF Connect for Desktop > Toolchain Manager.")

    print("\n[OK] Python environment ready.\n")
    return 0


def cmd_list(target: NcsTarget, args) -> int:
    workspace = detect_workspace(target)
    if not workspace:
        print(f"[FAIL] NCS workspace not found. "
              f"Run: python nordic_ncs_build.py {target.key} clone")
        return 1

    root = Path(workspace)
    print(f"\nSamples available for {target.label}:\n")
    found = False
    for rel in SAMPLE_ROOTS:
        base = root / rel
        if not base.is_dir():
            continue
        samples = sorted(p for p in base.rglob("prj.conf") if is_sample(p.parent))
        if not samples:
            continue
        print(f"  {rel}/")
        for sample in samples:
            print(f"    {sample.parent.relative_to(base).as_posix()}")
            found = True
        print()

    if not found:
        print("  (none found)\n")
        return 1

    print(f"Build with: --build <name>   (default: {target.default_example})\n")
    return 0


def cmd_build(target: NcsTarget, args) -> int:
    workspace = detect_workspace(target)
    if not workspace:
        print(f"[FAIL] NCS workspace not found. "
              f"Run: python nordic_ncs_build.py {target.key} clone")
        return 1

    west = detect_west()
    if not west:
        print("[FAIL] west not found. Run: python scripts/setup_venv.py")
        return 1

    example_path = resolve_example(workspace, args.example or target.default_example)
    if not example_path:
        return 1

    board = args.board or target.board
    if board not in target.variants:
        print(f"[WARNING] '{board}' is not a known {target.key} board target.")
        print(f"          Known: {', '.join(target.variants)}")

    out = build_dir(workspace, example_path)
    rel = example_path.relative_to(workspace).as_posix()
    print(f"\nBuilding {rel} for {board}...\n")

    cmd = [*west, "build", "-b", board, "-d", str(out)]
    if args.clean:
        cmd.append("--pristine")
    cmd += [str(example_path), *args.extra]

    rc = subprocess.call(cmd, cwd=workspace)
    if rc != 0:
        print(f"\n[FAIL] Build failed (exit {rc}).\n")
        return rc

    cfg = load_config(target)
    cfg["last_example"] = rel
    cfg["last_board"] = board
    save_config(target, cfg)

    print(f"\n[OK] Build complete. Artifacts in {out / 'zephyr'}\n")
    return 0


def cmd_clean(target: NcsTarget, args) -> int:
    workspace = detect_workspace(target)
    if not workspace:
        print("[INFO] NCS workspace not found; nothing to clean.\n")
        return 0

    if args.all:
        print(f"Removing: {workspace}")
        shutil.rmtree(workspace, ignore_errors=True)
        cfg = load_config(target)
        cfg.pop("workspace", None)
        save_config(target, cfg)
        print("[OK] nRF Connect SDK removed.\n")
        return 0

    root = Path(workspace) / "build"
    if args.example:
        example_path = resolve_example(workspace, args.example)
        if not example_path:
            return 1
        root = build_dir(workspace, example_path)

    if not root.exists():
        print(f"[INFO] Build directory not found: {root}\n")
        return 0

    print(f"Removing: {root}")
    shutil.rmtree(root, ignore_errors=True)
    print("[OK] Build artifacts cleaned.\n")
    return 0


def cmd_flash(target: NcsTarget, args) -> int:
    workspace = detect_workspace(target)
    if not workspace:
        print(f"[FAIL] NCS workspace not found. "
              f"Run: python nordic_ncs_build.py {target.key} clone")
        return 1

    west = detect_west()
    if not west:
        print("[FAIL] west not found. Run: python scripts/setup_venv.py")
        return 1

    example_path = resolve_example(workspace, args.example or target.default_example)
    if not example_path:
        return 1

    out = build_dir(workspace, example_path)
    if not out.exists():
        print(f"[FAIL] Build directory not found: {out}")
        print(f"       Build first: --build {example_path.name}")
        return 1

    print(f"\nFlashing {example_path.name} via {args.runner} ({target.jlink_device})\n")
    cmd = [*west, "flash", "-d", str(out), "-r", args.runner]
    if args.serial:
        # Both runners take the probe/segger id under the same option name.
        cmd += ["--dev-id", args.serial]
    rc = subprocess.call(cmd, cwd=workspace)
    if rc != 0:
        print(f"\n[FAIL] Flash failed (exit {rc}).\n")
    return rc


def cmd_log(target: NcsTarget, args) -> int:
    print(f"\n{target.label} Serial Monitor ({args.baudrate} baud)")
    print("   Use Ctrl+C to exit\n")

    import serial_logger
    return serial_logger.open_serial_monitor(args.port, args.baudrate)


# ============================================================================
# CLI
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="nordic_ncs_build.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("target", help=f"one of: {', '.join(TARGETS)}")
    sub = p.add_subparsers(dest="command", required=True)

    def add(name, func, help_text):
        sp = sub.add_parser(name, help=help_text)
        sp.set_defaults(func=func)
        return sp

    add("doctor", cmd_doctor, "show host, toolchain and workspace status")

    sp = add("clone", cmd_clone, "fetch the nRF Connect SDK with west")
    sp.add_argument("--revision", default=NCS_REVISION,
                    help=f"NCS tag or branch (default: {NCS_REVISION})")
    sp.add_argument("--workspace", help="where the west workspace is created")

    add("install", cmd_install, "install the Zephyr Python requirements")
    add("list", cmd_list, "list available samples")

    sp = add("build", cmd_build, "build a sample")
    sp.add_argument("example", nargs="?", help="sample name or path")
    sp.add_argument("--board", help="override the board target")
    sp.add_argument("--clean", action="store_true", help="pristine build")
    sp.add_argument("extra", nargs="*", help="extra arguments passed to west build")

    sp = add("clean", cmd_clean, "remove build artifacts")
    sp.add_argument("example", nargs="?", help="sample name (all builds if omitted)")
    sp.add_argument("--all", action="store_true", help="remove the whole NCS workspace")

    sp = add("flash", cmd_flash, "flash a built sample")
    sp.add_argument("example", nargs="?", help="sample name or path")
    sp.add_argument("--serial", help="debug probe serial number")
    sp.add_argument("--runner", default="nrfutil", choices=["nrfutil", "jlink"],
                    help="west runner (default: nrfutil)")

    sp = add("log", cmd_log, "open the serial monitor")
    sp.add_argument("port", nargs="?", default=None,
                    help="serial port (auto-detected if omitted)")
    sp.add_argument("--baudrate", type=int, default=115200)

    return p


def main() -> int:
    args = build_parser().parse_args()
    target = resolve_target(args.target)
    if target is None:
        print(f"[FAIL] Unknown target: {args.target}")
        print(f"       Known targets: {', '.join(TARGETS)}")
        return 1
    target_paths.ensure(target.slug)
    try:
        return args.func(target, args) or 0
    except KeyboardInterrupt:
        print("\n[WARNING] Interrupted.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
