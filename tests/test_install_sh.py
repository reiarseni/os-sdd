#!/usr/bin/env python3
"""Tests for install.sh — covers os-configuration/Destino ocupado, Enlace
propio colgante, Enlace colgante ajeno, Retirada sin confirmación."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALL_SH = ROOT / "install.sh"


def run_install(args: list[str], global_target: Path | None = None, input_text: str | None = None):
    env = dict(os.environ)
    if global_target is not None:
        env["CLAUDE_SKILLS_DIR"] = str(global_target)
    return subprocess.run(
        ["bash", str(INSTALL_SH), *args],
        capture_output=True,
        text=True,
        input=input_text,
        env=env,
    )


class InstallShTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_occupied_destination_is_skipped(self) -> None:
        project = self.tmp / "project"
        skills_dir = project / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        occupied = skills_dir / "os-apply"
        occupied.mkdir()
        (occupied / "marker.txt").write_text("mine\n")

        result = run_install([str(project)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((occupied / "marker.txt").exists())
        self.assertFalse(occupied.is_symlink())
        self.assertIn("os-apply", result.stdout)

    def test_own_dangling_link_is_removed(self) -> None:
        project = self.tmp / "project"
        skills_dir = project / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        dangling = skills_dir / "os-does-not-exist-xyz"
        dangling.symlink_to(ROOT / "skills" / "os-does-not-exist-xyz")
        self.assertTrue(dangling.is_symlink())

        result = run_install([str(project)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(dangling.is_symlink())
        self.assertIn("os-does-not-exist-xyz", result.stdout)

    def test_foreign_dangling_link_is_kept(self) -> None:
        project = self.tmp / "project"
        skills_dir = project / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        foreign = skills_dir / "os-foo"
        foreign.symlink_to(self.tmp / "somewhere-else" / "os-foo")
        self.assertTrue(foreign.is_symlink())

        result = run_install([str(project)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(foreign.is_symlink())

    def test_retired_apply_tdd_link_is_removed_apply_link_kept(self) -> None:
        project = self.tmp / "project"
        skills_dir = project / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        apply_tdd_link = skills_dir / "os-apply-tdd"
        apply_tdd_link.symlink_to(ROOT / "skills" / "os-apply-tdd")
        apply_link = skills_dir / "os-apply"
        apply_link.symlink_to(ROOT / "skills" / "os-apply")

        result = run_install([str(project)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(apply_tdd_link.is_symlink())
        self.assertTrue(apply_link.is_symlink())

    def test_retire_legacy_without_confirmation_deletes_nothing(self) -> None:
        global_target = self.tmp / "global-skills"
        global_target.mkdir(parents=True)
        legacy = global_target / "openspec-explore"
        legacy.symlink_to(self.tmp / "wherever" / "openspec-explore")
        self.assertTrue(legacy.is_symlink())

        result = run_install(["--retire-legacy"], global_target=global_target, input_text="n\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(legacy.is_symlink())

    def test_retire_legacy_with_confirmation_removes_symlinks(self) -> None:
        global_target = self.tmp / "global-skills"
        global_target.mkdir(parents=True)
        legacy = global_target / "openspec-explore"
        legacy.symlink_to(self.tmp / "wherever" / "openspec-explore")

        result = run_install(["--retire-legacy"], global_target=global_target, input_text="y\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(legacy.is_symlink())


if __name__ == "__main__":
    unittest.main()
