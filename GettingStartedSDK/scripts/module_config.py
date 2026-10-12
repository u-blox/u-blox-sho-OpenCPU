#!/usr/bin/env python3
"""
u-blox module configuration: RF calibration, TX power limits, regulatory
domain and MAC / Bluetooth device address.

One applier for every target. What gets applied is data, not code: each target
has a profile at ``modules/<target>/profile.json`` listing operations against
the fetched vendor SDK tree. The assets themselves stay where u-blox publishes
them, in the per-module folders at the repository root, and are referenced
rather than duplicated.

Normally driven by the launcher:

    ubx-sdk <target> --variant <PART> --region <DOMAIN> --rf-config
    ubx-sdk <target> --mac

Run directly only when debugging this layer:

    module_config.py <target> variants
    module_config.py <target> status
    module_config.py <target> apply --variant PART [--region ETSI] [--set k=v]
    module_config.py <target> revert
    module_config.py <target> mac [--serial PORT]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import target_paths

SDK_ROOT = target_paths.SDK_ROOT
REPO_ROOT = SDK_ROOT.parent
MODULES_DIR = SDK_ROOT / "modules"
BACKUP_SUFFIX = ".ubx-orig"
STATE_NAME = "rf_config.json"

TARGET_KEYS = ("alma-b20-b21", "iris-w10", "nora-b20-b21-b22", "nora-w30", "nora-w40", "nora-w50-w51")


def slug(key: str) -> str:
    return key.replace("-", "_")


# ============================================================================
# PROFILE
# ============================================================================

def profile_path(key: str) -> Path:
    return MODULES_DIR / target_paths.TARGETS[slug(key)] / "profile.json"


def load_profile(key: str) -> dict:
    path = profile_path(key)
    if not path.exists():
        raise FileNotFoundError(f"No module profile for {key}: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_variant(profile: dict, name: str | None) -> tuple[str | None, dict]:
    """Match a part number against the profile, tolerating ordering suffixes."""
    variants = profile.get("variants") or {}
    if not variants:
        return None, {}
    if not name:
        raise ValueError(
            "No variant selected. Pass --variant <PART>, one of: " + ", ".join(sorted(variants))
        )

    wanted = name.strip().upper()
    if wanted in variants:
        return wanted, variants[wanted]

    # 'IRIS-W101-00B-00' -> 'IRIS-W101-00B' -> 'IRIS-W101'
    parts = wanted.split("-")
    while len(parts) > 1:
        parts.pop()
        candidate = "-".join(parts)
        if candidate in variants:
            return candidate, variants[candidate]

    prefixed = [v for v in variants if v.startswith(wanted)]
    if len(prefixed) == 1:
        return prefixed[0], variants[prefixed[0]]
    if prefixed:
        raise ValueError(f"{name} is ambiguous. Did you mean: {', '.join(sorted(prefixed))}?")
    raise ValueError(f"Unknown variant {name}. Known: {', '.join(sorted(variants))}")


def build_vars(profile: dict, variant: str | None, variant_cfg: dict, overrides: dict) -> dict:
    values = dict(profile.get("variables") or {})
    values.update(variant_cfg.get("vars") or {})
    values.update(overrides)
    values["variant"] = variant or profile.get("label", "")
    return values


def expand(text: str, values: dict) -> str:
    try:
        return text.format(**values)
    except KeyError as exc:
        raise ValueError(f"Profile references undefined variable {exc} in: {text}") from exc


# ============================================================================
# VENDOR SDK LOCATION
# ============================================================================

def _build_config(key: str) -> dict:
    path = target_paths.config_file(slug(key))
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def vendor_sdk_root(key: str) -> Path | None:
    """Locate the fetched vendor SDK, mirroring each driver's own search order."""
    cfg = _build_config(key)
    s = slug(key)

    if key == "nora-w30":
        candidates = [cfg.get("sdk_path"),
                      SDK_ROOT / "ameba-rtos-d",
                      target_paths.sdk_dir(s) / "realtek-rtos-sdk"]
        marker = "component/common/drivers/wlan"
    elif key == "nora-w40":
        candidates = [cfg.get("idf_path"),
                      target_paths.sdk_dir(s) / "esp-idf",
                      SDK_ROOT / "esp-idf",
                      Path.home() / "esp" / "esp-idf"]
        marker = "components/esp_phy"
    elif key == "iris-w10":
        candidates = [cfg.get("workspace"),
                      target_paths.sdk_dir(s) / "mcuxpresso-sdk",
                      SDK_ROOT / "mcuxpresso-sdk",
                      REPO_ROOT / "mcuxpresso-sdk"]
        marker = None
    else:
        return None

    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if marker is None:
            # west workspace: assets sit in the mcuxsdk tree inside it.
            for inner in (path / "mcuxsdk", path):
                if (inner / "middleware").is_dir() or (inner / "components").is_dir():
                    return inner
        elif (path / marker).exists():
            return path
    return None


