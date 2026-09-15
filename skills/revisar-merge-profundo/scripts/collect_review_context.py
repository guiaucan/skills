#!/usr/bin/env python3
"""Coleta artefatos de review: GitLab MR, GitHub PR ou branch local vs base.

Exemplos:
  python collect_review_context.py --base-branch qas --output "%USERPROFILE%/.agents/work/<marca>/review-context.md"
  python collect_review_context.py --mr-url "https://gitlab.../merge_requests/123" --output ~/.agents/work/<marca>/review-context.md

Prefira path absoluto sob ~/.agents/work/<marca>/ (ver skills/work-path.md).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class CmdResult:
    command: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run(command: list[str]) -> CmdResult:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return CmdResult(
        command=" ".join(command),
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )


def truncate_lines(text: str, max_lines: int) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    head = "\n".join(lines[:max_lines])
    return f"{head}\n... [truncated {len(lines) - max_lines} lines]"


def parse_gitlab_mr_url(url: str) -> Optional[tuple[str, str]]:
    pattern = re.compile(
        r"^https?://[^/]+/(?P<project>.+?)(?:/-)?/merge_requests/(?P<iid>\d+)(?:[/?#].*)?$"
    )
    match = pattern.match(url)
    if not match:
        return None
    return match.group("project"), match.group("iid")


def parse_github_pr_url(url: str) -> Optional[tuple[str, str]]:
    pattern = re.compile(
        r"^https?://github\.com/(?P<repo>[^/]+/[^/]+)/pull/(?P<number>\d+)(?:[/?#].*)?$"
    )
    match = pattern.match(url)
    if not match:
        return None
    return match.group("repo"), match.group("number")


def render_command_section(title: str, result: CmdResult, max_lines: int) -> str:
    content = result.stdout if result.ok else f"ERROR ({result.returncode})\n{result.stderr}"
    content = truncate_lines(content, max_lines)
    return (
        f"## {title}\n"
        f"Command: `{result.command}`\n\n"
        f"```\n{content}\n```\n"
    )


def collect_gitlab(project: str, iid: str, max_lines: int) -> str:
    header = f"# Review Context\n\nTarget: GitLab MR `{project} !{iid}`\n\n"
    info = run(
        [
            "glab",
            "mr",
            "view",
            iid,
            "--repo",
            project,
            "--json",
            "iid,title,description,author,source_branch,target_branch,state,web_url,labels",
        ]
    )
    changes = run(["glab", "mr", "changes", iid, "--repo", project])
    return (
        header
        + render_command_section("MR Metadata", info, max_lines)
        + "\n"
        + render_command_section("MR Changes", changes, max_lines)
    )


def collect_github(repo: str, number: str, max_lines: int) -> str:
    header = f"# Review Context\n\nTarget: GitHub PR `{repo} #{number}`\n\n"
    info = run(
        [
            "gh",
            "pr",
            "view",
            number,
            "--repo",
            repo,
            "--json",
            "number,title,body,author,baseRefName,headRefName,state,url,labels",
        ]
    )
    diff = run(["gh", "pr", "diff", number, "--repo", repo])
    return (
        header
        + render_command_section("PR Metadata", info, max_lines)
        + "\n"
        + render_command_section("PR Diff", diff, max_lines)
    )


def detect_default_base_branch() -> str:
    remote_head = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"])
    if remote_head.ok and remote_head.stdout.startswith("refs/remotes/origin/"):
        return remote_head.stdout.rsplit("/", 1)[-1]
    return "main"


def collect_local(base_branch: Optional[str], max_lines: int) -> str:
    base = base_branch or detect_default_base_branch()
    current_branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    fetch = run(["git", "fetch", "origin", base])
    merge_base = run(["git", "merge-base", "HEAD", f"origin/{base}"])

    if not merge_base.ok:
        return (
            "# Review Context\n\n"
            f"Target: local branch review against `origin/{base}`\n\n"
            + render_command_section("Current Branch", current_branch, max_lines)
            + "\n"
            + render_command_section("Fetch Base Branch", fetch, max_lines)
            + "\n"
            + render_command_section("Merge Base", merge_base, max_lines)
        )

    base_sha = merge_base.stdout.strip()
    stat = run(["git", "diff", "--stat", f"{base_sha}..HEAD"])
    commits = run(["git", "log", "--oneline", f"{base_sha}..HEAD"])
    names = run(["git", "diff", "--name-only", f"{base_sha}..HEAD"])
    diff = run(["git", "diff", "--patch", "--find-renames", f"{base_sha}..HEAD"])

    return (
        "# Review Context\n\n"
        f"Target: local branch review against `origin/{base}`\n\n"
        + render_command_section("Current Branch", current_branch, max_lines)
        + "\n"
        + render_command_section("Fetch Base Branch", fetch, max_lines)
        + "\n"
        + render_command_section("Merge Base", merge_base, max_lines)
        + "\n"
        + render_command_section("Changed Files", names, max_lines)
        + "\n"
        + render_command_section("Diff Stat", stat, max_lines)
        + "\n"
        + render_command_section("Commit List", commits, max_lines)
        + "\n"
        + render_command_section("Patch Diff", diff, max_lines)
    )


def build_context(mr_url: Optional[str], base_branch: Optional[str], max_lines: int) -> str:
    if mr_url:
        gitlab = parse_gitlab_mr_url(mr_url)
        if gitlab:
            return collect_gitlab(gitlab[0], gitlab[1], max_lines)

        github = parse_github_pr_url(mr_url)
        if github:
            return collect_github(github[0], github[1], max_lines)

        raise ValueError(
            "Could not parse MR/PR URL. Expected GitLab .../merge_requests/<iid> or "
            "GitHub .../pull/<number>."
        )

    return collect_local(base_branch, max_lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mr-url", help="GitLab MR or GitHub PR URL.")
    parser.add_argument(
        "--base-branch",
        help="Base branch for local review (default: origin HEAD branch, fallback main).",
    )
    parser.add_argument(
        "--max-lines-per-section",
        type=int,
        default=2500,
        help="Max number of lines per command section before truncating.",
    )
    parser.add_argument(
        "--output",
        help="Arquivo de saída (.md). Preferir path absoluto em ~/.agents/work/<marca>/review-context.md. Sem isso, imprime no stdout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output = build_context(args.mr_url, args.base_branch, args.max_lines_per_section)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output + "\n", encoding="utf-8")
        print(f"Wrote review context to: {output_path}")
        return 0

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
