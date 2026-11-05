"""S00 acceptance only; parser and order-result tests start in S02."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("arguments", [[], ["--help"], ["--version"]])
def test_scaffold_entrypoint_is_available_without_data_files(
    arguments: list[str], tmp_path: Path,
) -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, "-m", "notesync", *arguments], cwd=tmp_path,
        env=env, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "notesync" in result.stdout
    if "--version" not in arguments:
        assert "not implemented" in result.stdout
    assert list(tmp_path.iterdir()) == []


def test_unimplemented_import_command_fails_without_creating_a_database(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "notesync", "import", "missing.json"], cwd=tmp_path,
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2
    assert "unrecognized arguments" in result.stderr
    assert list(tmp_path.iterdir()) == []