def idf_version(root: Path) -> tuple[int, int] | None:
    header = root / "components" / "esp_common" / "include" / "esp_idf_version.h"
    try:
        text = header.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    major = re.search(r"#define\s+ESP_IDF_VERSION_MAJOR\s+(\d+)", text)
    minor = re.search(r"#define\s+ESP_IDF_VERSION_MINOR\s+(\d+)", text)
    if major and minor:
        return int(major.group(1)), int(minor.group(1))
    return None


def mcux_version(root: Path) -> tuple[int, int] | None:
    """MCUXpresso release as (YY, MM), e.g. 25.06.00 -> (25, 6)."""
    try:
        text = (root / "MCUX_VERSION").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    year = re.search(r"CURRENT_YEAR\s*=\s*(\d+)", text)
    major = re.search(r"VERSION_MAJOR\s*=\s*(\d+)", text)
    if year and major:
        return int(year.group(1)), int(major.group(1))
    return None


def sdk_version(key: str, root: Path) -> tuple[int, int] | None:
    if key == "nora-w40":
        return idf_version(root)
    if key == "iris-w10":
        return mcux_version(root)
    return None


def step_applies(step: str | dict, found: tuple[int, int] | None) -> bool:
    if isinstance(step, str) or not step.get("sdk_version") or found is None:
        return True
    return version_matches(found, step["sdk_version"])


def step_text(step: str | dict) -> str:
    return step if isinstance(step, str) else step["text"]


def version_matches(found: tuple[int, int], spec: str) -> bool:
    """'>=5.1,<5.2 || >=6.2,<6.3': commas AND clauses, '||' ORs ranges."""
    for alternative in spec.split("||"):
        ok = True
        for clause in alternative.split(","):
            match = re.match(r"(>=|<=|<|>|==)\s*(\d+)\.(\d+)", clause.strip())
            if not match:
                continue
            operator, wanted = match.group(1), (int(match.group(2)), int(match.group(3)))
            ok = {
                ">=": found >= wanted, "<=": found <= wanted,
                ">": found > wanted, "<": found < wanted, "==": found == wanted,
            }[operator]
            if not ok:
                break
        if ok:
            return True
    return False


def check_requires(key: str, profile: dict, root: Path) -> list[str]:
    """Return a list of unmet requirements, empty when the SDK is usable."""
    spec = (profile.get("requires") or {}).get("sdk_version")
    if not spec or key != "nora-w40":
        return []
    found = sdk_version(key, root)
    if found is None:
        return ["ESP-IDF version could not be determined."]
    if not version_matches(found, spec):
        return [f"ESP-IDF {found[0]}.{found[1]} does not satisfy '{spec}'."]
    return []


# ============================================================================
# STATE
# ============================================================================

def state_path(key: str) -> Path:
    directory = target_paths.config_dir(slug(key))
    directory.mkdir(parents=True, exist_ok=True)
    return directory / STATE_NAME


