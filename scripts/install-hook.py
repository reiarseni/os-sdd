#!/usr/bin/env python3
"""Install (or update) the os-sdd SessionStart hook into a project.

Usage: install-hook.py <project> [--update]

Copies session-start.py, os_state.py, fingerprint.py, os_config.py and
VERSION into <project>/.claude/hooks/os/, writes SOURCE (this os-sdd root,
so the hook can detect a stale copy), and — unless
--update is passed — registers the hook in <project>/.claude/settings.json's
SessionStart array without duplicating or removing existing entries.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES_TO_COPY = [
    ROOT / "hooks" / "session-start.py",
    ROOT / "hooks" / "os_state.py",
    ROOT / "hooks" / "VERSION",
    ROOT / "scripts" / "fingerprint.py",
    ROOT / "scripts" / "os_config.py",
]

HOOK_COMMAND = 'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/os/session-start.py"'


def copy_files(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for source in FILES_TO_COPY:
        shutil.copyfile(source, target_dir / source.name)
    (target_dir / "SOURCE").write_text(str(ROOT))


def register_hook(settings_path: Path) -> bool:
    """Adds the SessionStart entry unless it's already registered. Returns
    True if it added it, False if it was already present."""
    settings = {}
    if settings_path.exists():
        settings = json.loads(settings_path.read_text())

    hooks = settings.setdefault("hooks", {})
    session_start = hooks.setdefault("SessionStart", [])

    for group in session_start:
        for entry in group.get("hooks", []):
            if entry.get("command") == HOOK_COMMAND:
                return False

    session_start.append({
        "hooks": [{"type": "command", "command": HOOK_COMMAND, "timeout": 10}]
    })
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n")
    return True


def main() -> int:
    args = sys.argv[1:]
    update_only = "--update" in args
    positional = [a for a in args if not a.startswith("--")]
    if not positional:
        print("usage: install-hook.py <project> [--update]", file=sys.stderr)
        return 2
    project = Path(positional[0]).resolve()

    target_dir = project / ".claude" / "hooks" / "os"
    copy_files(target_dir)
    print(f"copied hook files to {target_dir}")

    if update_only:
        print("--update: settings.json left untouched")
        return 0

    settings_path = project / ".claude" / "settings.json"
    added = register_hook(settings_path)
    if added:
        print(f"registered SessionStart hook in {settings_path}")
    else:
        print(f"SessionStart hook already registered in {settings_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
