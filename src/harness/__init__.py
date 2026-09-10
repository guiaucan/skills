from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path
from uuid import uuid4


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


class Harness:
    def __init__(self) -> None:
        self._workspaces: list[Workspace] = []
        self._runs: list[Run] = []

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

    def list_historico(self, workspace_path: str | Path) -> list[Run]:
        resolved = Path(workspace_path).resolve()
        return [run for run in self._runs if run.workspace_path == resolved]
