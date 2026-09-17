#!/usr/bin/env python3
"""Tests for tests/lint_skills.py — covers os-configuration/Copia divergente,
Script con ruta relativa, Pasos tomados de otra skill, Frase repetida en
SKILL.md y shared, Sección inexistente and Clave compartida fuera de metadata."""
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
import lint_skills  # noqa: E402


def make_skill(root: Path, body: str, frontmatter_extra: str = "", files: dict[str, str] | None = None) -> Path:
    skill_dir = root / "skills" / "os-demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: os-demo\ndescription: Use when testing.\n{frontmatter_extra}---\n\n{body}\n"
    )
    for name, content in (files or {}).items():
        path = skill_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return skill_dir


class LintSkillsTest(unittest.TestCase):
    def lint(self, shared_source: str = "# Contract\n", **kwargs) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "tool.py").write_text("print('ok')\n")
            (root / "shared").mkdir()
            (root / "shared" / "contract.md").write_text(shared_source)
            skill_dir = make_skill(root, **kwargs)
            with unittest.mock.patch.object(lint_skills, "SCRIPTS_DIR", root / "scripts"), \
                    unittest.mock.patch.object(lint_skills, "SHARED_DIR", root / "shared"):
                return lint_skills.lint_skill(skill_dir)

    def test_top_level_shared_key_fails(self):
        for key in ("shared", "shared-scripts"):
            with self.subTest(key=key):
                errors = self.lint(body="Body.", frontmatter_extra=f"{key}:\n  - contract.md\n")
                self.assertTrue(any(f"'{key}:' at the top level" in e and "metadata:" in e for e in errors), errors)

    def test_shared_under_metadata_passes(self):
        errors = self.lint(
            body="See `contract.md`.",
            frontmatter_extra="metadata:\n  shared:\n    - contract.md\n",
            files={"contract.md": "# Contract\n"},
        )
        self.assertEqual(errors, [])

    def test_diverging_shared_copy_fails(self):
        errors = self.lint(
            body="See `contract.md`.",
            frontmatter_extra="metadata:\n  shared:\n    - contract.md\n",
            files={"contract.md": "# Contract, edited locally\n"},
        )
        self.assertTrue(any("os-demo" in e and "'contract.md' diverges" in e for e in errors), errors)

    def test_bare_script_path_fails(self):
        errors = self.lint(body="Run `python3 scripts/tool.py <change> 2.1`.")
        self.assertTrue(any("without ${CLAUDE_SKILL_DIR}/" in e for e in errors), errors)

    def test_bundled_script_with_skill_dir_passes(self):
        errors = self.lint(
            body='Run `python3 "${CLAUDE_SKILL_DIR}/scripts/tool.py"`.',
            frontmatter_extra="metadata:\n  shared-scripts:\n    - tool.py\n",
            files={"scripts/tool.py": "print('ok')\n"},
        )
        self.assertEqual(errors, [])

    def test_skill_dir_script_missing_from_skill_fails(self):
        errors = self.lint(body='Run `python3 "${CLAUDE_SKILL_DIR}/scripts/tool.py"`.')
        self.assertTrue(any("has no scripts/tool.py" in e for e in errors), errors)

    def test_diverging_script_copy_fails(self):
        errors = self.lint(
            body='Run `python3 "${CLAUDE_SKILL_DIR}/scripts/tool.py"`.',
            frontmatter_extra="metadata:\n  shared-scripts:\n    - tool.py\n",
            files={"scripts/tool.py": "print('stale')\n"},
        )
        self.assertTrue(any("diverges" in e for e in errors), errors)

    def test_script_reference_in_supporting_file_fails(self):
        errors = self.lint(body="See `notes.md`.", files={"notes.md": "Run ${CLAUDE_SKILL_DIR}/scripts/tool.py\n"})
        self.assertTrue(any("notes.md references 'scripts/tool.py'" in e for e in errors), errors)
        self.assertTrue(any("only substitutes in SKILL.md" in e for e in errors), errors)

    def test_borrowed_steps_fail(self):
        for phrase in (
            "Same as `os-apply`: read everything.",
            "Lightweight review, same checklist as\n`os-apply`.",
            "Identical structure to `os-propose` step 4.",
            "Same gate as /os-propose.",
        ):
            with self.subTest(phrase=phrase):
                errors = self.lint(body=phrase)
                self.assertTrue(any("borrows steps from another skill" in e and "move the shared text to shared/" in e for e in errors), errors)

    def test_recommending_another_skill_passes(self):
        errors = self.lint(body="Use `/os-propose-drill` instead when decisions cascade. End with `Next: /os-verify <name>`.")
        self.assertEqual(errors, [])

    def test_repeated_phrase_in_skill_and_shared_fails(self):
        rule = "Never run the full test suite while applying a change's tasks."
        contract = f"# Contract\n\n*{rule}*\n"
        errors = self.lint(
            shared_source=contract,
            body=f"## 1. Apply\n\n{rule.upper()}",
            frontmatter_extra="metadata:\n  shared:\n    - contract.md\n",
            files={"contract.md": contract},
        )
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("SKILL.md and contract.md both say", errors[0])
        self.assertIn("never run the full test suite while applying a change's tasks", errors[0])

    def test_phrase_shorter_than_eight_words_passes(self):
        contract = "# Contract\n\nRun the tests for the files you touched.\n"
        errors = self.lint(
            shared_source=contract,
            body="Then run the tests for the files you changed.",
            frontmatter_extra="metadata:\n  shared:\n    - contract.md\n",
            files={"contract.md": contract},
        )
        self.assertEqual(errors, [])

    def test_missing_section_fails(self):
        for body in ('See "Close" in `contract.md`.', 'See `contract.md` ("Close").'):
            with self.subTest(body=body):
                errors = self.lint(body=body, files={"contract.md": "# Contract\n\n## Read once\n"})
                self.assertTrue(any("broken section reference" in e and "no heading 'Close'" in e for e in errors), errors)

    def test_existing_section_passes(self):
        errors = self.lint(body='See "Close" in\n`contract.md`.', files={"contract.md": "# Contract\n\n## Close\n"})
        self.assertEqual(errors, [])

    def test_section_in_missing_file_fails(self):
        errors = self.lint(body='See "Close" in `absent.md`.')
        self.assertTrue(any("doesn't include" in e for e in errors), errors)

    def test_bare_below_or_above_fails(self):
        for body in ("Fill in every section above.", "The rules below apply."):
            with self.subTest(body=body):
                errors = self.lint(body=body)
                self.assertTrue(any("without naming a section" in e for e in errors), errors)

    def test_named_section_below_must_exist_in_same_file(self):
        errors = self.lint(body='See "Close" below.\n\n## 2. Close\n')
        self.assertEqual(errors, [])
        errors = self.lint(body='See "Starting from an exploration" below.')
        self.assertTrue(any("no heading 'Starting from an exploration'" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