def load_state(key: str) -> dict:
    path = state_path(key)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_state(key: str, state: dict) -> None:
    state_path(key).write_text(json.dumps(state, indent=2), encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ============================================================================
# OPERATIONS
# ============================================================================

def backup(dst: Path, records: list) -> None:
    """Keep the vendor original once, so revert always restores the first state."""
    marker = dst.with_name(dst.name + BACKUP_SUFFIX)
    if dst.exists() and not marker.exists():
        shutil.copy2(dst, marker)
    if marker.exists() and str(marker) not in records:
        records.append(str(marker))


def apply_copy(src: Path, dst: Path, records: list, replace_only: bool,
               created: list) -> str:
    if not src.exists():
        return f"[FAIL] asset missing: {src}"
    if replace_only and not dst.exists():
        return f"[INFO] skipped, not part of this SDK: {dst}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    marker = dst.with_name(dst.name + BACKUP_SUFFIX)
    if not dst.exists() and not marker.exists() and str(dst) not in created:
        # No vendor original to restore, so revert has to delete it instead.
        created.append(str(dst))
    backup(dst, records)
    shutil.copy2(src, dst)
    return f"[OK]   {dst}"


def apply_copy_tree(src: Path, dst: Path) -> str:
    if not src.is_dir():
        return f"[FAIL] asset missing: {src}"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return f"[OK]   {dst}/"


def apply_replace_line(path: Path, old: str, new: str, records: list) -> str:
    if not path.exists():
        return f"[FAIL] file missing: {path}"
    # newline="" keeps the file's own line endings; a CRLF makefile breaks '\' continuations.
    with path.open(encoding="utf-8", errors="replace", newline="") as handle:
        text = handle.read()
    if new in text:
        # Never back up now - the file on disk is already the modified one.
        marker = path.with_name(path.name + BACKUP_SUFFIX)
        if marker.exists() and str(marker) not in records:
            records.append(str(marker))
        return f"[INFO] already applied: {path}"
    if old not in text:
        return f"[FAIL] anchor line not found in {path}: {old}"
    backup(path, records)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text.replace(old, new))
    return f"[OK]   {path}"


def _git_apply(directory: Path, patch: Path, strip: int, *flags: str) -> subprocess.CompletedProcess:
    # Inside a repo, git apply silently skips every path outside the repo-relative
    # prefix and still exits 0. Stop discovery so it behaves like plain patch.
    env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(directory.resolve().parent))
    cmd = ["git", "-C", str(directory), "apply", "-v", f"-p{strip}", *flags, str(patch)]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode == 0 and "Skipped patch" in (result.stderr + result.stdout):
        result.returncode = 1
    return result


def patch_applied(patch: Path, directory: Path, strip: int) -> bool:
    """True when the patch reverses cleanly, i.e. it is in place."""
    if shutil.which("patch"):
        probe = subprocess.run(["patch", "--dry-run", "-R", "-f", "-p", str(strip),
                                "-i", str(patch), "-d", str(directory)],
                               capture_output=True, text=True)
        return probe.returncode == 0
    if shutil.which("git"):
        return _git_apply(directory, patch, strip, "--check", "--reverse").returncode == 0
    return False


def run_patch(patch: Path, directory: Path, strip: int, reverse: bool = False) -> tuple[bool, str]:
    if not patch.exists():
        return False, f"[FAIL] patch missing: {patch}"
    if not directory.is_dir():
        return False, f"[FAIL] patch target missing: {directory}"

    if not reverse and patch_applied(patch, directory, strip):
        return True, f"[INFO] already applied: {patch.name}"

    if shutil.which("patch"):
        cmd = ["patch", "-f"] + (["-R"] if reverse else []) + \
              ["-p", str(strip), "-i", str(patch), "-d", str(directory)]
        result = subprocess.run(cmd, capture_output=True, text=True)
    elif shutil.which("git"):
        result = _git_apply(directory, patch, strip, *(["--reverse"] if reverse else []))
    else:
        return False, "[FAIL] neither 'patch' nor 'git' found; cannot apply the patch."

    if result.returncode != 0:
        lines = (result.stderr or result.stdout).strip().splitlines()
        detail = next((l for l in lines if l.startswith(("error", "Skipped"))), lines[0] if lines else "")
        return False, f"[FAIL] {patch.name}: {detail or 'patch failed'}"
    return True, f"[OK]   {patch.name}"


# ============================================================================
# COMMANDS
# ============================================================================

