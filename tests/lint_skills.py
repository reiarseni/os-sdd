#!/usr/bin/env python3
"""Lint every skills/os-*/SKILL.md against the family's conventions:

- frontmatter `name:` matches the directory name
- frontmatter `description:` contains "Use when"
- SKILL.md is under 200 lines
- local references stay one level deep (same directory, no `../`, no `/`)
- `shared:` / `shared-scripts:` live under frontmatter `metadata:`, never
  at the top level
- any file declared under `metadata.shared` is byte-identical to its
  source in shared/
- any script declared under `metadata.shared-scripts` is byte-identical to its
  source in scripts/ (copied to skills/<skill>/scripts/)
- script paths are portable: SKILL.md invokes bundled scripts only as
  `${CLAUDE_SKILL_DIR}/scripts/<file>` (a bare `scripts/<file>` resolves
  against the consumer project, where it doesn't exist), the script exists
  in the skill, and no supporting file mentions `scripts/<file>` or
  `${CLAUDE_SKILL_DIR}` at all (Claude Code only substitutes it in SKILL.md)
- no file borrows steps from another skill ("same as `os-apply`",
  "identical structure to `os-propose` step 4"): the other skill isn't
  loaded, so shared steps belong in shared/
- no rule lives twice inside a skill: a normalized run of 8 or more words
  must not appear both in SKILL.md and in one of its supporting *.md files
- no rule lives twice across skills: the same run must not appear in two
  different SKILL.md files either — headings, the "Before step 1" line and
  lines that only point at a section ('See "X" in `y.md`.') are exempt,
  since those are scaffolding rather than rules
- section references resolve: `"<Section>" in <file>.md` and
  `see <file>.md ("<Section>")` need a heading with that text in the skill's
  copy of <file>.md, `"<Section>" below/above` one in the same file, and a
  bare "below"/"above" (no section named) fails
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT / "shared"
SCRIPTS_DIR = ROOT / "scripts"
SKILLS_DIR = ROOT / "skills"

sys.path.insert(0, str(SCRIPTS_DIR))
from skill_frontmatter import parse_field, parse_metadata_list, read_frontmatter, top_level_list_keys  # noqa: E402

LINK_RE = re.compile(r"\]\(([^)]+)\)")
SKILL_DIR_VAR = "${CLAUDE_SKILL_DIR}"
SCRIPT_REF_RE = re.compile(r"(\$\{CLAUDE_SKILL_DIR\}/)?\bscripts/([\w.-]+\.(?:py|sh))")
CROSS_SKILL_RES = [
    re.compile(r"\b(?:same|identical)\b[^.;:\n]{0,60}?\b(?:as|to)\s+`?/?(os-[a-z0-9-]+)`?", re.IGNORECASE),
    re.compile(r"`?/?(os-[a-z0-9-]+)`?(?:'s)?\s+steps?\s+\d", re.IGNORECASE),
]

REPEATED_PHRASE_WORDS = 8
MARKDOWN_CHARS_RE = re.compile(r"[`*#>|\[\]()]")
WORD_RE = re.compile(r"[\w$<>{}./'-]+")
SECTION_IN_FILE_RES = [
    re.compile(r'"([^"\n]+)" in `?([\w.-]+\.md)`?'),
    re.compile(r'`?([\w.-]+\.md)`? \("([^"\n]+)"\)'),
]
SECTION_HERE_RE = re.compile(r'"([^"\n]+)" (below|above)\b')
BARE_DIRECTION_RE = re.compile(r"\b(below|above)\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^#+\s+(?:\d+\.\s+)?(.+?)\s*$", re.MULTILINE)

RETIRED_SKILL_NAMES = ("os-amend-spec", "os-review-spec", "os-propose-drill", "os-apply-tdd")
RETIRED_NAME_RE = re.compile(r"\b(?:" + "|".join(re.escape(n) for n in RETIRED_SKILL_NAMES) + r")\b")
REQUIRES_SESSION_OPTIONS = {"os-propose", "os-propose-grill", "os-review", "os-explore"}
BEFORE_STEP_1_RE = re.compile(r"Before step 1,[^\n]*", re.IGNORECASE)
MD_FILENAME_RE = re.compile(r"`([\w.-]+\.md)`")
MODE_FILENAME_RE = re.compile(r"`(modes/[\w.-]+\.md)`")
REQUIRED_MODE_FILES = {"os-apply": ("modes/standard.md", "modes/tdd.md")}


def before_step_1_files(text: str) -> set[str]:
    match = BEFORE_STEP_1_RE.search(text)
    if not match:
        return set()
    return set(MD_FILENAME_RE.findall(match.group(0)))


def before_step_1_mode_refs(text: str) -> set[str]:
    match = BEFORE_STEP_1_RE.search(text)
    if not match:
        return set()
    return set(MODE_FILENAME_RE.findall(match.group(0)))


def retired_directory_errors(skills_dir: Path) -> list[str]:
    errors = []
    for name in RETIRED_SKILL_NAMES:
        if (skills_dir / name).is_dir():
            errors.append(f"skills/{name}/ still exists — retired skill")
    return errors


def readme_retired_errors(readme_text: str) -> list[str]:
    migration_span = (-1, -1)
    migration_match = re.search(r"^## Migration\n(.*?)(\n## |\Z)", readme_text, re.DOTALL | re.MULTILINE)
    if migration_match:
        migration_span = migration_match.span(1)
    errors = []
    for m in RETIRED_NAME_RE.finditer(readme_text):
        if migration_span[0] <= m.start() < migration_span[1]:
            continue
        errors.append(f"README.md references retired skill '{m.group(0)}' outside '## Migration'")
    return errors


def normalized_words(text: str) -> list[str]:
    """Lowercase words with markdown markup and edge punctuation stripped."""
    words = WORD_RE.findall(MARKDOWN_CHARS_RE.sub(" ", text.lower()))
    return [w.strip(".,:;'-") for w in words if w.strip(".,:;'-")]


def find_repeated_phrases(text: str, other: str, size: int = REPEATED_PHRASE_WORDS) -> list[str]:
    """Returns each maximal run of `size`+ normalized words present in both texts."""
    words = normalized_words(text)
    other_words = normalized_words(other)
    other_ngrams = {tuple(other_words[i:i + size]) for i in range(len(other_words) - size + 1)}
    phrases: list[str] = []
    run_start = run_end = None
    for i in range(len(words) - size + 1):
        if tuple(words[i:i + size]) in other_ngrams:
            if run_end is not None and i <= run_end:
                run_end = i + size
            else:
                if run_start is not None:
                    phrases.append(" ".join(words[run_start:run_end]))
                run_start, run_end = i, i + size
    if run_start is not None:
        phrases.append(" ".join(words[run_start:run_end]))
    return phrases


POINTER_LINE_RE = re.compile(
    r"^\s*(?:\d+\.\s*)?(?:Then s|S)ee \"[^\"\n]+\"(?:(?: and| /) \"[^\"\n]+\")* in `[\w.-]+\.md`[.,]?\s*$"
)
BEFORE_STEP_1_LINE_RE = re.compile(r"^\s*Before step 1,", re.IGNORECASE)


def scaffolding_stripped(text: str) -> str:
    """SKILL.md body minus headings, the "Before step 1" line and pointer-only
    lines — what's left is the skill's own rules, which no other skill repeats."""
    kept = [
        line
        for line in body_without_frontmatter(text).splitlines()
        if not line.lstrip().startswith("#")
        and not BEFORE_STEP_1_LINE_RE.match(line)
        and not POINTER_LINE_RE.match(line)
    ]
    return "\n".join(kept)


def cross_skill_duplication_errors(skill_dirs: list[Path]) -> list[str]:
    """Returns every 8+ word run two different SKILL.md files both state."""
    bodies = {}
    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            bodies[skill_dir.name] = scaffolding_stripped(skill_md.read_text())
    errors = []
    names = sorted(bodies)
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            for phrase in find_repeated_phrases(bodies[first], bodies[second]):
                errors.append(
                    f"{first} and {second}: both SKILL.md say '{phrase}' — "
                    "move the shared text to shared/ and point at it from each skill"
                )
    return errors


def headings(text: str) -> set[str]:
    return {m.group(1) for m in HEADING_RE.finditer(text)}


def find_broken_section_refs(md_name: str, text: str, skill_dir: Path) -> list[str]:
    """Returns a description of every section reference that doesn't resolve."""
    body = re.sub(r"\s+", " ", body_without_frontmatter(text))
    broken: list[str] = []
    refs = [(m.group(1), m.group(2), m.group(0)) for m in SECTION_IN_FILE_RES[0].finditer(body)]
    refs += [(m.group(2), m.group(1), m.group(0)) for m in SECTION_IN_FILE_RES[1].finditer(body)]
    for section, filename, phrase in refs:
        target = skill_dir / filename
        if not target.exists():
            broken.append(f"'{phrase}' points at {filename}, which the skill doesn't include")
        elif section not in headings(target.read_text()):
            broken.append(f"'{phrase}': {filename} has no heading '{section}'")
    named_directions = set()
    for m in SECTION_HERE_RE.finditer(body):
        named_directions.add(m.start(2))
        if m.group(1) not in headings(text):
            broken.append(f"'{m.group(0)}': {md_name} has no heading '{m.group(1)}'")
    for m in BARE_DIRECTION_RE.finditer(body):
        if m.start() not in named_directions:
            context = body[max(0, m.start() - 30):m.end() + 10].strip()
            broken.append(f"'...{context}...' says '{m.group(1)}' without naming a section")
    return broken


