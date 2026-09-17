#!/usr/bin/env python3
"""Tests for scripts/task_brief.py — covers os-implementation/Resume
after compaction (the brief alone is enough to resume a task), Brief por id
de casilla and Id de tarea inexistente."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from task_brief import build_brief, parse_covers  # noqa: E402


def make_change(root: Path, mode: str) -> Path:
    change_dir = root / "openspec" / "changes" / "demo"
    (change_dir / "specs" / "os-implementation").mkdir(parents=True)
    (change_dir / "proposal.md").write_text(f"Implementation: {mode}\n")
    (change_dir / "design.md").write_text(
        "## Seams\n"
        "| Seam | Scenarios |\n"
        "|---|---|\n"
        "| CLI entrypoint | Resume after compaction |\n"
    )
    (change_dir / "specs" / "os-implementation" / "spec.md").write_text(
        "## ADDED Requirements\n\n"
        "### Requirement: Context read once\n\n"
        "#### Scenario: Resume after compaction\n"
        "- **WHEN** the context is compacted mid-change\n"
        "- **THEN** the skill resumes from the first unchecked task\n\n"
        "#### Scenario: Start with handoff\n"
        "- **WHEN** HANDOFF.md exists\n"
        "- **THEN** the skill reads it\n"
    )
    (change_dir / "tasks.md").write_text(
        "## 1. Section\n\n"
        "- [ ] 1.1 infra task — covers: none (scaffolding)\n"
        "- [ ] 1.2 real task — covers: os-implementation/Resume after compaction\n\n"
        "## 2. Section\n\n"
        "- [ ] 2.1 handoff task — covers: os-implementation/Start with handoff\n"
    )
    return root


class TaskBriefTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_covers_none_has_no_scenarios(self) -> None:
        make_change(self.root, "standard")
        brief = build_brief(self.root, "demo", 1)
        self.assertIn("infra task", brief)
        self.assertIn("No scenarios", brief)

    def test_standard_brief_has_scenario_text_no_seam(self) -> None:
        make_change(self.root, "standard")
        brief = build_brief(self.root, "demo", 2)
        self.assertIn("real task", brief)
        self.assertIn("the context is compacted mid-change", brief)
        self.assertNotIn("Seam:", brief)

    def test_tdd_brief_includes_seam(self) -> None:
        make_change(self.root, "tdd")
        brief = build_brief(self.root, "demo", 2)
        self.assertIn("Seam:", brief)
        self.assertIn("CLI entrypoint", brief)

    def test_out_of_range_task_errors(self) -> None:
        make_change(self.root, "standard")
        brief = build_brief(self.root, "demo", 99)
        self.assertIn("error", brief)

    def test_brief_by_task_id(self) -> None:
        make_change(self.root, "standard")
        brief = build_brief(self.root, "demo", "2.1")
        self.assertIn("handoff task", brief)
        self.assertIn("HANDOFF.md exists", brief)
        self.assertNotIn("real task", brief)

    def test_integer_string_is_still_a_position(self) -> None:
        make_change(self.root, "standard")
        self.assertIn("real task", build_brief(self.root, "demo", "2"))

    def test_unknown_task_id_lists_valid_ids(self) -> None:
        make_change(self.root, "standard")
        brief = build_brief(self.root, "demo", "9.9")
        self.assertTrue(brief.startswith("error:"), brief)
        self.assertIn("1.1, 1.2, 2.1", brief)

    def test_parse_covers_splits_multiple_scenarios(self) -> None:
        text, pairs = parse_covers("do X — covers: cap/One, cap/Two")
        self.assertEqual(text, "do X")
        self.assertEqual(pairs, [("cap", "One"), ("cap", "Two")])


if __name__ == "__main__":
    unittest.main()
