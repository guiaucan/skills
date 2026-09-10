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
    review_diff,
    upstream_ref,
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


class ParecerVerdict(str, Enum):
    APROVADO = "aprovado"
    COM_RESSALVAS = "com_ressalvas"
    REJEITADO = "rejeitado"


@dataclass(frozen=True)
class Run:
    id: str
    workspace_path: Path
    agent: Agent
    status: RunStatus
    proposed_message: str | None = None
    proposal_attempt: int = 0
    review_target: str | None = None


@dataclass(frozen=True)
class Parecer:
    id: str
    run_id: str
    workspace_path: Path
    target: str
    verdict: ParecerVerdict
    notes: str


class Harness:
    def __init__(self) -> None:
        self._workspaces: list[Workspace] = []
        self._runs: list[Run] = []
        self._denylist: list[str] = []
        self._pareceres: list[Parecer] = []

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

    def start_run(
        self,
        workspace_path: str | Path,
        agent: Agent,
        target: str | None = None,
    ) -> Run:
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
        if agent == Agent.REVIEWER:
            run = self._complete_review(run, target)
            self._runs.append(run)
            return run
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

    def list_pareceres(self, workspace_path: str | Path) -> list[Parecer]:
        resolved = Path(workspace_path).resolve()
        return [p for p in self._pareceres if p.workspace_path == resolved]

    def _complete_review(self, run: Run, target: str | None) -> Run:
        review_target = target
        if review_target is None:
            if upstream_ref(run.workspace_path) is None:
                raise ValueError(
                    "No upstream for default Reviewer target; Operador must define target"
                )
            review_target = "@{upstream}"
        diff = review_diff(run.workspace_path, review_target)
        parecer = self._build_parecer(run, review_target, diff)
        self._pareceres.append(parecer)
        return replace(
            run,
            status=RunStatus.COMPLETED,
            review_target=review_target,
        )

    def _build_parecer(self, run: Run, target: str, diff: str) -> Parecer:
        if not diff.strip():
            verdict = ParecerVerdict.APROVADO
            notes = "Nenhuma diferença no alvo revisado."
        elif "FIXME" in diff:
            verdict = ParecerVerdict.REJEITADO
            notes = "Diff contém FIXME."
        else:
            verdict = ParecerVerdict.COM_RESSALVAS
            notes = diff if len(diff) < 2000 else diff[:2000] + "\n..."
        return Parecer(
            id=str(uuid4()),
            run_id=run.id,
            workspace_path=run.workspace_path,
            target=target,
            verdict=verdict,
            notes=notes,
        )

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
