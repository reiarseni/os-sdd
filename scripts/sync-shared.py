#!/usr/bin/env python3
"""Copy shared contracts and scripts into the skills/os-*/ dirs that declare them.

A skill declares them in its SKILL.md frontmatter, e.g.:

    ---
    name: os-apply
    description: Use when ...
    metadata:
      shared:
        - select-change.md
        - next-step.md
      shared-scripts:
        - task_brief.py
    ---

`metadata.shared` files are copied verbatim from shared/<file> to
skills/<skill>/<file> (one level, same basename). `metadata.shared-scripts` files are
copied from scripts/<file> to skills/<skill>/scripts/<file>, so the skill can
run them as `${CLAUDE_SKILL_DIR}/scripts/<file>` from any project it's
installed into. scripts/ stays the source of truth because the SessionStart
hook and the tests import from there.
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_frontmatter import parse_metadata_list, read_skill_frontmatter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT / "shared"
SCRIPTS_DIR = ROOT / "scripts"
SKILLS_DIR = ROOT / "skills"


def sync() -> list[str]:
    copied: list[str] = []
    if not SKILLS_DIR.exists():
        return copied
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        frontmatter = read_skill_frontmatter(skill_md)
        for filename in parse_metadata_list(frontmatter, "shared"):
            source = SHARED_DIR / filename
            if not source.exists():
                print(f"warning: {skill_dir.name} declares {filename}, missing in shared/", file=sys.stderr)
                continue
            dest = skill_dir / filename
            shutil.copyfile(source, dest)
            copied.append(f"{skill_dir.name}/{filename}")
        for filename in parse_metadata_list(frontmatter, "shared-scripts"):
            source = SCRIPTS_DIR / filename
            if not source.exists():
                print(f"warning: {skill_dir.name} declares script {filename}, missing in scripts/", file=sys.stderr)
                continue
            dest = skill_dir / "scripts" / filename
            dest.parent.mkdir(exist_ok=True)
            shutil.copy2(source, dest)
            copied.append(f"{skill_dir.name}/scripts/{filename}")
    return copied


def main() -> int:
    copied = sync()
    for entry in copied:
        print(f"synced {entry}")
    print(f"{len(copied)} file(s) synced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
