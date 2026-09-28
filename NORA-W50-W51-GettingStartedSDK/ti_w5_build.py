#!/usr/bin/env python3
"""
Build TI SimpleLink Wi-Fi SDK examples for NORA-W50/W51 (TI CC35x1E).

Works on Windows, WSL2 and native Linux. It can use either:

  * an SDK installed by the TI installer   (C:\\ti\\simplelink_wifi_sdk_*, ~/ti/...)
  * TI's example repos cloned from GitHub  (SDK comes along as a git submodule)

Typical flow:

    python ti_w5_build.py doctor                    # what is installed / missing
    python ti_w5_build.py configure                 # write tool paths into imports.mak
    python ti_w5_build.py build-sdk                 # build SDK libraries (slow, once)
    python ti_w5_build.py list                      # show available examples
    python ti_w5_build.py build network_terminal

If you have no installed SDK, get one with:

    python ti_w5_build.py clone
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_BOARD = "LP_EM_CC35X1"

REPOS = {
    "wifi-examples": "https://github.com/TexasInstruments/simplelink-wifi-examples.git",
    "coresdk-examples": "https://github.com/TexasInstruments/simplelink-coresdk_wifi-examples.git",
}

# imports.mak keys this script manages; everything else in the file is left alone.
TOOL_KEYS = (
    "SYSCONFIG_TOOL",
    "TICLANG_ARMCOMPILER",
    "GCC_ARMCOMPILER",
    "CMAKE",
    "PYTHON",
    "SIMPLELINK_WIFI_TOOLBOX_INSTALL_DIR",
)


# --------------------------------------------------------------------------- #
# Host helpers
# --------------------------------------------------------------------------- #

def host_kind() -> str:
    if os.name == "nt":
        return "windows"
    if sys.platform.startswith("linux"):
        try:
            if "microsoft" in Path("/proc/version").read_text().lower():
                return "wsl"
        except OSError:
            pass
        return "linux"
    return platform.system().lower()


HOST = host_kind()
IS_WINDOWS = HOST == "windows"
EXE = ".exe" if IS_WINDOWS else ""


class Fail(Exception):
    pass


def log(msg: str) -> None:
    print(f"[ti-w5] {msg}", flush=True)


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> int:
    log(f"$ {' '.join(cmd)}" + (f"   (in {cwd})" if cwd else ""))
    rc = subprocess.call(cmd, cwd=str(cwd) if cwd else None)
    if check and rc != 0:
        raise Fail(f"command failed with exit code {rc}: {' '.join(cmd)}")
    return rc


def natural_key(p: Path):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def newest(patterns: list[str]) -> Path | None:
    """Highest-versioned existing path across a list of glob patterns."""
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
    return sorted(hits, key=natural_key)[-1] if hits else None


def short_path(value: str) -> str:
    """TI's imports.mak cannot handle spaces; fall back to the 8.3 name on Windows."""
    if not IS_WINDOWS or " " not in value:
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
    except Exception:  # noqa: BLE001 - best effort only
        pass
    return value


def mak_path(p: Path | str) -> str:
    """imports.mak wants forward slashes and no spaces, even on Windows."""
    return short_path(str(p)).replace("\\", "/")


# --------------------------------------------------------------------------- #
# Toolchain detection
# --------------------------------------------------------------------------- #

def detect_sysconfig() -> Path | None:
    name = "sysconfig_cli.bat" if IS_WINDOWS else "sysconfig_cli.sh"
    pats = (
        [f"C:/ti/sysconfig_*/{name}", f"C:/ti/ccs*/ccs/utils/sysconfig_*/{name}"]
        if IS_WINDOWS
        else [f"/opt/ti/sysconfig_*/{name}", f"~/ti/sysconfig_*/{name}",
              f"/opt/ti/ccs*/ccs/utils/sysconfig_*/{name}",
              f"~/ti/ccs*/ccs/utils/sysconfig_*/{name}"]
    )
    return newest(pats)


