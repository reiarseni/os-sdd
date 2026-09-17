#!/usr/bin/env python3
"""Tests for scripts/fingerprint.py — covers os-verification-gate scenarios
'Writing VERIFY.md does not invalidate it', 'Later commit', 'Modified code'."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from fingerprint import compute_fingerprint  # noqa: E402


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def init_repo(root: Path) -> None:
    run(["git", "init", "-q"], root)
    run(["git", "config", "user.email", "test@test.test"], root)
    run(["git", "config", "user.name", "Test"], root)


class FingerprintTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        init_repo(self.root)
        (self.root / "code.py").write_text("print('hi')\n")
        run(["git", "add", "."], self.root)
        run(["git", "commit", "-q", "-m", "initial"], self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_writing_verify_md_does_not_change_fingerprint(self) -> None:
        before = compute_fingerprint(self.root)
        (self.root / "VERIFY.md").write_text("Verdict: PASS\n")
        after = compute_fingerprint(self.root)
        self.assertEqual(before, after)

    def test_commit_without_content_change_keeps_fingerprint(self) -> None:
        before = compute_fingerprint(self.root)
        run(["git", "commit", "-q", "--allow-empty", "-m", "noop"], self.root)
        after = compute_fingerprint(self.root)
        self.assertEqual(before, after)

    def test_modifying_code_changes_fingerprint(self) -> None:
        before = compute_fingerprint(self.root)
        (self.root / "code.py").write_text("print('bye')\n")
        after = compute_fingerprint(self.root)
        self.assertNotEqual(before, after)

    def test_handoff_md_excluded(self) -> None:
        before = compute_fingerprint(self.root)
        (self.root / "HANDOFF.md").write_text("next step\n")
        after = compute_fingerprint(self.root)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
