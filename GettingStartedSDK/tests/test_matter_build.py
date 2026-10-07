"""Matter driver (scripts/matter_build.py): vendor example discovery, list, doctor, build."""

import argparse

import pytest

import matter_build as mb

W4 = mb.TARGETS["nora-w4"]
W5 = mb.TARGETS["nora-w5"]
IRIS = mb.TARGETS["iris-w1"]


def make(root, *dirs, files=()):
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)
    for f in files:
        (root / f).parent.mkdir(parents=True, exist_ok=True)
        (root / f).write_text("")


@pytest.fixture
def sdk(tmp_path, monkeypatch, calls):
    """A fake UBX_MATTER_ROOT with just enough of each vendor tree to be discovered."""
    monkeypatch.setenv("UBX_MATTER_ROOT", str(tmp_path))
    monkeypatch.setattr(mb.subprocess, "call", calls)
    make(tmp_path / "NORA-W5" / "ti-matter",
         ".git",
         "examples/lighting-app/ti/cc35xx",
         "examples/platform/ti/cc35xx",
         "examples/lock-app/ti/cc13x4_26x4")
    make(tmp_path / "NORA-W4",
         "esp-idf/.git", "esp-matter/.git",
         "esp-matter/examples/common",
         "esp-matter/examples/docs_only",
         files=["esp-matter/examples/light/CMakeLists.txt",
                "esp-matter/examples/door_lock/CMakeLists.txt"])
    make(tmp_path / "IRIS-W1" / "connectedhomeip",
         ".git", "examples/lighting-app/nxp/rt/rw61x", "examples/thermostat/nxp/rt/rw61x")
    return tmp_path


def ns(**kw):
    return argparse.Namespace(**kw)


# ---------------------------------------------------------------------------
# Table sanity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("target", mb.TARGETS.values(), ids=list(mb.TARGETS))
def test_target_definition(target):
    assert target.examples.split("/").count("*") == 1
    assert target.default_example
    assert target.repos
    if target.vendor_script:
        assert (mb.VENDOR_SCRIPTS / target.vendor_script).is_file()


def test_vendor_scripts_use_lf():
    for script in mb.VENDOR_SCRIPTS.glob("*.sh"):
        assert b"\r\n" not in script.read_bytes(), script.name


# ---------------------------------------------------------------------------
# matter_root
# ---------------------------------------------------------------------------

def test_matter_root_override(monkeypatch, tmp_path):
    monkeypatch.setenv("UBX_MATTER_ROOT", str(tmp_path))
    assert mb.matter_root(W5) == tmp_path / "NORA-W5"


def test_matter_root_defaults_to_home_in_wsl(monkeypatch, tmp_path):
    monkeypatch.delenv("UBX_MATTER_ROOT", raising=False)
    monkeypatch.setattr(mb, "host_kind", lambda: "wsl")
    monkeypatch.setattr(mb.target_paths, "sdk_dir", lambda slug: tmp_path / slug)
    assert mb.matter_root(W5) == mb.Path.home() / "ubx-matter" / "NORA-W5"


def test_matter_root_keeps_existing_in_tree_clone(monkeypatch, tmp_path):
    monkeypatch.delenv("UBX_MATTER_ROOT", raising=False)
    monkeypatch.setattr(mb, "host_kind", lambda: "wsl")
    monkeypatch.setattr(mb.target_paths, "sdk_dir", lambda slug: tmp_path / slug)
    make(tmp_path / "nora_w5" / "matter" / "ti-matter", ".git")
    assert mb.matter_root(W5) == tmp_path / "nora_w5" / "matter"


def test_matter_root_in_tree_on_windows(monkeypatch, tmp_path):
    monkeypatch.delenv("UBX_MATTER_ROOT", raising=False)
    monkeypatch.setattr(mb, "host_kind", lambda: "windows")
    monkeypatch.setattr(mb.target_paths, "sdk_dir", lambda slug: tmp_path / slug)
    assert mb.matter_root(W4) == tmp_path / "nora_w4" / "matter"


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def test_ti_examples_skip_platform_and_other_socs(sdk):
    assert list(mb.list_vendor_examples(W5)) == ["lighting-app"]


def test_esp_examples_need_cmakelists(sdk):
    assert list(mb.list_vendor_examples(W4)) == ["door_lock", "light"]


def test_nxp_examples(sdk):
    assert list(mb.list_vendor_examples(IRIS)) == ["lighting-app", "thermostat"]


def test_no_sdk_no_examples(sdk):
    assert mb.list_vendor_examples(mb.TARGETS["nora-w3"]) == {}


# ---------------------------------------------------------------------------
# list / doctor
# ---------------------------------------------------------------------------

