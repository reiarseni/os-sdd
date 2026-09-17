#!/usr/bin/env python3
"""Tests for hooks/os_state.py — covers os-session-continuity/Change in verify
phase, and the four change phases, using JSON shapes fixed from OpenSpec 1.3.1."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "hooks"))
sys.path.insert(0, str(ROOT / "scripts"))
import os_state  # noqa: E402
from fingerprint import compute_fingerprint  # noqa: E402

# Fixed shapes captured from `openspec` 1.3.1 --json output.
STATUS_JSON_ALL_DONE = {
    "changeName": "demo",
    "schemaName": "spec-driven",
    "isComplete": True,
    "applyRequires": ["tasks"],
    "artifacts": [
        {"id": "proposal", "outputPath": "proposal.md", "status": "done"},
        {"id": "design", "outputPath": "design.md", "status": "done"},
        {"id": "specs", "outputPath": "specs/**/*.md", "status": "done"},
        {"id": "tasks", "outputPath": "tasks.md", "status": "done"},
    ],
}

STATUS_JSON_TASKS_PENDING = {
    "changeName": "demo",
    "schemaName": "spec-driven",
    "isComplete": False,
    "applyRequires": ["tasks"],
    "artifacts": [
        {"id": "proposal", "outputPath": "proposal.md", "status": "done"},
        {"id": "design", "outputPath": "design.md", "status": "done"},
        {"id": "specs", "outputPath": "specs/**/*.md", "status": "done"},
        {"id": "tasks", "outputPath": "tasks.md", "status": "pending"},
    ],
}


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def init_repo(root: Path) -> None:
    run(["git", "init", "-q"], root)
    run(["git", "config", "user.email", "test@test.test"], root)
    run(["git", "config", "user.name", "Test"], root)


def make_change(root: Path, name: str) -> Path:
    change_dir = root / "openspec" / "changes" / name
    change_dir.mkdir(parents=True)
    (change_dir / "proposal.md").write_text("Implementation: standard\n")
    (change_dir / "design.md").write_text("# Design\n")
    (change_dir / "tasks.md").write_text("- [ ] 1.1 do thing\n")
    return change_dir


def fake_run_json(list_response: dict, status_response: dict):
    def _fake(cmd: list[str], cwd: Path):
        if cmd[1] == "list":
            return list_response
        return status_response

    return _fake


class OsStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        init_repo(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_missing_apply_required_artifact_is_propose_phase(self) -> None:
        make_change(self.root, "demo")
        status = dict(STATUS_JSON_ALL_DONE, artifacts=[
            {"id": "proposal", "status": "done"},
            {"id": "design", "status": "done"},
            {"id": "specs", "status": "done"},
            {"id": "tasks", "status": "pending"},
        ])
        list_json = {"changes": [{"name": "demo", "completedTasks": 0, "totalTasks": 0}]}
        with patch.object(os_state, "_run_json", side_effect=fake_run_json(list_json, status)):
            result = os_state.change_phase(self.root, "demo")
        self.assertEqual(result["phase"], "propose")
        self.assertEqual(result["skill"], "/os-propose")

    def test_pending_tasks_is_apply_phase(self) -> None:
        make_change(self.root, "demo")
        list_json = {"changes": [{"name": "demo", "completedTasks": 0, "totalTasks": 1}]}
        with patch.object(os_state, "_run_json", side_effect=fake_run_json(list_json, STATUS_JSON_ALL_DONE)):
            result = os_state.change_phase(self.root, "demo")
        self.assertEqual(result["phase"], "apply")
        self.assertEqual(result["skill"], "/os-apply")

    def test_all_tasks_done_no_verify_is_verify_phase(self) -> None:
        make_change(self.root, "demo")
        list_json = {"changes": [{"name": "demo", "completedTasks": 1, "totalTasks": 1}]}
        with patch.object(os_state, "_run_json", side_effect=fake_run_json(list_json, STATUS_JSON_ALL_DONE)):
            result = os_state.change_phase(self.root, "demo")
        self.assertEqual(result["phase"], "verify")
        self.assertEqual(result["skill"], "/os-verify")

    def test_fresh_pass_is_archive_phase(self) -> None:
        change_dir = make_change(self.root, "demo")
        run(["git", "add", "."], self.root)
        run(["git", "commit", "-q", "-m", "initial"], self.root)
        fingerprint = compute_fingerprint(self.root)
        (change_dir / "VERIFY.md").write_text(f"Verdict: PASS\nFingerprint: {fingerprint}\n")

        list_json = {"changes": [{"name": "demo", "completedTasks": 1, "totalTasks": 1}]}
        with patch.object(os_state, "_run_json", side_effect=fake_run_json(list_json, STATUS_JSON_ALL_DONE)):
            result = os_state.change_phase(self.root, "demo")
        self.assertEqual(result["phase"], "archive")
        self.assertEqual(result["skill"], "/os-verify")

    def test_stale_pass_is_verify_phase(self) -> None:
        change_dir = make_change(self.root, "demo")
        run(["git", "add", "."], self.root)
        run(["git", "commit", "-q", "-m", "initial"], self.root)
        fingerprint = compute_fingerprint(self.root)
        (change_dir / "VERIFY.md").write_text(f"Verdict: PASS\nFingerprint: {fingerprint}\n")
        (change_dir / "tasks.md").write_text("- [x] 1.1 do thing\n- [ ] 1.2 more\n")  # invalidates fingerprint

        list_json = {"changes": [{"name": "demo", "completedTasks": 2, "totalTasks": 2}]}
        with patch.object(os_state, "_run_json", side_effect=fake_run_json(list_json, STATUS_JSON_ALL_DONE)):
            result = os_state.change_phase(self.root, "demo")
        self.assertEqual(result["phase"], "verify")

    def test_exploration_is_open_until_a_change_links_it(self) -> None:
        explorations_dir = self.root / "openspec" / "explorations"
        explorations_dir.mkdir(parents=True)
        (explorations_dir / "2026-09-16-topic.md").write_text("## Open questions\n\n(none)\n")
        self.assertEqual(os_state.open_explorations(self.root), ["2026-09-16-topic.md"])

        change_dir = make_change(self.root, "demo")
        (change_dir / "proposal.md").write_text(
            "Exploration: openspec/explorations/2026-09-16-topic.md\n\nImplementation: standard\n"
        )
        self.assertEqual(os_state.open_explorations(self.root), [])

    def test_exploration_linked_from_an_archived_change_is_not_open(self) -> None:
        explorations_dir = self.root / "openspec" / "explorations"
        explorations_dir.mkdir(parents=True)
        (explorations_dir / "2026-09-16-topic.md").write_text("## Open questions\n\n(none)\n")
        archived_dir = self.root / "openspec" / "changes" / "archive" / "2026-09-16-demo"
        archived_dir.mkdir(parents=True)
        (archived_dir / "proposal.md").write_text(
            "Exploration: openspec/explorations/2026-09-16-topic.md\n"
        )
        self.assertEqual(os_state.open_explorations(self.root), [])

    def test_map_with_open_decision_subheading_is_open(self) -> None:
        maps_dir = self.root / "openspec" / "maps"
        maps_dir.mkdir(parents=True)
        (maps_dir / "demo-map.md").write_text(
            "## Open decisions\n\n### Which storage\n\nBlocked by: none\n"
        )
        self.assertEqual(os_state.open_maps(self.root), ["demo-map"])

    def test_map_with_placeholder_open_decisions_is_not_open(self) -> None:
        maps_dir = self.root / "openspec" / "maps"
        maps_dir.mkdir(parents=True)
        (maps_dir / "demo-map.md").write_text(
            "## Open decisions\n\n(none — this stretch is fully resolved)\n"
        )
        self.assertEqual(os_state.open_maps(self.root), [])

    def test_cli_failure_falls_back_to_disk(self) -> None:
        make_change(self.root, "demo")
        with patch.object(os_state, "_run_json", return_value=None):
            changes = os_state.list_changes(self.root)
        self.assertEqual(changes[0]["name"], "demo")
        self.assertEqual(changes[0]["totalTasks"], 1)
        self.assertEqual(changes[0]["completedTasks"], 0)


if __name__ == "__main__":
    unittest.main()
