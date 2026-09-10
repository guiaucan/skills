from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Workspace:
    path: Path


class Harness:
    def __init__(self) -> None:
        self._workspaces: list[Workspace] = []

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
