from pathlib import Path

import pytest

from harness import Harness


def test_operator_can_register_a_workspace_and_list_it(tmp_path: Path) -> None:
    harness = Harness()
    workspace_dir = tmp_path / "repo"
    workspace_dir.mkdir()

    harness.register_workspace(str(workspace_dir))

    workspaces = harness.list_workspaces()
    assert len(workspaces) == 1
    assert workspaces[0].path == workspace_dir.resolve()


def test_list_workspaces_is_empty_before_any_registration() -> None:
    harness = Harness()
    assert harness.list_workspaces() == []


def test_register_workspace_rejects_missing_directory(tmp_path: Path) -> None:
    harness = Harness()
    missing = tmp_path / "does-not-exist"

    with pytest.raises(FileNotFoundError):
        harness.register_workspace(str(missing))


def test_operator_can_register_multiple_workspaces(tmp_path: Path) -> None:
    harness = Harness()
    first = tmp_path / "one"
    second = tmp_path / "two"
    first.mkdir()
    second.mkdir()

    harness.register_workspace(str(first))
    harness.register_workspace(str(second))

    paths = [w.path for w in harness.list_workspaces()]
    assert paths == [first.resolve(), second.resolve()]