def body_without_frontmatter(text: str) -> str:
    frontmatter = read_frontmatter(text)
    return text[len(frontmatter) + 8:] if frontmatter else text


def find_script_refs(text: str) -> list[tuple[str, bool]]:
    """Returns [(script filename, prefixed with ${CLAUDE_SKILL_DIR}/), ...]."""
    return [(m.group(2), bool(m.group(1))) for m in SCRIPT_REF_RE.finditer(text)]


def find_cross_skill_refs(text: str) -> list[str]:
    """Returns the phrases that borrow steps from another os-* skill."""
    normalized = re.sub(r"\s+", " ", text)
    return [m.group(0) for regex in CROSS_SKILL_RES for m in regex.finditer(normalized)]


def lint_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"{skill_dir.name}: missing SKILL.md"]

    text = skill_md.read_text()
    frontmatter = read_frontmatter(text)
    if not frontmatter:
        return [f"{skill_dir.name}: SKILL.md has no frontmatter"]

    name = parse_field(frontmatter, "name")
    if name != skill_dir.name:
        errors.append(f"{skill_dir.name}: frontmatter name '{name}' != directory name")

    description = parse_field(frontmatter, "description")
    if "Use when" not in description:
        errors.append(f"{skill_dir.name}: description missing 'Use when'")

    for key in top_level_list_keys(frontmatter):
        errors.append(f"{skill_dir.name}: frontmatter declares '{key}:' at the top level — move it under metadata:")

    line_count = len(text.splitlines())
    if line_count >= 200:
        errors.append(f"{skill_dir.name}: SKILL.md has {line_count} lines (>= 200)")

    for match in LINK_RE.finditer(text):
        target = match.group(1)
        if target.startswith(("http://", "https://", "#")):
            continue
        if "/" in target:
            errors.append(f"{skill_dir.name}: reference '{target}' is not one level deep")

    shared_files = parse_metadata_list(frontmatter, "shared")
    if skill_dir.name in REQUIRES_SESSION_OPTIONS and "session-options.md" not in shared_files:
        errors.append(f"{skill_dir.name}: must declare session-options.md under metadata.shared")
    if "session-options.md" in shared_files and "session-options.md" not in before_step_1_files(text):
        errors.append(f"{skill_dir.name}: declares session-options.md under metadata.shared but doesn't list it in \"Before step 1\"")

    mode_refs = before_step_1_mode_refs(text)
    if mode_refs:
        errors.append(f"{skill_dir.name}: \"Before step 1\" names {', '.join(sorted(mode_refs))} — the mode is chosen at runtime, don't preload a specific mode file")

    for filename in REQUIRED_MODE_FILES.get(skill_dir.name, ()):
        if not (skill_dir / filename).exists():
            errors.append(f"{skill_dir.name}: missing {filename}")

    for filename in shared_files:
        source = SHARED_DIR / filename
        copy = skill_dir / filename
        if not copy.exists():
            errors.append(f"{skill_dir.name}: declares shared '{filename}' but has no local copy — run scripts/sync-shared.py")
            continue
        if not source.exists():
            errors.append(f"{skill_dir.name}: shared '{filename}' has no source in shared/")
            continue
        if source.read_text() != copy.read_text():
            errors.append(f"{skill_dir.name}: local copy of '{filename}' diverges from shared/{filename} — run scripts/sync-shared.py")

    for filename in parse_metadata_list(frontmatter, "shared-scripts"):
        source = SCRIPTS_DIR / filename
        copy = skill_dir / "scripts" / filename
        if not copy.exists():
            errors.append(f"{skill_dir.name}: declares shared script '{filename}' but has no scripts/{filename} — run scripts/sync-shared.py")
            continue
        if not source.exists():
            errors.append(f"{skill_dir.name}: shared script '{filename}' has no source in scripts/")
            continue
        if source.read_bytes() != copy.read_bytes():
            errors.append(f"{skill_dir.name}: scripts/{filename} diverges from scripts/{filename} at the repo root — run scripts/sync-shared.py")

    for filename, prefixed in find_script_refs(text):
        if not prefixed:
            errors.append(f"{skill_dir.name}: SKILL.md references 'scripts/{filename}' without {SKILL_DIR_VAR}/ — it won't resolve in a consumer project")
        elif not (skill_dir / "scripts" / filename).exists():
            errors.append(f"{skill_dir.name}: SKILL.md invokes '{SKILL_DIR_VAR}/scripts/{filename}' but the skill has no scripts/{filename} — declare it under metadata.shared-scripts")

    skill_body = body_without_frontmatter(text)
    for copy in sorted(skill_dir.glob("*.md")):
        if copy.name == "SKILL.md":
            continue
        filename = copy.name
        for phrase in find_repeated_phrases(skill_body, copy.read_text()):
            errors.append(f"{skill_dir.name}: SKILL.md and {filename} both say '{phrase}' — keep the rule in one file")

    for md in sorted(skill_dir.glob("*.md")):
        md_text = md.read_text()
        if md.name != "SKILL.md":
            for filename, _ in find_script_refs(md_text):
                errors.append(f"{skill_dir.name}: {md.name} references 'scripts/{filename}' — script invocations belong in SKILL.md with {SKILL_DIR_VAR}/")
            if SKILL_DIR_VAR in md_text:
                errors.append(f"{skill_dir.name}: {md.name} uses {SKILL_DIR_VAR}, which Claude Code only substitutes in SKILL.md")
        for phrase in find_cross_skill_refs(md_text):
            errors.append(f"{skill_dir.name}: {md.name} borrows steps from another skill ('{phrase}') — move the shared text to shared/")
        for m in RETIRED_NAME_RE.finditer(md_text):
            errors.append(f"{skill_dir.name}: {md.name} references retired skill '{m.group(0)}'")
        for problem in find_broken_section_refs(md.name, md_text, skill_dir):
            errors.append(f"{skill_dir.name}: {md.name} has a broken section reference: {problem}")

    return errors


def main() -> int:
    if not SKILLS_DIR.exists():
        print("no skills/ directory found")
        return 0

    all_errors: list[str] = []
    all_errors.extend(retired_directory_errors(SKILLS_DIR))
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir())
    for skill_dir in skill_dirs:
        all_errors.extend(lint_skill(skill_dir))
    all_errors.extend(cross_skill_duplication_errors(skill_dirs))

    readme = ROOT / "README.md"
    if readme.exists():
        all_errors.extend(readme_retired_errors(readme.read_text()))

    if all_errors:
        for error in all_errors:
            print(f"FAIL: {error}")
        print(f"{len(all_errors)} error(s) across {len(skill_dirs)} skill(s)")
        return 1

    print(f"OK: {len(skill_dirs)} skill(s) linted, no errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
