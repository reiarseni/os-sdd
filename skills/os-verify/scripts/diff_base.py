#!/usr/bin/env python3
"""Diff base for os-verify's evidence package.

Outside the default branch: the merge-base with it. On the default branch:
the parent of the commit that added the change's `.openspec.yaml` — or, if
that file was never committed, `HEAD` with a warning that the diff only
covers uncommitted changes.
"""
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def default_branch(repo_root: Path) -> str | None:
    origin_head = run(
        ["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], repo_root
    )
    if origin_head:
        return origin_head.rsplit("/", 1)[-1]
    for name in ("main", "master"):
        if run(["git", "rev-parse", "--verify", "-q", name], repo_root):
            return name
    return None


def current_branch(repo_root: Path) -> str:
    return run(["git", "symbolic-ref", "--short", "-q", "HEAD"], repo_root)


def commit_that_added(repo_root: Path, path: str) -> str | None:
    sha = run(
        ["git", "log", "--follow", "--diff-filter=A", "--format=%H", "--", path],
        repo_root,
    )
    if not sha:
        return None
    return sha.splitlines()[-1]


def compute_diff_base(repo_root: Path, change: str) -> tuple[str, str | None]:
    head = run(["git", "rev-parse", "HEAD"], repo_root)
    default = default_branch(repo_root)
    branch = current_branch(repo_root)
    if default and branch and branch != default:
        base = run(["git", "merge-base", "HEAD", default], repo_root)
        if base:
            return base, None
    openspec_yaml = f"openspec/changes/{change}/.openspec.yaml"
    added_commit = commit_that_added(repo_root, openspec_yaml)
    if added_commit:
        parent = run(["git", "rev-parse", f"{added_commit}^"], repo_root)
        if parent:
            return parent, None
    return head, (
        f"'{openspec_yaml}' was never committed on this branch — "
        "the diff only covers uncommitted changes."
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: diff_base.py <change>", file=sys.stderr)
        return 2
    base, warning = compute_diff_base(Path.cwd(), sys.argv[1])
    print(f"BASE={base}")
    if warning:
        print(warning, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
