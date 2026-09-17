#!/usr/bin/env python3
"""Tests for scripts/os_config.py — covers os-configuration/Project
without os.yaml."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from os_config import read_config, session_hook_enabled  # noqa: E402


class OsConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_missing_file_defaults_to_off(self) -> None:
        config = read_config(self.root)
        self.assertEqual(config["session_hook"], "off")
        self.assertFalse(session_hook_enabled(self.root))

    def test_reads_session_hook_on(self) -> None:
        (self.root / "openspec").mkdir()
        (self.root / "openspec" / "os.yaml").write_text("version: 1\nsession_hook: on   # comment\n")
        self.assertTrue(session_hook_enabled(self.root))

    def test_reads_session_hook_off(self) -> None:
        (self.root / "openspec").mkdir()
        (self.root / "openspec" / "os.yaml").write_text("version: 1\nsession_hook: off\n")
        self.assertFalse(session_hook_enabled(self.root))


if __name__ == "__main__":
    unittest.main()
