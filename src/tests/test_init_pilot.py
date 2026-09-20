"""The init script renames the template and strips template-only blocks."""

import importlib.util
import shutil
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
        and "template-pilot-python" in p.read_text(errors="ignore")
        and p.name != "init_pilot.py"
    ]
    assert leftovers == []
    assert 'name = "pilot-demo-topic"' in (copy / "src/pyproject.toml").read_text()
    assert 'description = "a demo topic"' in (copy / "src/pyproject.toml").read_text()


def test_it_sets_the_tagline_and_drops_the_template_block_in_every_readme(copy):
    run(copy, "--keep-script")
    for readme in copy.glob("README*.md"):
        text = readme.read_text()
        assert "🚀 Pilot project for a demo topic" in text, readme.name
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
