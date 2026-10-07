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
    assert mc.main(["nora-w3", "apply", "--variant", "NORA-W999"]) == 1
    assert "[FAIL]" in capsys.readouterr().out
