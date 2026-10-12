"""Copilot customization files stay loadable and in sync with the launcher."""

import re

import pytest

import ubx
from conftest import SDK_ROOT

GITHUB = SDK_ROOT / ".github"


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert match, f"{path} has no YAML frontmatter"
    return dict(re.findall(r"^(\w[\w-]*):\s*(.+)$", match.group(1), re.M))


@pytest.mark.parametrize("skill", sorted(GITHUB.glob("skills/*/SKILL.md")), ids=lambda p: p.parent.name)
def test_skill_name_matches_folder(skill):
    meta = frontmatter(skill)
    assert meta.get("name") == skill.parent.name
    assert len(meta.get("description", "")) > 40


@pytest.mark.parametrize("path", sorted(GITHUB.glob("instructions/*.instructions.md")), ids=lambda p: p.name)
def test_instructions_have_description_and_scope(path):
    meta = frontmatter(path)
    assert meta.get("description")
    assert meta.get("applyTo") and meta["applyTo"].strip("\"'") != "**"


def documented_order(text):
    """The first run of distinct action flags from --doctor to --log."""
    for start in (m.start() for m in re.finditer(r"--doctor", text)):
        flags = []
        for flag in re.findall(r"--([a-z][a-z-]*)", text[start:start + 400]):
            if flag not in ubx.ACTION_ORDER:
                continue
            if flag in flags:
                break
            flags.append(flag)
            if flag == "log":
                return flags
    return []


@pytest.mark.parametrize("doc", [".github/copilot-instructions.md", "README.md",
                                 "docs/QUICK_BUILD_REFERENCE.md"])
def test_documented_flag_order_matches_launcher(doc):
    assert documented_order((SDK_ROOT / doc).read_text(encoding="utf-8")) == ubx.ACTION_ORDER


def test_skills_referenced_by_the_instructions_exist():
    text = (GITHUB / "copilot-instructions.md").read_text(encoding="utf-8")
    for name in re.findall(r"skill `([a-z0-9-]+)`", text):
        assert (GITHUB / "skills" / name / "SKILL.md").is_file(), name
