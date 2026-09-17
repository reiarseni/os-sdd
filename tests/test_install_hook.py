#!/usr/bin/env python3
"""Tests for scripts/install-hook.py — covers os-configuration/Install
with existing hooks, Install twice."""
import importlib.util
import json
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT / "scripts" / "install-hook.py"

spec = importlib.util.spec_from_file_location("install_hook", SCRIPT_PATH)
install_hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(install_hook)  # type: ignore[union-attr]


class InstallHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.project = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_copies_expected_files(self) -> None:
        target = self.project / ".claude" / "hooks" / "os"
        install_hook.copy_files(target)
        for name in ("session-start.py", "os_state.py", "VERSION", "fingerprint.py", "os_config.py", "SOURCE"):
            self.assertTrue((target / name).exists(), name)

    def test_register_with_existing_other_hooks_keeps_them(self) -> None:
        settings_path = self.project / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True)
        settings_path.write_text(json.dumps({
            "hooks": {
                "SessionStart": [
                    {"hooks": [{"type": "command", "command": "python3 other-hook.py"}]}
                ]
            }
        }))
        added = install_hook.register_hook(settings_path)
        self.assertTrue(added)
        data = json.loads(settings_path.read_text())
        commands = [
            entry["command"]
            for group in data["hooks"]["SessionStart"]
            for entry in group["hooks"]
        ]
        self.assertIn("python3 other-hook.py", commands)
        self.assertIn(install_hook.HOOK_COMMAND, commands)

    def test_register_twice_does_not_duplicate(self) -> None:
        settings_path = self.project / ".claude" / "settings.json"
        first = install_hook.register_hook(settings_path)
        second = install_hook.register_hook(settings_path)
        self.assertTrue(first)
        self.assertFalse(second)
        data = json.loads(settings_path.read_text())
        commands = [
            entry["command"]
            for group in data["hooks"]["SessionStart"]
            for entry in group["hooks"]
        ]
        self.assertEqual(commands.count(install_hook.HOOK_COMMAND), 1)

    def test_update_only_skips_settings(self) -> None:
        settings_path = self.project / ".claude" / "settings.json"
        with unittest.mock.patch("sys.argv", ["install-hook.py", str(self.project), "--update"]):
            install_hook.main()
        self.assertFalse(settings_path.exists())


if __name__ == "__main__":
    unittest.main()
