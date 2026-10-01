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
import shlex
import subprocess
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SDK_ROOT / "scripts"
MATTER_SCRIPT = SCRIPTS_DIR / "matter_build.py"
MODULE_CONFIG_SCRIPT = SCRIPTS_DIR / "module_config.py"

# Served by module_config.py for every target rather than by the per-target driver.
MODULE_ACTIONS = frozenset({"rf-config", "mac"})


@dataclass(frozen=True)
class Target:
    key: str
    label: str
    script: str
    default_example: str
    example_word: str
    linux_only: bool = False
    supports: frozenset[str] = frozenset()
    # Leading arguments the driver needs before its subcommand. Shared drivers
    # that serve several targets use this to receive the target key.
    driver_args: tuple[str, ...] = ()


TARGETS: dict[str, Target] = {
    "alma-b2": Target(
        key="alma-b2",
        label="ALMA-B2 (Nordic nRF54LM20)",
        script="nordic_ncs_build.py",
        default_example="hello_world",
        example_word="sample",
        supports=frozenset({"doctor", "clone", "install", "list", "clean", "build", "flash", "log"}),
        driver_args=("alma-b2",),
    ),
    "iris-w1": Target(
        key="iris-w1",
        label="IRIS-W1 (NXP RW612/RW610)",
        script="iris_w1_build.py",
        default_example="demo_apps/hello_world",
        example_word="example",
        supports=frozenset({"doctor", "clone", "install", "list", "clean", "build", "flash", "log"}),
    ),
    "nora-b2": Target(
        key="nora-b2",
        label="NORA-B2 (Nordic nRF54L15/L10/L05)",
        script="nordic_ncs_build.py",
        default_example="hello_world",
        example_word="sample",
        supports=frozenset({"doctor", "clone", "install", "list", "clean", "build", "flash", "log"}),
        driver_args=("nora-b2",),
    ),
    "nora-w3": Target(
        key="nora-w3",
        label="NORA-W3 (Realtek RTL8720DF)",
        script="nora_w3_build.py",
        default_example="project_hp",
        example_word="project",
        linux_only=True,
        supports=frozenset({"doctor", "clone", "install", "list", "clean", "build"}),
    ),
    "nora-w4": Target(
        key="nora-w4",
        label="NORA-W4 (Espressif ESP32-C6)",
        script="nora_w4_build.py",
        default_example="hello_world",
        example_word="example",
        supports=frozenset({"doctor", "clone", "install", "list", "clean", "build", "flash", "log"}),
    ),
    "nora-w5": Target(
        key="nora-w5",
        label="NORA-W5 (TI CC3501E/CC3551E)",
        script="nora_w5_build.py",
        default_example="network_terminal",
        example_word="example",
        supports=frozenset({"doctor", "clone", "install", "list", "clean", "build", "build-sdk", "flash", "log"}),
    ),
}

# Short keys are canonical; the full u-blox series names stay accepted.
ALIASES = {
    "alma": "alma-b2", "almab2": "alma-b2", "alma_b2": "alma-b2",
    "iris": "iris-w1", "irisw1": "iris-w1", "iris_w1": "iris-w1",
    "iris-w10": "iris-w1", "irisw10": "iris-w1", "w10": "iris-w1",
    "nora_b2": "nora-b2", "norab2": "nora-b2",
    "nora_w3": "nora-w3", "noraw3": "nora-w3",
    "nora-w30": "nora-w3", "noraw30": "nora-w3", "w3": "nora-w3", "w30": "nora-w3",
    "nora_w4": "nora-w4", "noraw4": "nora-w4",
    "nora-w40": "nora-w4", "noraw40": "nora-w4", "w4": "nora-w4", "w40": "nora-w4",
    # W50x and W51x only. W56x/W57x are u-connectXpress parts, not Open CPU.
    "nora_w5": "nora-w5", "noraw5": "nora-w5", "w5": "nora-w5",
    "nora-w50": "nora-w5", "nora-w51": "nora-w5",
    "w50": "nora-w5", "w51": "nora-w5",
}

# Execution order, independent of the order flags were typed.
# 'list' sits after the SDK is in place so '--clone --list' reads correctly.
# 'rf-config' mutates the SDK tree, so it has to land before anything is built.
ACTION_ORDER = ["doctor", "clone", "install", "build-sdk", "rf-config",
                "list", "clean", "build", "flash", "mac", "log"]


