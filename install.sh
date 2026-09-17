#!/usr/bin/env bash
# Installs the os-* skill family as symlinks — per-project by default, or
# globally in ~/.claude/skills/ for personal use across every project.
#
# Usage:
#   ./install.sh <project>        symlink skills/os-* into <project>/.claude/skills/ (idempotent)
#   ./install.sh                  symlink skills/os-* into ~/.claude/skills/ (idempotent, global)
#   ./install.sh --retire-legacy  remove openspec-* symlinks from the global skills dir, with confirmation
set -euo pipefail
shopt -s nullglob

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$ROOT/skills"
GLOBAL_TARGET_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

cleanup_dangling_own_links() {
  local target_dir="$1"
  [ -d "$target_dir" ] || return 0

  for dest in "$target_dir"/os-*; do
    [ -L "$dest" ] || continue
    [ -e "$dest" ] && continue  # resolves fine, not dangling
    name="$(basename "$dest")"
    raw_target="$(readlink "$dest")"
    case "$raw_target" in
      "$SKILLS_DIR"/*)
        rm "$dest"
        echo "removed dangling link: $name (pointed to $raw_target, no longer exists)"
        ;;
      *)
        echo "kept dangling link: $name (points outside this repository)"
        ;;
    esac
  done
}

retire_legacy() {
  local target_dir="$GLOBAL_TARGET_DIR"
  local matches=()
  for dest in "$target_dir"/openspec-*; do
    matches+=("$dest")
  done

  if [ ${#matches[@]} -eq 0 ]; then
    echo "no openspec-* links to retire in $target_dir"
    return 0
  fi

  echo "The following legacy links will be removed from $target_dir:"
  for m in "${matches[@]}"; do
    echo "  $(basename "$m")"
  done
  read -r -p "Remove these symlinks? [y/N] " confirm || confirm=""
  if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "aborted: no links removed"
    return 0
  fi

  for m in "${matches[@]}"; do
    if [ -L "$m" ]; then
      rm "$m"
      echo "removed: $(basename "$m")"
    else
      echo "skip: $(basename "$m") is not a symlink, leaving it alone"
    fi
  done
}

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
    cleanup_dangling_own_links "$GLOBAL_TARGET_DIR"
    install_skills "$GLOBAL_TARGET_DIR"
    ;;
  --retire-legacy)
    retire_legacy
    ;;
  --*)
    echo "usage: $0 [<project>|--retire-legacy]" >&2
    exit 2
    ;;
  *)
    cleanup_dangling_own_links "$1/.claude/skills"
    install_skills "$1/.claude/skills"
    ;;
esac
