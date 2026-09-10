from pathlib import Path

import pytest

from harness import Harness


def test_operator_can_register_a_workspace_and_list_it(tmp_path: Path) -> None:
    harness = Harness()
    workspace_dir = tmp_path / "repo"
    workspace_dir.mkdir()
    (workspace_dir / ".git").mkdir()

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
    (first / ".git").mkdir()
    (second / ".git").mkdir()

    harness.register_workspace(str(first))
    harness.register_workspace(str(second))

    paths = [w.path for w in harness.list_workspaces()]
    assert paths == [first.resolve(), second.resolve()]


def test_register_workspace_rejects_directory_that_is_not_a_git_repo(
    tmp_path: Path,
) -> None:
    harness = Harness()
    plain_dir = tmp_path / "not-git"
    plain_dir.mkdir()

    with pytest.raises(ValueError, match="git"):
        harness.register_workspace(str(plain_dir))


def test_register_workspace_is_idempotent_for_the_same_path(tmp_path: Path) -> None:
    harness = Harness()
    workspace_dir = tmp_path / "repo"
    workspace_dir.mkdir()
    (workspace_dir / ".git").mkdir()

    harness.register_workspace(str(workspace_dir))
    harness.register_workspace(str(workspace_dir))

    workspaces = harness.list_workspaces()
    assert len(workspaces) == 1
    assert workspaces[0].path == workspace_dir.resolve()