@dataclass
class Context:
    target: Target
    actions: set[str] = field(default_factory=set)
    example: str | None = None
    port: str | None = None
    probe: str | None = None
    mac_port: str | None = None
    variant: str | None = None
    region: str | None = None
    full: bool = False
    clean_all: bool = False
    matter: bool = False
    use_wsl: bool | None = None
    extra: list[str] = field(default_factory=list)


USAGE = """
u-blox Getting Started SDK launcher

  ubx-sdk <target> [flags...]

Targets                                             Open CPU parts
  alma-b2      Nordic nRF54LM20     nRF Connect SDK  ALMA-B20x/B21x
  iris-w1      NXP RW612/RW610      MCUXpresso       IRIS-W10x
  nora-b2      Nordic nRF54L15/L10  nRF Connect SDK  NORA-B20x/B21x/B22x
  nora-w3      Realtek RTL8720DF    Ameba (Linux)    NORA-W30x
  nora-w4      Espressif ESP32-C6   ESP-IDF          NORA-W40x
  nora-w5      TI CC3501E/CC3551E   SimpleLink       NORA-W50x/W51x

The u-connectXpress parts (NORA-W36x, W56x, W57x, B26x, B27x) ship pre-flashed
with AT-command firmware and are not built from this Open CPU SDK.

Flags (combinable; always run in this order)
  --doctor              Verify host tools for the target
  --clone               Fetch the vendor SDK on demand
    --full                IRIS-W1 only: full SDK instead of RW612 only
  --install             Install/refresh the SDK's own tool environment
  --build-sdk           NORA-W5 only: build the SDK libraries
  --rf-config           Apply the u-blox RF calibration / TX power configuration
    --variant <PART>      Module part number, e.g. NORA-W301, IRIS-W101-00B
    --region <DOMAIN>     Regulatory domain: FCC, ISED, ETSI, MKK, ACMA
  --list                List available examples
  --clean               Clean build artifacts
  --clean-all           Remove the fetched SDK entirely
  --build [NAME]        Build an example (target-specific default if omitted)
  --flash [SERIAL]      Flash via the target's debug probe
  --mac [PORT]          Report the module MAC / Bluetooth device address
  --log [PORT]          Open the serial monitor (port auto-detected if omitted)
  --setup-venv          Create/refresh the shared .venv, then exit
  --wsl / --no-wsl      Force or suppress the automatic hop into WSL2
  --                    Pass every remaining argument verbatim to the driver
  --help                Show this help

Firmware built without --rf-config uses the vendor reference-board RF data and
is not regulatory compliant. --doctor reports whether it has been applied.

Examples
  ubx-sdk nora-w4 --clone --install --build hello_world
  ubx-sdk nora-b2 --clone --build hello_world --flash --log
  ubx-sdk iris-w1 --doctor
  ubx-sdk iris-w1 --build demo_apps/hello_world --flash --log
  ubx-sdk nora-w5 --clone --build-sdk --build network_terminal
  ubx-sdk nora-w3 --build        (hops into WSL2 automatically on Windows)
  ubx-sdk nora-w3 --variant NORA-W301 --region ETSI --rf-config --build
  ubx-sdk iris-w1 --build hello_world -- --config release

Matter is a separate, optional layer with its own launcher: ubx-matter --help
""".strip()

MATTER_USAGE = """
u-blox Getting Started SDK - Matter launcher

  ubx-matter <target> [flags...]

Optional layer on top of the plain SDK examples. The Matter SDKs are large and
are only fetched when you ask for them; if you are not building Matter, ignore
this launcher and use 'ubx-sdk' instead.

Targets
  iris-w1      NXP RW612            NXP/matter (connectedhomeip fork)
  nora-w3      Realtek RTL8720DF    ameba-rtos-matter
  nora-w4      Espressif ESP32-C6   esp-matter
  nora-w5      TI CC3551E           TexasInstruments/matter
  nora-b2      Nordic nRF54L15/L10  nRF Connect SDK (nrf/samples/matter)
  alma-b2      Nordic nRF54LM20     nRF Connect SDK (nrf/samples/matter)

The Nordic targets get Matter from the nRF Connect SDK itself, so --clone
fetches the same NCS workspace 'ubx-sdk' uses and nothing extra is downloaded.
For them --build takes an nrf/samples/matter app and --flash/--log also work.

Flags (combinable; always run in this order)
  --doctor              Report Matter prerequisites and SDK state
  --clone               Fetch the Matter SDK for this target (several GB)
  --install             Run the app's one-time SDK setup
  --clean               Clean a Matter app
  --build [APP]         Build a Matter app from matter/<TARGET>/
  --list                List the Matter apps available for this target
  --flash [SERIAL]      Flash the app (Nordic targets only)
  --log [PORT]          Open the serial monitor (Nordic targets only)
  --setup-venv          Create/refresh the shared .venv, then exit
  --wsl / --no-wsl      Force or suppress the automatic hop into WSL2
  --help                Show this help

The vendor Matter toolchains are Linux-only, so --clone/--install/--build/
--clean hop into WSL2 automatically on Windows. Set UBX_MATTER_ROOT to keep the
checkout off a /mnt/<drive> path. The Nordic targets build natively on Windows
and never hop. See matter/README.md.

Examples
  ubx-matter nora-w4 --doctor
  ubx-matter nora-w4 --clone
  ubx-matter nora-w4 --list
  ubx-matter nora-w4 --build thermometer
  ubx-matter nora-b2 --list
  ubx-matter nora-b2 --build light_bulb --flash --log
""".strip()


