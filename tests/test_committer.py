from pathlib import Path
import subprocess

import pytest

from harness import Agent, Harness, RunStatus


def _run_git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _real_git_workspace(tmp_path: Path, name: str = "repo") -> Path:
    workspace = tmp_path / name
    workspace.mkdir()
    _run_git(workspace, "init")
    _run_git(workspace, "config", "user.email", "operador@example.com")
    _run_git(workspace, "config", "user.name", "Operador")
    (workspace / "README.md").write_text("base\n", encoding="utf-8")
    _run_git(workspace, "add", "README.md")
    _run_git(workspace, "commit", "-m", "initial")
    return workspace


def test_committer_proposes_message_then_commits_on_confirm(tmp_path: Path) -> None:
    harness = Harness()
    workspace = _real_git_workspace(tmp_path)
    harness.register_workspace(str(workspace))
    (workspace / "feature.txt").write_text("new\n", encoding="utf-8")

    run = harness.start_run(str(workspace), Agent.COMMITTER)
    assert run.status == RunStatus.RUNNING
    assert run.proposed_message
    assert "feature.txt" in run.proposed_message

    completed = harness.confirm_commit(run.id)
    assert completed.status == RunStatus.COMPLETED
    assert "feature.txt" in _run_git(workspace, "show", "--name-only", "--pretty=", "HEAD")
    assert "new" in _run_git(workspace, "show", "HEAD:feature.txt")


def test_committer_keeps_proposing_after_reject_until_confirm(tmp_path: Path) -> None:
    harness = Harness()
    workspace = _real_git_workspace(tmp_path)
    harness.register_workspace(str(workspace))
    (workspace / "a.txt").write_text("a\n", encoding="utf-8")

    run = harness.start_run(str(workspace), Agent.COMMITTER)
    first_message = run.proposed_message

    rejected = harness.reject_commit_message(run.id)
    assert rejected.status == RunStatus.RUNNING
    assert rejected.proposed_message
    assert rejected.proposed_message != first_message

    completed = harness.confirm_commit(run.id)
    assert completed.status == RunStatus.COMPLETED
    assert _run_git(workspace, "log", "-1", "--pretty=%s") == completed.proposed_message


def test_committer_excludes_gitignore_and_denylist_paths(tmp_path: Path) -> None:
    harness = Harness()
    harness.set_denylist([".env", "*.secret"])
    workspace = _real_git_workspace(tmp_path)
    (workspace / ".gitignore").write_text("ignored.log\n", encoding="utf-8")
    _run_git(workspace, "add", ".gitignore")
    _run_git(workspace, "commit", "-m", "ignore")
    harness.register_workspace(str(workspace))

    (workspace / "keep.txt").write_text("keep\n", encoding="utf-8")
    (workspace / "ignored.log").write_text("noise\n", encoding="utf-8")
    (workspace / ".env").write_text("SECRET=1\n", encoding="utf-8")
    (workspace / "token.secret").write_text("nope\n", encoding="utf-8")

    run = harness.start_run(str(workspace), Agent.COMMITTER)
    harness.confirm_commit(run.id)

    names = _run_git(workspace, "show", "--name-only", "--pretty=", "HEAD")
    assert "keep.txt" in names
    assert "ignored.log" not in names
    assert ".env" not in names
    assert "token.secret" not in names
    assert not _run_git(workspace, "ls-files", ".env")
    assert (workspace / ".env").read_text(encoding="utf-8") == "SECRET=1\n"


def test_committer_does_not_push(tmp_path: Path) -> None:
    harness = Harness()
    workspace = _real_git_workspace(tmp_path)
    remote = tmp_path / "remote.git"
    _run_git(tmp_path, "init", "--bare", str(remote))
    _run_git(workspace, "remote", "add", "origin", str(remote))
    harness.register_workspace(str(workspace))
    (workspace / "local-only.txt").write_text("x\n", encoding="utf-8")

    run = harness.start_run(str(workspace), Agent.COMMITTER)
    harness.confirm_commit(run.id)

    remote_count = _run_git(remote, "rev-list", "--count", "--all")
    assert remote_count == "0"


def test_cancel_committer_run_leaves_working_tree_uncommitted(tmp_path: Path) -> None:
    harness = Harness()
    workspace = _real_git_workspace(tmp_path)
    harness.register_workspace(str(workspace))
    (workspace / "pending.txt").write_text("pending\n", encoding="utf-8")

    run = harness.start_run(str(workspace), Agent.COMMITTER)
    harness.cancel_run(run.id)

    status = _run_git(workspace, "status", "--porcelain")
    assert "pending.txt" in status
    assert "pending" not in _run_git(workspace, "log", "--oneline")
