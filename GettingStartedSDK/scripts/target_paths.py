#!/usr/bin/env python3
"""
Shared per-target directory layout for the u-blox Getting Started SDK.

Every target owns a base folder under ``targets/`` that holds everything we
fetch or generate for it:

    targets/<target>/
        sdk/        vendor SDK clones / west workspaces, e.g. sdk/esp-idf
        config/     build.<host>.json tool cache, rf_config.json

SDKs that older versions fetched into the SDK root (esp-idf/, ameba-rtos-d/,
mcuxpresso-sdk/) are moved here by the launcher on first use.

Build artifacts are deliberately not relocated here: each vendor build system
(west, idf.py, Realtek make) emits in-tree and expects to find its own output.

Paths are anchored to this file rather than the current working directory, so
a script behaves the same no matter where it is invoked from.
"""

from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parent.parent
TARGETS_DIR = SDK_ROOT / "targets"

# Script slug -> base folder name shown in the explorer.
TARGETS: dict[str, str] = {
    "alma_b20_b21": "alma-b20-b21",
    "iris_w10": "iris-w10",
    "nora_b20_b21_b22": "nora-b20-b21-b22",
    "nora_w30": "nora-w30",
    "nora_w40": "nora-w40",
    "nora_w50_w51": "nora-w50-w51",
}

# Names used before the switch to full series names: (script slug, folder).
LEGACY: dict[str, tuple[str, str]] = {
    "alma_b20_b21": ("alma_b2", "ALMA-B2"),
    "iris_w10": ("iris_w1", "IRIS-W1"),
    "nora_b20_b21_b22": ("nora_b2", "NORA-B2"),
    "nora_w30": ("nora_w3", "NORA-W3"),
    "nora_w40": ("nora_w4", "NORA-W4"),
    "nora_w50_w51": ("nora_w5", "NORA-W5"),
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


def _merge(old: Path, new: Path) -> None:
    """Move old's contents into new without overwriting, then drop old if empty."""
    new.mkdir(parents=True, exist_ok=True)
    for child in old.iterdir():
        dest = new / child.name
        if not dest.exists():
            child.rename(dest)
        elif child.is_dir() and dest.is_dir():
            _merge(child, dest)
    try:
        old.rmdir()
    except OSError:
        pass


def adopt_legacy(new: Path, target: str) -> Path:
    """Return new, first moving in a sibling folder that still has the old target name."""
    old = new.parent / LEGACY[_slug(target)][1]
    if old.is_dir() and old.name != new.name:
        _merge(old, new)
    return new


def base_dir(target: str) -> Path:
    """Base folder for a target, e.g. targets/nora-w30."""
    return adopt_legacy(TARGETS_DIR / TARGETS[_slug(target)], target)


def sdk_dir(target: str) -> Path:
    return base_dir(target) / "sdk"


# Vendor SDKs that older versions fetched into the SDK root itself.
ROOT_SDKS: dict[str, str] = {
    "iris_w10": "mcuxpresso-sdk",
    "nora_w30": "ameba-rtos-d",
    "nora_w40": "esp-idf",
}


def vendor_sdk(target: str) -> Path:
    """Where the target's vendor SDK is fetched: targets/<target>/sdk/<repo>."""
    return sdk_dir(target) / ROOT_SDKS[_slug(target)]


def root_sdk(target: str) -> Path | None:
    """An SDK still sitting at the old root location, not yet adopted."""
    name = ROOT_SDKS.get(_slug(target))
    old = SDK_ROOT / name if name else None
    return old if old is not None and old.is_dir() else None


def adopt_root_sdk(target: str) -> Path | None:
    """Move <SDK root>/<repo> into targets/<target>/sdk/ and repoint the cached paths."""
    old = root_sdk(target)
    if old is None:
        return None
    new = vendor_sdk(target)
    if new.exists():
        print(f"[WARNING] Both {old} and {new} exist; using {new}. Remove the old one when done.")
        return None
    new.parent.mkdir(parents=True, exist_ok=True)
    try:
        old.rename(new)
    except OSError as exc:
        print(f"[WARNING] Could not move {old} to {new}: {exc}")
        print("          Close any shell or editor using it and run again.")
        return None
    print(f"[INFO] Moved vendor SDK {old.name}/ to {new}")
    rel_old = f"{SDK_ROOT.name}/{old.name}"
    rel_new = f"{SDK_ROOT.name}/targets/{TARGETS[_slug(target)]}/sdk/{old.name}"
    for cfg in config_dir(target).glob("*.json"):
        text = cfg.read_text(encoding="utf-8")
        # Cached paths may be Windows, POSIX or /mnt/<drive> form.
        updated = text.replace(rel_old, rel_new).replace(
            rel_old.replace("/", "\\\\"), rel_new.replace("/", "\\\\"))
        if updated != text:
            cfg.write_text(updated, encoding="utf-8")
    return new


def sdk_candidates(target: str) -> list[Path]:
    """The fetched vendor SDK location, plus the old root one if adoption has not run."""
    old = root_sdk(target)
    return [vendor_sdk(target)] + ([old] if old else [])


def config_dir(target: str) -> Path:
    return base_dir(target) / "config"


def config_file(target: str, host: str | None = None) -> Path:
    return config_dir(target) / f"build.{host or host_kind()}.json"


def legacy_config_file(target: str, host: str | None = None) -> Path:
    """Pre-targets/ location: a dotfile at the SDK root."""
    return SDK_ROOT / f".{LEGACY[_slug(target)][0]}_build.{host or host_kind()}.json"


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


def free_gb(path: Path) -> float | None:
    """Free space on the drive that holds path (or its nearest existing parent)."""
    probe = Path(path).absolute()
    while not probe.exists() and probe != probe.parent:
        probe = probe.parent
    try:
        return shutil.disk_usage(probe).free / 1024 ** 3
    except OSError:
        return None


def check_space(path: Path, needed_gb: float, what: str) -> bool:
    """Print a disk-space verdict for fetching `what` into path; False when it will not fit.

    needed_gb is an estimate. UBX_SKIP_SPACE_CHECK=1 turns a failure into a warning.
    """
    free = free_gb(path)
    if free is None:
        print(f"[WARNING] Could not determine free space for {path}.")
        return True
    if free >= needed_gb:
        print(f"[OK] Disk space: {free:.1f} GB free, {what} needs about {needed_gb:g} GB ({path})")
        return True
    print(f"[FAIL] Not enough disk space for {what}: about {needed_gb:g} GB needed, "
          f"{free:.1f} GB free at {path}.")
    if os.environ.get("UBX_SKIP_SPACE_CHECK"):
        print("[WARNING] UBX_SKIP_SPACE_CHECK is set; continuing anyway.")
        return True
    print("       Free some space or choose another location. "
          "Set UBX_SKIP_SPACE_CHECK=1 to try anyway.")
    return False
