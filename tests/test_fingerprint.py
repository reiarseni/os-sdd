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
from fingerprint import compute_fingerprint, compute_artifacts_fingerprint  # noqa: E402


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

    def test_review_md_excluded(self) -> None:
        before = compute_fingerprint(self.root)
        (self.root / "REVIEW.md").write_text("Verdict: READY\n")
        after = compute_fingerprint(self.root)
        self.assertEqual(before, after)

    def test_teamlead_md_excluded(self) -> None:
        before = compute_fingerprint(self.root)
        (self.root / "TEAMLEAD.md").write_text("feedback\n")
        after = compute_fingerprint(self.root)
        self.assertEqual(before, after)


class ArtifactsFingerprintTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.change_dir = Path(self._tmp.name) / "my-change"
        (self.change_dir / "specs" / "some-capability").mkdir(parents=True)
        (self.change_dir / "proposal.md").write_text("# Proposal\n")
        (self.change_dir / "design.md").write_text("# Design\n")
        (self.change_dir / "tasks.md").write_text(
            "- [ ] 1.1 Do the thing\n- [ ] 1.2 Do another thing\n"
        )
        (self.change_dir / "specs" / "some-capability" / "spec.md").write_text(
            "#### Scenario: Something\n- **WHEN** x\n- **THEN** y\n"
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_marking_tasks_does_not_change_artifacts_fingerprint(self) -> None:
        before = compute_artifacts_fingerprint(self.change_dir)
        (self.change_dir / "tasks.md").write_text(
            "- [x] 1.1 Do the thing\n- [X] 1.2 Do another thing\n"
        )
        after = compute_artifacts_fingerprint(self.change_dir)
        self.assertEqual(before, after)

    def test_editing_delta_spec_changes_artifacts_fingerprint(self) -> None:
        before = compute_artifacts_fingerprint(self.change_dir)
        (self.change_dir / "specs" / "some-capability" / "spec.md").write_text(
            "#### Scenario: Something else\n- **WHEN** x\n- **THEN** z\n"
        )
        after = compute_artifacts_fingerprint(self.change_dir)
        self.assertNotEqual(before, after)

    def test_review_and_teamlead_files_excluded_from_artifacts_fingerprint(self) -> None:
        before = compute_artifacts_fingerprint(self.change_dir)
        (self.change_dir / "REVIEW.md").write_text("Verdict: READY\n")
        (self.change_dir / "TEAMLEAD.md").write_text("feedback\n")
        after = compute_artifacts_fingerprint(self.change_dir)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
