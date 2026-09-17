#!/usr/bin/env python3
"""Tests for scripts/skill_frontmatter.py — the parser sync-shared.py and
lint_skills.py share."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from skill_frontmatter import parse_metadata_list, read_frontmatter, top_level_list_keys  # noqa: E402

FRONTMATTER = read_frontmatter(
    "---\n"
    "name: os-demo\n"
    "description: Use when testing.\n"
    "metadata:\n"
    "  shared:\n"
    "    - select-change.md\n"
    "    - next-step.md\n"
    "  shared-scripts:\n"
    "    - task_brief.py\n"
    "argument-hint: <change>\n"
    "---\n\nBody\n"
)


class SkillFrontmatterTests(unittest.TestCase):
    def test_reads_lists_under_metadata(self) -> None:
        self.assertEqual(parse_metadata_list(FRONTMATTER, "shared"), ["select-change.md", "next-step.md"])
        self.assertEqual(parse_metadata_list(FRONTMATTER, "shared-scripts"), ["task_brief.py"])

    def test_ignores_top_level_lists(self) -> None:
        frontmatter = "name: os-demo\nshared:\n  - next-step.md\n"
        self.assertEqual(parse_metadata_list(frontmatter, "shared"), [])
        self.assertEqual(top_level_list_keys(frontmatter), ["shared"])

    def test_metadata_lists_are_not_top_level(self) -> None:
        self.assertEqual(top_level_list_keys(FRONTMATTER), [])


if __name__ == "__main__":
    unittest.main()
