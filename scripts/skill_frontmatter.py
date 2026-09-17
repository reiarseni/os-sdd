#!/usr/bin/env python3
"""Frontmatter parsing shared by scripts/sync-shared.py and tests/lint_skills.py.

A skill declares the shared contracts and scripts it bundles under
`metadata:` (the documented field for custom frontmatter data), e.g.:

    ---
    name: os-apply
    description: Use when ...
    metadata:
      shared:
        - select-change.md
      shared-scripts:
        - task_brief.py
    ---
"""
from pathlib import Path

METADATA_LIST_KEYS = ("shared", "shared-scripts")


def read_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---", 4)
    if end == -1:
        return ""
    return text[4:end]


def read_skill_frontmatter(skill_md: Path) -> str:
    return read_frontmatter(skill_md.read_text())


def parse_field(frontmatter: str, field: str) -> str:
    for line in frontmatter.splitlines():
        if line.startswith(f"{field}:"):
            return line[len(field) + 1:].strip()
    return ""


def parse_metadata_list(frontmatter: str, key: str) -> list[str]:
    """Returns the items of `metadata.<key>` (list items indented four spaces)."""
    items: list[str] = []
    in_metadata = False
    in_key = False
    for line in frontmatter.splitlines():
        if not line.strip():
            continue
        if not line.startswith(" "):
            in_metadata = line.strip() == "metadata:"
            in_key = False
            continue
        if not in_metadata:
            continue
        if line.startswith("  ") and not line.startswith("   "):
            in_key = line.strip() == f"{key}:"
            continue
        if in_key and line.startswith("    - "):
            items.append(line[6:].strip())
    return items


def top_level_list_keys(frontmatter: str) -> list[str]:
    """Returns the metadata list keys wrongly declared at the top level."""
    return [
        key for key in METADATA_LIST_KEYS
        if any(line.rstrip() == f"{key}:" for line in frontmatter.splitlines())
    ]
