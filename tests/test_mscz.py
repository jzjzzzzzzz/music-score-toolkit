import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

from music_score_toolkit.mscz import (
    PitchRangeError,
    ScoreFormatError,
    transpose_mscx,
    transpose_mscz,
)

SCORE_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<museScore version="4.0">
  <Score>
    <Staff><Measure>
      <KeySig><accidental>-2</accidental></KeySig>
      <Chord id="keep-me"><durationType>quarter</durationType>
        <Note><pitch>70</pitch><tpc>12</tpc><accidental>flat</accidental><Tie/></Note>
        <Note><pitch>74</pitch><tpc>16</tpc></Note>
      </Chord>
      <Rest><durationType>half</durationType></Rest>
    </Measure></Staff>
  </Score>
</museScore>
"""


def test_transposes_notes_and_key_without_removing_structure():
    rendered, report = transpose_mscx(SCORE_XML, "Bb", "C")
    root = ET.fromstring(rendered)

    assert [int(item.text) for item in root.iter("pitch")] == [72, 76]
    assert root.find(".//KeySig/accidental").text == "0"
    assert root.find(".//Chord").attrib["id"] == "keep-me"
    assert root.find(".//Tie") is not None
    assert root.find(".//Rest/durationType").text == "half"
    assert report.notes_changed == 2
    assert report.key_signatures_changed == 1
    assert report.semitone_shift == 2


def test_preserves_explicit_flat_spelling_and_uses_target_for_unmarked_notes():
    rendered, _ = transpose_mscx(SCORE_XML, "Bb", "Db")
    tpcs = [int(item.text) for item in ET.fromstring(rendered).iter("tpc")]
    assert tpcs == [9, 13]


def test_rejects_out_of_range_pitch_by_default():
    xml = b"<museScore><Score><Note><pitch>127</pitch></Note></Score></museScore>"
    with pytest.raises(PitchRangeError):
        transpose_mscx(xml, "C", "D")


def test_transposes_archive_and_preserves_other_entries(tmp_path: Path):
    source = tmp_path / "source.mscz"
    output = tmp_path / "out.mscz"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("score.mscx", SCORE_XML)
        archive.writestr("META-INF/container.xml", b"container-marker")
        archive.writestr("Thumbnails/thumbnail.png", b"image-marker")

    report = transpose_mscz(source, output, "Bb", "C")

    with zipfile.ZipFile(output) as archive:
        assert archive.read("META-INF/container.xml") == b"container-marker"
        assert archive.read("Thumbnails/thumbnail.png") == b"image-marker"
        pitches = [int(item.text) for item in ET.fromstring(archive.read("score.mscx")).iter("pitch")]
    assert pitches == [72, 76]
    assert report.score_entries_changed == 1


def test_invalid_archive_is_reported(tmp_path: Path):
    source = tmp_path / "invalid.mscz"
    source.write_text("not a zip")
    with pytest.raises(ScoreFormatError):
        transpose_mscz(source, tmp_path / "out.mscz", "C", "D")
