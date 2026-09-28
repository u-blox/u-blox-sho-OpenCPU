#!/usr/bin/env python3
"""
Shared per-target directory layout for the u-blox Getting Started SDK.

Every target owns a base folder under ``targets/`` that holds the things we
generate, so the checked-in vendor SDKs (ameba-rtos-d, esp-idf,
mcuxpresso-sdk) stay untouched at the repo root:

    targets/<TARGET>/
        sdk/        on-demand SDK clones / west workspaces
        config/     build.<host>.json tool cache

Build artifacts are deliberately not relocated here: each vendor build system
(west, idf.py, Realtek make) emits in-tree and expects to find its own output.

Paths are anchored to this file rather than the current working directory, so
a script behaves the same no matter where it is invoked from.
"""

from __future__ import annotations

import platform
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parent.parent
TARGETS_DIR = SDK_ROOT / "targets"

# Script slug -> base folder name shown in the explorer.
TARGETS: dict[str, str] = {
    "iris_w10": "IRIS-W10",
    "nora_w30": "NORA-W30",
    "nora_w40": "NORA-W40",
    "nora_w50_w51": "NORA-W50-W51",
}

SUBDIRS = ("sdk", "config")


def host_kind() -> str:
    """Detect platform type: 'windows', 'wsl', or 'linux'."""
    if platform.system() == "Windows":
        return "windows"
    try:
        content = Path("/proc/version").read_text(encoding="utf-8", errors="replace").upper()
        if "WSL" in content or "MICROSOFT" in content:
            return "wsl"
    except OSError:
        pass
    return "linux"


def _slug(target: str) -> str:
    if target not in TARGETS:
        raise KeyError(f"Unknown target {target!r}. Known targets: {', '.join(sorted(TARGETS))}")
    return target


def base_dir(target: str) -> Path:
    """Base folder for a target, e.g. targets/NORA-W30."""
    return TARGETS_DIR / TARGETS[_slug(target)]


def sdk_dir(target: str) -> Path:
    return base_dir(target) / "sdk"


def config_dir(target: str) -> Path:
    return base_dir(target) / "config"


def config_file(target: str, host: str | None = None) -> Path:
    return config_dir(target) / f"build.{host or host_kind()}.json"


def legacy_config_file(target: str, host: str | None = None) -> Path:
    """Pre-targets/ location: a dotfile at the SDK root."""
    return SDK_ROOT / f".{_slug(target)}_build.{host or host_kind()}.json"


def ensure(target: str) -> Path:
    """Create the target's folder skeleton and return its base folder."""
    base = base_dir(target)
    for name in SUBDIRS:
        (base / name).mkdir(parents=True, exist_ok=True)
    return base


def resolve_config(target: str, host: str | None = None) -> Path:
    """Config path for a target, migrating the old root dotfile on first use."""
    host = host or host_kind()
    new = config_file(target, host)
    new.parent.mkdir(parents=True, exist_ok=True)
    old = legacy_config_file(target, host)
    if old.exists() and not new.exists():
        new.write_text(old.read_text(encoding="utf-8"), encoding="utf-8")
        old.unlink()
    return new
