"""module_config.py: SDK location, version gates, report sections and esptool MAC reads."""

import subprocess

import pytest

import module_config as mc


# ---------------------------------------------------------------------------
# vendor SDK location and version
# ---------------------------------------------------------------------------

@pytest.fixture
def build_cfg(monkeypatch, tmp_path):
    cfg = {}
    path = tmp_path / "build.json"
    monkeypatch.setattr(mc.target_paths, "config_file", lambda slug: path)
    monkeypatch.setattr(mc.target_paths, "installed_sdks", lambda slug: [])
    monkeypatch.setattr(mc.Path, "home", lambda: tmp_path / "home")

    def write(**values):
        cfg.update(values)
        path.write_text(mc.json.dumps(cfg))
    return write


def test_build_config_tolerates_bad_json(build_cfg, tmp_path):
    assert mc._build_config("nora-w40") == {}
    (tmp_path / "build.json").write_text("{")
    assert mc._build_config("nora-w40") == {}


@pytest.mark.parametrize("key,cfg_key,marker", [
    ("nora-w30", "sdk_path", "component/common/drivers/wlan"),
    ("nora-w40", "idf_path", "components/esp_phy"),
])
def test_vendor_sdk_root_needs_marker(build_cfg, tmp_path, key, cfg_key, marker):
    sdk = tmp_path / "sdk"
    sdk.mkdir()
    build_cfg(**{cfg_key: str(sdk)})
    assert mc.vendor_sdk_root(key) is None
    (sdk / marker).mkdir(parents=True)
    assert mc.vendor_sdk_root(key) == sdk


def test_vendor_sdk_root_iris_prefers_mcuxsdk(build_cfg, tmp_path):
    ws = tmp_path / "ws"
    (ws / "mcuxsdk" / "middleware").mkdir(parents=True)
    build_cfg(workspace=str(ws))
    assert mc.vendor_sdk_root("iris-w10") == ws / "mcuxsdk"


def test_vendor_sdk_root_other_targets(build_cfg):
    assert mc.vendor_sdk_root("nora-b20-b21-b22") is None


def test_idf_and_mcux_versions(tmp_path):
    assert mc.idf_version(tmp_path) is None and mc.mcux_version(tmp_path) is None
    header = tmp_path / "components/esp_common/include/esp_idf_version.h"
    header.parent.mkdir(parents=True)
    header.write_text("#define ESP_IDF_VERSION_MAJOR 6\n#define ESP_IDF_VERSION_MINOR 2\n")
    (tmp_path / "MCUX_VERSION").write_text("CURRENT_YEAR = 25\nVERSION_MAJOR = 6\n")
    assert mc.sdk_version("nora-w40", tmp_path) == (6, 2)
    assert mc.sdk_version("iris-w10", tmp_path) == (25, 6)
    assert mc.sdk_version("nora-w30", tmp_path) is None
    header.write_text("// nothing\n")
    (tmp_path / "MCUX_VERSION").write_text("junk\n")
    assert mc.idf_version(tmp_path) is None and mc.mcux_version(tmp_path) is None


def test_step_applies():
    assert mc.step_applies("plain text", (6, 0))
    assert mc.step_applies({"text": "x", "sdk_version": ">=6.0"}, None)
    assert mc.step_applies({"text": "x", "sdk_version": ">=6.0"}, (6, 1))
    assert not mc.step_applies({"text": "x", "sdk_version": ">=6.0"}, (5, 4))


# ---------------------------------------------------------------------------
# report sections
# ---------------------------------------------------------------------------

REGULATORY = {"regulatory": {
    "api": "esp_wifi_set_country_code(\"<code>\")", "when": "before esp_wifi_start()",
    "domains": {"ETSI": "EU", "FCC": "US"}, "notes": ["Certified tables only."]}}


def test_print_regulatory(capsys):
    mc.print_regulatory({}, "ETSI")
    assert capsys.readouterr().out == ""
    mc.print_regulatory(REGULATORY, "etsi")
    out = capsys.readouterr().out
    assert 'esp_wifi_set_country_code("EU")' in out and "before esp_wifi_start" in out
    mc.print_regulatory(REGULATORY, "MARS")
    assert "Unknown domain 'MARS'" in capsys.readouterr().out
    mc.print_regulatory(REGULATORY, None)
    out = capsys.readouterr().out
    assert "No --region given" in out and "FCC" in out and "Certified tables only." in out


