#!/usr/bin/env python3
"""
Shared core of the batch build check: build every target, one after the
other, through the real launcher shim.

Developer check, not a user tool. Two thin entry points sit on top of it:

    scripts/build_all_sdk.py      -> ubx-sdk.cmd / ubx-sdk.sh
    scripts/build_all_matter.py   -> ubx-matter.cmd / ubx-matter.sh

The .cmd shim runs on Windows, the .sh shim elsewhere, the same way a user
would call them. Each step's output is echoed and saved to a log file and a
summary table closes the run. A failing target does not stop the rest unless
--stop-on-fail is given.

Clean is the default: a stale CMake cache or an old SDK path then fails here
instead of being hidden by a previous build. --incremental skips it.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matter_build  # noqa: E402
import ubx  # noqa: E402

SDK_ROOT = ubx.SDK_ROOT

# Examples built per target, in order. NORA-W30 links the KM0 image into KM4.
SDK_PLAN: dict[str, list[str]] = {key: [t.default_example] for key, t in ubx.TARGETS.items()}
SDK_PLAN["nora-w30"] = ["project_lp", "project_hp"]

# The Nordic targets take Matter from NCS; the launcher scopes the name to matter/.
MATTER_PLAN: dict[str, list[str]] = {
    key: [matter_build.TARGETS[key].default_example] if key in matter_build.TARGETS
    else [ubx.matter_sample(None).split("/", 1)[1]]
    for key in ubx.TARGETS
}


@dataclass
class Step:
    target: str
    example: str
    argv: list[str]
    result: str = "pending"
    seconds: float = 0.0
    log: Path | None = None


def host_is_windows() -> bool:
    return os.name == "nt"


def shim_name(matter: bool) -> str:
    base = "ubx-matter" if matter else "ubx-sdk"
    return f"{base}.cmd" if host_is_windows() else f"{base}.sh"


def shim_command(argv: list[str], matter: bool = False) -> list[str]:
    shim = str(SDK_ROOT / shim_name(matter))
    if host_is_windows():
        return ["cmd", "/c", shim, *argv]
    return ["bash", shim, *argv]


def plan_steps(targets: list[str], clean: bool, setup: bool, dry_run: bool,
               matter: bool = False) -> list[Step]:
    plan = MATTER_PLAN if matter else SDK_PLAN
    steps = []
    for key in targets:
        target = ubx.TARGETS[key]
        for n, example in enumerate(plan[key]):
            argv = [key]
            if setup and n == 0:
                argv += ["--clone", "--install"]
                if not matter and "build-sdk" in target.supports:
                    argv.append("--build-sdk")
            if clean:
                argv.append("--clean")
            argv += ["--build", example]
            if dry_run:
                argv.append("--dry-run")
            steps.append(Step(key, example, argv))
    return steps


def run_step(cmd: list[str], log_path: Path) -> int:
    """Run one launcher call, echoing its output and saving it to log_path."""
    env = dict(os.environ, PYTHONUNBUFFERED="1")
    with open(log_path, "wb") as log:
        log.write(f"$ {subprocess.list2cmdline(cmd)}\n\n".encode())
        proc = subprocess.Popen(cmd, cwd=str(SDK_ROOT), env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            # Chunks rather than lines, so progress bars and prompts show up.
            for chunk in iter(lambda: proc.stdout.read1(65536), b""):
                sys.stdout.buffer.write(chunk)
                sys.stdout.flush()
                log.write(chunk)
            return proc.wait()
        except KeyboardInterrupt:
            # The child got the same Ctrl+C; let it stop on its own.
            try:
                proc.communicate(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
            return 130


def duration(seconds: float) -> str:
    s = int(seconds)
    if s >= 3600:
        return f"{s // 3600}h {s % 3600 // 60:02d}m"
    if s >= 60:
        return f"{s // 60}m {s % 60:02d}s"
    return f"{s}s"


def summary(steps: list[Step], header: str, log_dir: Path) -> str:
    marks = {"ok": "[OK]", "fail": "[FAIL]", "skipped": "[SKIP]", "pending": "-"}
    lines = [f"\n=== {header} ===\n",
             "| Target | Example | Result | Time |",
             "|--------|---------|--------|------|"]
    for s in steps:
        time_text = duration(s.seconds) if s.result in ("ok", "fail") else "-"
        lines.append(f"| {s.target} | `{s.example}` | {marks[s.result]} | {time_text} |")
    lines.append("")
    for s in steps:
        if s.result == "fail" and s.log:
            lines.append(f"[FAIL] {s.target} {s.example}: {s.log}")
    lines.append(f"[INFO] Logs: {log_dir}")
    return "\n".join(lines)


def resolve_targets(names: list[str]) -> list[str] | int:
    if not names:
        return list(ubx.TARGETS)
    keys: list[str] = []
    for name in names:
        target = ubx.resolve_target(name)
        if target is None:
            return ubx.fail_unknown_target(name)
        if target.key not in keys:
            keys.append(target.key)
    return keys


def needs_linux(key: str, matter: bool) -> bool:
    if matter:
        return key in matter_build.TARGETS and matter_build.TARGETS[key].linux_only
    return ubx.TARGETS[key].linux_only


def main(argv: list[str] | None = None, matter: bool = False) -> int:
    layer = "matter" if matter else "sdk"
    parser = argparse.ArgumentParser(
        prog=f"build_all_{layer}.py",
        description=f"Build every target through the {shim_name(matter).split('.')[0]} launcher.")
    parser.add_argument("targets", nargs="*", help="targets to build (default: all)")
    parser.add_argument("--incremental", action="store_true",
                        help="skip --clean; reuses the previous build output")
    parser.add_argument("--setup", action="store_true",
                        help="add --clone --install" + ("" if matter else " (and --build-sdk)")
                        + " before the first build")
    parser.add_argument("--stop-on-fail", action="store_true",
                        help="stop at the first failing target")
    parser.add_argument("--dry-run", action="store_true",
                        help="pass --dry-run to the launcher")
    parser.add_argument("--log-dir", type=Path,
                        help="where to put the per-step logs (default: a temp folder)")
    args = parser.parse_args(argv)

    targets = resolve_targets(args.targets)
    if isinstance(targets, int):
        return targets

    stamp = time.strftime("%Y%m%d-%H%M%S")
    log_dir = args.log_dir or Path(tempfile.gettempdir()) / "ubx-build-all" / f"{layer}-{stamp}"
    log_dir.mkdir(parents=True, exist_ok=True)

    clean = not args.incremental
    steps = plan_steps(targets, clean, args.setup, args.dry_run, matter)
    header = f"{'clean' if clean else 'incremental'} build via {shim_name(matter)}"
    print(f"[INFO] {header}: {', '.join(targets)}")
    print(f"[INFO] Logs: {log_dir}")

    started = time.monotonic()
    failed_targets: set[str] = set()
    stopped = interrupted = False
    for step in steps:
        if stopped or step.target in failed_targets:
            step.result = "skipped"
            continue
        if needs_linux(step.target, matter) and sys.platform == "darwin":
            print(f"[INFO] {step.target} builds on Linux only; skipping on macOS.")
            step.result = "skipped"
            continue
        step.log = log_dir / f"{step.target}-{step.example.replace('/', '_')}.log"
        print(f"\n##### {step.target} :: {step.example} #####", flush=True)
        t0 = time.monotonic()
        rc = run_step(shim_command(step.argv, matter), step.log)
        step.seconds = time.monotonic() - t0
        step.result = "ok" if rc == 0 else "fail"
        if rc == 130:
            print("\n[INFO] Stopped (Ctrl+C).")
            stopped = interrupted = True
        elif rc != 0:
            failed_targets.add(step.target)
            stopped = args.stop_on_fail

    header += f", {duration(time.monotonic() - started)}"
    print(summary(steps, header, log_dir))
    if interrupted:
        return 130
    return 1 if any(s.result == "fail" for s in steps) else 0
