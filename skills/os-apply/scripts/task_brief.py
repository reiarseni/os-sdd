#!/usr/bin/env python3
"""Print the brief for one task: its text, the full scenarios its `covers:`
points to, and — in tdd changes — the seam for each scenario. Used by
os-apply* so a task can be worked on without re-reading every artifact.

Usage: task_brief.py <change> <id>

<id> is the task's id as written in tasks.md (e.g. `2.1`). A plain integer
with no dot is still accepted as the task's 1-based position among all
checkbox lines, in document order.
"""
import re
import sys
from pathlib import Path

TASK_RE = re.compile(r"^\s*-\s\[( |x)\]\s*(.+)$")
TASK_ID_RE = re.compile(r"^(\d+(?:\.\d+)+)\b")
COVERS_RE = re.compile(r"—\s*covers:\s*(.+)$")
SCENARIO_RE = re.compile(r"^#### Scenario:\s*(.+)$")


def find_change_dir(project_root: Path, change: str) -> Path:
    return project_root / "openspec" / "changes" / change


def read_tasks(change_dir: Path) -> list[str]:
    tasks_file = change_dir / "tasks.md"
    lines = []
    for line in tasks_file.read_text().splitlines():
        match = TASK_RE.match(line)
        if match:
            lines.append(match.group(2))
    return lines


def parse_covers(task_text: str) -> tuple[str, list[tuple[str, str]]]:
    """Returns (task text without the covers suffix, [(capability, scenario), ...])."""
    match = COVERS_RE.search(task_text)
    if not match:
        return task_text, []
    covers_str = match.group(1)
    base_text = task_text[: match.start()].rstrip(" —")
    if covers_str.strip().startswith("none"):
        return base_text, []
    pairs = []
    for entry in covers_str.split(","):
        entry = entry.strip()
        if "/" not in entry:
            continue
        capability, scenario = entry.split("/", 1)
        pairs.append((capability.strip(), scenario.strip()))
    return base_text, pairs


def find_scenario_block(spec_path: Path, scenario_name: str) -> str | None:
    if not spec_path.exists():
        return None
    lines = spec_path.read_text().splitlines()
    start = None
    for i, line in enumerate(lines):
        match = SCENARIO_RE.match(line.strip())
        if match and match.group(1).strip() == scenario_name:
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        stripped = lines[j].strip()
        if stripped.startswith("#### Scenario:") or stripped.startswith("### ") or stripped.startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end]).strip()


def find_seam(design_path: Path, scenario_name: str) -> str | None:
    if not design_path.exists():
        return None
    text = design_path.read_text()
    match = re.search(r"## Seams\n(.*?)(\n## |\Z)", text, re.DOTALL)
    if not match:
        return None
    for line in match.group(1).splitlines():
        if scenario_name in line and "|" in line:
            return line.strip()
    return None


def implementation_mode(change_dir: Path) -> str:
    proposal = change_dir / "proposal.md"
    if not proposal.exists():
        return "standard"
    for line in proposal.read_text().splitlines():
        if line.strip() == "Implementation: tdd":
            return "tdd"
    return "standard"


def task_id(task_text: str) -> str | None:
    match = TASK_ID_RE.match(task_text)
    return match.group(1) if match else None


def build_brief(project_root: Path, change: str, task: int | str) -> str:
    change_dir = find_change_dir(project_root, change)
    tasks = read_tasks(change_dir)
    if isinstance(task, int) or "." not in task:
        n = int(task)
        if n < 1 or n > len(tasks):
            return f"error: task {n} out of range (change has {len(tasks)} tasks)"
        task_text = tasks[n - 1]
    else:
        matches = [text for text in tasks if task_id(text) == task]
        if not matches:
            valid = ", ".join(i for i in (task_id(text) for text in tasks) if i)
            return f"error: no task with id {task} (valid ids: {valid})"
        task_text = matches[0]

    task_text, covers = parse_covers(task_text)
    mode = implementation_mode(change_dir)

    parts = [f"Task {task}: {task_text}", ""]
    if not covers:
        parts.append("No scenarios (infrastructure/docs task).")
    for capability, scenario in covers:
        spec_path = change_dir / "specs" / capability / "spec.md"
        block = find_scenario_block(spec_path, scenario)
        parts.append(f"## {capability}/{scenario}")
        parts.append(block if block else "(scenario text not found — check tasks.md covers: suffix)")
        if mode == "tdd":
            seam = find_seam(change_dir / "design.md", scenario)
            parts.append(f"Seam: {seam if seam else '(not declared — stop and recommend /os-review)'}")
        parts.append("")
    return "\n".join(parts).strip()


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: task_brief.py <change> <id>", file=sys.stderr)
        return 2
    change, task = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r"\d+(?:\.\d+)*", task):
        print(f"error: <id> must look like 2.1 (or a plain position), got {task!r}", file=sys.stderr)
        return 2
    brief = build_brief(Path.cwd(), change, task)
    if brief.startswith("error:"):
        print(brief, file=sys.stderr)
        return 1
    print(brief)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
