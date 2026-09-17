#!/usr/bin/env python3
"""Tests for scripts/diff_base.py — covers os-verification-gate scenarios
'Change en rama propia con commits', 'Verificación en la rama por defecto',
'Change nunca commiteado en la rama por defecto'."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from diff_base import compute_diff_base  # noqa: E402


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def init_repo(root: Path) -> None:
    run(["git", "init", "-q", "-b", "main"], root)
    run(["git", "config", "user.email", "test@test.test"], root)
    run(["git", "config", "user.name", "Test"], root)


def commit_all(root: Path, message: str) -> str:
    run(["git", "add", "."], root)
    run(["git", "commit", "-q", "-m", message], root)
    return run(["git", "rev-parse", "HEAD"], root)


class DiffBaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        init_repo(self.root)
        (self.root / "README.md").write_text("hi\n")
        commit_all(self.root, "initial")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _add_change(self, name: str) -> None:
        change_dir = self.root / "openspec" / "changes" / name
        change_dir.mkdir(parents=True)
        (change_dir / ".openspec.yaml").write_text("id: 1\n")

    def test_own_branch_with_commits_uses_merge_base(self) -> None:
        run(["git", "checkout", "-q", "-b", "feature"], self.root)
        self._add_change("my-change")
        commit_all(self.root, "add change")
        (self.root / "scratch.txt").write_text("wip\n")  # uncommitted
        main_sha = run(["git", "rev-parse", "main"], self.root)
        base, warning = compute_diff_base(self.root, "my-change")
        self.assertEqual(base, main_sha)
        self.assertIsNone(warning)

    def test_default_branch_with_change_committed_uses_parent_commit(self) -> None:
        before_sha = run(["git", "rev-parse", "HEAD"], self.root)
        self._add_change("my-change")
        commit_all(self.root, "add change")
        (self.root / "src.py").write_text("print(1)\n")
        commit_all(self.root, "implement")
        base, warning = compute_diff_base(self.root, "my-change")
        self.assertEqual(base, before_sha)
        self.assertIsNone(warning)

    def test_default_branch_never_committed_uses_head_with_warning(self) -> None:
        self._add_change("my-change")  # never committed
        head_sha = run(["git", "rev-parse", "HEAD"], self.root)
        base, warning = compute_diff_base(self.root, "my-change")
        self.assertEqual(base, head_sha)
        self.assertIsNotNone(warning)


if __name__ == "__main__":
    unittest.main()