def detect_ticlang() -> Path | None:
    pats = (
        ["C:/ti/ti-cgt-armllvm*", "C:/ti/ccs*/ccs/tools/compiler/ti-cgt-armllvm*"]
        if IS_WINDOWS
        else ["/opt/ti/ti-cgt-armllvm*", "~/ti/ti-cgt-armllvm*",
              "/opt/ti/ccs*/ccs/tools/compiler/ti-cgt-armllvm*"]
    )
    hit = newest(pats)
    return hit if hit and (hit / "bin" / f"tiarmclang{EXE}").exists() else None


def detect_gcc() -> Path | None:
    pats = (
        ["C:/arm-none-eabi-gcc/*", "C:/ti/arm-none-eabi*", "C:/arm-gnu-toolchain*",
         "C:/Program Files (x86)/Arm GNU Toolchain arm-none-eabi/*",
         "C:/Program Files/Arm GNU Toolchain arm-none-eabi/*",
         "C:/Program Files/Arm/GNU Toolchain*"]
        if IS_WINDOWS
        else ["/opt/arm-gnu-toolchain*", "/opt/gcc-arm-none-eabi*",
              "/usr/local/arm-gnu-toolchain*", "~/arm-gnu-toolchain*", "~/ti/arm-gnu-toolchain*"]
    )
    hit = newest(pats)
    if hit and (hit / "bin" / f"arm-none-eabi-gcc{EXE}").exists():
        return hit
    onpath = shutil.which("arm-none-eabi-gcc")
    return Path(onpath).resolve().parent.parent if onpath else None


def detect_make() -> Path | None:
    if IS_WINDOWS:
        # TI's own gmake is the best match for the SDK makefiles.
        hit = newest(["C:/ti/ccs*/ccs/utils/bin/gmake.exe"])
        if hit:
            return hit
        for name in ("gmake", "mingw32-make", "make"):
            found = shutil.which(name)
            if found:
                return Path(found)
        return newest([
            "~/AppData/Local/Microsoft/WinGet/Packages/ezwinports.make*/bin/make.exe",
            "C:/Program Files (x86)/GnuWin32/bin/make.exe",
            "C:/ProgramData/chocolatey/bin/make.exe",
            "C:/msys64/usr/bin/make.exe",
        ])
    found = shutil.which("make")
    return Path(found) if found else None


def detect_toolbox() -> Path | None:
    pats = (
        ["C:/ti/simplelink_wifi_toolbox*"]
        if IS_WINDOWS
        else ["/opt/ti/simplelink_wifi_toolbox*", "~/ti/simplelink_wifi_toolbox*"]
    )
    return newest(pats)


def detect_installed_sdk() -> Path | None:
    pats = (
        ["C:/ti/simplelink_wifi_sdk*"]
        if IS_WINDOWS
        else ["/opt/ti/simplelink_wifi_sdk*", "~/ti/simplelink_wifi_sdk*"]
    )
    hit = newest(pats)
    return hit if hit and (hit / "imports.mak").exists() else None


def detect_tools() -> dict[str, str]:
    cmake = shutil.which("cmake") or (
        newest(["C:/Program Files/CMake/bin/cmake.exe", "C:/cmake*/bin/cmake.exe"])
        if IS_WINDOWS else None
    )
    found: dict[str, object] = {
        "SYSCONFIG_TOOL": detect_sysconfig(),
        "TICLANG_ARMCOMPILER": detect_ticlang(),
        "GCC_ARMCOMPILER": detect_gcc(),
        "CMAKE": Path(cmake) if cmake else None,
        "SIMPLELINK_WIFI_TOOLBOX_INSTALL_DIR": detect_toolbox(),
        "MAKE": detect_make(),
        "GIT": Path(shutil.which("git")) if shutil.which("git") else None,
    }
    return {k: str(v) for k, v in found.items() if v}


# --------------------------------------------------------------------------- #
# Config (per host kind, so Windows and WSL can share the same folder)
# --------------------------------------------------------------------------- #

def config_file() -> Path:
    return SCRIPT_DIR / f".ti_w5_build.{HOST}.json"


