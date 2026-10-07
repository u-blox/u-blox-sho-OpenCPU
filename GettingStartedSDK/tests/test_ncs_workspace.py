"""NCS workspace selection and the shared disk-space check."""

import argparse

import pytest

import nordic_ncs_build as ncs
import target_paths

B2 = ncs.TARGETS["nora-b2"]


def make_ws(path, board=True):
    (path / ".west").mkdir(parents=True)
    (path / "nrf").mkdir()
    if board:
        (path / "zephyr/boards/u-blox/ubx_evknorab2").mkdir(parents=True)
    return path


@pytest.fixture
def host(tmp_path, monkeypatch):
    """Linux host whose home is tmp_path, with no config or env overrides."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(ncs, "host_kind", lambda: "linux")
    monkeypatch.setattr(ncs.Path, "home", lambda: home)
    monkeypatch.setattr(ncs.target_paths, "sdk_dir", lambda slug: tmp_path / "repo" / slug)
    monkeypatch.setattr(ncs.target_paths, "SDK_ROOT", tmp_path / "repo")
    monkeypatch.delenv(ncs.WORKSPACE_ENV, raising=False)
    monkeypatch.delenv("ZEPHYR_BASE", raising=False)
    cfg = {}
    monkeypatch.setattr(ncs, "load_config", lambda t: dict(cfg))
    monkeypatch.setattr(ncs, "save_config", lambda t, c: cfg.update(c))
    versions = {}
    monkeypatch.setattr(ncs, "workspace_revision", lambda ws: versions.get(ncs.Path(ws).name))
    return home, cfg, versions


def test_default_workspace_windows(monkeypatch):
    monkeypatch.setattr(ncs, "host_kind", lambda: "windows")
    monkeypatch.setenv("SystemDrive", "C:")
    assert ncs.default_workspace("v3.4.1").as_posix() == "C:/ncs/v3.4.1"


def test_default_workspace_linux(host):
    home, _, _ = host
    assert ncs.default_workspace("v3.4.1") == home / "ncs" / "v3.4.1"


def test_default_workspace_avoids_nesting(host):
    home, _, _ = host
    make_ws(home / "ncs")
    assert ncs.default_workspace("v3.4.1") == home / "ncs-v3.4.1"


def test_prefers_pinned_release_with_board(host):
    home, _, versions = host
    make_ws(home / "ncs" / "v3.3.0")
    pinned = make_ws(home / "ncs" / ncs.NCS_REVISION)
    versions.update({"v3.3.0": "v3.3.0", ncs.NCS_REVISION: ncs.NCS_REVISION})
    assert ncs.detect_workspace(B2) == str(pinned)


def test_skips_workspace_without_board(host):
    home, _, _ = host
    make_ws(home / "ncs", board=False)
    newer = make_ws(home / "ncs-v3.4.1")
    assert ncs.detect_workspace(B2) == str(newer)


def test_falls_back_to_any_workspace(host):
    home, _, _ = host
    old = make_ws(home / "ncs", board=False)
    assert ncs.detect_workspace(B2) == str(old)


def test_env_override_wins(host, monkeypatch, tmp_path):
    home, _, _ = host
    make_ws(home / "ncs" / ncs.NCS_REVISION)
    chosen = make_ws(tmp_path / "elsewhere")
    monkeypatch.setenv(ncs.WORKSPACE_ENV, str(chosen))
    assert ncs.detect_workspace(B2) == str(chosen)


def test_zephyr_base_is_detected(host, monkeypatch, tmp_path):
    ws = make_ws(tmp_path / "nordic")
    monkeypatch.setenv("ZEPHYR_BASE", str(ws / "zephyr"))
    assert ncs.detect_workspace(B2) == str(ws)


def test_use_saves_selection(host, tmp_path):
    _, cfg, _ = host
    ws = make_ws(tmp_path / "picked")
    assert ncs.cmd_use(B2, argparse.Namespace(path=str(ws))) == 0
    assert cfg["workspace"] == str(ws)
    assert ncs.detect_workspace(B2) == str(ws)


def test_use_rejects_non_workspace(host, tmp_path):
    assert ncs.cmd_use(B2, argparse.Namespace(path=str(tmp_path))) == 1


def test_use_rejects_workspace_without_board(host, tmp_path, capsys):
    ws = make_ws(tmp_path / "old", board=False)
    assert ncs.cmd_use(B2, argparse.Namespace(path=str(ws))) == 1
    assert "ubx_evknorab2" in capsys.readouterr().out


def test_use_lists_workspaces(host, capsys):
    home, _, _ = host
    make_ws(home / "ncs-v3.4.1")
    assert ncs.cmd_use(B2, argparse.Namespace(path=None)) == 0
    assert "ncs-v3.4.1" in capsys.readouterr().out


def test_clone_refuses_when_disk_is_full(host, monkeypatch, calls, capsys):
    monkeypatch.setattr(ncs, "detect_west", lambda: ["west"])
    monkeypatch.setattr(ncs.subprocess, "call", calls)
    monkeypatch.setattr(target_paths, "free_gb", lambda p: 1.0)
    monkeypatch.delenv("UBX_SKIP_SPACE_CHECK", raising=False)
    args = ncs.build_parser().parse_args(["nora-b2", "clone"])
    assert ncs.cmd_clone(B2, args) == 1
    assert not calls.calls
    assert "Not enough disk space" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# target_paths.check_space
# ---------------------------------------------------------------------------

def test_check_space_ok(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(target_paths, "free_gb", lambda p: 50.0)
    assert target_paths.check_space(tmp_path, 15, "NCS")
    assert "[OK] Disk space: 50.0 GB free" in capsys.readouterr().out


def test_check_space_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(target_paths, "free_gb", lambda p: 2.0)
    monkeypatch.delenv("UBX_SKIP_SPACE_CHECK", raising=False)
    assert not target_paths.check_space(tmp_path, 15, "NCS")


def test_check_space_override(monkeypatch, tmp_path):
    monkeypatch.setattr(target_paths, "free_gb", lambda p: 2.0)
    monkeypatch.setenv("UBX_SKIP_SPACE_CHECK", "1")
    assert target_paths.check_space(tmp_path, 15, "NCS")


def test_free_gb_walks_up_to_existing_parent(tmp_path):
    assert target_paths.free_gb(tmp_path / "not" / "yet" / "created") > 0
