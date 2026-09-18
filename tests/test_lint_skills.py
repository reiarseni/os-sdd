#!/usr/bin/env python3
"""Tests for tests/lint_skills.py — covers os-configuration/Copia divergente,
Script con ruta relativa, Pasos tomados de otra skill, Frase repetida en
SKILL.md y un fichero de apoyo, Frase repetida entre dos SKILL.md, Sección
inexistente and Clave compartida fuera de metadata."""
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
import lint_skills  # noqa: E402


def make_skill(root: Path, body: str, frontmatter_extra: str = "", files: dict[str, str] | None = None, name: str = "os-demo") -> Path:
    skill_dir = root / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Use when testing.\n{frontmatter_extra}---\n\n{body}\n"
    )
    for filename, content in (files or {}).items():
        path = skill_dir / filename
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
            (root / "shared" / "session-options.md").write_text("# Session options\n")
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
        errors = self.lint(body="Use `/os-propose-grill` instead when decisions cascade. End with `Next: /os-verify <name>`.")
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

    def test_repeated_phrase_in_skill_and_undeclared_file_fails(self):
        """The rule covers every supporting *.md, not only metadata.shared ones."""
        rule = "Never run the full test suite while applying a change's tasks."
        errors = self.lint(
            body=f"## 1. Apply\n\nSee `local.md`. {rule}",
            files={"local.md": f"# Local\n\n{rule}\n"},
        )
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("SKILL.md and local.md both say", errors[0])

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

    def test_retired_skill_reference_fails(self):
        errors = self.lint(body="Before step 1, read `contract.md`.\n\nEnd with `Next: /os-review-spec <name>`.")
        self.assertTrue(
            any("os-demo" in e and "os-review-spec" in e for e in errors), errors
        )

    def test_readme_migration_table_with_retired_names_passes(self):
        readme = (
            "# os-sdd\n\n"
            "## Migration\n\n"
            "| Old | New |\n"
            "|---|---|\n"
            "| `os-amend-spec` | removed |\n"
            "| `os-review-spec` | `os-review` |\n"
            "| `os-propose-drill` | `os-propose-grill` |\n"
        )
        self.assertEqual(lint_skills.readme_retired_errors(readme), [])

    def test_readme_retired_name_outside_migration_fails(self):
        readme = "# os-sdd\n\nSee `os-amend-spec` for details.\n\n## Migration\n\n(none)\n"
        errors = lint_skills.readme_retired_errors(readme)
        self.assertTrue(any("os-amend-spec" in e for e in errors), errors)

    def test_required_skill_without_session_options_fails(self):
        errors = self.lint(
            body="Before step 1, read `contract.md`.",
            frontmatter_extra="metadata:\n  shared:\n    - contract.md\n",
            files={"contract.md": "# Contract\n"},
            name="os-review",
        )
        self.assertTrue(any("os-review" in e and "session-options.md" in e for e in errors), errors)

    def test_wayfind_without_session_options_fails(self):
        errors = self.lint(
            body="Before step 1, read `contract.md`.",
            frontmatter_extra="metadata:\n  shared:\n    - contract.md\n",
            files={"contract.md": "# Contract\n"},
            name="os-wayfind",
        )
        self.assertTrue(any("os-wayfind" in e and "session-options.md" in e for e in errors), errors)

    def test_required_skill_with_session_options_passes(self):
        errors = self.lint(
            body="Before step 1, read `contract.md` and `session-options.md`.",
            frontmatter_extra="metadata:\n  shared:\n    - contract.md\n    - session-options.md\n",
            files={"contract.md": "# Contract\n", "session-options.md": "# Session options\n"},
            name="os-review",
        )
        self.assertEqual(errors, [])

    def test_apply_missing_tdd_mode_file_fails(self):
        errors = self.lint(
            body="Before step 1, read `contract.md`.",
            files={"modes/standard.md": "# Standard\n"},
            name="os-apply",
        )
        self.assertTrue(any("os-apply" in e and "modes/tdd.md" in e for e in errors), errors)

    def test_apply_before_step_1_names_mode_file_fails(self):
        errors = self.lint(
            body="Before step 1, read `modes/standard.md`.",
            files={"modes/standard.md": "# Standard\n", "modes/tdd.md": "# TDD\n"},
            name="os-apply",
        )
        self.assertTrue(
            any("os-apply" in e and "modes/standard.md" in e and "Before step 1" in e for e in errors), errors
        )

    def test_next_line_names_retired_apply_tdd_fails(self):
        errors = self.lint(body="Before step 1, read `contract.md`.\n\nEnd with `Next: /os-apply-tdd <name>`.")
        self.assertTrue(any("os-apply-tdd" in e for e in errors), errors)

    def test_retired_apply_tdd_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills"
            (skills_dir / "os-apply-tdd").mkdir(parents=True)
            errors = lint_skills.retired_directory_errors(skills_dir)
        self.assertTrue(any("os-apply-tdd" in e for e in errors), errors)

    def test_readme_apply_tdd_in_migration_only_passes(self):
        readme = (
            "# os-sdd\n\n"
            "## Migration\n\n"
            "| Old | New |\n"
            "|---|---|\n"
            "| `os-apply-tdd` | `os-apply` |\n"
        )
        self.assertEqual(lint_skills.readme_retired_errors(readme), [])

    def test_session_options_declared_but_missing_from_before_step_1_fails(self):
        errors = self.lint(
            body="Before step 1, read `contract.md`.",
            frontmatter_extra="metadata:\n  shared:\n    - contract.md\n    - session-options.md\n",
            files={"contract.md": "# Contract\n", "session-options.md": "# Session options\n"},
            name="os-explore",
        )
        self.assertTrue(
            any("os-explore" in e and "Before step 1" in e and "session-options.md" in e for e in errors), errors
        )


class CrossSkillDuplicationTest(unittest.TestCase):
    def errors(self, first_body: str, second_body: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = make_skill(root, body=first_body, name="os-first")
            second = make_skill(root, body=second_body, name="os-second")
            return lint_skills.cross_skill_duplication_errors([first, second])

    def test_same_rule_in_two_skills_fails(self):
        rule = "Ask the user before creating any artifact in the change directory."
        errors = self.errors(f"## 1. Start\n\n{rule}", f"## 1. Start\n\n{rule.upper()}")
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("os-first and os-second: both SKILL.md say", errors[0])
        self.assertIn("ask the user before creating any artifact", errors[0])

    def test_shared_scaffolding_passes(self):
        """Headings, the "Before step 1" line and pointer-only lines are exempt."""
        scaffolding = (
            "Before step 1, read `interview.md`, `proposal-flow.md`, `session-options.md` and `next-step.md`.\n\n"
            '## 1. Before the interview\n\nSee "Before the interview" in `proposal-flow.md`.\n\n'
        )
        errors = self.errors(
            scaffolding + "## 2. Interview\n\nOrder the rounds by theme, two to four questions each.",
            scaffolding + "## 2. Grill\n\nWork the frontier round after round until nothing is left.",
        )
        self.assertEqual(errors, [])

    def test_different_skills_pass(self):
        errors = self.errors("## 1. Map\n\nResolve exactly one open decision per invocation.", "## 1. Verify\n\nRun the full suite and cite its real output.")
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