def load_config() -> dict:
    f = config_file()
    try:
        return json.loads(f.read_text()) if f.exists() else {}
    except json.JSONDecodeError:
        return {}


def save_config(**updates) -> None:
    cfg = load_config()
    cfg.update({k: v for k, v in updates.items() if v is not None})
    config_file().write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")


def resolve_tools(args) -> dict[str, str]:
    """Detected tools, overridden by saved config, overridden by CLI flags."""
    tools = detect_tools()
    tools.update(load_config().get("tools", {}))
    for key in (*TOOL_KEYS, "MAKE"):
        override = getattr(args, key.lower(), None)
        if override:
            tools[key] = override
    return tools


def default_workspace() -> Path:
    env = os.environ.get("TI_W5_WORKSPACE")
    if env:
        return Path(env).expanduser().resolve()
    if HOST == "wsl":
        # /mnt/<drive> builds are painfully slow under WSL2.
        return Path.home() / "ti-w5"
    return SCRIPT_DIR / "workspace"


def workspace_of(args) -> Path:
    if getattr(args, "workspace", None):
        return Path(args.workspace).expanduser().resolve()
    saved = load_config().get("workspace")
    return Path(saved) if saved else default_workspace()


# --------------------------------------------------------------------------- #
# SDK trees
# --------------------------------------------------------------------------- #

class Tree:
    """An SDK plus the example tree that belongs to it."""

    def __init__(self, name: str, sdk: Path, examples: Path):
        self.name = name
        self.sdk = sdk
        self.examples = examples

    def imports_mak(self) -> list[Path]:
        found = {self.sdk / "imports.mak", self.examples.parent / "imports.mak"}
        return sorted(f for f in found if f.is_file())

    def __str__(self) -> str:
        return f"{self.name}  ({self.sdk})"


def submodule_sdk(repo_root: Path) -> Path | None:
    for name in ("Simplelink-wifi-sdk", "simplelink-wifi-sdk", "simplelink_wifi_sdk"):
        if (repo_root / name / "imports.mak").exists():
            return repo_root / name
    for child in sorted(p for p in repo_root.iterdir() if p.is_dir()):
        if (child / "imports.mak").exists() and child.name != "examples":
            return child
    return None


def discover_trees(ws: Path) -> dict[str, Tree]:
    trees: dict[str, Tree] = {}
    installed = detect_installed_sdk()
    if installed:
        trees["installed"] = Tree("installed", installed, installed / "examples")
    for repo in REPOS:
        root = ws / repo
        if not root.is_dir():
            continue
        sdk = submodule_sdk(root)
        if sdk:
            trees[repo] = Tree(repo, sdk, root / "examples")
    return trees


def active_tree(args) -> Tree:
    if getattr(args, "sdk", None):
        sdk = Path(args.sdk).expanduser().resolve()
        if not (sdk / "imports.mak").exists():
            raise Fail(f"{sdk} has no imports.mak, so it is not an SDK root")
        return Tree("custom", sdk, sdk / "examples")

    ws = workspace_of(args)
    trees = discover_trees(ws)
    if not trees:
        raise Fail(
            "no SDK found. Either install the TI SimpleLink Wi-Fi SDK "
            "(https://www.ti.com/tool/download/SIMPLELINK-WIFI-SDK), "
            "or run: python ti_w5_build.py clone"
        )

    wanted = getattr(args, "source", None) or load_config().get("source")
    if wanted and wanted in trees:
        return trees[wanted]
    if wanted:
        raise Fail(f"source '{wanted}' not available. Found: {', '.join(trees)}")
    return trees.get("installed") or next(iter(trees.values()))


# --------------------------------------------------------------------------- #
# imports.mak patching
# --------------------------------------------------------------------------- #

