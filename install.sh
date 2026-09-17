#!/usr/bin/env bash
# Installs the os-* skill family as symlinks — per-project by default, or
# globally in ~/.claude/skills/ for personal use across every project.
#
# Usage:
#   ./install.sh <project>        symlink skills/os-* into <project>/.claude/skills/ (idempotent)
#   ./install.sh                  symlink skills/os-* into ~/.claude/skills/ (idempotent, global)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$ROOT/skills"
GLOBAL_TARGET_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

install_skills() {
  local target_dir="$1"
  mkdir -p "$target_dir"
  local linked=0 skipped=0

  for skill_path in "$SKILLS_DIR"/os-*; do
    [ -d "$skill_path" ] || continue
    name="$(basename "$skill_path")"
    dest="$target_dir/$name"

    if [ -L "$dest" ]; then
      current_target="$(readlink -f "$dest" || true)"
      wanted_target="$(readlink -f "$skill_path")"
      if [ "$current_target" = "$wanted_target" ]; then
        echo "ok: $name already linked"
        continue
      fi
      echo "skip: $dest is a symlink to a different location, leaving it alone"
      skipped=$((skipped + 1))
      continue
    fi

    if [ -e "$dest" ]; then
      echo "skip: $dest exists and is not our symlink, leaving it alone"
      skipped=$((skipped + 1))
      continue
    fi

    ln -s "$skill_path" "$dest"
    echo "linked: $name"
    linked=$((linked + 1))
  done

  echo "$linked linked, $skipped skipped, in $target_dir"
}

case "${1:-}" in
  "")
    install_skills "$GLOBAL_TARGET_DIR"
    ;;
  --*)
    echo "usage: $0 [<project>]" >&2
    exit 2
    ;;
  *)
    install_skills "$1/.claude/skills"
    ;;
esac
