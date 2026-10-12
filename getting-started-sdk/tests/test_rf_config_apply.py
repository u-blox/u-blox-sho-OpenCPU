"""--rf-config apply / revert / status (scripts/module_config.py) on a fake SDK tree."""

import argparse
import copy
import shutil

import pytest

import module_config as mc

KEY = "nora-w30"  # any real key; profile, SDK root and state file are faked below

PROFILE = {
    "label": "Test module",
    "status": "ready",
    "assets": "assets",
    "variants": {"TEST-01": {"vars": {"table": "a"}}, "TEST-02": {"vars": {"table": "b"}}},
    "output_power": [{"op": "copy", "src": "power_{table}.c", "dst": "wlan/power.c"}],
    "calibration": [
        {"op": "copy", "src": "cal.bin", "dst": "new/cal.bin"},
        {"op": "replace", "src": "cal.bin", "dst": "missing/cal.bin"},
    ],
    "patches": [
        {"op": "replace-line", "file": "build/Makefile", "from": "TABLE = vendor", "to": "TABLE = ubx_{table}"},
        {"op": "copy-tree", "src": "component", "dst": "components/ubx"},
    ],
}


def args(**overrides):
    values = dict(variant="TEST-01", region=None, set=None, force=False, sdk=None)
    values.update(overrides)
    return argparse.Namespace(**values)


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.fixture
def profile():
    return copy.deepcopy(PROFILE)


@pytest.fixture
def sdk(tmp_path, monkeypatch, profile):
    assets = tmp_path / "repo" / "assets"
    (assets / "component").mkdir(parents=True)
    (assets / "component" / "ubx.c").write_bytes(b"u-blox component\n")
    (assets / "power_a.c").write_bytes(b"power A\n")
    (assets / "power_b.c").write_bytes(b"power B\n")
    (assets / "cal.bin").write_bytes(b"\x01\x02")

    root = tmp_path / "sdk"
    (root / "wlan").mkdir(parents=True)
    (root / "wlan" / "power.c").write_bytes(b"vendor power\n")
    (root / "build").mkdir()
    # CRLF on purpose: a makefile with LF-converted continuation lines breaks.
    (root / "build" / "Makefile").write_bytes(b"CC = gcc\r\nTABLE = vendor\r\n")

    monkeypatch.setattr(mc, "REPO_ROOT", tmp_path / "repo")
    monkeypatch.setattr(mc, "load_profile", lambda key: profile)
    monkeypatch.setattr(mc, "vendor_sdk_root", lambda key: root)
    state_file = tmp_path / "rf_config.json"
    monkeypatch.setattr(mc, "state_path", lambda key: state_file)
    return root


def test_apply_then_revert_restores_the_vendor_sdk(sdk, capsys):
    vendor = files(sdk)

    assert mc.cmd_apply(KEY, args()) == 0
    out = capsys.readouterr().out
    assert (sdk / "wlan" / "power.c").read_bytes() == b"power A\n"
    assert (sdk / "new" / "cal.bin").read_bytes() == b"\x01\x02"
    assert not (sdk / "missing").exists()
    assert "skipped, not part of this SDK" in out
    assert (sdk / "build" / "Makefile").read_bytes() == b"CC = gcc\r\nTABLE = ubx_a\r\n"
    assert (sdk / "components" / "ubx" / "ubx.c").is_file()
    assert "[OK] RF configuration applied for TEST-01" in out

    assert mc.cmd_revert(KEY, args()) == 0
    assert files(sdk) == vendor
    assert not mc.load_state(KEY).get("applied")


def test_applying_twice_keeps_the_vendor_original(sdk, capsys):
    vendor = files(sdk)
    assert mc.cmd_apply(KEY, args()) == 0
    assert mc.cmd_apply(KEY, args()) == 0
    assert "already applied" in capsys.readouterr().out
    assert mc.cmd_revert(KEY, args()) == 0
    assert files(sdk) == vendor