def patch_imports_mak(path: Path, tools: dict[str, str]) -> None:
    backup = path.with_suffix(path.suffix + ".orig")
    if not backup.exists():
        shutil.copy2(path, backup)
        log(f"backed up {path.name} -> {backup.name}")

    text = path.read_text(encoding="utf-8", errors="replace")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    applied: list[str] = []

    for key in TOOL_KEYS:
        value = tools.get(key)
        if not value:
            continue
        # Deliberately does not match commented-out lines; imports.mak documents
        # each variable with a '#   KEY ?= ...' example that must stay a comment.
        pattern = re.compile(rf"^\s*{re.escape(key)}\s*\??=.*$")
        replacement = f"{key:<22} ?= {mak_path(value)}"
        for i, line in enumerate(lines):
            if pattern.match(line):
                lines[i] = replacement
                break
        else:
            lines.append(replacement)
        applied.append(key)

    path.write_text(newline.join(lines) + newline, encoding="utf-8")
    log(f"configured {path}")
    log(f"  set: {', '.join(applied) or 'nothing'}")


# --------------------------------------------------------------------------- #
# Example discovery
# --------------------------------------------------------------------------- #

def board_root(tree: Tree, board: str) -> Path:
    return tree.examples / "rtos" / board


def find_examples(tree: Tree, board: str) -> dict[str, Path]:
    """name -> example folder (the one containing freertos/)."""
    out: dict[str, Path] = {}
    root = board_root(tree, board)
    if not root.is_dir():
        return out
    for group in sorted(p for p in root.iterdir() if p.is_dir()):
        for example in sorted(p for p in group.iterdir() if p.is_dir()):
            if (example / "freertos").is_dir():
                out[example.name] = example
    return out


def list_boards(tree: Tree) -> list[str]:
    rtos = tree.examples / "rtos"
    return sorted(p.name for p in rtos.iterdir() if p.is_dir()) if rtos.is_dir() else []


def build_dir(example: Path, toolchain: str) -> Path:
    d = example / "freertos" / toolchain
    if not d.is_dir():
        have = sorted(p.name for p in (example / "freertos").iterdir() if p.is_dir())
        raise Fail(f"{example.name}: no '{toolchain}' build dir (have: {', '.join(have)})")
    return d


def make_cmd(tools: dict[str, str], jobs: int, target: str | None = None) -> list[str]:
    make = tools.get("MAKE")
    if not make:
        hint = (
            "install Code Composer Studio (ships <ccs>/ccs/utils/bin/gmake.exe, best match "
            "for the TI makefiles) or run:  winget install ezwinports.make"
            if IS_WINDOWS else "run:  sudo apt install make"
        )
        raise Fail(f"no make/gmake found - {hint}")
    cmd = [make]
    if jobs and jobs > 1:
        cmd.append(f"-j{jobs}")
    if target:
        cmd.append(target)
    return cmd


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def cmd_doctor(args) -> None:
    ws = workspace_of(args)
    tools = resolve_tools(args)

    print(f"\nhost        : {HOST} ({platform.platform()})")
    print(f"python      : {sys.version.split()[0]}")
    print(f"workspace   : {ws}  {'(exists)' if ws.is_dir() else '(not created)'}")
    if HOST == "wsl" and str(ws).startswith("/mnt/"):
        print("  WARNING   : workspace is on a Windows drive; WSL2 builds will be very slow.")

    print("\ntoolchain:")
    required = ["GIT", "MAKE", "CMAKE", "SYSCONFIG_TOOL"]
    optional = ["TICLANG_ARMCOMPILER", "GCC_ARMCOMPILER", "SIMPLELINK_WIFI_TOOLBOX_INSTALL_DIR"]
    for key in required + optional:
        value = tools.get(key)
        note = ""
        if value and " " in value:
            note = ("  (spaces -> 8.3 short path)" if " " not in mak_path(value)
                    else "  WARNING: spaces in path, TI makefiles may fail")
        print(f"  {key:<36} {value or '-- NOT FOUND --'}{note}")

    missing = [k for k in required if k not in tools]
    if not tools.get("TICLANG_ARMCOMPILER") and not tools.get("GCC_ARMCOMPILER"):
        missing.append("TICLANG_ARMCOMPILER or GCC_ARMCOMPILER")

    print("\nSDK trees:")
    trees = discover_trees(ws)
    if not trees:
        print("  none found -- install the TI SDK or run 'clone'")
    for name, tree in trees.items():
        print(f"  {name:<20} {tree.sdk}")
        print(f"  {'':<20} boards: {', '.join(list_boards(tree)) or 'no examples'}")

    if missing:
        print("\nmissing: " + ", ".join(missing))
        print("See README.md section 2 for download links, or pass explicit paths:")
        print("  python ti_w5_build.py configure --gcc_armcompiler <dir>")
    else:
        print("\nall required tools found.")
    print()


