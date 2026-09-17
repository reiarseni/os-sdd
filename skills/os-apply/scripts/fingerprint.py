#!/usr/bin/env python3
"""Content fingerprint of a repo (or a subtree), for os-verify's PASS gate.

sha256 over the path and content of every file `git ls-files -co
--exclude-standard` reports (tracked + new untracked, minus ignored),
sorted by path, excluding any VERIFY.md or HANDOFF.md. Depends on neither
HEAD nor mtimes: a commit that changes nothing doesn't invalidate a PASS,
and writing VERIFY.md itself doesn't either.
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

EXCLUDED_NAMES = {"VERIFY.md", "HANDOFF.md", "REVIEW.md", "TEAMLEAD.md"}
CHECKBOX_RE = re.compile(r"^(\s*-\s\[)[xX](\])", re.MULTILINE)


def list_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    paths = [line for line in result.stdout.splitlines() if line]
    return sorted(p for p in paths if Path(p).name not in EXCLUDED_NAMES)


def compute_fingerprint(repo_root: Path) -> str:
    hasher = hashlib.sha256()
    for rel_path in list_files(repo_root):
        full_path = repo_root / rel_path
        try:
            content = full_path.read_bytes()
        except (FileNotFoundError, IsADirectoryError):
            continue
        hasher.update(rel_path.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(content)
        hasher.update(b"\0")
    return hasher.hexdigest()


def artifact_files(change_dir: Path) -> list[Path]:
    paths = []
    for name in ("proposal.md", "design.md", "tasks.md"):
        path = change_dir / name
        if path.exists():
            paths.append(path)
    specs_dir = change_dir / "specs"
    if specs_dir.exists():
        paths.extend(sorted(p for p in specs_dir.rglob("*") if p.is_file()))
    return sorted(p for p in paths if p.name not in EXCLUDED_NAMES)


def compute_artifacts_fingerprint(change_dir: Path) -> str:
    hasher = hashlib.sha256()
    for path in artifact_files(change_dir):
        rel_path = path.relative_to(change_dir).as_posix()
        content = path.read_bytes()
        if path.name == "tasks.md":
            content = CHECKBOX_RE.sub(r"\1 \2", content.decode("utf-8")).encode("utf-8")
        hasher.update(rel_path.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(content)
        hasher.update(b"\0")
    return hasher.hexdigest()


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--artifacts":
        change_dir = Path("openspec") / "changes" / args[1]
        print(compute_artifacts_fingerprint(change_dir))
        return 0
    repo_root = Path(args[0]) if args else Path.cwd()
    print(compute_fingerprint(repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
