#!/usr/bin/env python3
"""
Matter driver for the u-blox Getting Started SDK.

Mirrors the per-target SDK drivers, but for the Matter layer: the Matter SDK
for a target is fetched on demand into ``targets/<TARGET>/sdk/matter/`` and the
application sources live in ``matter/<TARGET>/<app>/``.

    python scripts/matter_build.py nora-w4 doctor
    python scripts/matter_build.py nora-w4 clone
    python scripts/matter_build.py nora-w4 build thermometer

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
MATTER_APPS_ROOT = SDK_ROOT / "matter"


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
    folder: str        # matter/<folder>
    label: str
    repos: tuple[Repo, ...]
    linux_only: bool
    note: str


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
    ),
    "nora-w3": MatterTarget(
        key="nora-w3",
        slug="nora_w3",
        folder="NORA-W3",
        label="NORA-W3 (Realtek RTL8720DF) Matter",
        repos=(
            Repo("ameba-rtos-d", "https://github.com/Ameba-AIoT/ameba-rtos-d.git",
                 "master", "~2 GB"),
            Repo("ameba-rtos-matter", "https://github.com/Ameba-AIoT/ameba-rtos-matter.git",
                 "release/v1.5", "~3 GB"),
        ),
        linux_only=True,
        note="ameba-rtos-matter must be synced into ameba-rtos-d before building.",
    ),
    "nora-w4": MatterTarget(
        key="nora-w4",
        slug="nora_w4",
        folder="NORA-W4",
        label="NORA-W4 (Espressif ESP32-C6) Matter",
        repos=(
            Repo("esp-idf", "https://github.com/espressif/esp-idf.git",
                 "v5.4.1", "~3 GB", submodules=True),
            Repo("esp-matter", "https://github.com/espressif/esp-matter.git",
                 "release/v1.5", "~6 GB", submodules=True),
        ),
        linux_only=True,
        note="Espressif only supports esp-matter on Linux/WSL2, not native Windows.",
    ),
    "nora-w5": MatterTarget(
        key="nora-w5",
        slug="nora_w5",
        folder="NORA-W5",
        label="NORA-W5 (TI CC3551E) Matter",
        repos=(
            Repo("ti-matter", "https://github.com/TexasInstruments/matter.git",
                 "matter-v1.5-ti-1.1", "~8 GB after submodules", submodules=True),
        ),
        linux_only=True,
        note="TI connectedhomeip fork, CC3551E on LP-EM-CC35X1. Ubuntu 22.04 only.",
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
    return target_paths.sdk_dir(target.slug) / "matter"


def apps_dir(target: MatterTarget) -> Path:
    return MATTER_APPS_ROOT / target.folder


def list_apps(target: MatterTarget) -> list[Path]:
    root = apps_dir(target)
    if not root.is_dir():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))


def host_kind() -> str:
    return target_paths.host_kind()


def cmd_doctor(target: MatterTarget, args) -> int:
    print(f"=== {target.label} ===")
    print(f"Host:        {host_kind()}")
    print(f"SDK root:    {matter_root(target)}")
    print(f"Apps root:   {apps_dir(target)}")
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

    apps = list_apps(target)
    print()
    if apps:
        print(f"[OK] {len(apps)} Matter app(s): {', '.join(p.name for p in apps)}")
    else:
        print(f"[WARNING] No Matter apps under {apps_dir(target)} yet.")
    return 0


def cmd_list(target: MatterTarget, args) -> int:
    apps = list_apps(target)
    if not apps:
        print(f"[WARNING] No Matter apps under {apps_dir(target)}.")
        print("          See matter/README.md for how to add one.")
        return 0
    print(f"Matter apps for {target.label}:")
    for app in apps:
        entry = "build.sh" if (app / "build.sh").exists() else "-"
        print(f"  {app.name:<28} {entry}")
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


def _app_script(app: Path) -> Path | None:
    for name in ("build.sh", "build.cmd"):
        candidate = app / name
        if candidate.exists():
            return candidate
    return None


def _resolve_app(target: MatterTarget, name: str | None) -> Path | None:
    apps = list_apps(target)
    if not apps:
        return None
    if name is None:
        return apps[0]
    for app in apps:
        if app.name == name:
            return app
    return None


def _run_app(target: MatterTarget, args, verb: str) -> int:
    app = _resolve_app(target, getattr(args, "app", None))
    if app is None:
        requested = getattr(args, "app", None) or "(default)"
        print(f"[FAIL] Matter app {requested!r} not found under {apps_dir(target)}.")
        print("       Run 'matter_build.py <target> list' to see what is available,")
        print("       or see matter/README.md for how to add one.")
        return 1

    script = _app_script(app)
    if script is None:
        print(f"[FAIL] {app.name} has no build.sh/build.cmd entry point.")
        return 1

    env = dict(os.environ)
    env["UBX_MATTER_SDK_ROOT"] = str(matter_root(target))
    if script.suffix == ".cmd":
        cmd = [str(script), verb]
    else:
        cmd = ["bash", str(script), verb]
    print(f"[INFO] {app.name}: {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(app), env=env)


def cmd_build(target: MatterTarget, args) -> int:
    return _run_app(target, args, "build")


def cmd_clean(target: MatterTarget, args) -> int:
    return _run_app(target, args, "clean")


def cmd_install(target: MatterTarget, args) -> int:
    root = matter_root(target)
    missing = [r.name for r in target.repos if not (root / r.name / ".git").exists()]
    if missing:
        print(f"[FAIL] Not cloned yet: {', '.join(missing)}. Run clone first.")
        return 1
    return _run_app(target, args, "setup")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="matter_build.py",
        description="Matter driver for the u-blox Getting Started SDK",
    )
    parser.add_argument("target", choices=sorted(TARGETS), help="module family")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Report Matter prerequisites and SDK state")
    sub.add_parser("clone", help="Fetch the Matter SDK for this target")
    sub.add_parser("list", help="List Matter apps for this target")

    install_parser = sub.add_parser("install", help="Run the app's one-time SDK setup")
    install_parser.add_argument("app", nargs="?", help="Matter app name")

    build_parser = sub.add_parser("build", help="Build a Matter app")
    build_parser.add_argument("app", nargs="?", help="Matter app name")

    clean_parser = sub.add_parser("clean", help="Clean a Matter app")
    clean_parser.add_argument("app", nargs="?", help="Matter app name")

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