def fail(message: str) -> int:
    print(f"[FAIL] {message}")
    return 1


def resolve_target(name: str) -> Target | None:
    key = ALIASES.get(name.lower(), name.lower())
    return TARGETS.get(key)


# Pre-flashed AT-command parts. Typing one of these is a product-line mix-up,
# not a typo, so say so rather than listing the Open CPU targets.
UCONNECTXPRESS = {
    "nora-w36": "nora-w3", "w36": "nora-w3",
    "nora-w56": "nora-w5", "w56": "nora-w5",
    "nora-w57": "nora-w5", "w57": "nora-w5",
    "nora-b26": "nora-b2", "b26": "nora-b2",
    "nora-b27": "nora-b2", "b27": "nora-b2",
}


# Open CPU modules this SDK does not cover. NORA-W1/W2 are ESP32-based and
# easy to confuse with IRIS-W1, which is NXP.
UNSUPPORTED = {
    "nora-w1": "NORA-W1 (ESP32) is not built by this SDK. Note IRIS-W1 is NXP RW612,\n"
               "       a different module. See NORA-W1-OutputPower/ in the repository root.",
    "nora-w2": "NORA-W2 (ESP32) is not built by this SDK.",
}


def fail_unknown_target(name: str) -> int:
    key = name.lower().replace("_", "-")
    series = key.rstrip("0123456789x") or key

    note = UNSUPPORTED.get(key) or UNSUPPORTED.get(series)
    if note:
        return fail(note)

    sibling = UCONNECTXPRESS.get(key) or UCONNECTXPRESS.get(key[:-1] if key[-1:].isdigit() else key)
    if sibling:
        return fail(
            f"{name} is a u-connectXpress module.\n"
            f"       It ships with AT-command firmware pre-flashed and is not built\n"
            f"       from this Open CPU SDK. The Open CPU sibling is '{sibling}'."
        )
    return fail(f"Unknown target: {name}\n       Known targets: {', '.join(TARGETS)}")


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
        return fail_unknown_target(argv[0])

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
        if matter and arg in ("--full", "--build-sdk", "--clean-all"):
            return fail(f"{arg} is an SDK-only flag and has no Matter equivalent.")
        if matter and arg in ("--rf-config", "--mac", "--variant", "--region"):
            return fail(f"{arg} is an SDK-only flag. Apply the module configuration with\n"
                        f"       'ubx-sdk {target.key} {arg} ...' before building Matter.")
        if matter and arg in ("--flash", "--log") and not is_ncs_matter(ctx):
            return fail(f"{arg} is an SDK-only flag and has no Matter equivalent.")
        if arg in ("--doctor", "--install", "--list", "--clean", "--build-sdk"):
            ctx.actions.add(arg[2:])
        elif arg == "--clone":
            ctx.actions.add("clone")
        elif arg == "--rf-config":
            ctx.actions.add("rf-config")
        elif arg in ("--variant", "--region"):
            value = peek()
            if not value:
                return fail(f"{arg} needs a value. Run '{name} {target.key} --rf-config' "
                            f"with no variant to see the known part numbers.")
            setattr(ctx, arg[2:], value)
            i += 1
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
        elif arg == "--mac":
            ctx.actions.add("mac")
            value = peek()
            if value:
                ctx.mac_port = value
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
    if (ctx.variant or ctx.region) and "rf-config" not in ctx.actions:
        print("[WARNING] --variant/--region only take effect with --rf-config; ignoring.")
    return ctx


def run_setup_venv() -> int:
    return subprocess.call([sys.executable, str(SCRIPTS_DIR / "setup_venv.py")])


