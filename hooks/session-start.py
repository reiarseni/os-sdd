#!/usr/bin/env python3
"""SessionStart hook: suggests the os-* skill that matches the project's
current state. Never blocks, never forces a skill.

Reads a JSON payload on stdin (hook_event_name, cwd, ...) and, only if
openspec/ exists and openspec/os.yaml has session_hook: on, prints
hookSpecificOutput.additionalContext with at most 5 lines. On any error, or
when disabled, exits 0 with no output — the session continues normally.
"""
import json
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))
if (_here.parent / "scripts").exists():
    sys.path.insert(0, str(_here.parent / "scripts"))

import os_config  # noqa: E402
import os_state  # noqa: E402

MAX_LINES = 5


def read_project_root() -> Path:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}
    cwd = payload.get("cwd")
    return Path(cwd) if cwd else Path.cwd()


def version_warning(hook_dir: Path) -> str | None:
    installed_version_file = hook_dir / "VERSION"
    source_file = hook_dir / "SOURCE"
    if not installed_version_file.exists() or not source_file.exists():
        return None
    try:
        installed_version = installed_version_file.read_text().strip()
        source_root = Path(source_file.read_text().strip())
        canonical_version_file = source_root / "hooks" / "VERSION"
        if not canonical_version_file.exists():
            return None
        canonical_version = canonical_version_file.read_text().strip()
    except OSError:
        return None
    if installed_version != canonical_version:
        return "os hook: stale copy — run scripts/install-hook.py --update"
    return None


def build_context(project_root: Path, hook_dir: Path) -> str | None:
    if not (project_root / "openspec").is_dir():
        return None
    if not os_config.session_hook_enabled(project_root):
        return None

    state = os_state.compute_state(project_root)
    lines: list[str] = []

    warning = version_warning(hook_dir)
    if warning:
        lines.append(warning)

    for change in state["changes"]:
        marker = " (HANDOFF.md)" if change.get("handoff") else ""
        lines.append(f"{change['name']}: phase {change['phase']}{marker} → {change['skill']}")

    if state["maps"]:
        lines.append("mapas abiertos: " + ", ".join(state["maps"]))
    if state["explorations"]:
        lines.append("exploraciones abiertas: " + ", ".join(state["explorations"]))

    if not lines:
        return None
    return "\n".join(lines[:MAX_LINES])


def main() -> int:
    try:
        project_root = read_project_root()
        hook_dir = Path(__file__).resolve().parent
        context = build_context(project_root, hook_dir)
    except Exception:
        return 0

    if not context:
        return 0

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