def cmd_clone(args) -> None:
    ws = workspace_of(args)
    ws.mkdir(parents=True, exist_ok=True)
    if HOST == "wsl" and str(ws).startswith("/mnt/"):
        log("WARNING: cloning onto a Windows drive from WSL2 - expect very slow builds.")

    for repo, url in REPOS.items():
        if args.repo not in ("both", repo):
            continue
        dest = ws / repo
        if (dest / ".git").exists():
            log(f"{repo}: already cloned, syncing submodules")
            if args.update:
                run(["git", "-C", str(dest), "pull", "--ff-only"], check=False)
            run(["git", "-C", str(dest), "submodule", "update", "--init", "--recursive"])
        else:
            run(["git", "clone", "--recurse-submodules", url, str(dest)])

    save_config(workspace=str(ws))


def cmd_configure(args) -> None:
    tree = active_tree(args)
    tools = resolve_tools(args)

    missing = [k for k in ("SYSCONFIG_TOOL", "CMAKE") if k not in tools]
    if not tools.get("TICLANG_ARMCOMPILER") and not tools.get("GCC_ARMCOMPILER"):
        missing.append("TICLANG_ARMCOMPILER or GCC_ARMCOMPILER")
    if missing:
        raise Fail("cannot configure, missing: " + ", ".join(missing) + " (run 'doctor')")

    log(f"using SDK: {tree}")
    for mak in tree.imports_mak():
        patch_imports_mak(mak, tools)

    save_config(workspace=str(workspace_of(args)), source=tree.name, tools=tools)


def cmd_build_sdk(args) -> None:
    tree = active_tree(args)
    tools = resolve_tools(args)
    # The SDK makefile is .NOTPARALLEL and lets cmake handle parallelism itself.
    target = None if args.toolchain == "all" else f"build-{args.toolchain}"
    log(f"building SDK libraries in {tree.sdk} ({args.toolchain}) - this takes a while")
    if args.clean:
        run(make_cmd(tools, 1, "clean"), cwd=tree.sdk, check=False)
    run(make_cmd(tools, 1, target), cwd=tree.sdk)


def cmd_list(args) -> None:
    tree = active_tree(args)
    print(f"\nSDK: {tree.sdk}")
    boards = list_boards(tree)
    print(f"boards: {', '.join(boards) or 'none'}\n")

    examples = find_examples(tree, args.board)
    if not examples:
        raise Fail(f"no examples for board {args.board} (available: {', '.join(boards)})")

    groups: dict[str, list[str]] = {}
    for name, path in examples.items():
        groups.setdefault(path.parent.name, []).append(name)
    for group in sorted(groups):
        print(f"{args.board}/{group}")
        for name in sorted(groups[group]):
            chains = sorted(p.name for p in (examples[name] / "freertos").iterdir() if p.is_dir())
            print(f"  {name:<26} [{', '.join(chains)}]")
        print()


