"""External-tool discovery and score conversion helpers."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable


class ExecutableNotFoundError(FileNotFoundError):
    """Raised when an optional desktop dependency cannot be located."""


MUSESCORE_COMMANDS = ("mscore", "musescore", "MuseScore4")
MUSESCORE_MAC_PATHS = ("/Applications/MuseScore 4.app/Contents/MacOS/mscore",)
MUSESCORE_WINDOWS_PATHS = (
    r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
    r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
)

SMARTSCORE_COMMANDS = ("SmartScore", "smartscore")
SMARTSCORE_MAC_PATHS = (
    "/Applications/SmartScore 64 Pro.app/Contents/MacOS/SmartScore 64 Pro",
    "/Applications/SmartScore.app/Contents/MacOS/SmartScore",
)
SMARTSCORE_WINDOWS_PATHS = (
    r"C:\Program Files (x86)\Musitek\SmartScore X2 Professional Edition\SmartScore_pro.exe",
)


def find_executable(
    *,
    label: str,
    env_var: str,
    commands: Iterable[str],
    known_paths: Iterable[str],
) -> Path:
    configured = os.environ.get(env_var)
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return candidate
        raise ExecutableNotFoundError(f"{env_var} points to a missing executable: {candidate}")

    for command in commands:
        discovered = shutil.which(command)
        if discovered:
            return Path(discovered)

    for path in known_paths:
        candidate = Path(path)
        if candidate.is_file():
            return candidate

    raise ExecutableNotFoundError(
        f"{label} was not found. Install it, add it to PATH, or set {env_var}."
    )


def find_musescore() -> Path:
    return find_executable(
        label="MuseScore 4",
        env_var="MUSESCORE_PATH",
        commands=MUSESCORE_COMMANDS,
        known_paths=(*MUSESCORE_MAC_PATHS, *MUSESCORE_WINDOWS_PATHS),
    )


def find_smartscore() -> Path:
    return find_executable(
        label="SmartScore",
        env_var="SMARTSCORE_PATH",
        commands=SMARTSCORE_COMMANDS,
        known_paths=(*SMARTSCORE_MAC_PATHS, *SMARTSCORE_WINDOWS_PATHS),
    )


def convert_score(
    input_path: str | Path,
    output_path: str | Path,
    *,
    musescore: str | Path | None = None,
) -> Path:
    """Convert a score through MuseScore's command-line interface."""

    source = Path(input_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Input score does not exist: {source}")
    executable = Path(musescore).expanduser() if musescore else find_musescore()
    if not executable.is_file():
        raise ExecutableNotFoundError(f"MuseScore executable does not exist: {executable}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [str(executable), str(source), "-o", str(destination)],
        check=True,
    )
    if not destination.exists():
        raise RuntimeError(f"MuseScore exited without creating the requested output: {destination}")
    return destination

