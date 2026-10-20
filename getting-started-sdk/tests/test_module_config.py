"""Module configuration (scripts/module_config.py): profiles, variants, version guards."""

import pytest

import module_config as mc


@pytest.mark.parametrize("key", mc.TARGET_KEYS)
def test_every_target_has_a_loadable_profile(key):
    profile = mc.load_profile(key)
    assert profile["label"]
    assert profile.get("status") in ("ready", "pending")
    if profile["status"] == "pending":
        assert not profile.get("variants")


@pytest.mark.parametrize("key", mc.TARGET_KEYS)
def test_variants_command(key, capsys):
    assert mc.main([key, "variants"]) == 0
    assert mc.load_profile(key)["label"] in capsys.readouterr().out


@pytest.mark.parametrize("key", [k for k in mc.TARGET_KEYS if mc.load_profile(k).get("variants")])
def test_resolve_variant_tolerates_case_and_suffixes(key):
    profile = mc.load_profile(key)
    for name in profile["variants"]:
        assert mc.resolve_variant(profile, name.lower())[0] == name
        assert mc.resolve_variant(profile, f"{name}-99")[0] == name


READY = [k for k in mc.TARGET_KEYS if mc.load_profile(k).get("status") == "ready"]


@pytest.mark.parametrize("key", READY)
def test_every_profile_asset_exists_in_the_repo(key):
    # Assets live in the repo-root folders, so a rename there must not go unnoticed.
    profile = mc.load_profile(key)
    assert (mc.REPO_ROOT / profile["assets"]).is_dir()
    assert mc.asset_path(profile, profile["source"], {}).is_file()
    missing = []
    for variant, cfg in profile["variants"].items():
        values = mc.build_vars(profile, variant, cfg, {})
        for op in mc.iter_ops(profile):
            for field in ("src", "patch"):
                if field in op and not mc.asset_path(profile, op[field], values).exists():
                    missing.append(f"{variant}: {op[field]}")
    assert not missing


def test_ops_are_applied_in_topic_order():
    profile = {"patches": [{"op": "p"}], "output_power": [{"op": "o"}], "calibration": [{"op": "c"}]}
    assert [(op["topic"], op["op"]) for op in mc.iter_ops(profile)] == \
        [("output_power", "o"), ("calibration", "c"), ("patches", "p")]


@pytest.mark.parametrize("key", mc.TARGET_KEYS)
def test_profiles_use_topics_not_the_old_flat_list(key):
    assert "sdk_patch" not in mc.load_profile(key)


@pytest.mark.parametrize("text", ["02:12:34:56:78:9a", "02-12-34-56-78-9A", "0212.3456.789a", "02123456789A"])
def test_parse_mac_accepts_common_forms(text):
    assert mc.parse_mac(text) == bytes.fromhex("02123456789A")


@pytest.mark.parametrize("text", ["02:12:34:56:78", "zz:12:34:56:78:9a", "00:00:00:00:00:00",
                                  "ff:ff:ff:ff:ff:ff", "01:12:34:56:78:9a"])
def test_parse_mac_rejects_unusable_addresses(text):
    with pytest.raises(ValueError):
        mc.parse_mac(text)


def test_mac_set_prints_runtime_override(capsys):
    assert mc.main(["iris-w10", "mac", "--address", "02:12:34:56:78:9a"]) == 0
    out = capsys.readouterr().out
    assert "{ 0x02, 0x12, 0x34, 0x56, 0x78, 0x9A }" in out
    assert "wlan_set_sta_mac_addr" in out


def test_mac_burn_refused_without_host_tool(capsys):
    assert mc.main(["nora-w30", "mac", "--address", "02:12:34:56:78:9a", "--burn"]) == 1
    assert "No host-side tool" in capsys.readouterr().out


def test_mac_burn_runs_espefuse_interactively(monkeypatch, calls):
    monkeypatch.setattr(mc, "esp_tool", lambda module: ["py", "-m", module])
    monkeypatch.setattr(mc.subprocess, "run", lambda *a, **k: mc.subprocess.CompletedProcess(
        a[0], 0, stdout="Commands: burn-custom-mac ..."))
    monkeypatch.setattr(mc.subprocess, "call", calls)
    assert mc.main(["nora-w40", "mac", "--address", "02:12:34:56:78:9a",
                    "--serial", "COM3", "--burn"]) == 0
    # No --do-not-confirm: espefuse itself asks the user to type BURN.
    assert calls.cmds == [["py", "-m", "espefuse", "--chip", "esp32c6", "--port", "COM3",
                           "burn-custom-mac", "02:12:34:56:78:9A"]]


def test_examples_command(capsys):
    assert mc.main(["nora-w40", "examples"]) == 0
    assert "--build ubx/rf-calibration" in capsys.readouterr().out
    assert mc.main(["iris-w10", "examples"]) == 0
    assert "Manual: replace driver_examples/romapi/otp/main.c" in capsys.readouterr().out
    assert mc.main(["nora-w50-w51", "examples"]) == 0
    assert "(none yet)" in capsys.readouterr().out