def test_list_marks_default(sdk, capsys):
    assert mb.cmd_list(W4, ns()) == 0
    out = capsys.readouterr().out
    assert "  light  (default)" in out
    assert "door_lock" in out
    assert "common" not in out


def test_list_without_sdk(sdk, capsys):
    assert mb.cmd_list(mb.TARGETS["nora-w3"], ns()) == 0
    out = capsys.readouterr().out
    assert "[WARNING]" in out and "--clone" in out


def test_list_says_when_build_is_not_wired(sdk, capsys):
    mb.cmd_list(IRIS, ns())
    assert "listed only" in capsys.readouterr().out


def test_doctor_reports_repos_and_examples(sdk, monkeypatch, capsys):
    monkeypatch.setattr(mb.shutil, "which", lambda tool: f"/usr/bin/{tool}")
    assert mb.cmd_doctor(W5, ns()) == 0
    out = capsys.readouterr().out
    assert "[OK] ti-matter" in out
    assert "[OK] 1 vendor example(s): lighting-app" in out
    assert "[FAIL]" not in out


def test_doctor_flags_missing_tools_and_clone(sdk, monkeypatch, capsys):
    monkeypatch.setattr(mb.shutil, "which", lambda tool: None)
    assert mb.cmd_doctor(mb.TARGETS["nora-w3"], ns()) == 0
    out = capsys.readouterr().out
    assert "[FAIL] git" in out
    assert "[FAIL] ameba-rtos-d" in out
    assert "No vendor examples" in out


# ---------------------------------------------------------------------------
# build / clean / install
# ---------------------------------------------------------------------------

def test_build_default_example(sdk, calls):
    assert mb.cmd_build(W5, ns(app=None, extra=[])) == 0
    call = calls.calls[0]
    assert call["cmd"][0] == "bash"
    assert call["cmd"][1].endswith("nora_w5.sh")
    assert call["cmd"][2:] == ["build", str(sdk / "NORA-W5/ti-matter/examples/lighting-app/ti/cc35xx")]
    assert call["env"]["UBX_MATTER_SDK_ROOT"] == str(sdk / "NORA-W5")
    assert call["cwd"] == str(sdk / "NORA-W5")


def test_build_forwards_extra(sdk, calls):
    mb.cmd_build(W4, ns(app="door_lock", extra=["-DFOO=1"]))
    assert calls.cmds[0][2:] == ["build", str(sdk / "NORA-W4/esp-matter/examples/door_lock"), "-DFOO=1"]


def test_build_empty_name_means_default(sdk, calls):
    mb.cmd_build(W4, ns(app="", extra=["-v"]))
    assert calls.cmds[0][3].endswith("light")


def test_build_returns_vendor_exit_code(sdk, calls):
    calls.returns = [2]
    assert mb.cmd_build(W5, ns(app=None, extra=[])) == 2


def test_build_unknown_example(sdk, calls, capsys):
    assert mb.cmd_build(W5, ns(app="thermometer", extra=[])) == 1
    assert not calls.calls
    assert "not found" in capsys.readouterr().out


def test_build_not_wired(sdk, calls, capsys):
    assert mb.cmd_build(IRIS, ns(app=None, extra=[])) == 1
    assert not calls.calls
    assert "not wired" in capsys.readouterr().out


def test_clean(sdk, calls):
    mb.cmd_clean(W4, ns(app="light"))
    assert calls.cmds[0][2] == "clean"


def test_install_requires_clone(sdk, calls, capsys):
    assert mb.cmd_install(mb.TARGETS["nora-w3"], ns()) == 1
    assert "Not cloned yet" in capsys.readouterr().out


def test_install_runs_vendor_setup(sdk, calls):
    assert mb.cmd_install(W5, ns()) == 0
    assert calls.cmds[0][2:] == ["setup"]


def test_install_not_wired(sdk, calls, capsys):
    assert mb.cmd_install(IRIS, ns()) == 1
    assert "not wired" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# clone
# ---------------------------------------------------------------------------

def test_clone_is_shallow_and_pinned(sdk, calls):
    assert mb.cmd_clone(mb.TARGETS["nora-w3"], ns()) == 0
    first = calls.cmds[0]
    assert first[:6] == ["git", "clone", "--branch", "master", "--depth", "1"]
    assert first[-1] == str(sdk / "NORA-W3" / "ameba-rtos-d")


def test_clone_skips_existing(sdk, calls, capsys):
    assert mb.cmd_clone(W5, ns()) == 0
    assert not calls.calls
    assert "already cloned" in capsys.readouterr().out


def test_clone_stops_on_failure(sdk, calls):
    calls.returns = [128]
    assert mb.cmd_clone(mb.TARGETS["nora-w3"], ns()) == 128
    assert len(calls.calls) == 1
