#!/usr/bin/env python3
"""Minimal reader for openspec/os.yaml — no PyYAML dependency.

Format (edited by hand):

    version: 1
    session_hook: off   # on | off

A missing file means everything is off.
"""
from pathlib import Path

DEFAULTS = {"version": "1", "session_hook": "off"}


def read_config(project_root: Path) -> dict:
    config_path = project_root / "openspec" / "os.yaml"
    config = dict(DEFAULTS)
    if not config_path.exists():
        return config
    for line in config_path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        config[key.strip()] = value.strip()
    return config


def session_hook_enabled(project_root: Path) -> bool:
    return read_config(project_root).get("session_hook") == "on"
