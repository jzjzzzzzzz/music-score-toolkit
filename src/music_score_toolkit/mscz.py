"""Loss-minimizing transposition for MuseScore MSCX and MSCZ scores."""

from __future__ import annotations

import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .keys import KEY_SIGNATURES, calculate_shift, normalize_key, spelling_for_key, tpc_for_pitch


class ScoreFormatError(ValueError):
    """Raised when a score container or XML document is unsupported."""


class PitchRangeError(ValueError):
    """Raised instead of silently clipping a note outside the MIDI range."""


@dataclass(frozen=True, slots=True)
class TransposeReport:
    from_key: str
    to_key: str
    semitone_shift: int
    notes_changed: int
    key_signatures_changed: int
    score_entries_changed: int = 1


def _spelling_preference(note: ET.Element, target_key: str) -> str:
    accidental = note.find("accidental")
    text = accidental.text.lower() if accidental is not None and accidental.text else ""
    if "flat" in text:
        return "flat"
    if "sharp" in text:
        return "sharp"
    return spelling_for_key(target_key)


def transpose_mscx(
    content: bytes | str,
    from_key: str,
    to_key: str,
    *,
    strict_pitch_range: bool = True,
) -> tuple[bytes, TransposeReport]:
    """Transpose one MuseScore XML document and return bytes plus a report.

    Only pitch, TPC spelling, and conventional key-signature fields are
    modified. Chords, durations, rests, ties, lyrics, layout, and other score
    elements remain structurally untouched.
    """

    source_key = normalize_key(from_key)
    target_key = normalize_key(to_key)
    shift = calculate_shift(source_key, target_key)
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise ScoreFormatError(f"Invalid MSCX XML: {exc}") from exc

    note_count = 0
    for note in root.iter("Note"):
        pitch = note.find("pitch")
        if pitch is None or pitch.text is None:
            continue
        try:
            current = int(pitch.text)
        except ValueError as exc:
            raise ScoreFormatError(f"Invalid MuseScore pitch value: {pitch.text!r}") from exc
        updated = current + shift
        if not 0 <= updated <= 127:
            if strict_pitch_range:
                raise PitchRangeError(
                    f"Transposition moves MIDI pitch {current} to {updated}; "
                    "no output was written."
                )
            updated = min(127, max(0, updated))
        pitch.text = str(updated)

        tpc = note.find("tpc")
        if tpc is None:
            tpc = ET.SubElement(note, "tpc")
        tpc.text = str(tpc_for_pitch(updated, _spelling_preference(note, target_key)))
        note_count += 1

    key_signature_count = 0
    target_signature = KEY_SIGNATURES.get(target_key)
    if target_signature is not None:
        for key_signature in root.iter("KeySig"):
            accidental = key_signature.find("accidental")
            if accidental is not None:
                accidental.text = str(target_signature)
                key_signature_count += 1

    had_declaration = (
        content.lstrip().startswith(b"<?xml")
        if isinstance(content, bytes)
        else content.lstrip().startswith("<?xml")
    )
    rendered = ET.tostring(root, encoding="utf-8", xml_declaration=had_declaration)
    return rendered, TransposeReport(
        from_key=source_key,
        to_key=target_key,
        semitone_shift=shift,
        notes_changed=note_count,
        key_signatures_changed=key_signature_count,
    )


def transpose_mscz(
    input_path: str | Path,
    output_path: str | Path,
    from_key: str,
    to_key: str,
    *,
    strict_pitch_range: bool = True,
) -> TransposeReport:
    """Transpose every MSCX score entry inside an MSCZ archive atomically."""

    source = Path(input_path).expanduser().resolve()
    destination = Path(output_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Input MSCZ file does not exist: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    note_count = 0
    signature_count = 0
    score_count = 0
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temp_name = handle.name

        try:
            source_zip = zipfile.ZipFile(source, "r")
        except zipfile.BadZipFile as exc:
            raise ScoreFormatError(f"Not a valid MSCZ/ZIP archive: {source}") from exc

        with source_zip, zipfile.ZipFile(temp_name, "w") as target_zip:
            score_entries = [info.filename for info in source_zip.infolist() if info.filename.endswith(".mscx")]
            if not score_entries:
                raise ScoreFormatError("MSCZ archive does not contain an .mscx score entry.")

            for info in source_zip.infolist():
                payload = source_zip.read(info.filename)
                if info.filename.endswith(".mscx"):
                    payload, report = transpose_mscx(
                        payload,
                        from_key,
                        to_key,
                        strict_pitch_range=strict_pitch_range,
                    )
                    note_count += report.notes_changed
                    signature_count += report.key_signatures_changed
                    score_count += 1
                target_zip.writestr(info, payload)

        os.replace(temp_name, destination)
        temp_name = None
    finally:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)

    return TransposeReport(
        from_key=normalize_key(from_key),
        to_key=normalize_key(to_key),
        semitone_shift=calculate_shift(from_key, to_key),
        notes_changed=note_count,
        key_signatures_changed=signature_count,
        score_entries_changed=score_count,
    )

