#!/usr/bin/env python3
"""
Compare every vendor SDK and Matter version this SDK uses with upstream.

Developer check, not a user tool. It reads the pins from the drivers
themselves (nothing is listed twice) and asks each upstream repository for its
tags and branches with 'git ls-remote', which downloads no code.

    python scripts/check_versions.py            SDK and Matter
    python scripts/check_versions.py --sdk      SDK only
    python scripts/check_versions.py --matter   Matter only

  [OK]       the pin is the newest stable release of its kind
  [WARNING]  a newer stable release exists, or the installed SDK is older
  [INFO]     the SDK tracks a branch (main/master); the newest release is shown
  [FAIL]     the pin no longer exists upstream, or upstream did not answer

Exit code 1 when anything is [WARNING] or [FAIL]. Pre-releases (rc, beta,
dev, ea, pvw) never count as newer. A newer release is a hint, not an
instruction: a vendor pin moves with its companion pins (esp-matter names the
ESP-IDF it needs) and needs a build-all run before it is changed.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import iris_w10_build  # noqa: E402
import matter_build  # noqa: E402
import nora_w30_build  # noqa: E402
import nora_w40_build  # noqa: E402
import nora_w50_w51_build  # noqa: E402
import nordic_ncs_build  # noqa: E402
import target_paths  # noqa: E402

PRERELEASE = re.compile(r"(?<![a-z])(rc|dev|beta|alpha|pre|ea|pvw)\d*(?![a-z])", re.IGNORECASE)
TRACKED_BRANCHES = ("main", "master")


@dataclass(frozen=True)
class Pin:
    layer: str           # 'sdk' or 'matter'
    owner: str           # target key(s)
    name: str
    url: str
    revision: str
    # For a tracked branch: what the vendor's releases look like.
    release: str | None = None


@dataclass
class Refs:
    tags: list[str]
    heads: list[str]


def pins() -> list[Pin]:
    sdk = [
        Pin("sdk", "nora-b20-b21-b22, alma-b20-b21", "nRF Connect SDK",
            nordic_ncs_build.NCS_MANIFEST_URL, nordic_ncs_build.NCS_REVISION),
        Pin("sdk", "alma-w10-w11", "nRF Connect SDK (nRF7120E pre-release)",
            nordic_ncs_build.NCS_MANIFEST_URL, nordic_ncs_build.NCS_NRF7120E_REVISION),
        Pin("sdk", "iris-w10", "MCUXpresso SDK", iris_w10_build.MANIFEST_URL,
            target_paths.default_version("iris_w10"), release=r"^v\d+\.\d+\.\d+$"),
        Pin("sdk", "nora-w30", "Ameba-D SDK", nora_w30_build.SDK_URL,
            target_paths.default_version("nora_w30")),
        Pin("sdk", "nora-w40", "ESP-IDF", nora_w40_build.IDF_URL,
            target_paths.default_version("nora_w40"), release=r"^v\d+\.\d+(\.\d+)?$"),
    ]
    sdk += [Pin("sdk", "nora-w50-w51", f"TI {name}", url,
                target_paths.default_version("nora_w50_w51"), release=r"^wifi-[\d.]+$")
            for name, url in nora_w50_w51_build.REPOS.items()]
    matter = [Pin("matter", key, repo.name, repo.url, repo.revision)
              for key, target in matter_build.TARGETS.items() for repo in target.repos]
    return sdk + matter


@lru_cache(maxsize=None)
def ls_remote(url: str) -> Refs | None:
    try:
        out = subprocess.run(["git", "ls-remote", "--tags", "--heads", url],
                             capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    tags, heads = [], []
    for line in out.stdout.splitlines():
        ref = line.split("\t", 1)[-1]
        if ref.startswith("refs/tags/") and not ref.endswith("^{}"):
            tags.append(ref[len("refs/tags/"):])
        elif ref.startswith("refs/heads/"):
            heads.append(ref[len("refs/heads/"):])
    return Refs(tags, heads)


def version_key(name: str) -> list:
    return [(0, int(p), "") if p.isdigit() else (1, 0, p) for p in re.split(r"(\d+)", name)]


def family(pin: str) -> re.Pattern:
    """Refs shaped like the pin: 'release/v1.5' matches 'release/v1.6.1'."""
    parts = re.split(r"(\d+(?:\.\d+)*)", pin)
    body = "".join(r"\d+(?:\.\d+)*" if i % 2 else re.escape(p) for i, p in enumerate(parts))
    return re.compile(f"^{body}$")


def newest(names: list[str], pattern: re.Pattern | str) -> str | None:
    pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
    stable = [n for n in names if pattern.match(n) and not PRERELEASE.search(n)]
    return max(stable, key=version_key) if stable else None


def check(pin: Pin, refs: Refs | None) -> tuple[str, str]:
    """(marker, message) for one pin."""
    if refs is None:
        return "FAIL", f"no answer from {pin.url}"

    if pin.revision in TRACKED_BRANCHES:
        if pin.revision not in refs.heads:
            return "FAIL", f"branch {pin.revision} no longer exists upstream"
        latest = newest(refs.tags, pin.release) if pin.release else None
        tail = f"; newest release {latest}" if latest else "; no release tags"
        return "INFO", f"tracks {pin.revision}{tail}"

    if pin.revision in refs.tags:
        kind, names = "tag", refs.tags
    elif pin.revision in refs.heads:
        kind, names = "branch", refs.heads
    else:
        return "FAIL", f"{pin.revision} no longer exists upstream"

    latest = newest(names, family(pin.revision))
    if latest is None or version_key(latest) <= version_key(pin.revision):
        return "OK", f"{pin.revision} is the newest {kind}"
    line = release_line(pin.revision)
    same_line = newest([n for n in names if release_line(n) == line], family(pin.revision))
    if same_line and version_key(same_line) > version_key(pin.revision):
        return "WARNING", f"{pin.revision}, newer {kind}: {same_line} (newest overall {latest})"
    return "WARNING", f"{pin.revision} is the newest {line}.x; newer {kind}: {latest}"


def release_line(name: str) -> str:
    """'v5.5.5' -> 'v5.5': the part a patch release keeps."""
    found = re.search(r"\d+(?:\.\d+)?", name)
    return name[:found.end()] if found else name


def installed_ti_sdk() -> tuple[str, str] | None:
    """The TI installer's SDK is not a git checkout; compare its folder name."""
    sdk = nora_w50_w51_build.detect_installed_sdk()
    if sdk is None:
        return None
    found = re.search(r"(\d+(?:_\d+)+)$", sdk.name)
    refs = ls_remote(nora_w50_w51_build.REPOS["wifi-examples"])
    latest = newest(refs.tags, r"^wifi-[\d.]+$") if refs else None
    if not found or not latest:
        return "INFO", f"installed {sdk.name}"
    have = found.group(1).replace("_", ".")
    if version_key(have) < version_key(latest[len("wifi-"):]):
        return "WARNING", f"installed {have}, newer release: {latest[len('wifi-'):]}"
    return "OK", f"installed {have} is the newest release"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="check_versions.py",
                                     description="Compare SDK and Matter pins with upstream.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--sdk", action="store_true", help="SDK pins only")
    group.add_argument("--matter", action="store_true", help="Matter pins only")
    args = parser.parse_args(argv)
    layers = {"sdk"} if args.sdk else {"matter"} if args.matter else {"sdk", "matter"}

    worst = 0
    current = None
    for pin in pins():
        if pin.layer not in layers:
            continue
        if pin.layer != current:
            current = pin.layer
            print(f"\n=== {'Vendor SDKs (ubx-sdk)' if current == 'sdk' else 'Matter SDKs (ubx-matter)'} ===")
        marker, message = check(pin, ls_remote(pin.url))
        print(f"{'[' + marker + ']':<10} {pin.owner:<31} {pin.name:<20} {message}")
        worst = max(worst, marker in ("WARNING", "FAIL"))

    if "sdk" in layers:
        ti = installed_ti_sdk()
        if ti:
            print(f"{'[' + ti[0] + ']':<10} {'nora-w50-w51':<31} {'TI Wi-Fi SDK':<20} {ti[1]}")
            worst = max(worst, ti[0] in ("WARNING", "FAIL"))
    print()
    return worst


if __name__ == "__main__":
    sys.exit(main())
