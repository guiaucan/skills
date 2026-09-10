from pathlib import Path
import subprocess

import pytest

from harness import Agent, Harness, ParecerVerdict, RunStatus


def _run_git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repo_with_upstream(tmp_path: Path) -> Path:
    workspace = tmp_path / "repo"
    workspace.mkdir()
    _run_git(workspace, "init")
    _run_git(workspace, "config", "user.email", "operador@example.com")
    _run_git(workspace, "config", "user.name", "Operador")
    _run_git(workspace, "checkout", "-b", "main")
    (workspace / "README.md").write_text("base\n", encoding="utf-8")
    _run_git(workspace, "add", "README.md")
    _run_git(workspace, "commit", "-m", "initial")
    _run_git(workspace, "checkout", "-b", "feature")
    (workspace / "feature.txt").write_text("work\n", encoding="utf-8")
    _run_git(workspace, "add", "feature.txt")
    _run_git(workspace, "commit", "-m", "feature")
    (workspace / "wip.txt").write_text("dirty\n", encoding="utf-8")
    _run_git(workspace, "branch", "--set-upstream-to=main", "feature")
    return workspace


def _repo_without_upstream(tmp_path: Path) -> Path:
    workspace = tmp_path / "solo"
    workspace.mkdir()
    _run_git(workspace, "init")
    _run_git(workspace, "config", "user.email", "operador@example.com")
    _run_git(workspace, "config", "user.name", "Operador")
    (workspace / "README.md").write_text("base\n", encoding="utf-8")
    _run_git(workspace, "add", "README.md")
    _run_git(workspace, "commit", "-m", "initial")
    return workspace


def test_reviewer_uses_upstream_default_and_stores_parecer(tmp_path: Path) -> None:
    harness = Harness()
    workspace = _repo_with_upstream(tmp_path)
    harness.register_workspace(str(workspace))

    run = harness.start_run(str(workspace), Agent.REVIEWER)

    assert run.status == RunStatus.COMPLETED
    assert run.agent == Agent.REVIEWER
    assert run.review_target == "@{upstream}"

    pareceres = harness.list_pareceres(str(workspace))
    assert len(pareceres) == 1
    parecer = pareceres[0]
    assert parecer.run_id == run.id
    assert parecer.verdict in {
        ParecerVerdict.APROVADO,
        ParecerVerdict.COM_RESSALVAS,
        ParecerVerdict.REJEITADO,
    }
    assert "feature.txt" in parecer.notes or "wip.txt" in parecer.notes


def test_reviewer_requires_explicit_target_without_upstream(tmp_path: Path) -> None:
    harness = Harness()
    workspace = _repo_without_upstream(tmp_path)
    harness.register_workspace(str(workspace))

    with pytest.raises(ValueError, match="upstream"):
        harness.start_run(str(workspace), Agent.REVIEWER)


def test_reviewer_accepts_explicit_target_without_upstream(tmp_path: Path) -> None:
    harness = Harness()
    workspace = _repo_without_upstream(tmp_path)
    (workspace / "change.txt").write_text("x\n", encoding="utf-8")
    harness.register_workspace(str(workspace))

    run = harness.start_run(str(workspace), Agent.REVIEWER, target="HEAD")

    assert run.status == RunStatus.COMPLETED
    assert run.review_target == "HEAD"
    pareceres = harness.list_pareceres(str(workspace))
    assert len(pareceres) == 1
    assert pareceres[0].target == "HEAD"


def test_parecer_does_not_block_committer(tmp_path: Path) -> None:
    harness = Harness()
    workspace = _repo_with_upstream(tmp_path)
    harness.register_workspace(str(workspace))
    harness.start_run(str(workspace), Agent.REVIEWER)

    committer = harness.start_run(str(workspace), Agent.COMMITTER)
    completed = harness.confirm_commit(committer.id)

    assert completed.status == RunStatus.COMPLETED
    assert "wip.txt" in _run_git(workspace, "show", "--name-only", "--pretty=", "HEAD")
