import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import check_versions as cv
import matter_build
import nordic_ncs_build

Refs = cv.Refs
REAL_LS_REMOTE = cv.ls_remote


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Every test supplies its own refs; a real ls-remote call fails the test."""
    REAL_LS_REMOTE.cache_clear()

    def refuse(*a, **k):
        raise AssertionError("check_versions tests must not reach the network")

    monkeypatch.setattr(cv.subprocess, "run", refuse)
    yield
    REAL_LS_REMOTE.cache_clear()


def pin(revision, release=None):
    return cv.Pin("matter", "nora-w40", "repo", "https://example.com/repo.git", revision, release)


def test_pins_come_from_the_drivers():
    found = cv.pins()
    assert any(p.revision == nordic_ncs_build.NCS_REVISION for p in found)
    matter = {(p.owner, p.name, p.revision) for p in found if p.layer == "matter"}
    assert matter == {(k, r.name, r.revision) for k, t in matter_build.TARGETS.items() for r in t.repos}
    assert {p.owner for p in found if p.layer == "sdk"} >= {"iris-w10", "nora-w30", "nora-w40", "nora-w50-w51"}


@pytest.mark.parametrize("name,stable", [
    ("release/v1.6", True), ("v6.1", True), ("develop", True),
    ("v6.0-rc1", False), ("v5.5-dev", False), ("v26.09.00-pvw2", False),
    ("matter-v1.5-ti-1.2-ea.1", False), ("v1.0-beta2", False),
])
def test_prerelease_markers_are_tokens_not_substrings(name, stable):
    assert (cv.PRERELEASE.search(name) is None) is stable


@pytest.mark.parametrize("pin_name,other,match", [
    ("release/v1.5", "release/v1.6.1", True),
    ("v1.6.0.0.1", "v1.4.0.2", True),
    ("matter-v1.5-ti-1.1", "matter-v1.5-ti-1.2", True),
    ("matter-v1.5-ti-1.1", "matter-v1.5-ti-1.2-ea.1", False),
    ("v5.5.5", "release/v5.5", False),
])
def test_family(pin_name, other, match):
    assert bool(cv.family(pin_name).match(other)) is match


def test_newest_sorts_numerically():
    assert cv.newest(["v5.10", "v5.9", "v5.10.1", "v6.0-rc1"], r"^v[\d.]+$") == "v5.10.1"
    assert cv.newest(["main"], r"^v[\d.]+$") is None


@pytest.mark.parametrize("revision,refs,marker,text", [
    ("v3.4.1", Refs(["v3.4.0", "v3.4.1", "v3.5.0-rc1"], []), "OK", "newest tag"),
    ("v5.5.4", Refs(["v5.5.4", "v5.5.5", "v6.1"], []), "WARNING", "newer tag: v5.5.5 (newest overall v6.1)"),
    ("v5.5.5", Refs(["v5.5.5", "v6.1"], []), "WARNING", "newest v5.5.x; newer tag: v6.1"),
    ("release/v1.5", Refs([], ["main", "release/v1.5", "release/v1.6.1"]), "WARNING",
     "newer branch: release/v1.6.1"),
    ("release/v1.6", Refs([], ["release/v1.5", "release/v1.6"]), "OK", "newest branch"),
    ("v9.9", Refs(["v1.0"], ["main"]), "FAIL", "no longer exists"),
    ("v1.0", None, "FAIL", "no answer"),
])
def test_check_pinned(revision, refs, marker, text):
    got = cv.check(pin(revision), refs)
    assert got[0] == marker and text in got[1]


def test_check_tracked_branch():
    refs = Refs(["v6.0", "v6.1", "v6.2-dev"], ["master"])
    assert cv.check(pin("master", r"^v[\d.]+$"), refs) == ("INFO", "tracks master; newest release v6.1")
    assert cv.check(pin("main"), Refs([], ["main"])) == ("INFO", "tracks main; no release tags")
    assert cv.check(pin("main"), Refs([], ["master"]))[0] == "FAIL"


def test_ls_remote_parses_tags_and_heads(monkeypatch):
    out = ("a\trefs/heads/main\nb\trefs/heads/release/v1.6\n"
           "c\trefs/tags/v1.0\nd\trefs/tags/v1.0^{}\ne\trefs/pull/1/head\n")
    seen = []

    def run(cmd, **kwargs):
        seen.append(cmd)
        return SimpleNamespace(returncode=0, stdout=out)

    monkeypatch.setattr(cv.subprocess, "run", run)
    refs = cv.ls_remote("https://example.com/a.git")
    assert refs == Refs(["v1.0"], ["main", "release/v1.6"])
    cv.ls_remote("https://example.com/a.git")
    assert len(seen) == 1 and seen[0][:4] == ["git", "ls-remote", "--tags", "--heads"]


@pytest.mark.parametrize("result", [SimpleNamespace(returncode=128, stdout=""),
                                    subprocess.TimeoutExpired("git", 120), OSError("no git")])
def test_ls_remote_failure_is_none(monkeypatch, result):
    def run(cmd, **kwargs):
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(cv.subprocess, "run", run)
    assert cv.ls_remote("https://example.com/b.git") is None


@pytest.mark.parametrize("folder,tags,marker", [
    ("simplelink_wifi_sdk_10_20_00_39", ["wifi-10.10.01.08", "wifi-10.20.00.39"], "OK"),
    ("simplelink_wifi_sdk_10_10_01_08", ["wifi-10.10.01.08", "wifi-10.20.00.39"], "WARNING"),
])
def test_installed_ti_sdk(monkeypatch, folder, tags, marker):
    monkeypatch.setattr(cv.nora_w50_w51_build, "detect_installed_sdk", lambda: Path("C:/ti") / folder)
    monkeypatch.setattr(cv, "ls_remote", lambda url: Refs(tags, ["main"]))
    assert cv.installed_ti_sdk()[0] == marker


def test_installed_ti_sdk_absent(monkeypatch):
    monkeypatch.setattr(cv.nora_w50_w51_build, "detect_installed_sdk", lambda: None)
    assert cv.installed_ti_sdk() is None


def test_main_exit_code_and_layers(monkeypatch, capsys):
    monkeypatch.setattr(cv, "installed_ti_sdk", lambda: None)

    def up_to_date(url):
        return Refs([p.revision for p in cv.pins() if p.url == url], ["main", "master"])

    monkeypatch.setattr(cv, "ls_remote", up_to_date)
    assert cv.main(["--matter"]) == 0
    out = capsys.readouterr().out
    assert "Matter SDKs" in out and "Vendor SDKs" not in out

    monkeypatch.setattr(cv, "ls_remote", lambda url: None)
    assert cv.main(["--sdk"]) == 1
    assert "[FAIL]" in capsys.readouterr().out