MATTER_ACTIONS = frozenset({"doctor", "clone", "install", "list", "build", "clean"})


def is_ncs_matter(ctx: Context) -> bool:
    """Matter on a Nordic target, which the NCS driver serves directly."""
    return ctx.matter and ctx.target.script == "nordic_ncs_build.py"


def matter_sample(name: str | None) -> str:
    """Scope a sample name to the NCS Matter subtree."""
    if not name:
        return "matter/light_bulb"
    # A bare name could also match a non-Matter sample, so anchor it.
    return name if "/" in name else f"matter/{name}"


def argv_for(ctx: Context, action: str) -> list[str] | None:
    """Translate one uniform action into the driver's own subcommand."""
    t = ctx.target
    example = ctx.example or t.default_example

    # Served by module_config.py, which covers every target including the
    # ones whose RF assets do not exist yet.
    if action == "rf-config":
        argv = ["apply"]
        if ctx.variant:
            argv += ["--variant", ctx.variant]
        if ctx.region:
            argv += ["--region", ctx.region]
        return argv
    if action == "mac":
        return ["mac", "--serial", ctx.mac_port] if ctx.mac_port else ["mac"]

    if is_ncs_matter(ctx):
        # Matter here is just the nrf/samples/matter subtree of the NCS
        # workspace, so reuse the SDK translation with a Matter-scoped name.
        if action == "list":
            return ["list", "--matter"]
        scoped = replace(ctx, matter=False, example=matter_sample(ctx.example))
        return argv_for(scoped, action)

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
        if ctx.full and t.key == "iris-w1":
            argv.append("--full")
        return argv

    if action == "clean":
        if t.key == "nora-w5":
            if ctx.clean_all:
                print("[WARNING] --clean-all is not supported for NORA-W5; "
                      "delete the workspace manually. Skipping.")
                return None
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
        # idf.py monitor must run inside an example directory.
        if t.key == "nora-w4":
            argv = ["log", example]
            if ctx.port:
                argv += ["--serial", ctx.port]
            return argv
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
    forwarded = shlex.join(argv)
    shim = "./ubx-matter.sh" if ctx.matter else "./ubx-sdk.sh"
    print(f"[INFO] {ctx.target.label} builds on Linux; hopping into WSL2.")
    print(f"[INFO] WSL path: {sdk_wsl}")
    command = f"cd {shlex.quote(sdk_wsl)} && {shim} {forwarded}"
    return subprocess.call(["wsl", "--", "bash", "-lc", command])


def needs_linux(ctx: Context) -> bool:
    if ctx.target.linux_only:
        return True
    # NCS builds natively on Windows; only the vendor Matter toolchains
    # (esp-matter, connectedhomeip, ameba-rtos-matter) are Linux-only.
    # doctor/list still work natively and stay on Windows.
    if is_ncs_matter(ctx):
        return False
    return ctx.matter and bool(ctx.actions & {"build", "clean", "install", "clone"})


def run(ctx: Context, raw_argv: list[str]) -> int:
    if needs_linux(ctx) and host_is_windows() and ctx.use_wsl is not False:
        return hop_to_wsl(ctx, [a for a in raw_argv if a != "--wsl"])

    script = MATTER_SCRIPT if ctx.matter else SCRIPTS_DIR / ctx.target.script
    if is_ncs_matter(ctx):
        script = SCRIPTS_DIR / ctx.target.script
    if not script.exists():
        return fail(f"Driver script not found: {script}")

    for action in ACTION_ORDER:
        if action not in ctx.actions:
            continue
        sub = argv_for(ctx, action)
        if sub is None:
            continue
        if action in MODULE_ACTIONS:
            cmd = [sys.executable, str(MODULE_CONFIG_SCRIPT), ctx.target.key, *sub]
        else:
            prefix = [ctx.target.key] if ctx.matter and not is_ncs_matter(ctx) \
                else list(ctx.target.driver_args)
            cmd = [sys.executable, str(script), *prefix, *sub]
        banner = "matter " if ctx.matter else ""
        print(f"\n=== {ctx.target.label} :: {banner}{action} ===", flush=True)
        rc = subprocess.call(cmd, cwd=str(SDK_ROOT))
        if action == "doctor" and not ctx.matter:
            # Tools can all be present while the firmware is still non-compliant,
            # and a failing doctor is exactly when that matters most.
            subprocess.call([sys.executable, str(MODULE_CONFIG_SCRIPT),
                             ctx.target.key, "status"], cwd=str(SDK_ROOT))
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
