#!/usr/bin/env python3
"""
nRF Connect SDK (NCS) build driver for u-blox Nordic-based Open CPU modules.

One driver serves every NCS target because they differ only in board target and
J-Link device; the toolchain, west workspace layout and build verbs are
identical. The target key is the first positional argument, matching the way
matter_build.py is invoked by the launcher:

    python scripts/nordic_ncs_build.py nora-b20-b21-b22 build hello_world

Supports: Windows, WSL2, Linux, macOS
"""

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import target_paths
from target_paths import host_kind

# Latest NCS general-availability release. Pinned rather than tracking main so a
# clone is reproducible.
NCS_REVISION = "v3.4.1"
NCS_MANIFEST_URL = "https://github.com/nrfconnect/sdk-nrf"
WORKSPACE_NAME = "ncs"
# Approximate size of a full west update plus a few builds.
NCS_SIZE_GB = 15
# Points at an existing workspace and overrides detection.
WORKSPACE_ENV = "UBX_NCS_WORKSPACE"


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
    "nora-b20-b21-b22": NcsTarget(
        key="nora-b20-b21-b22",
        slug="nora_b20_b21_b22",
        label="NORA-B20-B21-B22 (Nordic nRF54L15/L10/L05)",
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
    "alma-b20-b21": NcsTarget(
        key="alma-b20-b21",
        slug="alma_b20_b21",
        label="ALMA-B20-B21 (Nordic nRF54LM20A/B)",
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

# Where samples are searched for, in priority order, relative to the workspace.
SAMPLE_ROOTS = ("nrf/samples", "nrf/applications", "zephyr/samples")


def resolve_target(name: str) -> Optional[NcsTarget]:
    return TARGETS.get(name.lower().replace("_", "-"))


WEST_MISSING = "[FAIL] west not found. Run: ubx-sdk --setup-venv, or install nRF Connect for Desktop."


def no_workspace(target: NcsTarget) -> str:
    return f"[FAIL] NCS workspace not found. Run: ubx-sdk {target.key} --clone"


# ============================================================================
# PLATFORM & ENVIRONMENT DETECTION
# ============================================================================

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
                 Path(os.environ.get("SystemDrive", "C:") + "/") / "ncs" / "toolchains",
                 Path("/opt/zephyr-sdk")):
        if root.is_dir():
            return str(root)
    return None


def default_workspace(revision: str = NCS_REVISION) -> Path:
    """Where clone puts a new workspace: <drive>/ncs/<rev> like Nordic's own tools, never the repo drive."""
    if host_kind() == "windows":
        return Path(os.environ.get("SystemDrive", "C:") + "/") / "ncs" / revision
    home_ncs = Path.home() / "ncs"
    # A workspace cannot be nested inside another west workspace.
    if (home_ncs / ".west").exists():
        return Path.home() / f"ncs-{revision}"
    return home_ncs / revision


def _workspace_candidates(target: NcsTarget) -> List[Path]:
    paths: List[Path] = []
    cfg = load_config(target)
    if cfg.get("workspace"):
        paths.append(Path(cfg["workspace"]))
    if os.environ.get("ZEPHYR_BASE"):
        paths.append(Path(os.environ["ZEPHYR_BASE"]).parent)
    roots = [Path(os.environ.get("SystemDrive", "C:") + "/") / "ncs"] if host_kind() == "windows" else []
    roots += [Path.home() / "ncs"]
    for root in roots:
        paths.append(root)
        if root.is_dir():
            paths += sorted(root.iterdir(), reverse=True)
    paths += sorted(Path.home().glob("ncs-*"), reverse=True)
    paths += [*target_paths.installed_sdks(target.slug), target_paths.SDK_ROOT / WORKSPACE_NAME]
    return paths


def find_workspaces(target: NcsTarget) -> List[Path]:
    """Every west workspace on this host that looks like an NCS checkout, deduplicated."""
    found, seen = [], set()
    for path in _workspace_candidates(target):
        try:
            key = path.resolve()
        except OSError:
            continue
        if key in seen or not (path / ".west").exists() or not (path / "nrf").is_dir():
            continue
        seen.add(key)
        found.append(path)
    return found


def detect_workspace(target: NcsTarget) -> Optional[str]:
    """The workspace to build in.

    Order: UBX_NCS_WORKSPACE, the one chosen with 'use' or created by 'clone',
    then the best detected one (has the board, preferring the pinned release).
    """
    env = os.environ.get(WORKSPACE_ENV)
    if env:
        return env if (Path(env) / ".west").exists() else None

    cfg = load_config(target)
    if cfg.get("workspace") and (Path(cfg["workspace"]) / ".west").exists():
        return cfg["workspace"]

    workspaces = find_workspaces(target)
    with_board = [w for w in workspaces if board_available(str(w), target.board)]
    for ws in with_board:
        if workspace_revision(str(ws)) == NCS_REVISION:
            return str(ws)
    best = with_board or workspaces
    return str(best[0]) if best else None


# ============================================================================
# CONFIGURATION CACHE
# ============================================================================

def config_file(target: NcsTarget) -> Path:
    return target_paths.resolve_config(target.slug, host_kind())


def load_config(target: NcsTarget) -> Dict:
    return target_paths.load_json(config_file(target))


def save_config(target: NcsTarget, cfg: Dict) -> None:
    target_paths.save_json(config_file(target), cfg)


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


def workspace_revision(workspace: str) -> Optional[str]:
    """NCS release the workspace is on, e.g. 'v2.9.0'."""
    try:
        result = subprocess.run(["git", "-C", str(Path(workspace) / "nrf"), "describe", "--tags"],
                                capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def board_available(workspace: str, board: str) -> bool:
    """True when the board's definition exists in the workspace's board roots."""
    name = board.split("/")[0]
    root = Path(workspace)
    return any(any((root / rel).glob(f"*/{name}")) for rel in ("zephyr/boards", "nrf/boards"))


def missing_board_hint(target: NcsTarget, workspace: str, board: str) -> None:
    found = workspace_revision(workspace) or "unknown version"
    print(f"[FAIL] Board '{board.split('/')[0]}' is not in the NCS workspace at {workspace} ({found}).")
    print(f"       It needs a newer NCS. Fetch the pinned {NCS_REVISION} into {default_workspace()} with:")
    print(f"         ubx-sdk {target.key} --clone")
    print(f"       or select another workspace: python scripts/nordic_ncs_build.py {target.key} use <path>")
    print(f"       (or set {WORKSPACE_ENV}=<path>)")


# ============================================================================
# COMMANDS
# ============================================================================

def cmd_doctor(target: NcsTarget, args) -> int:
    print(f"\n=== {target.label} ===")
    print(f"Host:        {host_kind()}")
    print(f"SoC:         {target.soc}")
    print(f"Board:       {target.board}")
    print(f"NCS:         {NCS_REVISION} (pinned)")
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
    others = [w for w in find_workspaces(target) if not workspace or w.resolve() != Path(workspace).resolve()]
    if workspace:
        found = workspace_revision(workspace)
        print(f"\n[OK] NCS workspace   {workspace} ({found or 'version unknown'})")
        if found and found != NCS_REVISION:
            print(f"[WARNING] Workspace is {found}, this SDK is tested with {NCS_REVISION}.")
        if not board_available(workspace, target.board):
            missing_board_hint(target, workspace, target.board)
            missing.append("board")
    else:
        print(f"\n[FAIL] NCS workspace not found. "
              f"Run: ubx-sdk {target.key} --clone   (creates {default_workspace()})")
        missing.append("workspace")

    if others:
        print("\nOther NCS workspaces on this host:")
        for ws in others:
            board = "has board" if board_available(str(ws), target.board) else "no board"
            print(f"  {ws}  ({workspace_revision(str(ws)) or 'version unknown'}, {board})")
        print(f"  Select one with: python scripts/nordic_ncs_build.py {target.key} use <path>")
        print(f"  or set {WORKSPACE_ENV}=<path>")

    if missing:
        print(f"\n[WARNING] Missing: {', '.join(missing)}")
        if set(missing) - {"board", "workspace"}:
            print("          Install the nRF Connect SDK toolchain via nRF Connect for "
                  "Desktop (Toolchain Manager),")
            print("          or see docs/nora_b20_b21_b22_README.md for a manual setup.")
        print()
        return 1

    print("\n[OK] Ready to build.\n")
    return 0


def cmd_clone(target: NcsTarget, args) -> int:
    west = detect_west()
    if not west:
        print(WEST_MISSING)
        return 1

    workspace = Path(args.workspace) if args.workspace else default_workspace(args.revision)

    if (workspace / ".west").exists():
        print(f"[INFO] {workspace} already initialised. Skipping west init.\n")
    else:
        if not target_paths.check_space(workspace, NCS_SIZE_GB, f"nRF Connect SDK {args.revision}"):
            return 1
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


def cmd_use(target: NcsTarget, args) -> int:
    if not args.path:
        current = detect_workspace(target)
        workspaces = find_workspaces(target)
        if not workspaces:
            print(f"[INFO] No NCS workspace found. Run: ubx-sdk {target.key} --clone")
            return 1
        print(f"\nNCS workspaces for {target.label} (board {target.board}):\n")
        for ws in workspaces:
            mark = "*" if current and ws.resolve() == Path(current).resolve() else " "
            board = "has board" if board_available(str(ws), target.board) else "no board"
            print(f" {mark} {ws}  ({workspace_revision(str(ws)) or 'version unknown'}, {board})")
        print("\n * = in use\n")
        return 0

    workspace = Path(args.path).expanduser()
    if not (workspace / ".west").exists():
        print(f"[FAIL] {workspace} is not a west workspace (no .west/ folder).")
        return 1
    if not board_available(str(workspace), target.board):
        missing_board_hint(target, str(workspace), target.board)
        return 1
    cfg = load_config(target)
    cfg["workspace"] = str(workspace)
    save_config(target, cfg)
    print(f"[OK] {target.key} now uses {workspace} ({workspace_revision(str(workspace)) or 'version unknown'})")
    return 0


def cmd_install(target: NcsTarget, args) -> int:
    """Install the Python requirements the NCS workspace declares."""
    workspace = detect_workspace(target)
    if not workspace:
        print(no_workspace(target))
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
        print(no_workspace(target))
        return 1

    only_matter = getattr(args, "matter", False)
    root = Path(workspace)
    kind = "Matter samples" if only_matter else "Samples"
    print(f"\n{kind} available for {target.label}:\n")
    found = False
    for rel in SAMPLE_ROOTS:
        base = root / rel
        if not base.is_dir():
            continue
        samples = sorted(p for p in base.rglob("prj.conf") if is_sample(p.parent))
        if only_matter:
            samples = [p for p in samples
                       if "matter" in p.parent.relative_to(base).parts]
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

    default = "matter/light_bulb" if only_matter else target.default_example
    print(f"Build with: --build <name>   (default: {default})\n")
    return 0


def cmd_build(target: NcsTarget, args) -> int:
    workspace = detect_workspace(target)
    if not workspace:
        print(no_workspace(target))
        return 1

    west = detect_west()
    if not west:
        print(WEST_MISSING)
        return 1

    example_path = resolve_example(workspace, args.example or target.default_example)
    if not example_path:
        return 1

    board = args.board or target.board
    if board not in target.variants:
        print(f"[WARNING] '{board}' is not a known {target.key} board target.")
        print(f"          Known: {', '.join(target.variants)}")
    elif not board_available(workspace, board):
        missing_board_hint(target, workspace, board)
        return 1

    out = build_dir(workspace, example_path)
    rel = example_path.relative_to(workspace).as_posix()
    print(f"\nBuilding {rel} for {board}...\n")

    # Both Nordic targets share <ncs>/build/<sample>; 'auto' starts over when
    # the cached board differs instead of failing.
    cmd = [*west, "build", "-b", board, "-d", str(out),
           "--pristine" if args.clean else "--pristine=auto"]
    # west build takes CMake cache entries only after its own '--'.
    cmake_args = [a for a in args.extra if a.startswith("-D")]
    cmd += [*(a for a in args.extra if not a.startswith("-D")), str(example_path)]
    if cmake_args:
        cmd += ["--", *cmake_args]

    rc = subprocess.call(cmd, cwd=workspace)
    if rc != 0:
        print(f"\n[FAIL] Build failed (exit {rc}).\n")
        return rc

    cfg = load_config(target)
    cfg["last_example"] = rel
    cfg["last_board"] = board
    save_config(target, cfg)

    # Sysbuild nests the application image in <build>/<app>/zephyr.
    images = out / example_path.name / "zephyr"
    artifacts = images if (images / "zephyr.elf").exists() else out / "zephyr"
    print(f"\n[OK] Build complete. Artifacts in {artifacts}\n")
    return 0


def cmd_clean(target: NcsTarget, args) -> int:
    workspace = detect_workspace(target)
    if not workspace:
        print("[INFO] NCS workspace not found; nothing to clean.\n")
        return 0

    if args.all:
        cfg = load_config(target)
        created = cfg.get("revision") and cfg.get("workspace") \
            and Path(cfg["workspace"]).resolve() == Path(workspace).resolve()
        if not created:
            # Detected or selected with 'use': it may belong to nRF Connect for Desktop.
            print(f"[FAIL] {workspace} was not created by 'ubx-sdk {target.key} --clone'; not removing it.")
            print("       Delete it yourself if you no longer need it.")
            return 1
        print(f"Removing: {workspace}")
        shutil.rmtree(workspace, ignore_errors=True)
        cfg.pop("workspace", None)
        cfg.pop("revision", None)
        save_config(target, cfg)
        if Path(workspace).exists():
            print(f"[FAIL] Could not remove everything in {workspace} (files in use?).")
            return 1
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
        print(no_workspace(target))
        return 1

    west = detect_west()
    if not west:
        print(WEST_MISSING)
        return 1

    example_path = resolve_example(workspace, args.example or target.default_example)
    if not example_path:
        return 1

    out = build_dir(workspace, example_path)
    if not out.exists():
        print(f"[FAIL] Build directory not found: {out}")
        print(f"       Build first: --build {example_path.name}")
        return 1

    runner = args.runner or ("nrfutil" if detect_nrfutil() else "jlink")
    print(f"\nFlashing {example_path.name} via {runner} ({target.jlink_device})\n")
    cmd = [*west, "flash", "-d", str(out), "-r", runner]
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
    sp.add_argument("--workspace", help="where the west workspace is created "
                                        "(default: <system drive>/ncs/<revision>)")

    sp = add("use", cmd_use, "select an existing NCS workspace, or list the detected ones")
    sp.add_argument("path", nargs="?", help="workspace directory (the one holding .west/)")

    add("install", cmd_install, "install the Zephyr Python requirements")

    sp = add("list", cmd_list, "list available samples")
    sp.add_argument("--matter", action="store_true",
                    help="list only nrf/samples/matter apps")

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
    sp.add_argument("--runner", choices=["nrfutil", "jlink"],
                    help="west runner (default: nrfutil, or jlink when nrfutil is not installed)")

    sp = add("log", cmd_log, "open the serial monitor")
    sp.add_argument("port", nargs="?", default=None,
                    help="serial port (auto-detected if omitted)")
    sp.add_argument("--baudrate", type=int, default=115200)

    return p


def build_passthrough(argv: List[str]) -> List[str]:
    """Arguments of 'build' meant for west, in the order they were given."""
    out: List[str] = []
    example_seen = False
    rest = argv[2:]
    i = 0
    while i < len(rest):
        arg = rest[i]
        if arg == "--":
            out += rest[i + 1:]
            break
        if arg == "--board":
            i += 2
            continue
        if arg.startswith("--board=") or arg == "--clean":
            pass
        elif not example_seen and not arg.startswith("-"):
            example_seen = True
        else:
            out.append(arg)
        i += 1
    return out


def main() -> int:
    parser = build_parser()
    args, unknown = parser.parse_known_args()
    if args.command == "build":
        # Options this driver does not know (-DCONFIG_X=y, --sysbuild, -S snippet) go to west.
        args.extra = build_passthrough(sys.argv[1:])
    elif unknown:
        parser.error(f"unrecognized arguments: {' '.join(unknown)}")
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
    sys.exit(target_paths.run_main(main))