def print_pending(profile: dict) -> int:
    print(f"[WARNING] No u-blox RF configuration is available for {profile['label']}.")
    print(f"          {profile.get('pending_reason', '')}")
    for step in profile.get("manual_steps") or []:
        print(f"          - {step_text(step)}")
    return 0


def cmd_variants(key: str, args) -> int:
    profile = load_profile(key)
    print(f"\n{profile['label']}  ({profile.get('status', 'unknown')})\n")
    variants = profile.get("variants") or {}
    if not variants:
        return print_pending(profile)
    width = max(len(v) for v in variants)
    for name in sorted(variants):
        print(f"  {name:<{width}}  {variants[name].get('description', '')}")
    print()
    return 0


def cmd_apply(key: str, args) -> int:
    profile = load_profile(key)
    if profile.get("status") != "ready":
        return print_pending(profile)

    overrides = dict(pair.split("=", 1) for pair in (args.set or []))
    state = load_state(key)
    variant, variant_cfg = resolve_variant(profile, args.variant or state.get("variant"))
    values = build_vars(profile, variant, variant_cfg, overrides)

    if state.get("applied") and state.get("variant") != variant:
        # Variant ops overlap (e.g. the same makefile line), so start from vendor files.
        print(f"[INFO] Switching from {state.get('variant')} to {variant}; reverting first.")
        cmd_revert(key, args)
        state = load_state(key)

    root = Path(args.sdk).expanduser().resolve() if getattr(args, "sdk", None) else vendor_sdk_root(key)
    if root is None or not root.is_dir():
        print(f"[FAIL] {profile['label']} SDK not found. Run --clone first.")
        return 1
    if state.get("applied") and state.get("sdk_root") not in (None, str(root)):
        # One state file per target; mixing two SDK trees would make revert lose one.
        print(f"[FAIL] RF configuration is applied to {state['sdk_root']}.")
        print(f"       Revert it first: python scripts/module_config.py {key} revert")
        return 1

    problems = check_requires(key, profile, root)
    if problems and not args.force:
        for problem in problems:
            print(f"[FAIL] {problem}")
        hint = (profile.get("requires") or {}).get("hint")
        if hint:
            print(f"       {hint}")
        print(f"       Override with: python scripts/module_config.py {key} apply --force")
        return 1
    for problem in problems:
        print(f"[WARNING] {problem} (forced)")

    print(f"\nApplying u-blox RF configuration for {variant}")
    print(f"  SDK:     {root}")
    print(f"  Profile: {profile_path(key)}\n")

    backups: list[str] = list(state.get("backups") or [])
    created: list[str] = list(state.get("created") or [])
    applied: list[dict] = []
    failed = False
    found_version = sdk_version(key, root)

    def record(message: str) -> bool:
        """An op counts as in place whether we just did it or found it done."""
        return message.startswith("[OK]") or message.startswith("[INFO] already applied")

    for op in profile.get("sdk_patch", []):
        kind = op["op"]
        spec = op.get("sdk_version")
        if spec and found_version and not version_matches(found_version, spec):
            continue
        note = expand(op.get("note", ""), values)
        if note:
            print(f"  {note}")
        if op.get("warning"):
            print(f"    [WARNING] {expand(op['warning'], values)}")

        if kind in ("copy", "replace"):
            src = REPO_ROOT / expand(op["src"], values)
            dst = root / expand(op["dst"], values)
            message = apply_copy(src, dst, backups, replace_only=(kind == "replace"),
                                 created=created)
            if record(message):
                applied.append({"op": kind, "path": str(dst), "sha256": sha256(dst)})
        elif kind == "copy-tree":
            src = REPO_ROOT / expand(op["src"], values)
            dst = root / expand(op["dst"], values)
            message = apply_copy_tree(src, dst)
            if record(message):
                applied.append({"op": kind, "path": str(dst)})
        elif kind == "replace-line":
            path = root / expand(op["file"], values)
            message = apply_replace_line(path, expand(op["from"], values),
                                         expand(op["to"], values), backups)
            if record(message):
                applied.append({"op": kind, "path": str(path), "sha256": sha256(path)})
        elif kind == "patch":
            patch = REPO_ROOT / expand(op["patch"], values)
            directory = root / expand(op.get("dir", "."), values)
            ok, message = run_patch(patch, directory, int(op.get("strip", 1)))
            if ok and record(message):
                applied.append({"op": kind, "patch": str(patch),
                                "dir": str(directory), "strip": int(op.get("strip", 1))})
        else:
            message = f"[FAIL] unknown op '{kind}' in {profile_path(key)}"

        print(f"    {message}")
        failed = failed or message.startswith("[FAIL]")

    save_state(key, {
        "variant": variant,
        "region": args.region or state.get("region"),
        "variables": {k: v for k, v in values.items() if k != "variant"},
        "sdk_root": str(root),
        "applied": applied,
        "backups": backups,
        "created": created,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })

    print_regulatory(profile, args.region or state.get("region"))
    print_manual(profile, values, found_version)
    print_verify(profile)

    if failed:
        print("[FAIL] RF configuration incomplete. The build is not regulatory compliant.\n")
        return 1
    print(f"[OK] RF configuration applied for {variant}.\n")
    return 0


