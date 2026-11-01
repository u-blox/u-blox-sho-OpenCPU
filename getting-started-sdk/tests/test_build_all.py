import sys

import pytest

import build_all
import ubx


@pytest.fixture
def fake_run(monkeypatch):
    """Replaces run_step; returns queued exit codes per target, then 0."""
    seen = []
    codes: dict[str, list[int]] = {}

    def run(cmd, log_path):
        seen.append(cmd)
        target = next(a for a in cmd if a in ubx.TARGETS)
        queue = codes.get(target, [])
        return queue.pop(0) if queue else 0

    monkeypatch.setattr(build_all, "run_step", run)
    run.seen, run.codes = seen, codes
    return run


@pytest.mark.parametrize("plan", [build_all.SDK_PLAN, build_all.MATTER_PLAN])
def test_plan_covers_every_target(plan):
    assert list(plan) == list(ubx.TARGETS)
    assert all(plan.values())


def test_nora_w30_builds_km0_before_km4():
    assert build_all.SDK_PLAN["nora-w30"] == ["project_lp", "project_hp"]


def test_matter_plan_uses_the_vendor_defaults():
    assert build_all.MATTER_PLAN["nora-w40"] == ["light"]
    assert build_all.MATTER_PLAN["nora-b20-b21-b22"] == ["light_bulb"]


@pytest.mark.parametrize("windows,matter,prefix,shim", [
    (True, False, ["cmd", "/c"], "ubx-sdk.cmd"),
    (False, False, ["bash"], "ubx-sdk.sh"),
    (True, True, ["cmd", "/c"], "ubx-matter.cmd"),
    (False, True, ["bash"], "ubx-matter.sh"),
])
def test_shim_follows_the_host(monkeypatch, windows, matter, prefix, shim):
    monkeypatch.setattr(build_all, "host_is_windows", lambda: windows)
    cmd = build_all.shim_command(["nora-w40", "--build"], matter)
    assert cmd == [*prefix, str(build_all.SDK_ROOT / shim), "nora-w40", "--build"]


def test_clean_is_the_default():
    steps = build_all.plan_steps(["nora-w40"], clean=True, setup=False, dry_run=False)
    assert [s.argv for s in steps] == [["nora-w40", "--clean", "--build", "hello_world"]]
    steps = build_all.plan_steps(["nora-w40"], clean=False, setup=False, dry_run=True)
    assert [s.argv for s in steps] == [["nora-w40", "--build", "hello_world", "--dry-run"]]


def test_setup_only_on_the_first_step_and_build_sdk_only_where_supported():
    steps = build_all.plan_steps(["nora-w30", "nora-w50-w51"], clean=False, setup=True, dry_run=False)
    assert [s.argv for s in steps] == [
        ["nora-w30", "--clone", "--install", "--build", "project_lp"],
        ["nora-w30", "--build", "project_hp"],
        ["nora-w50-w51", "--clone", "--install", "--build-sdk", "--build", "network_terminal"],
    ]
    matter = build_all.plan_steps(["nora-w50-w51"], clean=True, setup=True, dry_run=False, matter=True)
    assert matter[0].argv == ["nora-w50-w51", "--clone", "--install", "--clean", "--build", "lighting-app"]


def test_targets_accept_aliases_and_reject_uconnectxpress(capsys):
    assert build_all.resolve_targets([]) == list(ubx.TARGETS)
    assert build_all.resolve_targets(["w40", "nora_w40", "iris"]) == ["nora-w40", "iris-w10"]
    assert build_all.resolve_targets(["nora-w36"]) == 1
    assert "u-connectXpress" in capsys.readouterr().out


def test_all_ok(fake_run, tmp_path, capsys):
    assert build_all.main(["--log-dir", str(tmp_path)]) == 0
    assert len(fake_run.seen) == sum(len(v) for v in build_all.SDK_PLAN.values())
    assert "[FAIL]" not in capsys.readouterr().out


def test_failure_skips_the_rest_of_that_target_only(fake_run, tmp_path, capsys):
    fake_run.codes["nora-w30"] = [2]
    assert build_all.main(["nora-w30", "nora-w40", "--log-dir", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "| nora-w30 | `project_lp` | [FAIL] |" in out
    assert "| nora-w30 | `project_hp` | [SKIP] | - |" in out
    assert "| nora-w40 | `hello_world` | [OK] |" in out
    assert str(tmp_path / "nora-w30-project_lp.log") in out


def test_stop_on_fail(fake_run, tmp_path, capsys):
    fake_run.codes["iris-w10"] = [1]
    assert build_all.main(["iris-w10", "nora-w40", "--stop-on-fail", "--log-dir", str(tmp_path)]) == 1
    assert "| nora-w40 | `hello_world` | [SKIP] |" in capsys.readouterr().out
    assert len(fake_run.seen) == 1


def test_ctrl_c_stops_the_batch(fake_run, tmp_path):
    fake_run.codes["iris-w10"] = [130]
    assert build_all.main(["iris-w10", "nora-w40", "--log-dir", str(tmp_path)]) == 130
    assert len(fake_run.seen) == 1


def test_matter_runs_the_matter_shim(fake_run, tmp_path, monkeypatch):
    monkeypatch.setattr(build_all, "host_is_windows", lambda: False)
    assert build_all.main(["nora-b20-b21-b22", "--log-dir", str(tmp_path)], matter=True) == 0
    assert fake_run.seen[0][1].endswith("ubx-matter.sh")
    assert fake_run.seen[0][2:] == ["nora-b20-b21-b22", "--clean", "--build", "light_bulb"]


def test_run_step_tees_output_and_returns_the_exit_code(tmp_path, capfd):
    log = tmp_path / "step.log"
    code = "import sys; print('hello from step'); sys.exit(3)"
    assert build_all.run_step([sys.executable, "-c", code], log) == 3
    assert "hello from step" in capfd.readouterr().out
    assert "hello from step" in log.read_text()


@pytest.mark.parametrize("seconds,text", [(5, "5s"), (125, "2m 05s"), (3725, "1h 02m")])
def test_duration(seconds, text):
    assert build_all.duration(seconds) == text


@pytest.mark.parametrize("script,matter", [("build_all_sdk.py", False), ("build_all_matter.py", True)])
def test_entry_points_call_build_all(monkeypatch, script, matter):
    import runpy
    from conftest import SDK_ROOT
    seen = []
    monkeypatch.setattr(build_all, "main", lambda matter=False: seen.append(matter) or 0)
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(SDK_ROOT / "scripts" / script), run_name="__main__")
    assert exc.value.code == 0 and seen == [matter]
