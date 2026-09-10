from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from uuid import uuid4

from harness.git_workspace import (
    changed_paths,
    create_commit,
    filter_commit_paths,
    propose_message,
)


@dataclass(frozen=True)
class Workspace:
    path: Path


class Agent(str, Enum):
    STUB = "stub"
    CODER = "coder"
    REVIEWER = "reviewer"
    COMMITTER = "committer"


class RunStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True)
class Run:
    id: str
    workspace_path: Path
    agent: Agent
    status: RunStatus
    proposed_message: str | None = None
    proposal_attempt: int = 0


class Harness:
    def __init__(self) -> None:
        self._workspaces: list[Workspace] = []
        self._runs: list[Run] = []
        self._denylist: list[str] = []

    def register_workspace(self, path: str | Path) -> Workspace:
        resolved = Path(path).resolve()
        if not resolved.is_dir():
            raise FileNotFoundError(f"Workspace path is not a directory: {resolved}")
        if not (resolved / ".git").exists():
            raise ValueError(f"Workspace path is not a git repository: {resolved}")
        for existing in self._workspaces:
            if existing.path == resolved:
                return existing
        workspace = Workspace(path=resolved)
        self._workspaces.append(workspace)
        return workspace

    def list_workspaces(self) -> list[Workspace]:
        return list(self._workspaces)

    def set_denylist(self, patterns: list[str]) -> None:
        self._denylist = list(patterns)

    def list_denylist(self) -> list[str]:
        return list(self._denylist)

    def start_run(self, workspace_path: str | Path, agent: Agent) -> Run:
        resolved = Path(workspace_path).resolve()
        if not any(w.path == resolved for w in self._workspaces):
            raise ValueError(f"Workspace is not registered: {resolved}")
        if any(
            r.workspace_path == resolved and r.status == RunStatus.RUNNING
            for r in self._runs
        ):
            raise RuntimeError(f"Workspace already has a running Run: {resolved}")
        run = Run(
            id=str(uuid4()),
            workspace_path=resolved,
            agent=agent,
            status=RunStatus.RUNNING,
        )
        if agent == Agent.COMMITTER:
            run = self._with_commit_proposal(run, attempt=1)
        self._runs.append(run)
        return run

    def cancel_run(self, run_id: str) -> Run:
        for index, run in enumerate(self._runs):
            if run.id != run_id:
                continue
            if run.status != RunStatus.RUNNING:
                raise RuntimeError(f"Run is not running: {run_id}")
            cancelled = replace(run, status=RunStatus.CANCELLED)
            self._runs[index] = cancelled
            return cancelled
        raise KeyError(f"Unknown Run: {run_id}")

    def reject_commit_message(self, run_id: str) -> Run:
        run = self._require_running_committer(run_id)
        updated = self._with_commit_proposal(run, attempt=run.proposal_attempt + 1)
        self._replace_run(updated)
        return updated

    def confirm_commit(self, run_id: str) -> Run:
        run = self._require_running_committer(run_id)
        if not run.proposed_message:
            raise RuntimeError(f"Committer Run has no proposed message: {run_id}")
        paths = filter_commit_paths(
            changed_paths(run.workspace_path),
            self._denylist,
        )
        create_commit(run.workspace_path, paths, run.proposed_message)
        completed = replace(run, status=RunStatus.COMPLETED)
        self._replace_run(completed)
        return completed

    def list_historico(self, workspace_path: str | Path) -> list[Run]:
        resolved = Path(workspace_path).resolve()
        return [run for run in self._runs if run.workspace_path == resolved]

    def _with_commit_proposal(self, run: Run, attempt: int) -> Run:
        paths = filter_commit_paths(changed_paths(run.workspace_path), self._denylist)
        message = propose_message(paths, attempt)
        return replace(run, proposed_message=message, proposal_attempt=attempt)

    def _require_running_committer(self, run_id: str) -> Run:
        for run in self._runs:
            if run.id != run_id:
                continue
            if run.agent != Agent.COMMITTER:
                raise RuntimeError(f"Run is not a Committer: {run_id}")
            if run.status != RunStatus.RUNNING:
                raise RuntimeError(f"Run is not running: {run_id}")
            return run
        raise KeyError(f"Unknown Run: {run_id}")

    def _replace_run(self, updated: Run) -> None:
        for index, run in enumerate(self._runs):
            if run.id == updated.id:
                self._runs[index] = updated
                return
        raise KeyError(f"Unknown Run: {updated.id}")