def test_status_reports_files_changed_after_apply(sdk, capsys):
    assert mc.cmd_status(KEY, args()) == 0
    assert "NOT applied" in capsys.readouterr().out

    mc.cmd_apply(KEY, args())
    capsys.readouterr()
    assert mc.cmd_status(KEY, args()) == 0

    (sdk / "wlan" / "power.c").write_bytes(b"edited by hand\n")
    assert mc.cmd_status(KEY, args()) == 1
    assert "changed since apply" in capsys.readouterr().out


def test_switching_variant_reverts_first(sdk, capsys):
    vendor = files(sdk)
    mc.cmd_apply(KEY, args(variant="TEST-01"))
    assert mc.cmd_apply(KEY, args(variant="TEST-02")) == 0
    assert "Switching from TEST-01 to TEST-02" in capsys.readouterr().out
    assert (sdk / "wlan" / "power.c").read_bytes() == b"power B\n"
    assert (sdk / "build" / "Makefile").read_bytes() == b"CC = gcc\r\nTABLE = ubx_b\r\n"

    mc.cmd_revert(KEY, args())
    assert files(sdk) == vendor


def test_apply_refuses_a_second_sdk_tree(sdk, tmp_path, capsys):
    mc.cmd_apply(KEY, args())
    other = tmp_path / "other-sdk"
    other.mkdir()
    assert mc.cmd_apply(KEY, args(sdk=str(other))) == 1
    assert "Revert it first" in capsys.readouterr().out


def test_missing_asset_fails_and_says_not_compliant(sdk, tmp_path, capsys):
    (tmp_path / "repo" / "assets" / "cal.bin").unlink()
    assert mc.cmd_apply(KEY, args()) == 1
    out = capsys.readouterr().out
    assert "asset missing" in out
    assert "not regulatory compliant" in out


def test_missing_anchor_line_fails(sdk, capsys):
    (sdk / "build" / "Makefile").write_bytes(b"CC = gcc\r\n")
    assert mc.cmd_apply(KEY, args()) == 1
    assert "anchor line not found" in capsys.readouterr().out


def test_apply_without_a_fetched_sdk_fails(sdk, monkeypatch, capsys):
    monkeypatch.setattr(mc, "vendor_sdk_root", lambda key: None)
    assert mc.cmd_apply(KEY, args()) == 1
    assert "Run --clone first" in capsys.readouterr().out


def test_revert_without_apply_does_nothing(sdk, capsys):
    assert mc.cmd_revert(KEY, args()) == 0
    assert "Nothing to revert" in capsys.readouterr().out


def test_pending_profile_applies_nothing(capsys):
    assert mc.cmd_apply("nora-w50-w51", args()) == 0
    assert "No u-blox RF configuration is available" in capsys.readouterr().out


def text(path):
    # git apply honours core.autocrlf, so on Windows it may write CRLF.
    return path.read_bytes().replace(b"\r\n", b"\n")


@pytest.mark.skipif(not (shutil.which("patch") or shutil.which("git")), reason="needs patch or git")
def test_patch_op_applies_and_reverts(sdk, profile, tmp_path, capsys):
    (tmp_path / "repo" / "assets" / "fix.patch").write_bytes(
        b"--- a/src/main.c\n+++ b/src/main.c\n@@ -1 +1 @@\n-int x = 0;\n+int x = 1;\n")
    (sdk / "src").mkdir()
    (sdk / "src" / "main.c").write_bytes(b"int x = 0;\n")
    profile["patches"] = [{"op": "patch", "patch": "fix.patch", "dir": ".", "strip": 1}]

    assert mc.cmd_apply(KEY, args()) == 0
    assert text(sdk / "src" / "main.c") == b"int x = 1;\n"
    assert mc.cmd_apply(KEY, args()) == 0
    assert "already applied: fix.patch" in capsys.readouterr().out

    assert mc.cmd_revert(KEY, args()) == 0
    assert text(sdk / "src" / "main.c") == b"int x = 0;\n"
