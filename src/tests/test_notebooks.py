"""Every notebook must be valid nbformat, so a broken one fails in CI instead of in Jupyter."""

from pathlib import Path

import nbformat
import pytest

NOTEBOOKS = sorted((Path(__file__).parent.parent / "notebooks").glob("*.ipynb"))


def test_there_is_at_least_one_notebook():
    assert NOTEBOOKS


@pytest.mark.parametrize("path", NOTEBOOKS, ids=lambda p: p.name)
def test_notebook_is_valid_nbformat(path):
    nbformat.validate(nbformat.read(path, as_version=4))
