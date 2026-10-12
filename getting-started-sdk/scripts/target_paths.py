#!/usr/bin/env python3
r"""
Shared directory layout for the u-blox Getting Started SDK.

    modules/<target>/
        profile.json    u-blox configuration (tracked)
        config/         build.<host>.json tool cache, rf_config.json (gitignored)
    sdks/<vendor>/<version>/
                        vendor SDK clone or west workspace (gitignored)

<version> is the branch or tag that was fetched (`ubx-sdk <target> --clone
<version>`), so several versions of one vendor SDK can sit side by side. The
SDK path cached in build.<host>.json picks the one a target builds with.

nRF Connect SDK defaults to C:\ncs\<rev> or ~/ncs/<rev>, and the WSL2 Matter
SDKs to ~/ubx-matter/<target>; both stay outside this tree.

Under WSL2 with this tree on /mnt/<drive>, vendor SDKs go to ~/ubx-sdk/sdks
instead: builds on the Windows drive are many times slower. UBX_SDKS_DIR
overrides the location on any host.

Build artifacts stay where each vendor build system puts them, inside the SDK
or example tree.

Paths are anchored to this file, not the working directory.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
from pathlib import Path

SDK_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = SDK_ROOT / "modules"
SDKS_DIR = SDK_ROOT / "sdks"
WSL_SDKS_DIR = Path.home() / "ubx-sdk" / "sdks"

# Script slug -> folder name under modules/ (the target key).
TARGETS: dict[str, str] = {
    "alma_b20_b21": "alma-b20-b21",
    "iris_w10": "iris-w10",
    "nora_b20_b21_b22": "nora-b20-b21-b22",
    "nora_w30": "nora-w30",
    "nora_w40": "nora-w40",
    "nora_w50_w51": "nora-w50-w51",
}

# Script slug -> sdks/<vendor> folder. Both Nordic targets share one NCS.
VENDORS: dict[str, str] = {
    "alma_b20_b21": "ncs",
    "iris_w10": "mcuxpresso-sdk",
    "nora_b20_b21_b22": "ncs",
    "nora_w30": "ameba-rtos-d",
    "nora_w40": "esp-idf",
    "nora_w50_w51": "simplelink-wifi",
}

# Version folder for a clone without a version: the vendor's default branch.
DEFAULT_VERSIONS: dict[str, str] = {
    "iris_w10": "main",
    "nora_w30": "main",
    "nora_w40": "master",
    "nora_w50_w51": "main",
}


def host_kind() -> str:
    """Detect platform type: 'windows', 'macos', 'wsl', or 'linux'."""
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


def run_main(main) -> int:
    """A driver's entry point. Ctrl+C reaches every process in the console; the launcher reports it."""
    try:
        return main()
    except KeyboardInterrupt:
        return 130


def load_json(path: Path) -> dict:
    """A cached JSON config, or {} when it is missing or unreadable."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_json(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def newest(patterns: list[str]) -> Path | None:
    """Highest-versioned existing path across glob patterns ('~' and absolute patterns allowed)."""
    hits: list[Path] = []
    for pattern in patterns:
        expanded = os.path.expanduser(pattern)
        anchor = Path(expanded).anchor
        root, rel = (anchor, expanded[len(anchor):]) if anchor else (".", expanded)
        try:
            hits.extend(Path(root).glob(rel))
        except (OSError, ValueError, NotImplementedError):
            continue
    hits = [h for h in hits if h.exists()]
    return max(hits, key=lambda p: _version_key(str(p))) if hits else None


def short_path(value: str | Path) -> str:
    """The Windows 8.3 form of a path with spaces, for makefiles that cannot quote; unchanged elsewhere."""
    value = str(value)
    if host_kind() != "windows" or " " not in value:
        return value
    try:
        import ctypes
        from ctypes import wintypes

        fn = ctypes.windll.kernel32.GetShortPathNameW
        fn.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        fn.restype = wintypes.DWORD
        buf = ctypes.create_unicode_buffer(1024)
        if fn(value, buf, 1024) and buf.value:
            return buf.value
    except (OSError, AttributeError, ValueError):
        pass
    return value


def _slug(target: str) -> str:
    if target not in TARGETS:
        raise KeyError(f"Unknown target {target!r}. Known targets: {', '.join(sorted(TARGETS))}")
    return target


def module_dir(target: str) -> Path:
    """modules/<target>: the tracked profile plus the gitignored config/."""
    return MODULES_DIR / TARGETS[_slug(target)]


def sdks_root() -> Path:
    """Where new vendor SDKs are fetched: sdks/, or the WSL2 file system when this tree is on /mnt."""
    override = os.environ.get("UBX_SDKS_DIR")
    if override:
        return Path(override).expanduser()
    if host_kind() == "wsl" and SDK_ROOT.as_posix().startswith("/mnt/"):
        return WSL_SDKS_DIR
    return SDKS_DIR


def vendor_dir(target: str) -> Path:
    """sdks/<vendor>, holding one folder per fetched version."""
    return sdks_root() / VENDORS[_slug(target)]


def default_version(target: str) -> str:
    return DEFAULT_VERSIONS.get(_slug(target), "main")


def sdk_dir(target: str, version: str | None = None) -> Path:
    """sdks/<vendor>/<version>; version defaults to the vendor's default branch."""
    return vendor_dir(target) / (version or default_version(target))


def matter_dir(target: str) -> Path:
    """sdks/matter/<target>: in-tree Matter SDKs (native Linux and Windows hosts)."""
    return SDKS_DIR / "matter" / TARGETS[_slug(target)]


def _version_key(name: str) -> list:
    # 'v5.10' after 'v5.9': digit runs compare as numbers.
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]


def installed_sdks(target: str) -> list[Path]:
    """Fetched versions of the target's vendor SDK, newest tag first, branch names last."""
    found: dict[str, Path] = {}
    for root in (vendor_dir(target), SDKS_DIR / VENDORS[_slug(target)]):
        if root.is_dir():
            for p in root.iterdir():
                if p.is_dir():
                    found.setdefault(p.name, p)
    return sorted(found.values(), key=lambda p: _version_key(p.name), reverse=True)


def config_dir(target: str) -> Path:
    return module_dir(target) / "config"


def config_file(target: str, host: str | None = None) -> Path:
    return config_dir(target) / f"build.{host or host_kind()}.json"


def ensure(target: str) -> Path:
    """Create the target's config/ folder; return the module folder."""
    config_dir(target).mkdir(parents=True, exist_ok=True)
    return module_dir(target)


def resolve_config(target: str, host: str | None = None) -> Path:
    """Config file for a target, with its config/ folder created."""
    ensure(target)
    return config_file(target, host)


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