# esptool read_mac on an ESP32-C6: EUI-64 first, then the 6-byte base.
ESP32C6_READ_MAC = """\
MAC:                60:55:f9:ff:fe:f7:2c:fe
BASE MAC:           60:55:f9:f7:2c:fe
MAC_EXT:            ff:fe
"""


def test_esptool_mac_prints_every_derived_address(capsys):
    mc.print_esptool_mac(ESP32C6_READ_MAC, mc.load_profile("nora-w40")["mac"]["derived"])
    out = capsys.readouterr().out
    assert "Base MAC (eFuse):     60:55:F9:F7:2C:FE" in out
    assert "Wi-Fi station:        60:55:F9:F7:2C:FE" in out
    assert "Wi-Fi SoftAP:         60:55:F9:F7:2C:FF" in out
    # The last octet wraps without carry, as in ESP-IDF's generate_mac().
    assert "Bluetooth LE:         60:55:F9:F7:2C:00" in out
    assert "IEEE 802.15.4:        60:55:F9:FF:FE:F7:2C:FE" in out


def test_esptool_mac_without_eui64_uses_mac_as_base(capsys):
    mc.print_esptool_mac("MAC: 24:0a:c4:00:00:01\n", [{"name": "Bluetooth LE", "offset": 2},
                                                      {"name": "IEEE 802.15.4", "from": "eui64"}])
    out = capsys.readouterr().out
    assert "Base MAC (eFuse):     24:0A:C4:00:00:01" in out
    assert "Bluetooth LE:         24:0A:C4:00:00:03" in out
    assert "802.15.4" not in out


@pytest.mark.parametrize("key,expected", [
    ("iris-w10", "--build wifi_examples/wifi_cli --flash --log, then type: wlan-mac"),
    ("nora-w30", "--build project_hp --flash --log, then type: ATW?"),
    ("nora-b20-b21-b22", "--build bluetooth/beacon --flash --log"),
    ("alma-b20-b21", "--build bluetooth/beacon --flash --log"),
])
def test_mac_explains_how_to_read_it_on_the_module(key, expected, capsys):
    assert mc.main([key, "mac"]) == 0
    assert expected in capsys.readouterr().out


def test_nora_w40_read_mac_example_is_listed(capsys):
    assert mc.main(["nora-w40", "examples"]) == 0
    assert "--build ubx/read-mac" in capsys.readouterr().out


@pytest.mark.parametrize("key", READY)
def test_every_example_exists_in_the_repo(key):
    profile = mc.load_profile(key)
    for example in profile.get("examples") or []:
        if example["kind"] == "project":
            assert (mc.example_dir(key, example) / "CMakeLists.txt").is_file()
        else:
            assert mc.asset_path(profile, example["file"], {}).is_file()


def test_resolve_variant_errors():
    profile = {"variants": {"NORA-W301": {}, "NORA-W306": {}}}
    with pytest.raises(ValueError, match="No variant selected"):
        mc.resolve_variant(profile, None)
    with pytest.raises(ValueError, match="ambiguous"):
        mc.resolve_variant(profile, "NORA-W30")
    with pytest.raises(ValueError, match="Unknown variant"):
        mc.resolve_variant(profile, "NORA-W999")
    assert mc.resolve_variant({}, None) == (None, {})


@pytest.mark.parametrize("found,spec,ok", [
    ((5, 1), ">=5.1,<5.2", True),
    ((5, 2), ">=5.1,<5.2", False),
    ((6, 2), ">=5.1,<5.2 || >=6.2,<6.3", True),
    ((5, 5), ">=5.1,<5.2 || >=6.2,<6.3", False),
    ((25, 6), "==25.6", True),
])
def test_version_matches(found, spec, ok):
    assert mc.version_matches(found, spec) is ok


def test_expand_reports_undefined_variables():
    assert mc.expand("{a}-{b}", {"a": 1, "b": 2}) == "1-2"
    with pytest.raises(ValueError, match="undefined variable"):
        mc.expand("{missing}", {})


def test_unknown_variant_is_a_clean_failure(capsys):
    assert mc.main(["nora-w30", "apply", "--variant", "NORA-W999"]) == 1
    assert "[FAIL]" in capsys.readouterr().out


def test_default_sdk_versions_satisfy_the_profile_requirements():
    # A plain --clone must fetch an SDK that --rf-config accepts.
    import re

    import target_paths

    for slug, key in target_paths.TARGETS.items():
        spec = (mc.load_profile(key).get("requires") or {}).get("sdk_version")
        if not spec:
            continue
        found = re.match(r"v?(\d+)\.(\d+)", target_paths.default_version(slug))
        assert found, f"{key}: default version is not a release, but the profile requires {spec}"
        assert mc.version_matches((int(found[1]), int(found[2])), spec), key
