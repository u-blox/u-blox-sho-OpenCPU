"""End-to-end: the real entry points in a subprocess, with --dry-run so nothing is executed."""

import os
import shutil
import subprocess
import sys

import pytest

from conftest import SDK_ROOT

SCRIPTS = SDK_ROOT / "scripts"
WINDOWS = sys.platform == "win32"


def run(script, *args, env=None):
    proc = subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                          capture_output=True, text=True, cwd=SDK_ROOT,
                          env={**os.environ, **(env or {})}, stdin=subprocess.DEVNULL, timeout=120)
    return proc.returncode, proc.stdout + proc.stderr


def dry_lines(out):
    return [line[len("[DRY-RUN] "):] for line in out.splitlines() if line.startswith("[DRY-RUN] ")]


def test_sdk_help():
    rc, out = run("ubx_sdk.py", "--help")
    assert rc == 0
    assert "--dry-run" in out


def test_matter_help():
    rc, out = run("ubx_matter.py", "--help")
    assert rc == 0
    assert "ubx-matter <target>" in out


def test_unknown_target_exit_code():
    rc, out = run("ubx_sdk.py", "nora-w36", "--list")
    assert rc == 1
    assert "u-connectXpress" in out


def test_dry_run_prints_commands_in_order():
    rc, out = run("ubx_sdk.py", "nora-w40", "--dry-run", "--build", "--doctor", "--list")
    assert rc == 0
    lines = dry_lines(out)
    assert len(lines) == 5
    assert "nora_w40_build.py doctor" in lines[0]
    assert "module_config.py nora-w40 status" in lines[1]
    assert "nora_w40_build.py list" in lines[2]
    assert "module_config.py nora-w40 examples" in lines[3]
    assert "nora_w40_build.py build hello_world" in lines[4]


def test_dry_run_rf_config():
    rc, out = run("ubx_sdk.py", "nora-w30", "--dry-run", "--no-wsl",
                  "--variant", "NORA-W301", "--region", "ETSI", "--rf-config")
    assert rc == 0
    assert dry_lines(out) and dry_lines(out)[0].endswith(
        "module_config.py nora-w30 apply --variant NORA-W301 --region ETSI")


def test_dry_run_matter_vendor():
    rc, out = run("ubx_matter.py", "nora-w50-w51", "--dry-run", "--list", env={"UBX_WSL_DISTRO": ""})
    assert rc == 0
    (line,) = dry_lines(out)
    if WINDOWS:
        assert line.startswith("wsl -d Ubuntu-22.04 -- bash -lc")
        assert "./ubx-matter.sh nora-w50-w51 --dry-run --list" in line
    else:
        assert line.endswith("matter_build.py nora-w50-w51 list")


def test_dry_run_matter_ncs():
    rc, out = run("ubx_matter.py", "nora-b20-b21-b22", "--dry-run", "--build", "--flash")
    assert rc == 0
    lines = dry_lines(out)
    assert lines[0].endswith("nordic_ncs_build.py nora-b20-b21-b22 build matter/light_bulb")
    assert lines[1].endswith("nordic_ncs_build.py nora-b20-b21-b22 flash matter/light_bulb")


def test_matter_driver_lists_fake_sdk(tmp_path):
    (tmp_path / "nora-w50-w51/ti-matter/examples/lighting-app/ti/cc35xx").mkdir(parents=True)
    rc, out = run("matter_build.py", "nora-w50-w51", "list", env={"UBX_MATTER_ROOT": str(tmp_path)})
    assert rc == 0
    assert "lighting-app  (default)" in out


def test_module_config_variants():
    rc, out = run("module_config.py", "nora-w30", "variants")
    assert rc == 0
    assert "NORA-W301" in out


def _driver_cases():
    import ubx
    cases, seen = [], set()
    for target in ubx.TARGETS.values():
        if target.script not in seen:
            seen.add(target.script)
            cases.append(pytest.param(target, id=target.script))
    return cases


@pytest.mark.parametrize("target", _driver_cases())
def test_driver_offers_every_launcher_action(target):
    rc, out = run(target.script, "--help")
    assert rc == 0, out
    # NORA-W50-W51 has no clean subcommand; the launcher maps --clean onto a clean build.
    wanted = set(target.supports) - {"clean"} if target.key == "nora-w50-w51" else set(target.supports)
    for action in wanted:
        assert action in out, f"{target.script} has no '{action}' subcommand"


@pytest.mark.parametrize("target", _driver_cases())
def test_driver_doctor_does_not_crash(target):
    # Tools may be missing on this host; doctor must report that, not raise.
    rc, out = run(target.script, *target.driver_args, "doctor")
    assert "Traceback" not in out, out
    assert rc in (0, 1)


@pytest.mark.skipif(not WINDOWS, reason="cmd shim")
def test_cmd_shim():
    proc = subprocess.run(["cmd", "/c", str(SDK_ROOT / "ubx-sdk.cmd"), "nora-w40", "--dry-run", "--list"],
                          capture_output=True, text=True, cwd=SDK_ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "nora_w40_build.py list" in proc.stdout


@pytest.mark.skipif(WINDOWS or not shutil.which("bash"), reason="bash shim")
def test_sh_shim():
    proc = subprocess.run(["bash", str(SDK_ROOT / "ubx-sdk.sh"), "nora-w40", "--dry-run", "--list"],
                          capture_output=True, text=True, cwd=SDK_ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "nora_w40_build.py list" in proc.stdout


@pytest.mark.skipif(WINDOWS or not shutil.which("bash"), reason="needs bash")
@pytest.mark.parametrize("script", sorted((SCRIPTS / "matter_vendor").glob("*.sh")), ids=lambda p: p.name)
def test_vendor_scripts_parse(script):
    assert subprocess.run(["bash", "-n", str(script)]).returncode == 0
