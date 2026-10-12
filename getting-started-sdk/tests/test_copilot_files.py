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


REPO_ROOT = SDK_ROOT.parent
DOCS = sorted({*SDK_ROOT.glob("*.md"), *SDK_ROOT.glob("docs/*.md"), SDK_ROOT / "modules" / "README.md",
               *GITHUB.rglob("*.md"), *REPO_ROOT.glob("*.md")})


def anchors(path):
    """GitHub-style heading anchors of a Markdown file."""
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
    return {re.sub(r"[^\w\- ]", "", h.strip().lower()).replace(" ", "-")
            for h in re.findall(r"^#+\s+(.+)$", text, re.M)}


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_relative_links_resolve(doc):
    text = re.sub(r"```.*?```", "", doc.read_text(encoding="utf-8"), flags=re.S)
    broken = []
    for link in re.findall(r"\]\(([^)\s]+)\)", text):
        if re.match(r"[a-z]+:", link):
            continue
        target, _, anchor = link.partition("#")
        # A leading '/' is the repository root on GitLab and GitHub.
        base = REPO_ROOT if target.startswith("/") else doc.parent
        path = (base / target.lstrip("/")).resolve() if target else doc
        if not path.exists():
            broken.append(link)
        elif anchor and path.suffix == ".md" and anchor not in anchors(path):
            broken.append(link)
    assert not broken, f"broken links: {broken}"


@pytest.mark.parametrize("script", sorted((SDK_ROOT / "scripts").glob("*_build.py")), ids=lambda p: p.name)
def test_hints_name_the_launcher_not_the_driver(script):
    """Users run ubx-sdk; a hint to call a driver directly sends them around it."""
    text = script.read_text(encoding="utf-8")
    assert not re.findall(r"(?:Run|run|Build with|Next)[: ]+'?python3? (?:scripts/)?\w+_build\.py", text)


LINT_COMMANDS = (
    "ruff==0.17.0",
    "ruff check --isolated --target-version py310 --select E4,E7,E9,F",
    "shellcheck -S warning ubx-*.sh scripts/matter_vendor/*.sh",
)


@pytest.mark.parametrize("path", [
    SDK_ROOT.parent / ".gitlab-ci.yml",
    SDK_ROOT.parent / ".github" / "workflows" / "getting-started-sdk.yml",
    SDK_ROOT / "README.md",
], ids=lambda p: p.name)
def test_lint_commands_identical_everywhere(path):
    text = path.read_text(encoding="utf-8")
    for command in LINT_COMMANDS:
        assert command in text, f"{path.name} lacks: {command}"
