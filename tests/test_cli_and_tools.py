from pathlib import Path
import os

import pytest

from music_score_toolkit.cli import main
from music_score_toolkit.tools import ExecutableNotFoundError, find_executable
from music_score_toolkit.workflows import newest_score_file, wait_for_score_file


def test_cli_reports_missing_input(capsys, tmp_path: Path):
    result = main(
        [
            "transpose",
            str(tmp_path / "missing.mscz"),
            str(tmp_path / "out.mscz"),
            "--from-key",
            "C",
            "--to-key",
            "D",
        ]
    )
    assert result == 2
    assert "does not exist" in capsys.readouterr().err


def test_configured_executable_is_respected(monkeypatch, tmp_path: Path):
    executable = tmp_path / "tool"
    executable.write_text("tool")
    monkeypatch.setenv("TEST_TOOL_PATH", str(executable))
    assert (
        find_executable(
            label="Test tool",
            env_var="TEST_TOOL_PATH",
            commands=(),
            known_paths=(),
        )
        == executable
    )


def test_missing_configured_executable_is_actionable(monkeypatch):
    monkeypatch.setenv("TEST_TOOL_PATH", os.devnull + "-missing")
    with pytest.raises(ExecutableNotFoundError, match="TEST_TOOL_PATH"):
        find_executable(
            label="Test tool",
            env_var="TEST_TOOL_PATH",
            commands=(),
            known_paths=(),
        )


def test_newest_score_file_ignores_unrelated_files(tmp_path: Path):
    (tmp_path / "notes.txt").write_text("ignore")
    first = tmp_path / "first.musicxml"
    second = tmp_path / "second.mxl"
    first.write_text("first")
    second.write_text("second")
    os.utime(first, (10, 10))
    os.utime(second, (20, 20))
    assert newest_score_file(tmp_path) == second


def test_wait_for_score_file_times_out(tmp_path: Path):
    with pytest.raises(TimeoutError):
        wait_for_score_file(tmp_path, timeout=0.01, poll_interval=0.001)
