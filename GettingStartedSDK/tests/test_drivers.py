"""Per-target driver internals that can be checked without an SDK or toolchain."""

import subprocess

import pytest

import iris_w1_build
import nora_w3_build
import nora_w4_build
import nordic_ncs_build as ncs

B2 = ncs.TARGETS["nora-b2"]
ALMA = ncs.TARGETS["alma-b2"]


def test_armgcc_dir_prefers_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("ARMGCC_DIR", str(tmp_path))
    assert iris_w1_build.armgcc_dir() == (str(tmp_path), "ARMGCC_DIR")


def test_armgcc_dir_derived_from_detected_gcc(monkeypatch, tmp_path):
    gcc = tmp_path / "toolchain" / "bin" / "arm-none-eabi-gcc"
    monkeypatch.delenv("ARMGCC_DIR", raising=False)
    monkeypatch.setattr(iris_w1_build, "detect_arm_gcc", lambda: str(gcc))
    assert iris_w1_build.armgcc_dir() == (str(tmp_path / "toolchain"), "auto-detected")


def test_armgcc_dir_missing(monkeypatch):
    monkeypatch.delenv("ARMGCC_DIR", raising=False)
    monkeypatch.setattr(iris_w1_build, "detect_arm_gcc", lambda: None)
    assert iris_w1_build.armgcc_dir() == (None, "not found")


def test_newest_expands_absolute_globs(tmp_path):
    for version in ("12.3", "14.2"):
        exe = tmp_path / f"Arm GNU Toolchain {version}" / "bin" / "gcc"
        exe.parent.mkdir(parents=True)
        exe.write_text("")
    found = iris_w1_build.newest([str(tmp_path / "Arm GNU Toolchain*" / "bin" / "gcc")])
    assert "14.2" in found


@pytest.mark.parametrize("module", [nora_w3_build, nora_w4_build], ids=["nora_w3", "nora_w4"])
def test_git_detection_does_not_shell_out(module, monkeypatch):
    # There is no 'which' binary in cmd.exe or PowerShell.
    monkeypatch.setattr(module, "host_kind", lambda: "linux")
    monkeypatch.setattr(module.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(module.subprocess, "run",
                        lambda *a, **k: pytest.fail(f"unexpected subprocess: {a}"))
    assert module.detect_git() == "/usr/bin/git"


def make_board(ws, rel):
    (ws / rel).mkdir(parents=True)


def test_board_available_in_zephyr(tmp_path):
    make_board(tmp_path, "zephyr/boards/u-blox/ubx_evknorab2")
    assert ncs.board_available(str(tmp_path), B2.board)


def test_board_available_in_nrf(tmp_path):
    make_board(tmp_path, "nrf/boards/nordic/nrf54lm20dk")
    assert ncs.board_available(str(tmp_path), ALMA.board)


def test_board_missing_in_old_workspace(tmp_path):
    make_board(tmp_path, "zephyr/boards/u-blox/ubx_evkninab3")
    assert not ncs.board_available(str(tmp_path), B2.board)


def test_workspace_revision(monkeypatch):
    monkeypatch.setattr(ncs.subprocess, "run",
                        lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, "v2.9.0\n", ""))
    assert ncs.workspace_revision("ws") == "v2.9.0"
    monkeypatch.setattr(ncs.subprocess, "run",
                        lambda cmd, **kw: subprocess.CompletedProcess(cmd, 128, "", "fatal"))
    assert ncs.workspace_revision("ws") is None


def test_build_refuses_missing_board(tmp_path, monkeypatch, calls, capsys):
    ws = tmp_path / "ncs"
    sample = ws / "zephyr/samples/hello_world"
    sample.mkdir(parents=True)
    (sample / "CMakeLists.txt").write_text("")
    (sample / "prj.conf").write_text("")
    monkeypatch.setattr(ncs, "detect_workspace", lambda t: str(ws))
    monkeypatch.setattr(ncs, "detect_west", lambda: ["west"])
    monkeypatch.setattr(ncs, "workspace_revision", lambda w: "v2.9.0")
    monkeypatch.setattr(ncs.subprocess, "call", calls)
    args = ncs.build_parser().parse_args(["nora-b2", "build", "hello_world"])
    assert ncs.cmd_build(B2, args) == 1
    assert not calls.calls
    out = capsys.readouterr().out
    assert "ubx_evknorab2" in out and "v2.9.0" in out and ncs.NCS_REVISION in out


def test_variants_share_the_default_board_family():
    for target in ncs.TARGETS.values():
        assert target.board in target.variants
        family = target.board.split("/")[0]
        assert all(v.split("/")[0] == family for v in target.variants)
