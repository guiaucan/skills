from pathlib import Path

import pytest

from harness import Agent, Harness, RunStatus


def _git_workspace(tmp_path: Path, name: str = "repo") -> Path:
    workspace_dir = tmp_path / name
    workspace_dir.mkdir()
    (workspace_dir / ".git").mkdir()
    return workspace_dir


def test_operator_can_start_a_stub_run_and_see_it_in_historico(tmp_path: Path) -> None:
    harness = Harness()
    workspace_dir = _git_workspace(tmp_path)
    harness.register_workspace(str(workspace_dir))

    run = harness.start_run(str(workspace_dir), Agent.STUB)

    assert run.agent == Agent.STUB
    assert run.status == RunStatus.RUNNING
    assert run.workspace_path == workspace_dir.resolve()

    history = harness.list_historico(str(workspace_dir))
    assert len(history) == 1
    assert history[0].id == run.id


def test_second_run_on_same_workspace_is_rejected(tmp_path: Path) -> None:
    harness = Harness()
    workspace_dir = _git_workspace(tmp_path)
    harness.register_workspace(str(workspace_dir))
    harness.start_run(str(workspace_dir), Agent.STUB)

    with pytest.raises(RuntimeError, match="Run"):
        harness.start_run(str(workspace_dir), Agent.STUB)


def test_cancel_run_ends_without_altering_workspace(tmp_path: Path) -> None:
    harness = Harness()
    workspace_dir = _git_workspace(tmp_path)
    marker = workspace_dir / "keep-me.txt"
    marker.write_text("untouched", encoding="utf-8")
    harness.register_workspace(str(workspace_dir))
    run = harness.start_run(str(workspace_dir), Agent.STUB)

    cancelled = harness.cancel_run(run.id)

    assert cancelled.status == RunStatus.CANCELLED
    assert marker.read_text(encoding="utf-8") == "untouched"
    assert (workspace_dir / ".git").is_dir()


def test_after_cancel_operator_can_start_another_run(tmp_path: Path) -> None:
    harness = Harness()
    workspace_dir = _git_workspace(tmp_path)
    harness.register_workspace(str(workspace_dir))
    first = harness.start_run(str(workspace_dir), Agent.STUB)
    harness.cancel_run(first.id)

    second = harness.start_run(str(workspace_dir), Agent.STUB)

    assert second.id != first.id
    assert second.status == RunStatus.RUNNING
    history = harness.list_historico(str(workspace_dir))
    assert [r.status for r in history] == [RunStatus.CANCELLED, RunStatus.RUNNING]


def test_runs_on_different_workspaces_can_be_active_together(tmp_path: Path) -> None:
    harness = Harness()
    first_dir = _git_workspace(tmp_path, "one")
    second_dir = _git_workspace(tmp_path, "two")
    harness.register_workspace(str(first_dir))
    harness.register_workspace(str(second_dir))

    first = harness.start_run(str(first_dir), Agent.STUB)
    second = harness.start_run(str(second_dir), Agent.STUB)

    assert first.status == RunStatus.RUNNING
    assert second.status == RunStatus.RUNNING


def test_start_run_requires_registered_workspace(tmp_path: Path) -> None:
    harness = Harness()
    workspace_dir = _git_workspace(tmp_path)

    with pytest.raises(ValueError, match="registered"):
        harness.start_run(str(workspace_dir), Agent.STUB)