def cmd_build(args) -> None:
    tree = active_tree(args)
    tools = resolve_tools(args)
    examples = find_examples(tree, args.board)
    if not examples:
        raise Fail(f"no examples for board {args.board} under {tree.examples}")

    if args.all:
        targets = sorted(examples)
    else:
        targets = []
        for name in args.example:
            if name in examples:
                targets.append(name)
                continue
            close = [e for e in examples if name.lower() in e.lower()]
            hint = f" Did you mean: {', '.join(close)}?" if close else " Run 'list'."
            raise Fail(f"unknown example '{name}'.{hint}")

    built: list[str] = []
    failed: list[str] = []
    for name in targets:
        bdir = build_dir(examples[name], args.toolchain)
        try:
            if args.clean:
                run(make_cmd(tools, 1, "clean"), cwd=bdir, check=False)
            run(make_cmd(tools, args.jobs), cwd=bdir)
            built.append(name)
        except Fail as exc:
            if not args.keep_going:
                raise
            log(f"FAILED {name}: {exc}")
            failed.append(name)

    print()
    for name in built:
        bdir = build_dir(examples[name], args.toolchain)
        images = sorted(p for p in bdir.iterdir() if p.suffix in (".out", ".axf", ".bin", ".hex"))
        log(f"OK {name}")
        for image in images:
            log(f"   {image}")
    if failed:
        raise Fail("failed: " + ", ".join(failed))


def cmd_all(args) -> None:
    if args.clone:
        cmd_clone(args)
    cmd_configure(args)
    cmd_build_sdk(args)
    cmd_build(args)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ti_w5_build.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--workspace", help="where cloned repos live "
                                       "(default: ~/ti-w5 on WSL, ./workspace otherwise)")
    p.add_argument("--sdk", help="use this SDK root directly")
    p.add_argument("--source", choices=["installed", *REPOS], help="which SDK tree to use")
    for key in TOOL_KEYS:
        p.add_argument(f"--{key.lower()}", help=f"override {key} in imports.mak")
    p.add_argument("--make", dest="make", help="path to make/gmake")
    p.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 4, help="parallel make jobs")
    sub = p.add_subparsers(dest="command", required=True)

    def add(name, func, help_text):
        sp = sub.add_parser(name, help=help_text)
        sp.set_defaults(func=func)
        return sp

    def add_build_opts(sp):
        sp.add_argument("--board", default=DEFAULT_BOARD, help=f"default: {DEFAULT_BOARD}")
        sp.add_argument("--toolchain", choices=["ticlang", "gcc"], default="ticlang")
        sp.add_argument("--clean", action="store_true")
        sp.add_argument("--keep-going", action="store_true", help="continue past failures")

    add("doctor", cmd_doctor, "show host, toolchain and SDK status")

    sp = add("clone", cmd_clone, "clone TI example repos (SDK included as submodule)")
    sp.add_argument("--repo", choices=[*REPOS, "both"], default="both")
    sp.add_argument("--update", action="store_true", help="pull latest if already cloned")

    add("configure", cmd_configure, "write tool paths into imports.mak (backs up as .orig)")

    sp = add("build-sdk", cmd_build_sdk, "build SDK libraries (required before examples)")
    sp.add_argument("--toolchain", choices=["all", "ticlang", "gcc", "iar"], default="all",
                    help="build libraries for one toolchain only (much faster)")
    sp.add_argument("--clean", action="store_true")

    sp = add("list", cmd_list, "list available examples")
    sp.add_argument("--board", default=DEFAULT_BOARD, help=f"default: {DEFAULT_BOARD}")

    sp = add("build", cmd_build, "build one or more examples")
    sp.add_argument("example", nargs="*", help="example name(s), e.g. network_terminal")
    sp.add_argument("--all", action="store_true", help="build every example")
    add_build_opts(sp)

    sp = add("all", cmd_all, "configure + build-sdk + build (add --clone to fetch repos first)")
    sp.add_argument("--example", nargs="*", default=["network_terminal"])
    sp.add_argument("--all", action="store_true", help="build every example")
    sp.add_argument("--clone", action="store_true", help="clone the example repos first")
    sp.add_argument("--repo", choices=[*REPOS, "both"], default="both")
    sp.add_argument("--update", action="store_true")
    add_build_opts(sp)
    return p


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "build" and not args.example and not args.all:
        log("nothing to build: name an example or use --all (see 'list')")
        return 2
    try:
        args.func(args)
    except Fail as exc:
        log(f"ERROR: {exc}")
        return 1
    except KeyboardInterrupt:
        log("interrupted")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
