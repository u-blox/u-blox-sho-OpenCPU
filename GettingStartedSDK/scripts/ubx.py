#!/usr/bin/env python3
"""
Shared launcher core for every u-blox Getting Started SDK target.

Not run directly. Two thin entry points sit on top of it, each with its own
shim at the SDK root:

    ubx-sdk.cmd / ubx-sdk.sh        -> scripts/ubx_sdk.py     -> main()
    ubx-matter.cmd / ubx-matter.sh  -> scripts/ubx_matter.py  -> main(matter=True)

The flag surface is deliberately uniform across targets; this module translates
it into the subcommands each per-target driver actually understands.

Matter is kept off the plain SDK flag surface because most users never build
it and its SDKs are multi-GB.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SDK_ROOT / "scripts"
MATTER_SCRIPT = SCRIPTS_DIR / "matter_build.py"


@dataclass(frozen=True)
class Target:
    key: str
    label: str
    script: str
    default_example: str
    example_word: str
    linux_only: bool = False
    supports: frozenset[str] = frozenset()


TARGETS: dict[str, Target] = {
    "iris-w10": Target(
        key="iris-w10",
        label="IRIS-W10 (NXP RW612/RW610)",
        script="iris_w10_build.py",
        default_example="demo_apps/hello_world",
        example_word="example",
        supports=frozenset({"doctor", "clone", "install", "list", "clean", "build", "flash", "log"}),
    ),
    "nora-w30": Target(
        key="nora-w30",
        label="NORA-W30 (Realtek RTL872x)",
        script="nora_w30_build.py",
        default_example="project_hp",
        example_word="project",
        linux_only=True,
        supports=frozenset({"doctor", "clone", "install", "list", "clean", "build"}),
    ),
    "nora-w40": Target(
        key="nora-w40",
        label="NORA-W40 (Espressif ESP32-C6)",
        script="nora_w40_build.py",
        default_example="hello_world",
        example_word="example",
        supports=frozenset({"doctor", "clone", "install", "list", "clean", "build"}),
    ),
    "nora-w50-w51": Target(
        key="nora-w50-w51",
        label="NORA-W50/W51 (TI CC35XX)",
        script="nora_w50_w51_build.py",
        default_example="network_terminal",
        example_word="example",
        supports=frozenset({"doctor", "clone", "install", "list", "clean", "build", "build-sdk", "flash", "log"}),
    ),
}

ALIASES = {
    "iris": "iris-w10", "irisw10": "iris-w10", "iris_w10": "iris-w10", "w10": "iris-w10",
    "nora_w30": "nora-w30", "noraw30": "nora-w30", "w30": "nora-w30",
    "nora_w40": "nora-w40", "noraw40": "nora-w40", "w40": "nora-w40",
    "nora-w50": "nora-w50-w51", "nora-w51": "nora-w50-w51",
    "nora_w50_w51": "nora-w50-w51", "w50": "nora-w50-w51", "w51": "nora-w50-w51",
}

# Execution order, independent of the order flags were typed.
ACTION_ORDER = ["doctor", "clone", "install", "build-sdk", "clean", "build", "flash", "log"]


@dataclass
class Context:
    target: Target
    actions: set[str] = field(default_factory=set)
    example: str | None = None
    port: str | None = None
    probe: str | None = None
    full: bool = False
    clean_all: bool = False
    matter: bool = False
    use_wsl: bool | None = None
    extra: list[str] = field(default_factory=list)


USAGE = """
u-blox Getting Started SDK launcher

  ubx-sdk <target> [flags...]

Targets
  iris-w10        IRIS-W10      NXP RW612/RW610      (MCUXpresso / west)
  nora-w30        NORA-W30      Realtek RTL872x      (Linux or WSL2 only)
  nora-w40        NORA-W40      Espressif ESP32-C6   (ESP-IDF)
  nora-w50-w51    NORA-W50/W51  TI CC35XX            (SimpleLink)

Flags (combinable; always run in this order)
  --doctor              Verify host tools for the target
  --clone               Fetch the vendor SDK on demand
    --full                IRIS-W10 only: full SDK instead of RW612 only
  --install             Install/refresh the SDK's own tool environment
  --build-sdk           NORA-W50/W51 only: build the SDK libraries
  --clean               Clean build artifacts
  --clean-all           Remove the fetched SDK entirely
  --build [NAME]        Build an example (target-specific default if omitted)
  --flash [SERIAL]      Flash via the target's debug probe
  --log [PORT]          Open the serial monitor (port auto-detected if omitted)
  --list                List available examples
  --setup-venv          Create/refresh the shared .venv, then exit
  --wsl / --no-wsl      Force or suppress the automatic hop into WSL2
  --                    Pass every remaining argument verbatim to the driver
  --help                Show this help