def print_regulatory(profile: dict, region: str | None) -> None:
    regulatory = profile.get("regulatory")
    if not regulatory:
        return
    print("\nRegulatory domain")
    domains = regulatory.get("domains") or {}
    if region:
        code = domains.get(region.upper())
        if code is None:
            print(f"  [WARNING] Unknown domain '{region}'. Known: {', '.join(domains)}")
        else:
            print(f"  {regulatory['api'].replace('<code>', code).replace('<cc>', code)}")
            print(f"  Apply {regulatory.get('when', '')}.")
    else:
        print("  [WARNING] No --region given. The channel plan and the certified power")
        print("            table are selected at runtime and are not set by --rf-config.")
        if domains:
            print(f"  {regulatory.get('api', '')}")
            for name, code in domains.items():
                print(f"    {name:<6} {code}")
    for note in regulatory.get("notes") or []:
        print(f"  - {note}")


def print_manual(profile: dict, values: dict, found: tuple[int, int] | None) -> None:
    steps = [s for s in profile.get("manual_steps") or [] if step_applies(s, found)]
    if not steps:
        return
    print("\nStill manual" + (f" (SDK {found[0]}.{found[1]:02d})" if found else ""))
    for step in steps:
        print(f"  - {expand(step_text(step), values)}")


def print_verify(profile: dict) -> None:
    verify = profile.get("verify") or {}
    if not verify:
        return
    print("\nVerify")
    if verify.get("log_contains"):
        print(f"  - The application log must contain: {verify['log_contains']}")
    for note in verify.get("notes") or []:
        print(f"  - {note}")


def cmd_status(key: str, args) -> int:
    profile = load_profile(key)
    state = load_state(key)

    print(f"\n{profile['label']} - module configuration")
    if profile.get("status") != "ready":
        print(f"  [WARNING] {profile.get('pending_reason', 'Not available yet.')}\n")
        return 0
    if not state.get("applied"):
        print("  [WARNING] RF configuration NOT applied - firmware built from this SDK")
        print("            is not regulatory compliant.")
        print(f"            Fix: --variant <PART> --rf-config   ({', '.join(sorted(profile['variants']))})\n")
        return 0

    print(f"  Variant: {state['variant']}")
    print(f"  Region:  {state.get('region') or '[WARNING] not set'}")
    print(f"  Applied: {state['timestamp']}")
    drifted = 0
    for entry in state["applied"]:
        path = Path(entry.get("path", entry.get("dir", "")))
        if entry["op"] == "patch":
            if patch_applied(Path(entry["patch"]), Path(entry["dir"]), entry["strip"]):
                print(f"  [OK]   patch {Path(entry['patch']).name}")
            else:
                print(f"  [FAIL] patch no longer in place: {Path(entry['patch']).name}")
                drifted += 1
            continue
        if not path.exists():
            print(f"  [FAIL] missing: {path}")
            drifted += 1
        elif entry.get("sha256") and sha256(path) != entry["sha256"]:
            print(f"  [WARNING] changed since apply: {path}")
            drifted += 1
        else:
            print(f"  [OK]   {path}")
    print()
    return 1 if drifted else 0


