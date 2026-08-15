import zipfile
from pathlib import Path

import pytest

from music_score_toolkit.mscz import transpose_mscz

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    "fixture",
    ["auto-transpose-sample.mscz", "auto-music-transpose-sample.mscz"],
)
def test_original_mscz_samples_transpose_successfully(fixture: str, tmp_path: Path):
    source = FIXTURES / fixture
    output = tmp_path / fixture
    with zipfile.ZipFile(source) as before:
        original_entries = set(before.namelist())

    report = transpose_mscz(source, output, "Bb", "C")

    with zipfile.ZipFile(output) as after:
        assert set(after.namelist()) == original_entries
        assert after.testzip() is None
    assert report.notes_changed > 0
    assert report.score_entries_changed >= 1