Examples
  ubx-sdk nora-w40 --clone --install --build hello_world
  ubx-sdk iris-w10 --doctor
  ubx-sdk iris-w10 --build demo_apps/hello_world --flash --log
  ubx-sdk nora-w50-w51 --clone --build-sdk --build network_terminal
  ubx-sdk nora-w30 --build        (hops into WSL2 automatically on Windows)
  ubx-sdk iris-w10 --build hello_world -- --config release

Matter is a separate, optional layer with its own launcher: ubx-matter --help
""".strip()

MATTER_USAGE = """
u-blox Getting Started SDK - Matter launcher

  ubx-matter <target> [flags...]

Optional layer on top of the plain SDK examples. The Matter SDKs are large and
are only fetched when you ask for them; if you are not building Matter, ignore
this launcher and use 'ubx-sdk' instead.

Targets
  iris-w10        NXP RW612        connectedhomeip (NXP rt/rw61x)
  nora-w30        Realtek RTL872x  ameba-rtos-matter
  nora-w40        ESP32-C6         esp-matter
  nora-w50-w51    TI CC35XX        no public Matter SDK yet

Flags (combinable; always run in this order)
  --doctor              Report Matter prerequisites and SDK state
  --clone               Fetch the Matter SDK for this target (several GB)
  --install             Run the app's one-time SDK setup
  --clean               Clean a Matter app
  --build [APP]         Build a Matter app from matter/<TARGET>/
  --list                List the Matter apps available for this target
  --setup-venv          Create/refresh the shared .venv, then exit
  --wsl / --no-wsl      Force or suppress the automatic hop into WSL2
  --help                Show this help

Matter toolchains are Linux-only, so --clone/--install/--build/--clean hop into
WSL2 automatically on Windows. Set UBX_MATTER_ROOT to keep the checkout off a
/mnt/<drive> path. See matter/README.md.

Examples
  ubx-matter nora-w40 --doctor
  ubx-matter nora-w40 --clone
  ubx-matter nora-w40 --list
  ubx-matter nora-w40 --build thermometer
""".strip()


def fail(message: str) -> int:
    print(f"[FAIL] {message}")
    return 1


def resolve_target(name: str) -> Target | None:
    key = ALIASES.get(name.lower(), name.lower())
    return TARGETS.get(key)


def host_is_windows() -> bool:
    return os.name == "nt"


def parse(argv: list[str], matter: bool = False) -> Context | int:
    usage = MATTER_USAGE if matter else USAGE
    name = "ubx-matter" if matter else "ubx-sdk"

    if not argv or argv[0] in ("--help", "-h", "help"):
        print(usage)
        return 0

    if argv[0] == "--setup-venv":
        return run_setup_venv()

    target = resolve_target(argv[0])
    if target is None:
        return fail(f"Unknown target: {argv[0]}\n       Known targets: {', '.join(TARGETS)}")

    ctx = Context(target=target, matter=matter)
    rest = argv[1:]
    i = 0

    def peek() -> str | None:
        """Next token, if it is a value rather than another flag."""
        if i + 1 < len(rest) and not rest[i + 1].startswith("-"):
            return rest[i + 1]
        return None

    while i < len(rest):
        arg = rest[i]
        if arg == "--":
            ctx.extra = rest[i + 1:]
            break
        if arg in ("--help", "-h"):
            print(usage)
            return 0
        if arg == "--setup-venv":
            return run_setup_venv()
        if arg == "--matter":
            others = " ".join(a for a in rest if a != "--matter")
            return fail(f"Matter has its own launcher: ubx-matter {target.key} {others}".rstrip())
        if matter and arg in ("--full", "--build-sdk", "--flash", "--log", "--clean-all"):
            return fail(f"{arg} is an SDK-only flag and has no Matter equivalent.")
        if arg in ("--doctor", "--install", "--list", "--clean", "--build-sdk"):
            ctx.actions.add(arg[2:])
        elif arg == "--clone":
            ctx.actions.add("clone")
        elif arg == "--clean-all":
            ctx.actions.add("clean")
            ctx.clean_all = True
        elif arg == "--full":
            ctx.full = True
        elif arg == "--wsl":
            ctx.use_wsl = True
        elif arg == "--no-wsl":
            ctx.use_wsl = False
        elif arg == "--build":
            ctx.actions.add("build")
            value = peek()
            if value:
                ctx.example = value
                i += 1
        elif arg == "--flash":
            ctx.actions.add("flash")
            value = peek()
            if value:
                ctx.probe = value
                i += 1
        elif arg == "--log":
            ctx.actions.add("log")
            value = peek()
            if value:
                ctx.port = value
                i += 1
        else:
            return fail(f"Unknown argument: {arg}\n       Run '{name} --help' for usage.")
        i += 1

    if not ctx.actions:
        print(usage)
        return 0
    return ctx


def run_setup_venv() -> int:
    return subprocess.call([sys.executable, str(SCRIPTS_DIR / "setup_venv.py")])


MATTER_ACTIONS = frozenset({"doctor", "clone", "install", "list", "build", "clean"})


def argv_for(ctx: Context, action: str) -> list[str] | None:
    """Translate one uniform action into the driver's own subcommand."""
    t = ctx.target
    example = ctx.example or t.default_example

    if ctx.matter:
        if action not in MATTER_ACTIONS:
            print(f"[WARNING] --{action} is not supported for Matter builds; skipping.")
            return None
        if action in ("build", "clean"):
            return [action, ctx.example] if ctx.example else [action]
        return [action]

    if action not in t.supports:
        print(f"[WARNING] --{action} is not supported for {t.label}; skipping.")
        return None

    if action in ("doctor", "install", "list", "build-sdk"):
        return [action]

    if action == "clone":
        argv = ["clone"]
        if ctx.full and t.key == "iris-w10":
            argv.append("--full")
        return argv

    if action == "clean":
        if t.key == "nora-w50-w51" and not ctx.clean_all:
            # No standalone clean subcommand; a clean build is the equivalent.
            return ["build", example, "--clean"]
        argv = ["clean"]
        if ctx.clean_all:
            argv.append("--all")
        return argv

    if action == "build":
        return ["build", example, *ctx.extra]

    if action == "flash":
        argv = ["flash", example]
        if ctx.probe:
            argv += ["--serial", ctx.probe]
        return argv

    if action == "log":
        return ["log", ctx.port] if ctx.port else ["log"]

    return None


