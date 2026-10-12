"""A fresh clone works: only the files git would hand a customer, no SDKs, venv or host config."""

import os
import re
import shutil
import subprocess
import sys

import pytest

from conftest import SDK_ROOT

REPO = SDK_ROOT.parent
# Set inside the copy, so the suite run there does not copy the repository again.
NESTED = "UBX_FRESH_CLONE"

def _git_works():
    if not shutil.which("git") or not (REPO / ".git").exists():
        return False
    # CI containers may refuse the checkout ("dubious ownership"); skip rather than error.
    return subprocess.run(["git", "-C", str(REPO), "ls-files", "--error-unmatch", "README.md"],
                          capture_output=True).returncode == 0


pytestmark = pytest.mark.skipif(
    bool(os.environ.get(NESTED)) or not _git_works(),
    reason="needs a working git checkout (and not already inside the fresh-clone copy)")


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True).stdout


def clean_env(tmp):
    env = {k: v for k, v in os.environ.items() if not k.startswith("UBX_")}
    env.update(UBX_SDKS_DIR=str(tmp / "no-sdks"), UBX_MATTER_ROOT=str(tmp / "no-matter"), **{NESTED: "1"})
    return env


@pytest.fixture(scope="module")
def clone(tmp_path_factory):
    """The working tree as it would be committed: tracked plus new, not ignored, files."""
    root = tmp_path_factory.mktemp("clone")
    for rel in filter(None, git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")):
        src = REPO / rel
        if src.is_file():
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    return (root / SDK_ROOT.name).resolve()


def run(clone, script, *args):
    proc = subprocess.run([sys.executable, str(clone / "scripts" / script), *args],
                          capture_output=True, text=True, cwd=clone, env=clean_env(clone.parent),
                          stdin=subprocess.DEVNULL, timeout=120)
    return proc.returncode, proc.stdout + proc.stderr


HOST_SPECIFIC = re.compile(
    r"(^|/)(\.venv|__pycache__|sdks|build)/|\.pyc$|/config/(build\.\w+|rf_config)\.json$"
    r"|(^|/)(coverage|report)\.xml$|\.ubx-orig$")


def test_nothing_host_specific_is_tracked():
    tracked = git("ls-files", "-z").split("\0")
    assert not [p for p in tracked if HOST_SPECIFIC.search(p)]


def test_shims_keep_their_mode_and_line_endings():
    for line in git("ls-files", "-s", "--", f"{SDK_ROOT.name}/ubx-*.sh").splitlines():
        assert line.startswith("100755"), line
    for shim in ("ubx-sdk.cmd", "ubx-matter.cmd"):
        assert git("check-attr", "eol", "--", f"{SDK_ROOT.name}/{shim}").strip().endswith("crlf")


def test_clone_has_no_sdk_or_host_state(clone):
    assert not (clone / "sdks").exists() and not (clone / ".venv").exists()
    assert not list((clone / "modules").glob("*/config"))


ALL_ACTIONS = ["--doctor", "--clone", "--install", "--build-sdk", "--list", "--clean", "--build",
               "--flash", "--log"]


@pytest.mark.parametrize("target", ["iris-w10", "nora-w30", "nora-w40", "nora-w50-w51",
                                    "nora-b20-b21-b22", "alma-b20-b21"])
def test_launcher_dry_run_in_the_clone(clone, target):
    rc, out = run(clone, "ubx_sdk.py", target, "--dry-run", "--no-wsl", *ALL_ACTIONS)
    assert rc == 0 and "Traceback" not in out, out
    lines = [line for line in out.splitlines() if line.startswith("[DRY-RUN] ")]
    assert lines and all(str(clone) in line for line in lines), out


@pytest.mark.parametrize("target", ["iris-w10", "nora-w30", "nora-w40", "nora-w50-w51",
                                    "nora-b20-b21-b22", "alma-b20-b21"])
def test_module_config_reports_in_the_clone(clone, target):
    for command in ("variants", "status", "examples"):
        rc, out = run(clone, "module_config.py", target, command)
        assert rc == 0 and "Traceback" not in out, out
    assert "Applied:" not in run(clone, "module_config.py", target, "status")[1]


def test_ubx_example_resolves_to_the_clone(clone):
    rc, out = run(clone, "ubx_sdk.py", "nora-w40", "--dry-run", "--variant", "NORA-W401",
                  "--rf-config", "--build", "ubx/rf-calibration")
    assert rc == 0, out
    assert str(clone.parent / "esp-idf" / "nora-w40") in out


@pytest.mark.parametrize("shim,banner", [("ubx-sdk", "Getting Started SDK launcher"),
                                         ("ubx-matter", "Matter launcher")])
def test_host_shim_runs_without_a_venv(clone, shim, banner):
    """What a customer types first: the shim must find a Python on its own."""
    if os.name == "nt":
        cmd = ["cmd", "/c", str(clone / f"{shim}.cmd")]
    elif shutil.which("bash"):
        cmd = ["bash", str(clone / f"{shim}.sh")]
    else:
        pytest.skip("no bash")
    env = clean_env(clone.parent)
    opts = dict(capture_output=True, text=True, cwd=clone, env=env, stdin=subprocess.DEVNULL, timeout=120)
    help_out = subprocess.run([*cmd, "--help"], **opts)
    assert help_out.returncode == 0 and banner in help_out.stdout, help_out.stdout + help_out.stderr
    proc = subprocess.run([*cmd, "nora-b20-b21-b22", "--dry-run", "--list"], **opts)
    assert proc.returncode == 0 and "[DRY-RUN]" in proc.stdout, proc.stdout + proc.stderr


@pytest.mark.parametrize("target", ["iris-w10", "nora-w30", "nora-w40", "nora-w50-w51",
                                    "nora-b20-b21-b22", "alma-b20-b21"])
def test_matter_dry_run_in_the_clone(clone, target):
    rc, out = run(clone, "ubx_matter.py", target, "--dry-run", "--no-wsl", "--doctor", "--list", "--build")
    assert rc == 0 and "Traceback" not in out, out


def test_suite_passes_in_the_clone(clone):
    """Profiles, assets, examples and doc links checked against committed files only."""
    proc = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
                          capture_output=True, text=True, cwd=clone, env=clean_env(clone.parent),
                          stdin=subprocess.DEVNULL, timeout=600)
    assert proc.returncode == 0, proc.stdout[-4000:] + proc.stderr[-2000:]
