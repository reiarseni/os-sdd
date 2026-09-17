#!/usr/bin/env python3
"""Tests for hooks/session-start.py — covers os-session-continuity/Hook
disabled or no OpenSpec, Internal error; os-configuration/Stale
copy."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = ROOT / "hooks" / "session-start.py"

spec = importlib.util.spec_from_file_location("session_start", HOOK_PATH)
session_start = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_start)  # type: ignore[union-attr]


class BuildContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_no_openspec_dir_returns_none(self) -> None:
        self.assertIsNone(session_start.build_context(self.root, ROOT / "hooks"))

    def test_hook_off_returns_none(self) -> None:
        (self.root / "openspec").mkdir()
        (self.root / "openspec" / "os.yaml").write_text("version: 1\nsession_hook: off\n")
        self.assertIsNone(session_start.build_context(self.root, ROOT / "hooks"))

    def test_missing_os_yaml_returns_none(self) -> None:
        (self.root / "openspec").mkdir()
        self.assertIsNone(session_start.build_context(self.root, ROOT / "hooks"))

    def test_stale_copy_warns(self) -> None:
        (self.root / "openspec").mkdir()
        (self.root / "openspec" / "os.yaml").write_text("session_hook: on\n")
        hook_dir = self.root / ".claude" / "hooks" / "os"
        hook_dir.mkdir(parents=True)
        (hook_dir / "VERSION").write_text("0\n")
        source_root = self.root / "os-sdd-source"
        (source_root / "hooks").mkdir(parents=True)
        (source_root / "hooks" / "VERSION").write_text("1\n")
        (hook_dir / "SOURCE").write_text(str(source_root))
        context = session_start.build_context(self.root, hook_dir)
        self.assertIn("stale copy", context)


class MainEntryPointTests(unittest.TestCase):
    def run_hook(self, payload: dict) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )

    def test_no_openspec_exits_zero_silently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_hook({"cwd": tmp})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")

    def test_bad_json_on_stdin_exits_zero(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HOOK_PATH)],
            input="not json",
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