def to_wsl_path(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    tail = str(resolved)[len(resolved.drive):].replace("\\", "/")
    return f"/mnt/{drive}{tail}"


def hop_to_wsl(ctx: Context, argv: list[str]) -> int:
    """Re-run this invocation inside WSL2, where the Realtek build works."""
    sdk_wsl = to_wsl_path(SDK_ROOT)
    forwarded = " ".join(f"'{a}'" for a in argv)
    shim = "./ubx-matter.sh" if ctx.matter else "./ubx-sdk.sh"
    print(f"[INFO] {ctx.target.label} builds on Linux; hopping into WSL2.")
    print(f"[INFO] WSL path: {sdk_wsl}")
    command = f"cd '{sdk_wsl}' && {shim} {forwarded}"
    return subprocess.call(["wsl", "--", "bash", "-lc", command])


def needs_linux(ctx: Context) -> bool:
    if ctx.target.linux_only:
        return True
    # Matter toolchains (esp-matter, connectedhomeip, ameba-rtos-matter) are
    # Linux-only; doctor/list still work natively and stay on Windows.
    return ctx.matter and bool(ctx.actions & {"build", "clean", "install", "clone"})


def run(ctx: Context, raw_argv: list[str]) -> int:
    if needs_linux(ctx) and host_is_windows() and ctx.use_wsl is not False:
        return hop_to_wsl(ctx, [a for a in raw_argv if a != "--wsl"])

    script = MATTER_SCRIPT if ctx.matter else SCRIPTS_DIR / ctx.target.script
    if not script.exists():
        return fail(f"Driver script not found: {script}")

    for action in ACTION_ORDER:
        if action not in ctx.actions:
            continue
        sub = argv_for(ctx, action)
        if sub is None:
            continue
        prefix = [ctx.target.key] if ctx.matter else []
        cmd = [sys.executable, str(script), *prefix, *sub]
        banner = "matter " if ctx.matter else ""
        print(f"\n=== {ctx.target.label} :: {banner}{action} ===", flush=True)
        rc = subprocess.call(cmd, cwd=str(SDK_ROOT))
        if rc != 0:
            return fail(f"{banner}{action} failed (exit {rc}).")
    return 0


def main(argv: list[str] | None = None, matter: bool = False) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    parsed = parse(raw, matter=matter)
    if isinstance(parsed, int):
        return parsed
    return run(parsed, raw)


if __name__ == "__main__":
    sys.exit(main())
