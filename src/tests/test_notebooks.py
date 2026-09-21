"""Notebooks are the published verification, so CI checks what they contain, not only their schema.

Two kinds, told apart by `metadata.pilot.kind`:

- `example`: a starter that is intentionally not executed yet. Only its schema is checked, plus the
  provider-independent cells (tagged `offline`), which are run here without any credentials.
- `result` (the default when the field is missing): a notebook whose outputs are published. Every
  code cell must have run, none may have failed, and at least one must have kept an output.

Flip a notebook from `example` to `result` after running it live (see docs/03-recipe.md).
"""

from __future__ import annotations

import os
from pathlib import Path

import nbformat
import pytest
from nbformat import NotebookNode

NOTEBOOKS_DIR = Path(__file__).parent.parent / "notebooks"
NOTEBOOKS = sorted(NOTEBOOKS_DIR.glob("*.ipynb"))
OFFLINE_TAG = "offline"


def kind_of(nb: NotebookNode) -> str:
    return nb.metadata.get("pilot", {}).get("kind", "result")


def code_cells(nb: NotebookNode) -> list[NotebookNode]:
    return [c for c in nb.cells if c.cell_type == "code"]


def result_problems(nb: NotebookNode) -> list[str]:
    """Why a notebook cannot be published as a result. Empty means it can."""
    problems = []
    cells = code_cells(nb)
    if not cells:
        problems.append("has no code cells")
    for index, cell in enumerate(cells, start=1):
        if cell.get("execution_count") is None:
            problems.append(f"code cell {index} was never executed")
        if any(o.get("output_type") == "error" for o in cell.get("outputs", [])):
            problems.append(f"code cell {index} kept an error output")
    if cells and not any(c.get("outputs") for c in cells):
        problems.append("no code cell kept an output")
    return problems


def run_offline_cells(nb: NotebookNode, cwd: Path) -> int:
    """Run the cells tagged `offline` in one namespace, like a notebook. Returns how many ran."""
    namespace: dict = {"__name__": "__notebook__"}
    ran = 0
    previous = Path.cwd()
    os.chdir(cwd)  # notebooks add `Path.cwd().parent` to sys.path
    try:
        for cell in code_cells(nb):
            if OFFLINE_TAG in cell.metadata.get("tags", []):
                exec(compile(cell.source, "<notebook cell>", "exec"), namespace)
                ran += 1
    finally:
        os.chdir(previous)
    return ran


def notebook(*cells: NotebookNode, kind: str | None = None) -> NotebookNode:
    nb = nbformat.v4.new_notebook(cells=list(cells))
    if kind:
        nb.metadata["pilot"] = {"kind": kind}
    return nb


def executed(source: str = "print(1)", count: int = 1, output: bool = True) -> NotebookNode:
    cell = nbformat.v4.new_code_cell(source, execution_count=count)
    if output:
        cell.outputs = [nbformat.v4.new_output("stream", name="stdout", text="1\n")]
    return cell


def test_there_is_at_least_one_notebook():
    assert NOTEBOOKS


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_is_valid_nbformat(path):
    nbformat.validate(nbformat.read(path, as_version=4))


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_declares_a_known_kind_and_meets_its_contract(path):
    nb = nbformat.read(path, as_version=4)
    assert kind_of(nb) in {"example", "result"}
    if kind_of(nb) == "result":
        assert result_problems(nb) == [], f"{path.name} is not an executed result notebook"


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_provider_independent_cells_run_without_credentials(path, monkeypatch):
    for name in ("TYPESAFE_API_KEY", "NVIDIA_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    nb = nbformat.read(path, as_version=4)
    if kind_of(nb) == "example":
        assert run_offline_cells(nb, path.parent) >= 1, "an example notebook needs an offline cell"


def test_an_unexecuted_notebook_is_not_a_result():
    nb = notebook(nbformat.v4.new_code_cell("print(1)"))
    assert "code cell 1 was never executed" in result_problems(nb)


def test_a_notebook_without_outputs_is_not_a_result():
    assert result_problems(notebook(executed(output=False))) == ["no code cell kept an output"]


def test_a_failed_cell_is_not_a_result():
    cell = executed()
    cell.outputs = [nbformat.v4.new_output("error", ename="ValueError", evalue="x", traceback=[])]
    assert "code cell 1 kept an error output" in result_problems(notebook(cell))


def test_an_executed_notebook_with_outputs_is_a_result():
    assert result_problems(notebook(executed(count=1), executed("print(2)", count=2))) == []


def test_a_notebook_with_no_code_is_not_a_result():
    assert result_problems(notebook(nbformat.v4.new_markdown_cell("text"))) == ["has no code cells"]


def test_the_default_kind_is_result_and_only_example_is_exempt():
    assert kind_of(notebook()) == "result"
    assert kind_of(notebook(kind="example")) == "example"


def test_offline_cells_run_and_others_do_not(tmp_path):
    ok = nbformat.v4.new_code_cell("value = 1")
    ok.metadata["tags"] = [OFFLINE_TAG]
    boom = nbformat.v4.new_code_cell("raise RuntimeError('live only')")
    assert run_offline_cells(notebook(ok, boom), tmp_path) == 1


def test_a_failing_offline_cell_fails_the_test(tmp_path):
    bad = nbformat.v4.new_code_cell("raise RuntimeError('broken')")
    bad.metadata["tags"] = [OFFLINE_TAG]
    with pytest.raises(RuntimeError, match="broken"):
        run_offline_cells(notebook(bad), tmp_path)
