"""NCS workspace selection and the shared disk-space check."""

import argparse
import sys

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
    monkeypatch.setattr(ncs.target_paths, "installed_sdks", lambda slug: [])
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
# target_paths layout
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_sdk_root(tmp_path, monkeypatch):
    root = tmp_path / "getting-started-sdk"
    monkeypatch.setattr(target_paths, "SDK_ROOT", root)
    monkeypatch.setattr(target_paths, "MODULES_DIR", root / "modules")
    monkeypatch.setattr(target_paths, "SDKS_DIR", root / "sdks")
    return root


def test_layout_paths(fake_sdk_root):
    assert target_paths.config_dir("nora_w40") == fake_sdk_root / "modules" / "nora-w40" / "config"
    assert target_paths.sdk_dir("nora_w40") == fake_sdk_root / "sdks" / "esp-idf" / "v5.5.5"
    assert target_paths.sdk_dir("nora_w40", "v5.5.1") == fake_sdk_root / "sdks" / "esp-idf" / "v5.5.1"
    assert target_paths.vendor_dir("alma_b20_b21") == target_paths.vendor_dir("nora_b20_b21_b22")
    assert target_paths.matter_dir("nora_w40") == fake_sdk_root / "sdks" / "matter" / "nora-w40"


def test_every_target_has_a_vendor():
    assert set(target_paths.VENDORS) == set(target_paths.TARGETS)


def test_installed_sdks_newest_tag_first_branches_last(fake_sdk_root):
    for name in ("master", "v5.5.1", "v5.10", "v6.2", "4d59230ddff1"):
        target_paths.sdk_dir("nora_w40", name).mkdir(parents=True)
    names = [p.name for p in target_paths.installed_sdks("nora_w40")]
    assert names == ["v6.2", "v5.10", "v5.5.1", "master", "4d59230ddff1"]


def test_installed_sdks_without_any(fake_sdk_root):
    assert target_paths.installed_sdks("iris_w10") == []


def test_run_main_turns_ctrl_c_into_130():
    assert target_paths.run_main(lambda: 3) == 3

    def interrupted():
        raise KeyboardInterrupt
    assert target_paths.run_main(interrupted) == 130


def test_sdks_root_moves_into_wsl2_for_a_mnt_checkout(fake_sdk_root, monkeypatch, tmp_path):
    monkeypatch.setattr(target_paths, "WSL_SDKS_DIR", tmp_path / "home" / "sdks")
    assert target_paths.sdks_root() == fake_sdk_root / "sdks"
    monkeypatch.setattr(target_paths, "host_kind", lambda: "wsl")
    assert target_paths.sdks_root() == fake_sdk_root / "sdks"
    monkeypatch.setattr(target_paths, "SDK_ROOT", target_paths.Path("/mnt/e/getting-started-sdk"))
    assert target_paths.sdk_dir("nora_w30") == tmp_path / "home" / "sdks" / "ameba-rtos-d" / "main"
    monkeypatch.setenv("UBX_SDKS_DIR", str(tmp_path / "custom"))
    assert target_paths.vendor_dir("nora_w30") == tmp_path / "custom" / "ameba-rtos-d"


def test_installed_sdks_also_lists_the_in_tree_ones(fake_sdk_root, monkeypatch, tmp_path):
    monkeypatch.setenv("UBX_SDKS_DIR", str(tmp_path / "wsl"))
    (tmp_path / "wsl" / "ameba-rtos-d" / "main").mkdir(parents=True)
    (fake_sdk_root / "sdks" / "ameba-rtos-d" / "main").mkdir(parents=True)
    (fake_sdk_root / "sdks" / "ameba-rtos-d" / "v1.0").mkdir(parents=True)
    assert target_paths.installed_sdks("nora_w30") == [
        fake_sdk_root / "sdks" / "ameba-rtos-d" / "v1.0", tmp_path / "wsl" / "ameba-rtos-d" / "main"]


def test_resolve_config_creates_config_folder(fake_sdk_root):
    path = target_paths.resolve_config("nora_w30", "wsl")
    assert path == fake_sdk_root / "modules" / "nora-w30" / "config" / "build.wsl.json"
    assert path.parent.is_dir()
    assert not (fake_sdk_root / "sdks").exists()


@pytest.mark.parametrize("system,proc,expected", [
    ("Windows", "", "windows"),
    ("Darwin", "", "macos"),
    ("Linux", "Linux version 5.15 microsoft-standard-WSL2", "wsl"),
    ("Linux", "Linux version 6.8 generic", "linux"),
    ("Linux", OSError, "linux"),
])
def test_host_kind(monkeypatch, system, proc, expected):
    monkeypatch.setattr(target_paths.platform, "system", lambda: system)

    def read_text(self, **kw):
        if proc is OSError:
            raise OSError("no /proc")
        return proc
    monkeypatch.setattr(target_paths.Path, "read_text", read_text)
    assert target_paths.host_kind() == expected


def test_unknown_target_is_rejected():
    with pytest.raises(KeyError, match="Unknown target 'nora_w3'"):
        target_paths.sdk_dir("nora_w3")


def test_free_gb_unreadable_drive(monkeypatch, tmp_path):
    def boom(path):
        raise OSError("not ready")
    monkeypatch.setattr(target_paths.shutil, "disk_usage", boom)
    assert target_paths.free_gb(tmp_path) is None


def test_check_space_unknown_free_space(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(target_paths, "free_gb", lambda p: None)
    assert target_paths.check_space(tmp_path, 15, "NCS")
    assert "Could not determine free space" in capsys.readouterr().out


def test_json_round_trip(tmp_path):
    path = tmp_path / "config" / "build.linux.json"
    assert target_paths.load_json(path) == {}
    target_paths.save_json(path, {"workspace": "/ws"})
    assert target_paths.load_json(path) == {"workspace": "/ws"}
    path.write_text("{broken")
    assert target_paths.load_json(path) == {}


def test_newest_picks_the_highest_version(tmp_path, monkeypatch):
    for name in ("tool-9.0", "tool-10.1"):
        (tmp_path / name).mkdir()
    assert target_paths.newest([str(tmp_path / "tool-*")]).name == "tool-10.1"
    monkeypatch.chdir(tmp_path)
    assert target_paths.newest(["tool-9*"]).name == "tool-9.0"
    assert target_paths.newest([str(tmp_path / "none-*"), ""]) is None


def test_short_path(monkeypatch, tmp_path):
    monkeypatch.setattr(target_paths, "host_kind", lambda: "linux")
    assert target_paths.short_path("/a b") == "/a b"
    monkeypatch.setattr(target_paths, "host_kind", lambda: "windows")
    assert target_paths.short_path("C:\\nospace") == "C:\\nospace"
    # Off Windows ctypes has no windll; on Windows the path does not exist. Both keep the value.
    assert target_paths.short_path("C:\\Does Not Exist\\x") == "C:\\Does Not Exist\\x"


@pytest.mark.skipif(sys.platform != "win32", reason="GetShortPathNameW is Windows-only")
def test_short_path_on_windows(tmp_path):
    spaced = tmp_path / "with space"
    spaced.mkdir()
    assert " " not in target_paths.short_path(spaced)
