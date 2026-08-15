"""High-level workflows retained from the original toolkit repositories."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from .tools import convert_score, find_smartscore


SCORE_SUFFIXES = (".mxl", ".musicxml", ".xml")


def newest_score_file(directory: Path, *, newer_than: float = 0) -> Path | None:
    candidates = [
        item
        for item in directory.rglob("*")
        if item.is_file() and item.suffix.lower() in SCORE_SUFFIXES and item.stat().st_mtime >= newer_than
    ]
    return max(candidates, key=lambda item: item.stat().st_mtime) if candidates else None


def wait_for_score_file(
    directory: str | Path,
    *,
    newer_than: float = 0,
    timeout: float | None = None,
    poll_interval: float = 2,
) -> Path:
    """Wait for SmartScore (or a user) to export a MusicXML-family file."""

    output_directory = Path(directory).expanduser().resolve()
    started = time.monotonic()
    while True:
        match = newest_score_file(output_directory, newer_than=newer_than)
        if match is not None:
            return match
        if timeout is not None and time.monotonic() - started >= timeout:
            raise TimeoutError(f"No MusicXML file appeared in {output_directory} within {timeout}s.")
        time.sleep(poll_interval)


def recognize_pdf_with_smartscore(
    pdf_path: str | Path,
    output_directory: str | Path,
    *,
    smartscore: str | Path | None = None,
    musescore: str | Path | None = None,
    timeout: float | None = None,
) -> Path:
    """Launch SmartScore, wait for manual MusicXML export, then create MSCZ."""

    source = Path(pdf_path).expanduser().resolve()
    destination_directory = Path(output_directory).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Input PDF does not exist: {source}")
    destination_directory.mkdir(parents=True, exist_ok=True)
    executable = Path(smartscore).expanduser() if smartscore else find_smartscore()
    if not executable.is_file():
        raise FileNotFoundError(f"SmartScore executable does not exist: {executable}")

    started_at = time.time()
    subprocess.Popen([str(executable), str(source)])
    exported = wait_for_score_file(
        destination_directory,
        newer_than=started_at,
        timeout=timeout,
    )
    return convert_score(
        exported,
        destination_directory / f"{exported.stem}.mscz",
        musescore=musescore,
    )

