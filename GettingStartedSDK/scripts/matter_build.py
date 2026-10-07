#!/usr/bin/env python3
"""
Matter driver for the u-blox Getting Started SDK.

Mirrors the per-target SDK drivers, but for the Matter layer: the vendor's
Matter SDK for a target is fetched on demand and only the examples that SDK
ships are listed and built. No u-blox application code lives here.

    python scripts/matter_build.py nora-w4 doctor
    python scripts/matter_build.py nora-w4 clone
    python scripts/matter_build.py nora-w4 build light

Usually invoked via the Matter launcher: ``ubx-matter nora-w4 --doctor``.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import target_paths  # noqa: E402

SDK_ROOT = Path(__file__).resolve().parent.parent
VENDOR_SCRIPTS = Path(__file__).resolve().parent / "matter_vendor"


@dataclass(frozen=True)
class Repo:
    name: str
    url: str
    revision: str
    size_hint: str
    submodules: bool = False


@dataclass(frozen=True)
class MatterTarget:
    key: str
    slug: str          # target_paths key
    folder: str        # <UBX_MATTER_ROOT>/<folder>
    label: str
    repos: tuple[Repo, ...]
    linux_only: bool
    note: str
    # Glob under matter_root() for the vendor's own examples; '*' is the name.
    examples: str
    default_example: str
    # Only directories containing this file count as examples.
    example_marker: str | None = None
    # scripts/matter_vendor/<name>: setup | build <dir> [args] | clean <dir>.
    vendor_script: str | None = None


TARGETS: dict[str, MatterTarget] = {
    "iris-w1": MatterTarget(
        key="iris-w1",
        slug="iris_w1",
        folder="IRIS-W1",
        label="IRIS-W1 (NXP RW612) Matter",
        repos=(
            Repo("connectedhomeip", "https://github.com/NXP/matter.git",
                 "v1.6.0.0.1", "~10 GB after submodules", submodules=False),
        ),
        linux_only=True,
        note="Builds the NXP connectedhomeip fork, examples/*/nxp/rt/rw61x (GN + ninja).",
        examples="connectedhomeip/examples/*/nxp/rt/rw61x",
        default_example="lighting-app",
    ),
    "nora-w3": MatterTarget(
        key="nora-w3",
        slug="nora_w3",
        folder="NORA-W3",
        label="NORA-W3 (Realtek RTL8720DF) Matter",
        repos=(
            Repo("ameba-rtos-d", "https://github.com/Ameba-AIoT/ameba-rtos-d.git",
                 "main", "~2 GB"),
            Repo("ameba-rtos-matter", "https://github.com/Ameba-AIoT/ameba-rtos-matter.git",
                 "release/v1.5", "~3 GB"),
        ),
        linux_only=True,
        note="ameba-rtos-matter must be synced into ameba-rtos-d before building.",
        examples="ameba-rtos-matter/examples/*",
        default_example="light",
    ),
    "nora-w4": MatterTarget(
        key="nora-w4",
        slug="nora_w4",
        folder="NORA-W4",
        label="NORA-W4 (Espressif ESP32-C6) Matter",
        repos=(
            Repo("esp-idf", "https://github.com/espressif/esp-idf.git",
                 "v5.5.5", "~3 GB", submodules=True),
            Repo("esp-matter", "https://github.com/espressif/esp-matter.git",
                 "release/v1.5", "~6 GB after setup", submodules=False),
        ),
        linux_only=True,
        note="Espressif only supports esp-matter on Linux/WSL2. --install fetches "
             "only the esp32 connectedhomeip submodules.",
        examples="esp-matter/examples/*",
        default_example="light",
        example_marker="CMakeLists.txt",
        vendor_script="nora_w4.sh",
    ),
    "nora-w5": MatterTarget(
        key="nora-w5",
        slug="nora_w5",
        folder="NORA-W5",
        label="NORA-W5 (TI CC3551E) Matter",
        repos=(
            # --install fetches only the cc35xx + linux submodules.
            Repo("ti-matter", "https://github.com/TexasInstruments/matter.git",
                 "matter-v1.5-ti-1.1", "~4 GB after --install"),
        ),
        linux_only=True,
        note="TI connectedhomeip fork, CC3551E on LP-EM-CC35X1. Ubuntu 22.04 only.",
        examples="ti-matter/examples/*/ti/cc35xx",
        default_example="lighting-app",
        vendor_script="nora_w5.sh",
    ),
}


def matter_root(target: MatterTarget) -> Path:
    """Where the Matter SDKs are checked out.

    ESP-IDF/esp-matter and connectedhomeip must not live on a /mnt/<drive>
    path when built from WSL2, so allow an override.
    """
    override = os.environ.get("UBX_MATTER_ROOT")
    if override:
        return Path(override).expanduser() / target.folder
    in_tree = target_paths.sdk_dir(target.slug) / "matter"
    if host_kind() == "wsl" and not any((in_tree / r.name / ".git").exists() for r in target.repos):
        # The repo is on a /mnt/<drive> path, where these SDKs must not be built.
        return Path.home() / "ubx-matter" / target.folder
    return in_tree


def list_vendor_examples(target: MatterTarget) -> dict[str, Path]:
    index = target.examples.split("/").index("*")
    found: dict[str, Path] = {}
    for path in sorted(matter_root(target).glob(target.examples)):
        name = path.relative_to(matter_root(target)).parts[index]
        # Shared support code, not buildable examples.
        if not path.is_dir() or name.startswith((".", "_")) or name in ("common", "platform"):
            continue
        if target.example_marker and not (path / target.example_marker).exists():
            continue
        found[name] = path
    return found


def vendor_script(target: MatterTarget) -> Path | None:
    return VENDOR_SCRIPTS / target.vendor_script if target.vendor_script else None


def host_kind() -> str:
    return target_paths.host_kind()


def cmd_doctor(target: MatterTarget, args) -> int:
    print(f"=== {target.label} ===")
    print(f"Host:        {host_kind()}")
    print(f"SDK root:    {matter_root(target)}")
    print(f"Note:        {target.note}\n")

    if target.linux_only and host_kind() == "windows":
        print("[WARNING] This Matter build requires Linux or WSL2.")

    for tool in ("git", "python3" if os.name != "nt" else "python", "cmake", "ninja"):
        path = shutil.which(tool)
        print(f"[{'OK' if path else 'FAIL'}] {tool:<8} {path or 'not found'}")

    print()
    for repo in target.repos:
        dest = matter_root(target) / repo.name
        state = "present" if (dest / ".git").exists() else "missing"
        mark = "OK" if state == "present" else "FAIL"
        print(f"[{mark}] {repo.name:<20} {repo.revision:<14} {state}")

    vendor = list_vendor_examples(target)
    print()
    if vendor:
        print(f"[OK] {len(vendor)} vendor example(s): {', '.join(vendor)}")
    else:
        print("[INFO] No vendor examples found; clone the SDK first.")
    if vendor_script(target) is None:
        print(f"[INFO] --build is not wired for {target.key} yet; examples are listed only.")
    return 0


def cmd_list(target: MatterTarget, args) -> int:
    vendor = list_vendor_examples(target)
    if not vendor:
        print(f"[WARNING] No vendor examples under {matter_root(target)}.")
        print(f"          Run 'ubx-matter {target.key} --clone' first.")
        return 0
    print(f"Vendor Matter examples for {target.label} ({target.examples}):")
    for name in vendor:
        mark = "  (default)" if name == target.default_example else ""
        print(f"  {name}{mark}")
    if vendor_script(target) is None:
        print(f"\n[INFO] --build is not wired for {target.key} yet; examples are listed only.")
    return 0


def cmd_clone(target: MatterTarget, args) -> int:
    root = matter_root(target)
    root.mkdir(parents=True, exist_ok=True)
    total = ", ".join(f"{r.name} {r.size_hint}" for r in target.repos)
    print(f"[INFO] Destination: {root}")
    print(f"[INFO] Disk needed: {total}\n")

    for repo in target.repos:
        dest = root / repo.name
        if (dest / ".git").exists():
            print(f"[OK] {repo.name} already cloned at {dest}")
            continue
        cmd = ["git", "clone", "--branch", repo.revision, "--depth", "1"]
        if repo.submodules:
            cmd += ["--recurse-submodules", "--shallow-submodules"]
        cmd += [repo.url, str(dest)]
        print(f"[INFO] {' '.join(cmd)}")
        rc = subprocess.call(cmd)
        if rc != 0:
            print(f"[FAIL] Clone of {repo.name} failed (exit {rc}).")
            return rc
        print(f"[OK] {repo.name} cloned")
    return 0


def _run_vendor(target: MatterTarget, verb: str, *argv: str) -> int:
    env = dict(os.environ)
    env["UBX_MATTER_SDK_ROOT"] = str(matter_root(target))
    cmd = ["bash", str(vendor_script(target)), verb, *argv]
    print(f"[INFO] {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(matter_root(target)), env=env)


def _run_example(target: MatterTarget, args, verb: str) -> int:
    name = getattr(args, "app", None) or target.default_example
    extra = list(getattr(args, "extra", None) or [])
    example = list_vendor_examples(target).get(name)
    if example is None:
        print(f"[FAIL] Matter example {name!r} not found for {target.key}.")
        print(f"       Run 'ubx-matter {target.key} --list' to see what is available.")
        return 1
    if vendor_script(target) is None:
        print(f"[FAIL] Building vendor examples is not wired for {target.key} yet.")
        print(f"       See {example / 'README.md'}")
        return 1
    return _run_vendor(target, verb, str(example), *extra)


def cmd_build(target: MatterTarget, args) -> int:
    return _run_example(target, args, "build")


def cmd_clean(target: MatterTarget, args) -> int:
    return _run_example(target, args, "clean")


def cmd_install(target: MatterTarget, args) -> int:
    root = matter_root(target)
    missing = [r.name for r in target.repos if not (root / r.name / ".git").exists()]
    if missing:
        print(f"[FAIL] Not cloned yet: {', '.join(missing)}. Run clone first.")
        return 1
    if vendor_script(target) is None:
        print(f"[FAIL] --install is not wired for {target.key} yet. See the vendor SDK README.")
        return 1
    return _run_vendor(target, "setup")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="matter_build.py",
        description="Matter driver for the u-blox Getting Started SDK",
    )
    parser.add_argument("target", choices=sorted(TARGETS), help="module family")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Report Matter prerequisites and SDK state")
    sub.add_parser("clone", help="Fetch the Matter SDK for this target")
    sub.add_parser("list", help="List the vendor's Matter examples")
    sub.add_parser("install", help="One-time SDK setup (submodules, bootstrap, tools)")

    build_parser = sub.add_parser("build", help="Build a vendor Matter example")
    build_parser.add_argument("app", nargs="?", help="Example name (target default if omitted)")
    build_parser.add_argument("extra", nargs=argparse.REMAINDER,
                              help="Passed to the vendor build, e.g. GN args or idf.py options")

    clean_parser = sub.add_parser("clean", help="Clean a vendor Matter example")
    clean_parser.add_argument("app", nargs="?", help="Example name (target default if omitted)")

    args = parser.parse_args()
    target = TARGETS[args.target]

    commands = {
        "doctor": cmd_doctor,
        "clone": cmd_clone,
        "list": cmd_list,
        "install": cmd_install,
        "build": cmd_build,
        "clean": cmd_clean,
    }
    return commands[args.command](target, args)


if __name__ == "__main__":
    sys.exit(main())