def test_print_manual_and_verify(capsys):
    profile = {"manual_steps": ["Set {table}.", {"text": "New SDK only.", "sdk_version": ">=9.0"}],
               "verify": {"log_contains": "TX power table W40", "notes": ["Check the log."]}}
    mc.print_manual(profile, {"table": "W401"}, (6, 2))
    mc.print_verify(profile)
    out = capsys.readouterr().out
    assert "Still manual (SDK 6.02)" in out and "Set W401." in out and "New SDK only" not in out
    assert "TX power table W40" in out and "Check the log." in out
    mc.print_manual({}, {}, None)
    mc.print_verify({})
    assert capsys.readouterr().out == ""


def test_print_esptool_mac_without_output(capsys):
    mc.print_esptool_mac("Connecting...\n", [])
    assert "printed no MAC" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# esptool fallbacks
# ---------------------------------------------------------------------------

@pytest.fixture
def esptool(monkeypatch, tmp_path):
    monkeypatch.setattr(mc, "vendor_sdk_root", lambda key: tmp_path)
    bundled = tmp_path / "components/esptool_py/esptool/esptool.py"
    bundled.parent.mkdir(parents=True)
    bundled.write_text("")
    monkeypatch.setattr(mc, "idf_pythons", lambda: ["idfpy"])
    monkeypatch.setattr(mc.shutil, "which", lambda name: None)
    seen = []

    def use(*results):
        queue = list(results)

        def run(cmd, **kw):
            seen.append(cmd)
            result = queue.pop(0)
            if isinstance(result, Exception):
                raise result
            return subprocess.CompletedProcess(cmd, *result)
        monkeypatch.setattr(mc.subprocess, "run", run)
        return seen
    return use


def test_read_mac_falls_back_until_one_works(esptool, capsys):
    seen = esptool(OSError("no python"), (1, "", "No module named esptool"),
                   (0, "MAC: f0:f5:bd:01:02:03\n", ""))
    assert mc.read_mac_esptool("nora-w40", "COM5", [{"name": "Wi-Fi STA", "offset": 0}]) == 0
    assert seen[1][-3:] == ["--port", "COM5", "read_mac"] and seen[2][0] == "idfpy"
    assert "F0:F5:BD:01:02:03" in capsys.readouterr().out


def test_read_mac_reports_tool_error(esptool, capsys):
    esptool((2, "", "A fatal error occurred: Could not open port\n"))
    assert mc.read_mac_esptool("nora-w40", None, []) == 1
    assert "Could not open port" in capsys.readouterr().out


def test_read_mac_without_any_esptool(esptool, monkeypatch, capsys):
    monkeypatch.setattr(mc.shutil, "which", lambda name: "/usr/bin/esptool.py")
    seen = esptool(*[(1, "", "No module named esptool")] * 4)
    assert mc.read_mac_esptool("nora-w40", None, []) == 1
    assert seen[0] == ["esptool.py", "read_mac"]
    assert "esptool not found" in capsys.readouterr().out


def test_idf_pythons_and_esp_tool(monkeypatch, tmp_path):
    for rel in ("idf5.5_py3.12_env/bin/python", "idf6.0_py3.12_env/Scripts/python.exe"):
        exe = tmp_path / ".espressif/python_env" / rel
        exe.parent.mkdir(parents=True)
        exe.write_text("")
    monkeypatch.setattr(mc.Path, "home", lambda: tmp_path)
    pythons = mc.idf_pythons()
    assert "idf6.0" in pythons[0] and len(pythons) == 2
    monkeypatch.setattr(mc.subprocess, "run",
                        lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0 if cmd[0] == pythons[1] else 1))
    assert mc.esp_tool("espefuse") == [pythons[1], "-m", "espefuse"]
    monkeypatch.setattr(mc.subprocess, "run", lambda cmd, **kw: subprocess.CompletedProcess(cmd, 1))
    assert mc.esp_tool("espefuse") is None
