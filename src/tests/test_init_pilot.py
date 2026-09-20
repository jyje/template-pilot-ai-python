"""The init script renames the template and strips template-only blocks."""

import importlib.util
import shutil
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_script():
    spec = importlib.util.spec_from_file_location("init_pilot", ROOT / "scripts" / "init_pilot.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def copy(tmp_path):
    target = tmp_path / "copy"
    shutil.copytree(
        ROOT,
        target,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            ".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "temp"
        ),
    )
    return target


def run(copy, *extra):
    script = load_script()
    return script.main(["pilot-demo-topic", "--description", "a demo topic", *extra], root=copy)


def test_it_renames_the_template_everywhere(copy):
    assert run(copy, "--keep-script") == 0
    leftovers = [
        p.relative_to(copy)
        for p in copy.rglob("*")
        if p.is_file()
        and not p.is_symlink()
        and ".git" not in p.parts
        and p.suffix not in {".png", ".ipynb"}
        and "template-pilot-ai-python" in p.read_text(errors="ignore")
        and p.name != "init_pilot.py"
    ]
    assert leftovers == []
    assert 'name = "pilot-demo-topic"' in (copy / "src/pyproject.toml").read_text()
    assert 'description = "a demo topic"' in (copy / "src/pyproject.toml").read_text()


def test_it_sets_the_tagline_and_drops_the_template_block_in_every_readme(copy):
    run(copy, "--keep-script")
    for readme in copy.glob("README*.md"):
        text = readme.read_text()
        assert "\n\n🚀 Pilot project for a demo topic\n\n" in text, readme.name  # its own paragraph
        assert "template:begin" not in text, readme.name
        assert "jyje/pilot-demo-topic" in text, readme.name


def test_it_deletes_itself_and_its_test_unless_asked_not_to(copy):
    run(copy)
    assert not (copy / "scripts" / "init_pilot.py").exists()
    assert not (copy / "src" / "tests" / "test_init_pilot.py").exists()


def test_dry_run_writes_nothing(copy):
    before = (copy / "README.md").read_text()
    run(copy, "--dry-run")
    assert (copy / "README.md").read_text() == before
    assert (copy / "scripts" / "init_pilot.py").exists()


def test_bad_names_are_rejected(copy):
    script = load_script()
    with pytest.raises(SystemExit):
        script.main(["Bad Name", "--description", "x"], root=copy)


@pytest.mark.parametrize(
    "description",
    [
        'a "quoted" description',
        "a description with a backslash: " + chr(92),
        "a description\nwith a newline",
        "an 한국어 description",
    ],
)
def test_special_characters_in_a_description_keep_pyproject_toml_valid(copy, description):
    script = load_script()
    assert script.main(["pilot-demo-topic", "--description", description, "--keep-script"], root=copy) == 0
    pyproject = tomllib.loads((copy / "src" / "pyproject.toml").read_text())
    assert pyproject["project"]["description"] == description


@pytest.mark.parametrize(
    "url",
    [
        "git@github.com:someone/pilot-x.git",
        "https://github.com/someone/pilot-x",
        "https://github.com/someone/pilot-x.git",
    ],
)
def test_the_owner_comes_from_the_origin_remote(tmp_path, url):
    import subprocess

    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "remote", "add", "origin", url], check=True)
    assert load_script().detect_owner(tmp_path) == "someone"


def test_the_owner_falls_back_to_the_template_owner_without_a_remote(tmp_path):
    script = load_script()
    assert script.detect_owner(tmp_path) == script.TEMPLATE_OWNER
