"""NCS workspace selection and the shared disk-space check."""

import argparse

import pytest

import nordic_ncs_build as ncs
import target_paths

B2 = ncs.TARGETS["nora-b20-b21-b22"]


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
    args = ncs.build_parser().parse_args(["nora-b20-b21-b22", "clone"])
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


# ---------------------------------------------------------------------------
# target_paths.adopt_legacy
# ---------------------------------------------------------------------------

def test_adopt_legacy_merges_old_folder(tmp_path):
    old = tmp_path / "NORA-W4"
    (old / "sdk" / "esp-idf").mkdir(parents=True)
    (old / "config").mkdir()
    (old / "config" / "rf_config.json").write_text("{}")
    new = tmp_path / "nora-w40"
    (new / "sdk").mkdir(parents=True)
    (new / "sdk" / ".gitkeep").write_text("")

    assert target_paths.adopt_legacy(new, "nora_w40") == new
    assert (new / "sdk" / "esp-idf").is_dir()
    assert (new / "config" / "rf_config.json").read_text() == "{}"
    assert not old.exists()


def test_adopt_legacy_without_old_folder(tmp_path):
    new = tmp_path / "nora-w50-w51"
    assert target_paths.adopt_legacy(new, "nora_w50_w51") == new
    assert not new.exists()


def test_every_target_has_a_legacy_name():
    assert set(target_paths.LEGACY) == set(target_paths.TARGETS)


# ---------------------------------------------------------------------------
# target_paths.adopt_root_sdk
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_sdk_root(tmp_path, monkeypatch):
    root = tmp_path / "getting-started-sdk"
    monkeypatch.setattr(target_paths, "SDK_ROOT", root)
    monkeypatch.setattr(target_paths, "TARGETS_DIR", root / "targets")
    return root


def test_adopt_root_sdk_moves_sdk_and_repoints_config(fake_sdk_root):
    (fake_sdk_root / "esp-idf" / "components").mkdir(parents=True)
    config = target_paths.config_dir("nora_w40")
    config.mkdir(parents=True)
    (config / "build.windows.json").write_text('{"idf_path": "E:/x/getting-started-sdk/esp-idf"}')
    (config / "build.wsl.json").write_text('{"idf_path": "E:\\\\x\\\\getting-started-sdk\\\\esp-idf"}')

    new = target_paths.adopt_root_sdk("nora_w40")

    assert new == fake_sdk_root / "targets" / "nora-w40" / "sdk" / "esp-idf"
    assert (new / "components").is_dir()
    assert not (fake_sdk_root / "esp-idf").exists()
    assert "getting-started-sdk/targets/nora-w40/sdk/esp-idf" in (config / "build.windows.json").read_text()
    assert "targets\\\\nora-w40\\\\sdk\\\\esp-idf" in (config / "build.wsl.json").read_text()
    assert target_paths.sdk_candidates("nora_w40") == [new]


def test_adopt_root_sdk_keeps_both_when_new_exists(fake_sdk_root, capsys):
    (fake_sdk_root / "ameba-rtos-d").mkdir(parents=True)
    target_paths.vendor_sdk("nora_w30").mkdir(parents=True)

    assert target_paths.adopt_root_sdk("nora_w30") is None
    assert "Both" in capsys.readouterr().out
    assert len(target_paths.sdk_candidates("nora_w30")) == 2


def test_adopt_root_sdk_ignores_targets_without_root_sdk(fake_sdk_root):
    assert target_paths.adopt_root_sdk("nora_b20_b21_b22") is None
    assert target_paths.adopt_root_sdk("iris_w10") is None


def test_cached_paths_follow_the_sdk_folder_rename(fake_sdk_root):
    config = target_paths.config_dir("nora_w30")
    config.mkdir(parents=True)
    (config / "build.wsl.json").write_text('{"sdk_path": "/mnt/e/r/GettingStartedSDK/targets/nora-w30/sdk/ameba-rtos-d"}')
    (config / "build.windows.json").write_text('{"p": "E:\\\\r\\\\GettingStartedSDK\\\\x"}')

    target_paths.adopt_renamed_root()

    assert "/mnt/e/r/getting-started-sdk/targets/" in (config / "build.wsl.json").read_text()
    assert "\\\\getting-started-sdk\\\\x" in (config / "build.windows.json").read_text()
