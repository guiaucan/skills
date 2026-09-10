from __future__ import annotations

import subprocess
from fnmatch import fnmatch
from pathlib import Path


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def changed_paths(cwd: Path) -> list[str]:
    output = git(cwd, "status", "--porcelain")
    if not output:
        return []
    paths: list[str] = []
    for line in output.splitlines():
        entry = line[3:]
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        paths.append(entry.strip('"'))
    return paths


def filter_commit_paths(paths: list[str], denylist: list[str]) -> list[str]:
    allowed: list[str] = []
    for path in paths:
        if any(fnmatch(path, pattern) or fnmatch(Path(path).name, pattern) for pattern in denylist):
            continue
        allowed.append(path)
    return allowed


def propose_message(paths: list[str], attempt: int) -> str:
    if not paths:
        base = "Empty working tree"
    elif len(paths) == 1:
        base = f"Update {paths[0]}"
    else:
        base = f"Update {paths[0]} and {len(paths) - 1} more"
    if attempt <= 1:
        return base
    return f"{base} (revision {attempt})"


def create_commit(cwd: Path, paths: list[str], message: str) -> None:
    if not paths:
        raise RuntimeError("No paths left to commit after gitignore and Denylist")
    git(cwd, "add", "--", *paths)
    git(cwd, "commit", "-m", message)