def cmd_revert(key: str, args) -> int:
    state = load_state(key)
    if not state.get("applied"):
        print("[INFO] Nothing to revert.")
        return 0

    for entry in reversed(state["applied"]):
        if entry["op"] == "patch":
            ok, message = run_patch(Path(entry["patch"]), Path(entry["dir"]),
                                    entry["strip"], reverse=True)
            print(f"  {message}")
        elif entry["op"] == "copy-tree":
            path = Path(entry["path"])
            if path.exists():
                shutil.rmtree(path)
            print(f"  [OK]   removed {path}")

    for marker in state.get("backups", []):
        original = Path(marker)
        if original.exists():
            shutil.move(str(original), str(original.with_name(original.name[:-len(BACKUP_SUFFIX)])))
            print(f"  [OK]   restored {original.name[:-len(BACKUP_SUFFIX)]}")

    for added in state.get("created", []):
        path = Path(added)
        if path.exists():
            path.unlink()
            print(f"  [OK]   removed {path.name}")

    save_state(key, {"variant": state.get("variant"), "region": state.get("region")})
    print("[OK] Reverted to the vendor SDK files.\n")
    return 0


def cmd_mac(key: str, args) -> int:
    profile = load_profile(key)
    mac = profile.get("mac") or {}
    print(f"\n{profile['label']} - MAC / device address")
    print(f"  Source: {mac.get('source', 'unknown')}")

    if mac.get("read") == "esptool":
        rc = read_mac_esptool(key, args.serial)
    else:
        print("  [INFO] No host-side reader is wired up for this target.")
        rc = 0

    for note in mac.get("notes") or []:
        print(f"  - {note}")
    for step in profile.get("manual_steps") or []:
        if "address" in step_text(step).lower():
            print(f"  - {step_text(step)}")
    print()
    return rc


def read_mac_esptool(key: str, port: str | None) -> int:
    root = vendor_sdk_root(key)
    candidates = [[sys.executable, "-m", "esptool"]]
    if root:
        bundled = root / "components" / "esptool_py" / "esptool" / "esptool.py"
        if bundled.exists():
            candidates.append([sys.executable, str(bundled)])
    if shutil.which("esptool.py"):
        candidates.insert(0, ["esptool.py"])

    for base in candidates:
        cmd = list(base) + (["--port", port] if port else []) + ["read_mac"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
        except OSError:
            continue
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "MAC:" in line:
                    print(f"  {line.strip()}")
            return 0
        if "No module named" not in result.stderr:
            print(f"  [FAIL] {(result.stderr or result.stdout).strip().splitlines()[-1]}")
            return 1
    print("  [FAIL] esptool not found. Run '--install' first, or 'pip install esptool'.")
    return 1


# ============================================================================
# ENTRY POINT
# ============================================================================

COMMANDS = {
    "variants": cmd_variants,
    "status": cmd_status,
    "apply": cmd_apply,
    "revert": cmd_revert,
    "mac": cmd_mac,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="module_config.py",
        description="Apply u-blox RF calibration, TX power and regulatory configuration.")
    parser.add_argument("target", choices=TARGET_KEYS)
    parser.add_argument("command", choices=sorted(COMMANDS))
    parser.add_argument("--variant", help="u-blox part number, e.g. NORA-W301")
    parser.add_argument("--region", help="Regulatory domain, e.g. ETSI")
    parser.add_argument("--serial", help="Serial port, for 'mac'")
    parser.add_argument("--set", action="append", metavar="KEY=VALUE",
                        help="Override a profile variable, e.g. --set flash_vendor=Fidelex")
    parser.add_argument("--force", action="store_true",
                        help="Apply even when the SDK version is out of range")
    parser.add_argument("--sdk", help="Vendor SDK root to patch instead of the auto-detected one, "
                                      "e.g. the Matter ESP-IDF checkout")
    args = parser.parse_args(argv)

    try:
        return COMMANDS[args.command](args.target, args)
    except (ValueError, FileNotFoundError) as exc:
        print(f"[FAIL] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
