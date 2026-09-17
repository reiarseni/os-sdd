#!/usr/bin/env python3
"""Compute os-sdd state for a project: change phases, HANDOFF.md presence,
open maps and explorations.

Uses `openspec list --json` / `openspec status --change <name> --json` and
falls back to reading disk directly if the CLI is missing, errors, or its
output isn't valid JSON — so an OpenSpec upgrade that changes the JSON
shape degrades gracefully instead of crashing the hook.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
for _candidate in (_here, _here.parent / "scripts"):
    if (_candidate / "fingerprint.py").exists():
        sys.path.insert(0, str(_candidate))
        break
from fingerprint import compute_fingerprint, compute_artifacts_fingerprint  # noqa: E402


def _run_json(cmd: list[str], cwd: Path) -> dict | None:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, OSError):
        return None
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def list_changes(project_root: Path) -> list[dict]:
    data = _run_json(["openspec", "list", "--json"], project_root)
    if data is not None:
        return data.get("changes", [])

    changes_dir = project_root / "openspec" / "changes"
    changes: list[dict] = []
    if not changes_dir.exists():
        return changes
    for entry in sorted(changes_dir.iterdir()):
        if not entry.is_dir() or entry.name == "archive":
            continue
        tasks_file = entry / "tasks.md"
        total = done = 0
        if tasks_file.exists():
            for line in tasks_file.read_text().splitlines():
                match = re.match(r"\s*-\s\[( |x)\]", line)
                if match:
                    total += 1
                    if match.group(1) == "x":
                        done += 1
        changes.append({"name": entry.name, "completedTasks": done, "totalTasks": total})
    return changes


def status_for_all(project_root: Path) -> dict[str, dict] | None:
    data = _run_json(["openspec", "status", "--all", "--json"], project_root)
    if data is None:
        return None
    return {c["changeName"]: c for c in data.get("changes", [])}


def artifacts_status(project_root: Path, name: str, batch: dict[str, dict] | None = None) -> dict:
    if batch is not None:
        if name in batch:
            return batch[name]
    else:
        data = _run_json(["openspec", "status", "--change", name, "--json"], project_root)
        if data is not None:
            return data

    change_dir = project_root / "openspec" / "changes" / name
    artifacts = []
    for artifact_id, rel_path in (("proposal", "proposal.md"), ("design", "design.md"), ("tasks", "tasks.md")):
        status = "done" if (change_dir / rel_path).exists() else "pending"
        artifacts.append({"id": artifact_id, "status": status})
    specs_dir = change_dir / "specs"
    specs_status = "done" if specs_dir.exists() and any(specs_dir.rglob("*.md")) else "pending"
    artifacts.append({"id": "specs", "status": specs_status})
    return {"changeName": name, "applyRequires": ["tasks"], "artifacts": artifacts}


def verify_is_fresh(project_root: Path, name: str) -> bool:
    verify_md = project_root / "openspec" / "changes" / name / "VERIFY.md"
    if not verify_md.exists():
        return False
    text = verify_md.read_text()
    verdict = re.search(r"^Verdict:\s*(\S+)", text, re.MULTILINE)
    fingerprint = re.search(r"^Fingerprint:\s*(\S+)", text, re.MULTILINE)
    if not verdict or not fingerprint or verdict.group(1) != "PASS":
        return False
    return compute_fingerprint(project_root) == fingerprint.group(1)


def review_is_fresh(project_root: Path, name: str) -> bool:
    change_dir = project_root / "openspec" / "changes" / name
    review_md = change_dir / "REVIEW.md"
    if not review_md.exists():
        return False
    text = review_md.read_text()
    verdict = re.search(r"^Verdict:\s*(\S+)", text, re.MULTILINE)
    fingerprint = re.search(r"^Fingerprint:\s*(\S+)", text, re.MULTILINE)
    if not verdict or not fingerprint or verdict.group(1) != "READY":
        return False
    return compute_artifacts_fingerprint(change_dir) == fingerprint.group(1)


def planning_is_complete(status: dict) -> bool:
    if "isPlanningComplete" in status:
        return bool(status["isPlanningComplete"])
    apply_requires = status.get("applyRequires", ["tasks"])
    artifacts = {a["id"]: a["status"] for a in status.get("artifacts", [])}
    return all(artifacts.get(a) == "done" for a in apply_requires)


def change_phase(
    project_root: Path,
    name: str,
    batch: dict[str, dict] | None = None,
    task_counts: dict | None = None,
) -> dict:
    status = artifacts_status(project_root, name, batch=batch)
    if not planning_is_complete(status):
        return {"name": name, "phase": "propose", "skill": "/os-propose"}

    if task_counts is None:
        task_counts = next((c for c in list_changes(project_root) if c["name"] == name), {})
    total = task_counts.get("totalTasks", 0)
    done = task_counts.get("completedTasks", 0)
    if total > done:
        if review_is_fresh(project_root, name):
            return {"name": name, "phase": "apply", "skill": "/os-apply"}
        return {"name": name, "phase": "review", "skill": "/os-review"}

    if verify_is_fresh(project_root, name):
        return {"name": name, "phase": "archive", "skill": "/os-verify"}

    return {"name": name, "phase": "verify", "skill": "/os-verify"}


def has_handoff(project_root: Path, name: str) -> bool:
    return (project_root / "openspec" / "changes" / name / "HANDOFF.md").exists()


def _section_has_subheading(text: str, heading: str) -> bool:
    """True if the named section has at least one `### ` entry — a
    placeholder like '(none)' with no subheading doesn't count. Each open
    decision in a map is one `### ` block (see MAP-TEMPLATE.md)."""
    match = re.search(rf"## {re.escape(heading)}\n(.*?)(\n## |\Z)", text, re.DOTALL)
    if not match:
        return False
    return "### " in match.group(1)


def open_maps(project_root: Path) -> list[str]:
    maps_dir = project_root / "openspec" / "maps"
    if not maps_dir.exists():
        return []
    return sorted(
        p.stem for p in maps_dir.glob("*.md") if _section_has_subheading(p.read_text(), "Open decisions")
    )


def _linked_explorations(project_root: Path) -> set[str]:
    """Exploration paths (as written after 'Exploration:') already linked
    from some change's proposal.md."""
    changes_dir = project_root / "openspec" / "changes"
    linked: set[str] = set()
    if not changes_dir.exists():
        return linked
    proposals = list(changes_dir.glob("*/proposal.md")) + list(changes_dir.glob("archive/*/proposal.md"))
    for proposal in proposals:
        match = re.search(r"^Exploration:\s*(\S+)", proposal.read_text(), re.MULTILINE)
        if match:
            linked.add(Path(match.group(1)).name)
    return linked


def open_explorations(project_root: Path) -> list[str]:
    """An exploration is open until some change links back to it.
    Its own 'Open questions' section doesn't decide this: a resolved
    exploration with an empty/n-a checklist is still waiting for
    os-propose(-drill) to turn it into a change."""
    explorations_dir = project_root / "openspec" / "explorations"
    if not explorations_dir.exists():
        return []
    linked = _linked_explorations(project_root)
    return sorted(p.name for p in explorations_dir.glob("*.md") if p.name not in linked)


def compute_state(project_root: Path) -> dict:
    entries = list_changes(project_root)
    batch = status_for_all(project_root)
    changes = []
    for entry in entries:
        phase = change_phase(project_root, entry["name"], batch=batch, task_counts=entry)
        phase["handoff"] = has_handoff(project_root, entry["name"])
        changes.append(phase)
    return {
        "changes": changes,
        "maps": open_maps(project_root),
        "explorations": open_explorations(project_root),
    }


def main() -> int:
    project_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    print(json.dumps(compute_state(project_root), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
